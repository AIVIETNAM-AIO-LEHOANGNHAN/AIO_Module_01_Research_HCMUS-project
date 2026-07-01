# Task 11 — Error Analysis Report

- **Model version phân tích:** `models/classifier.py` @ `origin/main` (bản đã qua QA Task 7), sao chép
  trung thực trong `scripts/task11_classifier_main.py` để không phá vỡ `app.py` / `pipeline/run_pipeline.py`
  trên nhánh `feat/pipeline-streamlit-app` (2 bản classifier khác nhau đang tồn tại song song trong repo).
- **Vocab:** 1 bộ vocab dùng chung cho cả 2 cấu hình — `models/vocab/pos_vocab.json` (500 từ),
  `models/vocab/neg_vocab.json` (820 từ) — đúng như thiết kế trên `origin/main`.
- **Test set:** `data/test/cleaned.csv`, 2000 câu có nhãn thật.
- **Cấu hình:**
  - **Exp A — giữ stopwords:** `use_stopwords_retrieval=False`
  - **Exp B — loại stopwords:** `use_stopwords_retrieval=True` (loại theo `data/stopwords/custom.txt`)
  - Cả 2 dùng chung `data/stopwords/protected.txt` (15 từ: `không, chưa, chẳng, chả, đừng, rất, quá,
    hơi, kém, tốt, tệ, hay, dở, nên, cần`) làm danh sách "negative_words" — token nào nằm trong danh sách
    này sẽ đảo dấu (`negative *= -1`) cho **đúng 1 token kế tiếp**.
  - Rule dự đoán: `score > 0 → Positive`, ngược lại `→ Negative` (không có lớp Neutral).
- File sinh ra: [error_analysis_exp_a.csv](error_analysis_exp_a.csv),
  [error_analysis_exp_b.csv](error_analysis_exp_b.csv), script tái tạo:
  [scripts/task11_error_analysis.py](../scripts/task11_error_analysis.py).

---

## 1. Thống kê tổng quan lỗi

| Cấu hình | Tổng test | Số câu sai | False Positive | False Negative | Accuracy |
|---|---:|---:|---:|---:|---:|
| **Exp A** (giữ stopwords) | 2000 | **964** | 954 | 10 | **51.8%** |
| **Exp B** (loại stopwords) | 2000 | **890** | 860 | 30 | **55.5%** |

*Số liệu khớp confusion matrix Task 7 / `docs/Error_Analysis.md` (964 lỗi A / 890 lỗi B, cùng tỉ lệ
Neg→Pos áp đảo) — xác nhận đang phân tích đúng phiên bản classifier đã được QA review.*

So sánh tập lỗi (theo nội dung câu):

| So sánh | Số câu |
|---|---:|
| Cả A và B cùng sai | **861** |
| Chỉ A sai — B đã sửa được | **103** |
| Chỉ B sai — B tạo lỗi mới so với A | **29** |

→ Loại stopwords giảm được ròng **74 lỗi** (964 → 890 = 103 sửa được − 29 lỗi mới phát sinh).
Đây là bằng chứng loại stopword **không thuần túy chỉ có lợi**: nó sửa nhiều hơn số nó phá, nhưng vẫn
tạo ra lỗi mới (mục 4).

## 2. So sánh FP/FN giữa A và B

| Loại lỗi | Exp A | Exp B | Thay đổi |
|---|---:|---:|---:|
| False Positive (Neg→Pos) | 954 | 860 | **−94** |
| False Negative (Pos→Neg) | 10 | 30 | **+20** |

**Loại stopwords chủ yếu giúp giảm False Positive**, gần như không đụng tới False Negative theo hướng
tốt — ngược lại **FN tăng gấp 3 lần** (10 → 30). Lỗi vẫn lệch một chiều gần như tuyệt đối: model gần như
luôn đoán "Positive" ở cả 2 cấu hình (954/964 và 860/890 lỗi là Neg→Pos), tức bias hệ thống không đổi
bản chất, chỉ đổi mức độ.

## 3. Top pattern lỗi phổ biến + ví dụ

| # | Nguyên nhân | Số lỗi A | Số lỗi B | Mô tả |
|---|---|---:|---:|---|
| C1 | Negation chỉ đảo dấu **đúng 1 token kế tiếp** | 693 | 635 | Từ trong `protected.txt` (`không, chưa, rất, hơi, tốt, hay, dở...`) chỉ lật dấu của từ ngay sau nó; nếu từ mang cảm xúc thật sự nằm xa hơn 1 token → không bị đảo, hoặc từ trung tính đứng giữa vô tình "hứng" lượt đảo dấu thay vì từ cần đảo. |
| C4 | Từ vựng tích cực (pos_vocab) áp đảo câu phê bình không có neg-vocab tương ứng | 192 | 164 | Câu góp ý/phê bình dùng từ học thuật trung tính nhưng lại nằm trong `pos_vocab` (`kiến thức, chất lượng, năng lực, nội dung, chương trình…`) → cộng dồn thành điểm dương dù ý câu là tiêu cực. |
| C2 | Cấu trúc nhượng bộ "tuy...nhưng" | 69 | 61 | Model cộng điểm cả 2 vế câu, không nhận biết vế sau "nhưng" mới là ý chính. |

**Ví dụ pattern C1** (negation 1-token không đủ phạm vi):
- `"giáo viên dạy chưa tốt ."` → score = **+2** → *Positive* (đúng ra: "chưa" phủ định "tốt", nhưng
  "chưa" và "tốt" đều nằm trong `protected.txt`; "tốt" tự lật dấu cho từ *kế tiếp* thay vì bị "chưa" lật
  dấu đủ, nên vẫn cộng dương ở cả 2 cấu hình A và B).
- `"còn những phần tìm bao đóng , chứng minh dạng chuẩn chưa làm rõ ."` → score = **+7** → *Positive*
  (từ cảm xúc thật "rõ" đứng cách "chưa" hơn 1 token nên không bị đảo dấu).

**Ví dụ pattern C4** (pos_vocab áp đảo câu phê bình không có neg-vocab):
- `"cơ sở vật chất còn ảnh hưởng đến chất lượng môn học ."` → score = **+1** → *Positive* ("chất lượng"
  nằm trong pos_vocab, không có từ nào trong neg_vocab để cân bằng).
- `"nên sử dụng máy chiếu để hiện rõ chữ , để giảm thời gian viết , tập trung thời gian vào việc giải
  bài tập minh họa ."` → score = **+9** → *Positive* (câu góp ý/yêu cầu cải thiện toàn bộ bị đọc thành
  tích cực vì không một từ nào rơi vào neg_vocab).

**Ví dụ pattern C2** (nhượng bộ):
- `"cô dạy khá nhiệt tình , tuy nhiên lý thuyết dạy cô còn hay nhầm lần , làm sinh viên mơ hồ ."` →
  score = **+10 (A) / +4 (B)** → *Positive*, dù nhãn thật là *Negative* — vế sau "tuy nhiên" (ý chính,
  phê bình) bị vế trước ("khá nhiệt tình") và các token "hay" tự nhân điểm dương.
- `"kiến thức tổng quan thì có thể tiếp nhận nhưng kiến thức về chi tiết nội dung thì mập mờ ."` →
  score = **+9** → *Positive*.

**Pattern False Negative đáng chú ý — câu tích cực rất ngắn, không có từ nào trong vocab** (D2, 9 lỗi ở A,
25 lỗi ở B — tăng vì bị stopword-removal xoá luôn từ mang nghĩa):
- `"tỉ mỉ ."` → score = 0 → *Negative* (từ "tỉ mỉ" hoàn toàn không có trong `pos_vocab`/`neg_vocab`).
- `"rất hữu ích ."`, `"rất thân thiện ."`, `"rất thực tiễn ."` → score = 0 → *Negative* ("hữu ích",
  "thân thiện", "thực tiễn" không nằm trong vocab; "rất" chỉ lật dấu cho token kế mà không có gì để lật).

## 4. Nhận xét về tác động của Stopwords

- **Giúp giảm được:** phần lớn 103 câu "chỉ A sai, B đúng" là các câu mà loại bỏ từ nối/hư từ
  (và, là, của, các, những…) làm token cảm xúc thật (vd. "nhiệt_tình", "hay") **dịch lại gần** một token
  `protected.txt` khác không liên quan, vô tình huỷ bỏ một phép đảo dấu sai trước đó → điểm số về đúng
  hướng một cách tình cờ hơn là vì logic phủ định được cải thiện thật sự.
- **Chưa giúp được / còn gây hại — 29 câu "chỉ B sai":** cùng cơ chế nhưng theo chiều ngược lại: xoá
  stopword làm từ cảm xúc **dịch lại gần** một token `protected.txt` (thường là "rất"/"hay") mà lẽ ra
  phải cách xa để không bị đảo dấu. Ví dụ đã trace trực tiếp qua code:
  - `"cô dạy hay và rất nhiệt tình ."` (nhãn thật: Positive)
    - Token đầy đủ (A): `cô, dạy, hay, và, rất, nhiệt_tình, .` → score = **+2** → *Positive* (đúng).
    - Token sau khi loại stopword (B): `dạy, hay, rất, nhiệt_tình, .` → score = **0** → *Negative* (sai).
    - Nguyên nhân: bỏ "và" khiến "rất" (một *negative_word*) đứng sát ngay trước "nhiệt_tình" hơn,
      chuỗi đảo dấu liên hoàn ("hay" → đảo "rất"; "rất" tự đảo tiếp cho "nhiệt_tình") triệt tiêu điểm
      dương mà bản gốc (có "và" chen giữa) không bị.
  - `"cô giảng bài rất là hay và không nhàm chán ."` → A: score = **+3** (đúng, Positive) → B (loại "là",
    "và"): score = **−1** (sai, Negative) — cùng cơ chế: xoá stopword đẩy "không" tới sát
    "nhàm_chán" theo cách khác với bản gốc.
  - **Kết luận:** vì cơ chế đảo dấu chỉ có phạm vi 1-token và phụ thuộc vị trí tuyệt đối trong chuỗi
    token, *bất kỳ* thay đổi nào ở danh sách token (không riêng gì việc bỏ stopword) đều có thể đổi kết
    quả một câu theo cả 2 chiều tốt/xấu một cách ngẫu nhiên — nên phần lớn benefit đo được của "loại
    stopwords" (+94 FP được sửa) lẫn phần hại của nó (+20 FN mới) đều là **tác dụng phụ của việc thay đổi
    vị trí token**, không phải bằng chứng cho thấy bản thân từ dừng mang nhiễu ngữ nghĩa.
- **Không giúp được (bất kể A/B):** 861 câu cả 2 cấu hình cùng sai — đây là lỗi hệ thống nằm ở
  (1) vocab thiếu / lẫn từ trung tính vào pos_vocab (pattern C4), (2) cấu trúc câu nhượng bộ (C2), và
  (3) bản chất cơ chế negation 1-token (C1) — loại stopwords không chạm tới những nguyên nhân gốc rễ này.

## 5. Đề xuất cải thiện

1. **Tách "negator" thật ra khỏi danh sách "negative_words" hiện tại và mở rộng phạm vi phủ định.**
   `protected.txt` hiện gộp chung negator (không, chưa, chẳng…), intensifier (rất, quá, hơi) và từ cảm
   xúc (tốt, kém, hay, dở) vào cùng một cơ chế đảo-dấu-1-token. Cần: (a) chỉ các negator thật sự mới được
   phép đảo dấu; (b) áp dụng trên một **cửa sổ 2–3 token** thay vì đúng 1 token kế tiếp, để bắt được các
   trường hợp như "chưa … làm rõ", "không … thực tế" (pattern C1, 693/964 lỗi A).
2. **Làm sạch lại pos_vocab/neg_vocab: loại các từ học thuật trung tính đang nằm trong pos_vocab**
   (`kiến thức, chất lượng, năng lực, nội dung, chương trình` — xuất hiện dày đặc ở pattern C4, 192/964
   lỗi A) bằng cách hạ ngưỡng `neutral_threshold` khi lọc từ trung tính, đồng thời bổ sung một lexicon
   "critique word" có trọng số âm thật sự (nên, cần, thiếu, hơi, chưa, ít) thay vì để chúng đứng chung
   danh sách negative_words không trọng số.
3. **Xử lý cấu trúc nhượng bộ "tuy...nhưng":** khi phát hiện "nhưng"/"tuy nhiên", chỉ tính điểm của vế
   câu **sau** liên từ (hoặc nhân đôi trọng số vế sau) — đây là mẫu câu tiếng Việt rất phổ biến trong dữ
   liệu đánh giá giảng viên và chiếm 60-70 lỗi ở mỗi cấu hình (pattern C2).
4. **Tách rời cơ chế đảo dấu khỏi việc loại stopword:** tính vị trí đảo dấu (negation scope) trên chuỗi
   token **gốc** (trước khi loại stopword), rồi mới lọc stopword ra khỏi phần tính điểm — tránh việc xoá
   một hư từ vô tình đổi khoảng cách giữa negator và từ cảm xúc, vốn đang gây ra toàn bộ nhóm lỗi mới
   phát sinh ở Exp B (29 câu "chỉ B sai", mục 4).
5. **Thêm lớp Neutral hoặc mở rộng vocab cho câu ngắn không khớp từ nào** (`score == 0`): hiện tại mặc
   định về "Negative", gây oan cho các câu tích cực ngắn như "tỉ mỉ .", "rất hữu ích ." (pattern D2,
   9→25 lỗi khi loại stopwords). Có thể bổ sung thêm từ đồng nghĩa phổ biến vào pos_vocab hoặc thêm nhãn
   Neutral để không ép các câu score=0 về phía Negative.
