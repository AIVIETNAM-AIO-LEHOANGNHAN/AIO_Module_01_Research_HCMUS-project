## 1. Giới thiệu
#### **Tên dự án:** NGHIÊN CỨU TÁC ĐỘNG CỦA VIỆC LOẠI BỎ TỪ DỪNG (STOPWORDS) ĐẾN ĐỘ CHÍNH XÁC CỦA HỆ THỐNG PHÂN LOẠI VĂN BẢN
#### Thông qua việc so sánh giữa hai phiên bản dữ liệu có từ dừng và loại bỏ từ dừng. Nhóm nghiên cứu đánh giá một cách định lượng ảnh hưởng của kỹ thuật tiền xử lý (Text Preprocessing) – cụ thể là loại bỏ từ dừng (stopwords) đến độ chính xác của hệ thống phân loại văn bản

## 2. Phân công vai trò
|Tên thành viên| Vai trò | Trách nhiệm chính |
| :--- | :--- | :--- |
|Lê Hoàng Nhân| **Tech Leader** | Điều phối dự án, quản lý tiến độ Jira, tổng hợp báo cáo. |
|Nguyễn Nhật Tuấn Kiệt| **AIE Data** | Thu thập, làm sạch dữ liệu, xây dựng bộ từ dừng (Stopwords). |
|Nguyễn Trần Duy Anh| **AIE Model** | Xây dựng logic phân loại, thiết lập thí nghiệm, phân tích sai số. |
|Nguyễn Võ Duy Tuân| **AIE Pipeline** | Tích hợp hệ thống end-to-end, triển khai Web App với Streamlit. |
|Nguyễn Quốc Duy Anh| **QA/QC** | Kiểm soát chất lượng, duyệt PR, đánh giá lỗi mô hình (Error Analysis). |

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
## 6. Câu trúc Repository

```text
├── data/           # Chứa raw data, processed data, stopwords.txt
├── models/         # Chứa logic phân loại và các hàm so sánh
├── pipeline/       # Chứa script xử lý luồng (End-to-end)
├── docs/           # Báo cáo Overleaf và tài liệu nghiên cứu
├── app.py          # Ứng dụng Streamlit minh họa
└── README.md       # Tài liệu dự án
```
### 7. Quy trình cộng tác
* Mọi tính năng đều được làm việc trên nhánh riêng. Cú pháp đặt tên nhánh: featủe/tên-task.
* QA/QC kiểm duyệt mã nguồn qua Pull Request (PR) trước khi merge vào nhánh main.




