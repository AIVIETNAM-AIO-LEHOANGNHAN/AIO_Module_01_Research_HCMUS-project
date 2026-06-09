from pathlib import Path

import pandas as pd
from datasets import load_dataset
from sklearn.model_selection import train_test_split


RANDOM_STATE = 42
OUT_DIR = Path("data")
OUT_DIR.mkdir(exist_ok=True)


def main():
    # 1. Load dataset UIT-VSFC
    dataset = load_dataset(
        "uitnlp/vietnamese_students_feedback",
        revision="refs/convert/parquet",
    )

    # 2. Gộp train/validation/test gốc thành một dataframe
    df = pd.concat(
        [dataset[split].to_pandas() for split in dataset.keys()],
        ignore_index=True
    )

    # 3. Chuẩn hóa tên cột
    df = df.rename(columns={
        "sentence": "text",
        "sentiment": "raw_sentiment"
    })

    # 4. Chỉ giữ 2 nhãn cần dùng:
    # raw_sentiment = 0: negative -> label = 0
    # raw_sentiment = 2: positive -> label = 1
    # raw_sentiment = 1: neutral -> bỏ
    df = df[df["raw_sentiment"].isin([0, 2])].copy()
    df["label"] = df["raw_sentiment"].map({0: 0, 2: 1}).astype(int)

    # 5. Làm sạch rất nhẹ cho Task 1:
    # chỉ strip khoảng trắng + bỏ dòng rỗng + bỏ duplicate
    df["text"] = (
        df["text"]
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    df = df[df["text"] != ""]
    df = df.drop_duplicates(subset=["text"]).reset_index(drop=True)

    # 6. Cân bằng dữ liệu, tối đa 5,000 mẫu mỗi lớp -> tổng tối đa 10,000 mẫu
    label_counts_before = df["label"].value_counts().to_dict()
    samples_per_class = min(5000, df["label"].value_counts().min())

    df_balanced = (
        df.groupby("label", group_keys=False)
        .apply(lambda x: x.sample(n=samples_per_class, random_state=RANDOM_STATE))
        .sample(frac=1, random_state=RANDOM_STATE)
        .reset_index(drop=True)
    )

    # 7. Chia train/test = 80/20
    train_df, test_df = train_test_split(
        df_balanced[["text", "label"]],
        test_size=0.2,
        stratify=df_balanced["label"],
        random_state=RANDOM_STATE
    )

    train_df = train_df.reset_index(drop=True)
    test_df = test_df.reset_index(drop=True)

    # 8. Xuất file chính cho Task 1
    train_df.to_csv(OUT_DIR / "train.csv", index=False, encoding="utf-8-sig")
    test_df.to_csv(OUT_DIR / "test.csv", index=False, encoding="utf-8-sig")

    # 9. Xuất sample 50 dòng cho QA kiểm tra nhanh
    qa_sample = df_balanced[["text", "label"]].sample(
        n=min(50, len(df_balanced)),
        random_state=RANDOM_STATE
    )
    qa_sample.to_csv(OUT_DIR / "qa_sample_50.csv", index=False, encoding="utf-8-sig")

    # 10. Tạo README_DATA.md
    train_counts = train_df["label"].value_counts().sort_index().to_dict()
    test_counts = test_df["label"].value_counts().sort_index().to_dict()

    readme = f"""# README_DATA.md

## 1. Nguồn dữ liệu

- Tên dataset: Vietnamese Students' Feedback Corpus (UIT-VSFC)
- Nguồn: Hugging Face dataset `uitnlp/vietnamese_students_feedback`
- Ngôn ngữ: Tiếng Việt
- Bài toán gốc: Phân loại cảm xúc và chủ đề trong phản hồi của sinh viên
- Bài toán sử dụng trong dự án: Phân loại cảm xúc nhị phân Positive/Negative

## 2. Lý do chọn dataset

Dataset này phù hợp với đề tài nghiên cứu tác động của stopwords lên phân loại văn bản vì:

- Dữ liệu là văn bản tiếng Việt.
- Có nhãn cảm xúc rõ ràng.
- Kích thước dữ liệu đủ lớn để nghiên cứu.
- Nội dung là các câu phản hồi ngắn, phù hợp với bài toán phân loại văn bản.

## 3. Quy đổi nhãn

Dataset gốc có 3 nhãn sentiment:

- `0`: Negative
- `1`: Neutral
- `2`: Positive

Trong dự án này, nhóm chỉ sử dụng bài toán nhị phân:

- `0`: Negative / Tiêu cực
- `1`: Positive / Tích cực

Các mẫu Neutral đã được loại bỏ.

## 4. Cấu trúc dữ liệu

Sau khi xử lý Task 1, dữ liệu được lưu trong thư mục `data/` gồm:

- `train.csv`: tập huấn luyện, chiếm 80% dữ liệu
- `test.csv`: tập kiểm tra, chiếm 20% dữ liệu
- `qa_sample_50.csv`: 50 dòng mẫu để QA kiểm tra nhanh
- `README_DATA.md`: tài liệu mô tả dữ liệu

Mỗi file `train.csv` và `test.csv` có 2 cột:

| Cột | Ý nghĩa |
|---|---|
| `text` | Văn bản tiếng Việt |
| `label` | Nhãn phân loại, 1 = tích cực, 0 = tiêu cực |

## 5. Thống kê dữ liệu

Số lượng dữ liệu trước khi cân bằng:

- Negative: {label_counts_before.get(0, 0)}
- Positive: {label_counts_before.get(1, 0)}

Số lượng dữ liệu sau khi cân bằng:

- Tổng số mẫu: {len(df_balanced)}
- Train: {len(train_df)}
- Test: {len(test_df)}

Phân bố nhãn trong train:

- Negative `0`: {train_counts.get(0, 0)}
- Positive `1`: {train_counts.get(1, 0)}

Phân bố nhãn trong test:

- Negative `0`: {test_counts.get(0, 0)}
- Positive `1`: {test_counts.get(1, 0)}

## 6. Kiểm tra chất lượng ban đầu

Các bước đã thực hiện:

- Loại bỏ mẫu Neutral.
- Chuẩn hóa khoảng trắng.
- Loại bỏ dòng rỗng.
- Loại bỏ dữ liệu trùng lặp theo cột `text`.
- Chia dữ liệu theo tỉ lệ 80/20.
- Đảm bảo file được lưu ở định dạng CSV UTF-8 with BOM (`utf-8-sig`) để mở đúng trong Excel.

## 7. Ghi chú

Task 1 chỉ thực hiện thu thập và chuẩn bị dữ liệu mẫu.  
Các bước tiền xử lý sâu hơn như lowercase, loại bỏ ký tự đặc biệt, chuẩn hóa dấu câu, loại bỏ stopwords sẽ được thực hiện ở Task 2.
"""

    (OUT_DIR / "README_DATA.md").write_text(readme, encoding="utf-8")

    print("Done Task 1.")
    print(f"Total balanced samples: {len(df_balanced)}")
    print(f"Train shape: {train_df.shape}")
    print(f"Test shape: {test_df.shape}")
    print("Files created:")
    print("- data/train.csv")
    print("- data/test.csv")
    print("- data/qa_sample_50.csv")
    print("- data/README_DATA.md")


if __name__ == "__main__":
    main()
