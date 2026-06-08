## 11 QUY TẮC VẬN HÀNH NHÓM
1. Thực hiện họp cập nhật tiến độ 2 lần/ tuần : họp khoảng 30 - 45 phút vào 21h thứ Tư và Chủ Nhật hàng tuần để cập nhật tiến độ dự án

2. Cập nhật trạng thái: Luôn cập nhật đúng trạng thái của Task trên bảng Kanban (Backlog, To Do, In Progress, Review, Done).

3. Ghi nhật ký (Work Log): Mỗi ngày làm việc phải dành 2 phút cuối giờ cập nhật 4 điểm: Đã xong gì - Đang vướng gì - Sắp làm gì - Tâm trạng như thế nào? vào phần Comment của task tương ứng trên Jira.

4. Giới hạn công việc (WIP Limit): Mỗi thành viên chỉ được phép có tối đa 2 task ở cột "In Progress". Khi chưa xong, đừng nhận thêm task mới.

5. Branching : Không ai được phép push trực tiếp vào nhánh main. Phải tạo nhánh riêng (feat/tên-task hoặc fix/tên-lỗi) trước khi code.

6. Pull Request (PR): Trước khi merge vào nhánh chính, task phải được QA review và Tech Leader Approve.

7. Commit Message: Phải tuân thủ cú pháp ngắn gọn, rõ ràng (ví dụ: feat: add data cleaning function hoặc fix: resolve stopword loading error).

8. Code: Code phải được comment giải thích logic, rõ ràng để ai đọc vào cũng hiểu (đặc biệt là các phần thuật toán phức tạp).

9. Đúng giờ (Deadline): Deadline là cam kết. Nếu task có nguy cơ trễ, thành viên phải báo trước cho Leader ít nhất 24 giờ.

10. Hỗ trợ đồng đội: Khi một thành viên bị Blocked quá 2 ngày, Tech Leader và các thành viên khác có trách nhiệm vào hỗ trợ. Dự án là của chung, không ai được bỏ lại phía sau.

11. QA là người gác cổng: Mọi đầu ra (Data sạch, Model, Pipeline) đều phải đi qua bước review của QA
