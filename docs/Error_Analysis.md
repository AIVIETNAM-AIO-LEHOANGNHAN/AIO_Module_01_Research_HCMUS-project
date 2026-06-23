# Error Analysis — Task 7 / Giai đoạn 2 · branch `feat/A-B-test`

- **QA/QC:** Tâm · **Date:** 2026-06-22
- **Source:** `Classifier` over `data/test/cleaned.csv` (2000 rows), both A/B configs.

## Aggregate
| Config | Errors / 2000 | Error rate | Neg→Pos | Pos→Neg |
|--------|--------------:|-----------:|--------:|--------:|
| A — no stopword removal | 964 | **48.2%** | 954 | 10 |
| B — stopword removal | 890 | **44.5%** | 860 | 30 |

**The model labels almost every negative review "Positive."** Errors are not random — they are a one-directional systematic bias (Neg→Pos). Stopword removal (B) only marginally reduces error (48.2% → 44.5%) and the classifier remains near chance. This is why the Task 7 conclusion cannot be trusted yet (finding QA-E4).

## Root-cause categories
| Cat | Description | Finding |
|-----|-------------|---------|
| **R1** | Negation/contrast word flips a negative word to positive (`score -= negative` with `negative=-1`); negation can't span tokens | QA-E4 (classifier negation) |
| **R2** | Criticism phrased without explicit negative vocab ("nên…", "cần…", "chưa…"); positive tokens dominate → score>0 | QA-E4 / tie→Neg |
| **R3** | Stopwords / domain-neutral words carry positive weight (vocab built without stopword removal) | QA-E9 |
| **R4** | Punctuation/digits/typos not stripped at predict time → tokens never match vocab | (classifier preprocessing) |
| **R5** | Tie / no-signal sentences resolved arbitrarily (no Neutral class) | tie→Negative |

## Case log (25 real cases — gold = Negative, predicted = Positive)
| # | Text | Cat | Why it failed |
|---|------|-----|---------------|
| 1 | không cho sinh viên nhiều kiến thức . | R1 | "không" negator; "kiến thức/nhiều" win |
| 2 | điều này gây mất công bằng và không đánh giá được đúng năng lực học tập của các bạn . | R1 | "không … đúng/năng lực" flipped |
| 3 | cơ sở vật chất còn ảnh hưởng đến chất lượng môn học . | R2 | criticism w/o neg-vocab; "chất lượng" positive |
| 4 | giảng viên nên dạy lâu hơn mỗi buổi học . | R2 | suggestion "nên"; no neg word |
| 5 | chuẩn bị âm thanh trước môn học ổn định để tránh mất thì giờ … | R2/R3 | "ổn định/chuẩn bị" positive |
| 6 | cần thể hiện chi tiết hơn nội dung … và nhiều ví dụ minh hoạ hơn . | R2 | "cần … hơn" = request, scored positive |
| 7 | số lượng buổi học hơi ít so với nội dung thực hành . | R2/R5 | mild complaint, no neg-vocab |
| 8 | còn những phần … chứng minh dạng chuẩn chưa làm rõ . | R1 | "chưa … rõ/chuẩn" positive |
| 9 | nên sử dụng máy chiếu để hiện rõ chữ … giải bài tập minh họa . | R2 | "nên/rõ/tập trung" positive |
| 10 | tóm lại thầy nên học một khóa về kỹ năng giao tiếp . | R2 | implicit criticism; "kỹ năng/học" positive |
| 11 | giáo viên dạy chưa tốt . | R1 | "chưa" negator but "tốt" still scored positive |
| 12 | cần đảm bảo thời gian lên lớp . | R2 | "đảm bảo" positive token |
| 13 | nên cập nhật slide thường xuyên vì quá cũ không tích hợp được … | R1/R2 | "không tích hợp" flipped; "cập nhật" positive |
| 14 | giáo trình môn học nên cập nhật thường xuyên . | R2 | "nên cập nhật" read positive |
| 15 | giáo trình quá ít và nội dung không khác nhau là mấy . | R1 | "không khác" flipped |
| 16 | … chỉ cần sai sót nhỏ sẽ rớt môn . | R2/R3 | neutral tokens; no neg-vocab |
| 17 | thời gian thầy giảng dạy ngắn , thường cho lớp về sớm . | R2 | "giảng dạy/thầy" positive; "ngắn" not in neg-vocab |
| 18 | ra đề thi midterm cả lớp toàn 0 , 1 , 2 đến 3 điểm . | R4/R5 | digits not stripped; no sentiment token |
| 19 | nên sắp lịch học phù hợp . | R2 | "phù hợp" positive |
| 20 | … kiến thức tổng quan thì có thể tiếp nhận nhưng … chi tiết thì mập mờ . | R1 | "nhưng" contrast flips; "tiếp nhận/kiến thức" positive |
| 21 | … thầy wzjwz33 mô phỏng lý thuyết bằng hình ảnh . | R4 | typo token noise; positive tokens dominate |
| 22 | giảng dạy còn một số chỗ hơi khó hiểu . | R3 | "giảng dạy" positive; "khó hiểu" unmatched |
| 23 | thầy nghỉ quá nhiều . | R2/R5 | no neg-vocab; "thầy/nhiều" → positive |
| 24 | không thấy được ứng dụng thực tế . | R1 | "không … thực tế/ứng dụng" flipped |
| 25 | cô dạy khá nhiệt tình , tuy nhiên lý thuyết còn hay nhầm lẫn … mơ hồ . | R1 | "tuy nhiên" contrast; "nhiệt tình/hay" overpower |

## Recommended fixes (priority order)
1. **[QA-E4] Rebuild negation handling** (fixes R1, the largest bucket): apply a negator to a forward window of sentiment words; invert positive→negative only, never turn an already-negative word positive; remove the `score -= negative` sign-flip on negative-vocab words.
2. **[QA-E9] Rebuild vocab with stopword removal / drop ambiguous tokens** (fixes R3) so config B truly isolates the stopword variable.
3. **Tie/Neutral handling** (R2/R5): add a critique-cue lexicon ("nên","cần","chưa","hơi","thiếu","ít") contributing negative weight, or a Neutral band.
4. **Shared preprocessing** between train & predict (R4): strip punctuation/digits identically at predict time.

## Re-check target
After fixes, re-run this analysis. **Target error rate < 25%** and the Neg→Pos bias eliminated (errors roughly balanced across directions) before the Task 7 stopword conclusion is accepted, then re-run the A/B experiment for the final numbers.
