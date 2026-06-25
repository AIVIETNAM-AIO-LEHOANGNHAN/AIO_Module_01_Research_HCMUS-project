# QA Testing Plan — Task 7 (A/B Testing) · branch `feat/A-B-test`

- **Project:** Vietnamese Sentiment Classification (rule-based) — HCMUS / AIO Conquer 2026
- **Author (QA/QC):** Tâm · **Date:** 2026-06-22

## 1. Mục tiêu kiểm thử
Xác nhận thí nghiệm A/B (Task 7) — so sánh "không lọc stopwords" (A) vs "có lọc stopwords" (B) —
**công bằng**, **tái lập được**, và kết quả (Accuracy/Precision/Recall/F1) **đáng tin** trước khi
dùng để chứng minh giả thuyết nghiên cứu của nhóm.

## 2. Phạm vi
**Trong phạm vi:** `experiments/run_experiment.py`, `results_raw.csv`, `results_cleaned.csv`,
`results_comparison.csv`, `results_comparison_chart.png`; `models/classifier.py` (ở mức ảnh hưởng
tính hợp lệ kết quả); `data/test/cleaned.csv`; `models/vocab/*.json`.
**Ngoài phạm vi:** huấn luyện mô hình ML/DL; tuning; triển khai.

## 3. Môi trường
Windows 10 · Python 3.13 · VS Code · `pytest 9.x`. Deps cần: `pandas, scikit-learn, pyvi, matplotlib`
(*`matplotlib` thiếu trong `requirements.txt` — QA-E10*).
Lệnh: `python -m pytest tests/ -v`; chạy thí nghiệm: `python -m experiments.run_experiment`.

## 4. Chiến lược kiểm thử (3 tiêu chí chính)

### 4.1 Functional Testing — `tests/test_experiment.py`
`evaluate_model()` trả đủ 4 chỉ số, giá trị ∈ [0,1], đúng chữ ký `evaluate_model(classifier, test_data)`;
script chạy hoàn tất và sinh đủ artifact.

### 4.2 Data Validation Testing — `tests/test_experiment.py`
Test set đúng schema, label ∈ {0,1}, không null, **không rò rỉ Train/Test**; ánh xạ nhãn trong
`evaluate_model` an toàn; file `results_*.csv` đã commit khớp với kết quả tính lại (không stale).

### 4.3 Experiment Validation Testing — `tests/test_experiment.py`
- **Tái lập:** chạy lại cho con số giống hệt.
- **Công bằng:** A và B dùng **cùng test set**, **chỉ khác** cờ `use_stopwords_removal`.
- **Có tín hiệu:** việc lọc stopwords làm thay đổi ≥1 chỉ số.
- **Tính hợp lệ:** accuracy phải > mức ngẫu nhiên; phân tích hướng lỗi (Neg↔Pos).

### 4.4 (Bổ trợ) Manual Review
Đọc bảng so sánh, biểu đồ, và kết luận; kiểm tra tính hermetic của test suite.

## 5. Tiêu chí Pass/Fail
- **Pass:** test đạt **và** thí nghiệm công bằng/tái lập **và** kết luận có bằng chứng.
- **Fail / Blocker:** kết quả dựa trên mô hình không tin cậy; script không chạy được; thiếu tài liệu phân tích.

## 6. Rủi ro nhận diện sớm
1. Kết quả A/B dựa trên classifier có lỗi phủ định → con số gần ngẫu nhiên (QA-E4).
2. Script phụ thuộc `PYTHONPATH` + stdout UTF-8 → không chạy out-of-the-box trên Windows (QA-E2/E3).
3. `build_vocab` ghi đè vocab đã commit → test không hermetic (QA-B5).

## 7. Deliverables
Test plan này; `tests/test_experiment.py`; báo cáo [QA_Testing_Report.md](QA_Testing_Report.md);
phân tích lỗi [Error_Analysis.md](Error_Analysis.md); checklist [QA_Checklist_Task7.md](QA_Checklist_Task7.md).
