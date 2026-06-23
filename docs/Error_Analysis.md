# Error Analysis — Giai đoạn 2

- **Branch:** `feat/sentiment-classifier` · **QA/QC:** Tâm · **Date:** 2026-06-22
- **Source:** Config A (no stopword removal) over `data/test/cleaned.csv` (2000 rows).
- **Aggregate:** **964 / 2000 misclassified (48.2% error).** In the sampled errors, **100% were Negative→Positive** — a one-directional systematic bias, not random noise.

> Method: `Classifier.predict` was run on every test row; rows where prediction ≠ gold label were collected. The 25 cases below are verbatim from the test set (gold = Negative, predicted = Positive unless noted).

## Root-cause categories

| Cat | Description | Finding | Share of sampled errors |
|-----|-------------|---------|--------------------------|
| **R1** | Negation/contrast word flips a negative word to positive (`score -= negative` with `negative=-1`) | [QA-C6] | Dominant |
| **R2** | Suggestion/criticism phrased without explicit negative-vocab words ("nên…", "cần…", "chưa…"); positive-looking tokens dominate → score>0 | [QA-C6]/[QA-C7] | High |
| **R3** | Stopwords / domain-neutral words carry positive weight (vocab polluted) | [QA-B2] | Medium |
| **R4** | Punctuation/typos not stripped at predict time; tokens never match vocab → defaults drift | [QA-C4] | Medium |
| **R5** | Tie / no-signal sentences resolved arbitrarily (no Neutral class) | [QA-C7] | Medium |

## Case log (25 cases)

| # | Text (gold = Negative) | Pred | Cat | Why it failed |
|---|------------------------|------|-----|---------------|
| 1 | không cho sinh viên nhiều kiến thức . | Positive | R1 | "không" negator; "kiến thức/nhiều" positive-leaning tokens win |
| 2 | điều này gây mất công bằng và không đánh giá được đúng năng lực học tập của các bạn . | Positive | R1 | "không … đúng/năng lực" flipped |
| 3 | cơ sở vật chất còn ảnh hưởng đến chất lượng môn học . | Positive | R2 | criticism w/o neg-vocab; "chất lượng" positive |
| 4 | giảng viên nên dạy lâu hơn mỗi buổi học . | Positive | R2 | suggestion "nên"; no neg word |
| 5 | chuẩn bị âm thanh trước môn học ổn định để tránh mất thì giờ … | Positive | R2/R3 | "ổn định/chuẩn bị" positive; criticism implicit |
| 6 | cần thể hiện chi tiết hơn nội dung của môn học và nhiều ví dụ minh hoạ hơn . | Positive | R2 | "cần … hơn" = request, scored positive |
| 7 | số lượng buổi học hơi ít so với nội dung thực hành . | Positive | R2/R5 | mild complaint, no neg-vocab |
| 8 | còn những phần tìm bao đóng , chứng minh dạng chuẩn chưa làm rõ . | Positive | R1 | "chưa … rõ" → "rõ/chuẩn" positive |
| 9 | nên sử dụng máy chiếu để hiện rõ chữ … tập trung … giải bài tập minh họa . | Positive | R2 | "nên/rõ/tập trung" positive tokens |
| 10 | tóm lại thầy nên học một khóa về kỹ năng giao tiếp . | Positive | R2 | implicit criticism; "kỹ năng/học" positive |
| 11 | giáo viên dạy chưa tốt . | Positive | R1 | "chưa" negator but "tốt" still scored positive — negation not applied to it |
| 12 | cần đảm bảo thời gian lên lớp . | Positive | R2 | "đảm bảo" positive token |
| 13 | nên cập nhật slide thường xuyên vì quá cũ không tích hợp được với chương trình bây giờ . | Positive | R1/R2 | "không tích hợp" flipped; "cập nhật" positive |
| 14 | giáo trình môn học nên cập nhật thường xuyên . | Positive | R2 | "nên cập nhật" read as positive |
| 15 | giáo trình quá ít và nội dung không khác nhau là mấy . | Positive | R1 | "không khác" flipped |
| 16 | … chỉ cần sai sót nhỏ sẽ rớt môn . | Positive | R2/R3 | neutral tokens; no neg-vocab hit |
| 17 | thời gian thầy giảng dạy ngắn , thường cho lớp về sớm . | Positive | R2 | "giảng dạy/thầy" positive; "ngắn" not in neg-vocab |
| 18 | ra đề thi midterm cả lớp toàn 0 , 1 , 2 đến 3 điểm . | Positive | R4/R5 | digits not stripped at predict; no sentiment token |
| 19 | nên sắp lịch học phù hợp . | Positive | R2 | "phù hợp" positive |
| 20 | … kiến thức tổng quan thì có thể tiếp nhận nhưng kiến thức chi tiết thì mập mờ . | Positive | R1 | "nhưng" contrast flips; "tiếp nhận/kiến thức" positive |
| 21 | … thầy wzjwz33 mô phỏng lý thuyết bằng hình ảnh . | Positive | R4 | typo token noise; positive tokens dominate |
| 22 | giảng dạy còn một số chỗ hơi khó hiểu . | Positive | R3 | "giảng dạy" positive; "khó hiểu" may be split/unmatched |
| 23 | thầy nghỉ quá nhiều . | Positive | R2/R5 | no neg-vocab; "thầy/nhiều" neutral→positive |
| 24 | không thấy được ứng dụng thực tế . | Positive | R1 | "không … thực tế/ứng dụng" flipped |
| 25 | cô dạy khá nhiệt tình , tuy nhiên lý thuyết còn hay nhầm lẫn , làm sinh viên mơ hồ . | Positive | R1 | "tuy nhiên" contrast; "nhiệt tình/hay" positive overpower |

## Recommended fixes (priority order)

1. **[QA-C6] Rebuild negation handling** *(fixes R1, the largest bucket)*
   - Apply a negator to a **forward window** of sentiment words (e.g. next 1–3 content tokens), not just the immediately-following token.
   - Negation should **invert a positive contribution to negative** and **leave/keep a negative contribution negative** — never turn an already-negative word positive. Remove the `score -= negative` sign-flip on neg-vocab words.
   - Add the failing edge cases (`không không tốt`, `không chẳng tốt`, `dạy hay nhưng dở`) to the regression suite.

2. **[QA-B2] Rebuild vocab with stopword removal / domain filtering** *(fixes R3)*
   - Build the vocab on the stopword-removed corpus for config B; drop tokens that are high-frequency in *both* classes (low discriminative value).

3. **[QA-C7] Introduce a Neutral band or explicit threshold** *(addresses R2/R5)*
   - Many "suggestion/criticism" comments carry no explicit negative lexicon. Consider a Neutral class or a lexicon of critique cues ("nên", "cần", "chưa", "hơi", "thiếu", "ít") that contribute negative weight.

4. **[QA-C4] Share one preprocessing function** between train and predict *(fixes R4)*
   - Strip punctuation/digits identically at predict time (currently only `build_vocab` does).

## Re-check target
After fixes: re-run this analysis. **Target error rate < 25%** and the Negative→Positive bias eliminated (errors should be roughly balanced across directions) before the Task 7 stopword conclusion is accepted.
