# QA Testing Plan — Giai đoạn 2 (Task 7 & Task 8)

- **Project:** Vietnamese Sentiment Classification (rule-based) — HCMUS / AIO Conquer 2026
- **Branch:** `feat/sentiment-classifier`
- **Author (QA/QC):** Tâm · **Date:** 2026-06-22

## 1. Mục tiêu kiểm thử (Test objectives)
QA/QC xác nhận, trước khi sang Giai đoạn 3 (tích hợp hệ thống), rằng:
- **Chất lượng dữ liệu:** Train/Test sạch, đúng định dạng, không rò rỉ, từ điển hợp lệ.
- **Chất lượng logic:** `tokenize()` và `predict()` chạy đúng đặc tả (kể cả phủ định, nhiễu, ca biên).
- **Chất lượng nghiên cứu:** thí nghiệm A/B (Task 7) **công bằng** và **tái lập được**, và con số đo lường đáng tin.

## 2. Phạm vi kiểm thử (Scope)
**Trong phạm vi:**
- `models/classifier.py` — `Classifier.predict`, `predict_batch`.
- `models/build_vocab.py` — xây dựng từ điển pos/neg.
- `utils/text_utils.py` — `tokenize`, `load_words`.
- `data/train`, `data/test`, `models/vocab/*.json`, `data/stopwords/*.txt`.
- `experiments/run_experiment.py` (Task 7) — *khi đã được merge vào branch này.*

**Ngoài phạm vi:** huấn luyện mô hình ML/DL; tinh chỉnh siêu tham số; hạ tầng triển khai.

## 3. Môi trường kiểm thử (Environment)
- OS: Windows 10 · Python 3.13 · VS Code
- Test runner: `pytest 9.x`
- Deps: `pandas`, `scikit-learn`, `pyvi`, `regex`, `matplotlib` (xem `requirements.txt` — *thiếu `regex`, `matplotlib`, `pytest`, xem QA-E/report*).
- Lệnh chạy: `python -m pytest tests/ -v`

## 4. Chiến lược kiểm thử (theo hướng dẫn — tập trung 3 nhóm chính)

### 4.1 Data Validation Testing — `tests/test_data_validation.py`
Kiểm tra: cột đúng `[text,label]`, không null, UTF-8, label ∈ {0,1}, cân bằng lớp, không trùng lặp, **không rò rỉ Train/Test**, vocab JSON hợp lệ & đủ `min_freq`, file stopwords nạp được, protected ∩ removal = ∅.

### 4.2 Functional Testing — `tests/test_classifier.py`
Kiểm tra `tokenize()` và `predict()` đúng logic: token đơn pos/neg, đa từ, batch, ca tie, nhiễu dấu câu, phủ định đơn/kép, chuỗi phủ định, chỉ stopwords.

### 4.3 Experiment Validation Testing — `tests/test_experiment_validation.py`
Kiểm tra **tính công bằng & tái lập** của A/B (Task 7):
- Dự đoán **tất định** (chạy lại cho kết quả giống nhau).
- Cấu hình A và B chạy **cùng một tập test**.
- A và B **chỉ khác nhau** ở cờ `use_stopwords_removal`.
- Việc lọc stopwords thực sự làm thay đổi ≥1 dự đoán (có tín hiệu để so sánh).
- (Khi có `experiments/run_experiment.py`) `evaluate_model` trả đủ 4 chỉ số trong [0,1].

### 4.4 (Bổ trợ) Edge Case + Manual Review
Câu rỗng, emoji, đảo nghĩa ("hay" = dở), 2 lần "không"; review PR, README, kết quả Accuracy, report.

## 5. Tiêu chí Pass/Fail
- **Pass:** test đạt **và** hành vi khớp đặc tả nghiên cứu.
- **Fail:** bất kỳ test fail, hoặc thí nghiệm A/B không công bằng/không tái lập, hoặc kết quả không có bằng chứng phân tích.
- **Blocker:** lỗi logic làm sai kết quả nghiên cứu, hoặc test làm hỏng artifact đã commit.

## 6. Rủi ro đã nhận diện sớm (QA preventive)
1. Hai branch tách rời (logic ở `feat/sentiment-classifier`, thí nghiệm ở `feat/A-B-test`) → khó tái lập Task 7. **Cần merge.**
2. Từ điển xây không lọc stopwords → A/B không cô lập đúng biến.
3. `build_vocab` ghi cứng vào `models/vocab/` → test ghi đè artifact thật.

## 7. Deliverables
- Test plan này; bộ test (`tests/`); báo cáo [QA_Testing_Report.md](QA_Testing_Report.md); phân tích lỗi [Error_Analysis.md](Error_Analysis.md); checklist [QA_Checklist_Task7_Task8.md](QA_Checklist_Task7_Task8.md).
