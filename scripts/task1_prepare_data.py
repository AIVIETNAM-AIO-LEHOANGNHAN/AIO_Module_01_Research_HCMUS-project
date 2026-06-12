"""
Task 1: Thu thập và chuẩn bị dataset UIT-VSFC.

Output:
  - data/train/raw.csv
  - data/test/raw.csv
  - data/qa_sample_50.csv
  - data/README_DATA.md
"""

import sys
from pathlib import Path

import pandas as pd
from datasets import load_dataset
from sklearn.model_selection import train_test_split

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from paths import PROJECT_ROOT, QA_SAMPLE, README_DATA, TEST_RAW, TRAIN_RAW


RANDOM_STATE = 42


def main() -> None:
    TRAIN_RAW.parent.mkdir(parents=True, exist_ok=True)
    TEST_RAW.parent.mkdir(parents=True, exist_ok=True)

    dataset = load_dataset(
        "uitnlp/vietnamese_students_feedback",
        revision="refs/convert/parquet",
    )

    df = pd.concat(
        [dataset[split].to_pandas() for split in dataset.keys()],
        ignore_index=True,
    )

    df = df.rename(columns={
        "sentence": "text",
        "sentiment": "raw_sentiment",
    })

    df = df[df["raw_sentiment"].isin([0, 2])].copy()
    df["label"] = df["raw_sentiment"].map({0: 0, 2: 1}).astype(int)

    df["text"] = (
        df["text"]
        .astype(str)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    df = df[df["text"] != ""]
    df = df.drop_duplicates(subset=["text"]).reset_index(drop=True)

    label_counts_before = df["label"].value_counts().to_dict()
    samples_per_class = min(5000, df["label"].value_counts().min())

    df_balanced = (
        df.groupby("label", group_keys=False)
        .apply(lambda x: x.sample(n=samples_per_class, random_state=RANDOM_STATE))
        .sample(frac=1, random_state=RANDOM_STATE)
        .reset_index(drop=True)
    )

    train_df, test_df = train_test_split(
        df_balanced[["text", "label"]],
        test_size=0.2,
        stratify=df_balanced["label"],
        random_state=RANDOM_STATE,
    )
    train_df = train_df.reset_index(drop=True)
    test_df = test_df.reset_index(drop=True)

    train_df.to_csv(TRAIN_RAW, index=False, encoding="utf-8-sig")
    test_df.to_csv(TEST_RAW, index=False, encoding="utf-8-sig")

    qa_sample = df_balanced[["text", "label"]].sample(
        n=min(50, len(df_balanced)),
        random_state=RANDOM_STATE,
    )
    qa_sample.to_csv(QA_SAMPLE, index=False, encoding="utf-8-sig")

    train_counts = train_df["label"].value_counts().sort_index().to_dict()
    test_counts = test_df["label"].value_counts().sort_index().to_dict()

    readme = f"""# README_DATA.md

## 1. Nguồn dữ liệu

- Tên dataset: Vietnamese Students' Feedback Corpus (UIT-VSFC)
- Nguồn: Hugging Face dataset `uitnlp/vietnamese_students_feedback`
- Ngôn ngữ: Tiếng Việt
- Bài toán sử dụng: Phân loại cảm xúc nhị phân Positive/Negative

## 2. Cấu trúc thư mục `data/`

```text
data/
├── train/
│   ├── raw.csv        # Dữ liệu gốc Task 1 (8000 dòng)
│   └── cleaned.csv    # Sau tiền xử lý Task 2
├── test/
│   ├── raw.csv        # Dữ liệu gốc Task 1 (2000 dòng)
│   └── cleaned.csv    # Sau tiền xử lý Task 2
├── stopwords/
│   ├── raw.txt        # Baseline từ GitHub
│   ├── custom.txt     # Stopwords dùng trong project
│   └── protected.txt  # Từ không được xóa
├── qa_sample_50.csv
└── README_DATA.md
```

Mỗi file CSV có 2 cột: `text`, `label` (0 = tiêu cực, 1 = tích cực).

`raw.csv` giữ nguyên text từ Hugging Face (Task 1 chỉ chuẩn hóa khoảng trắng). Dataset gốc UIT-VSFC đã ở dạng lowercase; Task 2 mới thực hiện lowercase và loại ký tự đặc biệt trên `cleaned.csv`.

## 3. Thống kê dữ liệu

Số lượng trước khi cân bằng:

- Negative: {label_counts_before.get(0, 0)}
- Positive: {label_counts_before.get(1, 0)}

Sau khi cân bằng:

- Tổng: {len(df_balanced)}
- Train: {len(train_df)}
- Test: {len(test_df)}

Phân bố train: Negative {train_counts.get(0, 0)}, Positive {train_counts.get(1, 0)}
Phân bố test : Negative {test_counts.get(0, 0)}, Positive {test_counts.get(1, 0)}
"""

    README_DATA.write_text(readme, encoding="utf-8")

    print("Done Task 1.")
    print(f"Total balanced samples: {len(df_balanced)}")
    print(f"Train shape: {train_df.shape}")
    print(f"Test shape: {test_df.shape}")
    print("Files created:")
    print(f"- {TRAIN_RAW.relative_to(PROJECT_ROOT)}")
    print(f"- {TEST_RAW.relative_to(PROJECT_ROOT)}")
    print(f"- {QA_SAMPLE.relative_to(PROJECT_ROOT)}")
    print(f"- {README_DATA.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
