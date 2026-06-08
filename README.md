## 1. Giới thiệu
#### **Tên dự án:** NGHIÊN CỨU TÁC ĐỘNG CỦA VIỆC LOẠI BỎ TỪ DỪNG (STOPWORDS) ĐẾN ĐỘ CHÍNH XÁC CỦA HỆ THỐNG PHÂN LOẠI VĂN BẢN
#### Thông qua việc so sánh giữa hai phiên bản dữ liệu có từ dừng và loại bỏ từ dừng. Nhóm nghiên cứu đánh giá một cách định lượng ảnh hưởng của kỹ thuật tiền xử lý (Text Preprocessing) – cụ thể là loại bỏ từ dừng (stopwords) đến độ chính xác của hệ thống phân loại văn bản

## 2. Phân công vai trò
|Tên thành viên| Vai trò | Trách nhiệm chính |
| :--- | :--- | :--- |
|Lê Hoàng Nhân| **Tech Leader** | Điều phối dự án, quản lý tiến độ Jira, tổng hợp báo cáo. |
|| **AIE Data** | Thu thập, làm sạch dữ liệu, xây dựng bộ từ dừng (Stopwords). |
|Nguyễn Trần Duy Anh| **AIE Model** | Xây dựng logic phân loại, thiết lập thí nghiệm, phân tích sai số. |
|Nguyễn Võ Duy Tuân| **AIE Pipeline** | Tích hợp hệ thống end-to-end, triển khai Web App với Streamlit. |
|Nguyễn Quốc Duy Anh| **QA/QC** | Kiểm soát chất lượng, duyệt PR, đánh giá lỗi mô hình (Error Analysis). |

## 3. Mục tiêu của dự án
> Đánh giá định lượng : Chứng minh sự thay đổi về độ chính xác (Accuracy) của mô hình phân loại khi loại bỏ từ dừng.
> 
