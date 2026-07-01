# Kịch bản thuyết trình — Task 11 Error Analysis (bản v2, 9 slide, ~5 phút)

**Người trình bày:** Tâm · **Thời lượng:** ~5 phút
**File slide:** `Task11_Error_Analysis_Presentation_v2.pptx`
**Nguồn số liệu:** chạy trực tiếp `pipeline/run_pipeline.py` + `scripts/task11_run_pipeline_hardtest.py` trên nhánh `feat/pipeline-streamlit-app`

---

## 0:00–0:20 — Slide 1: Mở đầu

"Đây là phần **Error Analysis của Task 11**. Lần này mình làm 2 việc: chạy đúng pipeline `run_pipeline.py` để lấy số liệu thật, và tự sinh **2000 câu khó** để stress-test — tức là những câu được thiết kế riêng để bẫy mô hình. Toàn bộ so sánh giữa Exp A (giữ stopwords) và Exp B (loại stopwords)."

## 0:20–0:50 — Slide 2: Phạm vi & phương pháp

"Ba việc chính: một, chạy chính `run_pipeline.py` — build vocab, clean vocab, rồi threshold search cho cả hai cấu hình; hai, sinh 2000 câu khó với nhãn biết chắc theo cấu trúc; ba, đối chiếu kết quả trên test thường với câu khó và mổ lỗi.

Lưu ý: classifier trên nhánh này là bản rule-based có negation window, intensifier (rất, quá, hơi) và critique word (nên, cần) — khác bản đơn giản trên main, nên số liệu ở đây lấy trực tiếp từ pipeline."

## 0:50–1:35 — Slide 3: Baseline trên tập test thường

"Trên 2000 câu test thường: Exp A đạt accuracy tốt nhất **60.3%**, Exp B **72.1%** — loại stopwords cải thiện gần **12 điểm**.

Nhưng nhìn vào biểu đồ FP/FN: model **over-predict 'Positive'** — Exp A có tới 731 False Positive so với chỉ 64 False Negative. Loại stopwords kéo FP xuống 351, nhưng lại đẩy FN tăng từ 64 lên 207. Tức là bias vẫn còn, chỉ dịch chuyển chứ chưa hết."

## 1:35–2:10 — Slide 4: 2000 câu khó

"Để ép mô hình lộ điểm yếu, mình sinh 2000 câu khó, cân bằng 1000/1000, mỗi câu sinh từ template nên biết chắc nhãn thật. Có 5 nhóm bẫy:
- **Phủ định đảo chiều**: 'thầy dạy không hay' → Negative.
- **Phủ định kép**: 'không hề nhàm chán' → Positive.
- **Nhượng bộ tuy…nhưng**: 'tuy hơi khó nhưng rất bổ ích' → Positive.
- **Câu góp ý / phê bình**: 'nên bổ sung thêm ví dụ' → Negative.
- **Bẫy từ trung tính**: 'nội dung còn sơ sài, thiếu chiều sâu' → Negative.

Đây đúng là những dạng câu mà rule-based hay sai."

## 2:10–2:50 — Slide 5: Kết quả stress-test câu khó

"Trên 2000 câu khó, accuracy tụt xuống: Exp A **65.95%**, Exp B **67.90%** — thấp hơn hẳn test thường, và FP vẫn áp đảo (594 và 481).

Vài câu điển hình model đoán sai: bên False Positive có 'Tuy cuốn hút nhưng dạy hơi khó theo dõi', 'Slide bài giảng nên sắp xếp nội dung logic hơn'; bên False Negative có 'Bài giảng chẳng hề buồn ngủ một chút nào', 'Tuy hơi chán nhưng rất dễ tiếp thu'. Toàn bộ đều rơi vào các nhóm bẫy vừa nói."

## 2:50–3:50 — Slide 6: Mổ xẻ 3 câu sai (token-by-token)

"Slide này quan trọng nhất — mình mổ xẻ điểm cộng dồn từng token bằng chính classifier, ngưỡng 2.0:

**Một, nhượng bộ:** 'Tuy tận tâm nhưng dạy cực kỳ mơ hồ'. Model cộng cả 2 vế — 'tuy', 'nhưng', 'dạy' đều bị tính +1 — nên dù 'mơ hồ' là −2, tổng vẫn +2.0 → đoán Positive, trong khi thật ra là chê.

**Hai, phủ định:** 'Phương pháp dạy chẳng hề khô khan' — đây là câu khen. Nhưng đảo dấu chỉ chạm 2 token, cộng thêm từ vựng xếp sai loại, nên tổng chỉ đạt +1.0, dưới ngưỡng 2.0 → đoán Negative.

**Ba, bẫy từ vựng:** 'Phần lý thuyết hơi nhàm chán' → tổng +2.5 → Positive. Nguyên nhân trực tiếp: từ **'nhàm chán' bị xếp NHẦM vào pos_vocab**, tính +0.5 thay vì âm — câu chê biến thành khen. Đây là bằng chứng rất rõ cho lỗi vocab."

## 3:50–4:15 — Slide 7: 3 nguyên nhân gốc

"Tổng hợp lại, ba nguyên nhân gốc: một là **phủ định chỉ tác dụng trong cửa sổ hẹp** — từ cảm xúc nằm ngoài cửa sổ không bị đảo; hai là **cộng điểm cả hai vế 'tuy…nhưng'** thay vì lấy vế sau; ba là **từ trung tính và từ góp ý chưa có trọng số đúng**, thậm chí từ tiêu cực lọt vào pos_vocab."

## 4:15–4:40 — Slide 8: Đề xuất cải thiện

"Bốn đề xuất: mở rộng cửa sổ phủ định và chỉ đảo tích cực → tiêu cực; xử lý riêng câu 'tuy…nhưng' bằng cách ưu tiên vế sau; làm sạch và bổ sung vocab, thêm lexicon góp ý có trọng số âm; và chọn ngưỡng theo F1 thay vì accuracy đơn thuần. Quan trọng: dùng bộ 2000 câu khó như 'bộ hồi quy' để kiểm tra mỗi lần sửa classifier."

## 4:40–5:00 — Slide 9: Kết luận

"Chốt lại: pipeline `run_pipeline.py` chạy ổn định end-to-end. Loại stopwords có giúp tăng accuracy nhưng cả hai cấu hình vẫn over-predict 'Positive', và trên câu khó chỉ còn ~66–68%. Nút thắt thật sự là **logic negation và xử lý câu nhượng bộ**, không phải stopwords — cần sửa 2 chỗ này trước, rồi chạy lại 2000 câu khó để đo tiến bộ."
