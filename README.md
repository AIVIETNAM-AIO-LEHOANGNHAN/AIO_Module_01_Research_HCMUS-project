## 1. Giới thiệu
- **Tên dự án:** NGHIÊN CỨU TÁC ĐỘNG CỦA VIỆC LOẠI BỎ TỪ DỪNG (STOPWORDS) ĐẾN ĐỘ CHÍNH XÁC CỦA HỆ THỐNG PHÂN LOẠI VĂN BẢN
- Thông qua việc so sánh giữa hai phiên bản dữ liệu có từ dừng và loại bỏ từ dừng. Nhóm nghiên cứu đánh giá một cách định lượng ảnh hưởng của kỹ thuật tiền xử lý (Text Preprocessing) – cụ thể là loại bỏ từ dừng (stopwords) đến độ chính xác của hệ thống phân loại văn bản

## 2. Phân công vai trò
|Tên thành viên| Vai trò | Trách nhiệm chính |
| :--- | :--- | :--- |
|Lê Hoàng Nhân| **Tech Leader** | Điều phối dự án, quản lý tiến độ Jira, tổng hợp báo cáo. |
|Nguyễn Nhật Tuấn Kiệt| **AIE Data** | Thu thập, làm sạch dữ liệu, xây dựng bộ từ dừng (Stopwords). |
|Nguyễn Trần Duy Anh| **AIE Model** | Xây dựng logic phân loại, thiết lập thí nghiệm, phân tích sai số. |
|Nguyễn Võ Duy Tuân| **AIE Pipeline** | Tích hợp hệ thống end-to-end, triển khai Web App với Streamlit. |
|Trần Quốc Minh Tâm| **QA/QC** | Kiểm soát chất lượng, duyệt PR, đánh giá lỗi mô hình (Error Analysis). |

## 3. Mục tiêu của dự án
* **Nghiên cứu khoa học:** So sánh độ chính xác giữa hai phiên bản dữ liệu (có và không có stopwords).
* **Ứng dụng thực tiễn:** Xây dựng ứng dụng minh họa (Demo App) giúp trực quan hóa quá trình xử lý văn bản.
* **Quy trình chuẩn:** Thực hành vận hành theo mô hình doanh nghiệp thu nhỏ với 5 vai trò chuyên biệt.
## 4. Công cụ
* **Ngôn ngữ:** Python (Xử lý chuỗi, logic phân loại).
* **Giao diện:** Streamlit (Triển khai ứng dụng minh họa).
* **Quản lý dự án:** Jira + framework KANBAN (quản lý Task, theo dõi tiến độ project), Overleaf (viết báo cáo).
* **Quản lý mã nguồn:** Git/GitHub (quy trình Feature Branching).
## 5. Quy trình triển khai (Pipeline)
Luồng dữ liệu được thiết kế như sau:
1. **Input:** Văn bản thô từ Dataset.
2. **Preprocessing:** Làm sạch (chuẩn hóa) và Loại bỏ Stopwords.
3. **Model:** Phân loại văn bản dựa trên luật (Rule-based).
4. **Evaluation:** Đánh giá và Phân tích lỗi (Error Analysis).
5. **Output:** Dashboard với giao diện Streamlit hiển thị kết quả so sánh.
## 6. Cấu trúc Repository

```text
├── data/
│   ├── train/          # raw.csv, cleaned.csv
│   ├── test/           # raw.csv, cleaned.csv
│   ├── stopwords/      # raw.txt, custom.txt, protected.txt
│   └── qa_sample_50.csv
├── scripts/
│   ├── task1_prepare_data.py
│   ├── task2_preprocess_text.py
│   └── task3_build_stopwords.py
├── models/             # Logic phân loại và các hàm so sánh
├── pipeline/           # Script xử lý luồng end-to-end
├── docs/               # Tài liệu nghiên cứu
├── app.py              # Ứng dụng Streamlit minh họa
├── requirements.txt
└── README.md
```
## 7. Quy trình cộng tác
```text
1. Pull mới nhất: Trước khi tạo nhánh, thành viên phải chạy lệnh <git pull origin main> để lấy code mới nhất về.
2. Tạo nhánh: chạy lệnh <git checkout -b feat/tên-task>
3. Làm việc: Thực hiện code, test trên nhánh đó.
4. Commit: chạy lệnh <git commit -m "mô tả ngắn gọn công việc"> (Ví dụ: commit -m "Thêm hàm loại bỏ stopwords tiếng Việt")
5. Push & PR:
- Chạy lệnh <git push origin feat/tên-task>
- Lên GitHub mở một Pull Request (PR) từ nhánh feat/tên-task vào nhánh main.
6. Review: QA/QC vào đọc PR.
- Nếu ổn: QA/QC nhấn nút Approve.
- Nếu chưa ổn: QA/QC nhấn nút Request Changes và ghi rõ lý do.
7. Merge: Sau khi được Approve, Tech Leader tiến hành Merge vào nhánh main.
```
## 8. Kết quả nghiên cứu
> Nhóm sẽ cập nhật các biểu đồ so sánh Accuracy và kết luận nghiên cứu tại đây.

### *Dự án thực hiện bởi Nhóm AIO_2026_Research_HCMUS - Module 1 - AIO Conquer 2026 - AI VIET NAM*






