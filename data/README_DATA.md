# README_DATA.md

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

- Negative: 7438
- Positive: 8038

Số lượng dữ liệu sau khi cân bằng:

- Tổng số mẫu: 10000
- Train: 8000
- Test: 2000

Phân bố nhãn trong train:

- Negative `0`: 4000
- Positive `1`: 4000

Phân bố nhãn trong test:

- Negative `0`: 1000
- Positive `1`: 1000

## 6. Kiểm tra chất lượng ban đầu

Các bước đã thực hiện:

- Loại bỏ mẫu Neutral.
- Chuẩn hóa khoảng trắng.
- Loại bỏ dòng rỗng.
- Loại bỏ dữ liệu trùng lặp theo cột `text`.
- Chia dữ liệu theo tỉ lệ 80/20.
- Đảm bảo file được lưu ở định dạng CSV UTF-8.

## 7. Ghi chú

Task 1 chỉ thực hiện thu thập và chuẩn bị dữ liệu mẫu.  
Các bước tiền xử lý sâu hơn như lowercase, loại bỏ ký tự đặc biệt, chuẩn hóa dấu câu, loại bỏ stopwords sẽ được thực hiện ở Task 2.
