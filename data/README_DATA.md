# README_DATA.md

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

## 3. Thống kê dữ liệu

- Tổng cân bằng: 10.000 mẫu (5.000/lớp)
- Train: 8.000 (4.000 negative + 4.000 positive)
- Test: 2.000 (1.000 + 1.000)

## 4. Scripts liên quan

| Task | Script | Input | Output |
|------|--------|-------|--------|
| 1 | `scripts/task1_prepare_data.py` | Hugging Face | `train/raw.csv`, `test/raw.csv` |
| 2 | `scripts/task2_preprocess_text.py` | `*/raw.csv` | `*/cleaned.csv` |
| 3 | `scripts/task3_build_stopwords.py` | `stopwords/raw.txt` | `stopwords/custom.txt` |
