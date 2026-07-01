# Kịch bản thuyết trình — Task 11: Error Analysis (5 phút, 8 slide)

**Người trình bày:** Tâm · **Thời lượng:** ~5 phút
**File slide:** `Task11_Error_Analysis_Presentation.pptx`
**Nguồn số liệu:** `docs/error_analysis_report.md`, `docs/error_analysis_exp_a.csv`, `docs/error_analysis_exp_b.csv`

---

## 0:00–0:20 — Slide 1: Mở đầu

"Phần này mình trình bày **Task 11 — Error Analysis**: đào sâu vào các câu mà model dự đoán sai, để trả lời câu hỏi mà thí nghiệm A/B ở Task 7 chưa trả lời — *tại sao* model sai, chứ không chỉ sai bao nhiêu. Phân tích chạy trên **2000 câu test**, so sánh 2 cấu hình: Exp A giữ stopwords, Exp B loại stopwords."

## 0:20–0:50 — Slide 2: Mục tiêu & phạm vi

"Ba mục tiêu chính: một, không chỉ đếm lỗi mà giải thích cơ chế gây lỗi; hai, tách rõ 2 loại lỗi — False Positive và False Negative; ba, so sánh trực tiếp lỗi giữa A và B để xem loại stopwords thật sự tác động thế nào.

Dữ liệu dùng đúng bản classifier đã được QA và cập nhật trên GitHub ở Task 7, với một bộ vocab dùng chung cho cả hai cấu hình."

## 0:50–1:40 — Slide 3: Thống kê tổng quan

"Exp A sai 964/2000 câu, accuracy 51.8%. Exp B sai 890/2000, accuracy 55.5%. Loại stopwords giúp giảm lỗi, nhưng nhìn kỹ hơn: **861 câu cả hai cấu hình cùng sai** — đây là lỗi hệ thống, không liên quan gì đến stopwords. B chỉ sửa được 103 câu so với A, nhưng đồng thời cũng **tạo ra 29 lỗi mới** mà A không có. Nên lợi ích ròng thực tế chỉ là 74 câu, không phải 103."

## 1:40–2:15 — Slide 4: Lỗi lệch một chiều

"Điều đáng chú ý nhất: lỗi không ngẫu nhiên. Ở Exp A, **99% lỗi là Negative bị đoán thành Positive**; ở Exp B là 97%. Model gần như luôn đoán 'Positive' — kể cả với câu phê bình rõ ràng. Loại stopwords làm giảm mức độ lệch một chút, nhưng không đổi bản chất của bias này."

## 2:15–3:15 — Slide 5: Top 3 pattern lỗi

"Mình đọc trực tiếp các câu sai và gom thành 3 nhóm nguyên nhân chính, chiếm hơn 95% tổng lỗi:

**Một, negation chỉ đảo dấu đúng 1 token kế tiếp** — chiếm gần 72% lỗi. Ví dụ 'giáo viên dạy chưa tốt' vẫn ra điểm dương, vì cơ chế đảo dấu không chạm đúng từ cảm xúc thật.

**Hai, từ học thuật trung tính lọt vào pos_vocab** — như 'chất lượng', 'năng lực', 'nội dung' — khiến câu phê bình cơ sở vật chất vẫn bị tính là tích cực.

**Ba, cấu trúc nhượng bộ 'tuy...nhưng'** — model cộng điểm cả hai vế câu, trong khi vế sau 'nhưng' mới là ý chính của người viết."

## 3:15–4:00 — Slide 6: Stopwords — con dao hai lưỡi

"Đây là phát hiện quan trọng nhất: vì negation chỉ dựa vào **vị trí** token, xoá stopword có thể vô tình đổi kết quả một câu theo cả hai chiều. Ví dụ trace trực tiếp bằng code: câu 'cô dạy hay và rất nhiệt tình' — giữ nguyên từ dừng thì model đoán đúng Positive; xoá từ 'và' đi thì vị trí từ 'rất' dịch sát vào từ 'nhiệt tình' hơn, kích hoạt một chuỗi đảo dấu liên hoàn làm điểm về 0, model đoán sai thành Negative.

Điều này có nghĩa: phần lớn lợi ích đo được của việc loại stopwords là **tác dụng phụ của việc dịch chuyển vị trí token**, chứ chưa hẳn là bằng chứng cho thấy bản thân từ dừng mang nhiễu ngữ nghĩa."

## 4:00–4:35 — Slide 7: Đề xuất cải thiện

"Từ đó nhóm đề xuất 4 hướng cải thiện cụ thể: mở rộng phạm vi negation ra 2–3 token thay vì 1; làm sạch lại pos_vocab và thêm lexicon phê bình có trọng số âm; xử lý riêng cấu trúc 'tuy...nhưng' bằng cách ưu tiên vế sau; và tách logic negation ra khỏi việc lọc stopword để tránh đổi kết quả một cách ngẫu nhiên. Riêng hai đề xuất đầu đã giải quyết khoảng 92% lỗi hiện đang đo được ở Exp A."

## 4:35–5:00 — Slide 8: Kết luận

"Tóm lại: loại stopwords có giảm lỗi ròng, nhưng làm False Negative tăng gấp 3 lần, và vẫn còn 861 lỗi hệ thống không liên quan đến stopwords. Vì vậy, trước khi khẳng định 'loại stopwords hiệu quả hơn' như kết luận ban đầu của Task 7, nhóm cần fix negation và vocab trước, rồi chạy lại A/B test để có con số đáng tin cậy hơn."
