# QA/QC Checklist — Task 7 (A/B Testing) on `feat/A-B-test`

- **Branch under review:** `feat/A-B-test`
- **Reviewer (QA/QC):** Tâm (AIO Conquer 2026)
- **Date:** 2026-06-22
- **Scope:** Task 7 — quy trình thực nghiệm A/B đo hiệu quả của việc loại bỏ stopwords (`experiments/run_experiment.py` + result artifacts). Logic phân loại (`models/`) được kiểm tra ở mức ảnh hưởng đến tính hợp lệ của kết quả.
- **Verdict:** ❌ **NOT APPROVED** — thí nghiệm *công bằng & tái lập được*, nhưng *kết quả không đáng tin* (mô hình gần như ngẫu nhiên) và thiếu tài liệu phân tích bắt buộc.

> Legend: `[x]` đạt · `[ ]` chưa đạt · `[~]` đạt một phần / có rủi ro

---

## 0. Task 7 deliverables (gate check)

| # | Required artifact | Present on `feat/A-B-test`? | Status |
|---|-------------------|------------------------------|--------|
| 0.1 | `experiments/run_experiment.py` with `evaluate_model(classifier, test_data)` | ✅ | [x] |
| 0.2 | `results_raw.csv` (config A) | ✅ | [x] |
| 0.3 | `results_cleaned.csv` (config B) | ✅ | [x] |
| 0.4 | `results_comparison.csv` | ✅ | [x] |
| 0.5 | Comparison chart `results_comparison_chart.png` | ✅ | [x] |
| 0.6 | Fixed `seed=42` per spec | ❌ no seed set | [ ] |
| 0.7 | Insight/analysis note (`docs/Experimental_Results.md`) | ❌ **missing** | [ ] |
| 0.8 | Script runs successfully out-of-the-box | ❌ crashes (import + Windows encoding) | [ ] |

---

## 1. Functional Testing — `evaluate_model()` & script

| # | Test case | Expected | Result | Finding |
|---|-----------|----------|--------|---------|
| F1 | `evaluate_model` returns Accuracy/Precision/Recall/F1 | 4 keys | ✅ PASS | — |
| F2 | All metrics ∈ [0,1] | ✅ | ✅ PASS | — |
| F3 | `evaluate_model(classifier, test_data)` signature matches spec | ✅ | ✅ PASS | — |
| F4 | `python experiments/run_experiment.py` runs from repo root | runs | ❌ **FAIL** `ModuleNotFoundError: models` | [QA-E2](#high) |
| F5 | Script completes on Windows default console | runs | ❌ **FAIL** `UnicodeEncodeError` before comparison.csv/chart | [QA-E3](#high) |
| F6 | All imports declared in `requirements.txt` | ✅ | ❌ `matplotlib` missing | [QA-E10](#medium) |

- [ ] **Functional Testing PASSED** — runs only with `PYTHONPATH` + UTF-8 stdout manually set.

## 2. Data Validation Testing — experiment inputs

| # | Test case | Expected | Result | Finding |
|---|-----------|----------|--------|---------|
| D1 | Test set columns `[text,label]` | ✅ | ✅ PASS | — |
| D2 | Labels ∈ {0,1}, no nulls | ✅ | ✅ PASS | — |
| D3 | No Train/Test leakage | ✅ | ✅ PASS | — |
| D4 | Label mapping in `evaluate_model` validated | strict | ❌ any value ≠ '1' silently → Negative | [QA-E7](#medium) |
| D5 | Committed `results_*.csv` match a fresh recomputation | match | ✅ PASS (not stale) | — |
| D6 | Both configs use the SAME vocab/resources | fair | [~] same vocab, but built WITHOUT stopword removal | [QA-E9](#medium) |

- [~] **Data Validation PASSED with risks.**

## 3. Experiment Validation Testing — fairness & reproducibility

| # | Test case | Expected | Result | Finding |
|---|-----------|----------|--------|---------|
| E1 | Re-running gives identical numbers | deterministic | ✅ PASS | — |
| E2 | A & B evaluate the same test set (same N) | ✅ | ✅ PASS | — |
| E3 | A & B differ ONLY by `use_stopwords_removal` | ✅ | ✅ PASS | — |
| E4 | Stopword removal changes ≥1 metric (has signal) | ✅ | ✅ PASS | — |
| E5 | `seed=42` fixed per spec | ✅ | ❌ not set (note determinism instead) | [QA-E1](#high) |
| E6 | Per-class metrics reported (not only weighted) | ✅ | ❌ only weighted; hides class collapse | [QA-E6](#medium) |
| E7 | Model accuracy meaningfully > chance | > ~0.5 | ❌ A=0.518 / B=0.555; F1 0.380/0.462 | [QA-E4](#critical) |
| E8 | Output written to a stable location (`paths.py`) | ✅ | ❌ bare filenames → CWD | [QA-E5](#medium) |

- [ ] **Experiment Validation PASSED** — process fair & reproducible, but the measured result is not trustworthy (see QA-E4).

## 4. Result interpretation (Manual Review)

| # | Check | Result | Finding |
|---|-------|--------|---------|
| R1 | Comparison table & Delta correct | ✅ A=0.518/B=0.555, ΔF1=+0.082 | — |
| R2 | Conclusion "lọc stopwords hiệu quả hơn" is justified | ❌ both near random; conclusion premature | [QA-E4](#critical) |
| R3 | Error direction analysed | ❌ 954/964 (A) errors are Neg→Pos — systematic bias | [QA-E4](#critical) |
| R4 | Suite is hermetic / order-independent | ❌ `test_build_vocab` overwrites committed vocab | [QA-B5](#critical) |

---

## 5. Severity summary

| Severity | Count | IDs |
|----------|-------|-----|
| 🔴 CRITICAL | 2 | QA-E4, QA-B5 |
| 🟠 HIGH | 3 | QA-E1, QA-E2, QA-E3 |
| 🟡 MEDIUM | 5 | QA-E5, QA-E6, QA-E7, QA-E9, QA-E10 |
| 🟢 LOW | 1 | QA-E8 |

## 6. Approval decision

❌ **Task 7 KHÔNG được Approve.** Blockers trước khi re-check:
1. **QA-E4** — kết quả dựa trên mô hình gần random (lỗi phủ định trong `classifier.py`); phải fix classifier rồi chạy lại A/B trước khi kết luận.
2. **QA-E2 / QA-E3** — script không chạy được out-of-the-box (import + encoding trên Windows); 2/3 deliverable không sinh ra trên môi trường tài liệu.
3. **0.7** — bổ sung `docs/Experimental_Results.md` (insight: vì sao B tốt hơn/tệ hơn).
4. **QA-E1** — set `seed=42` hoặc ghi chú lý do mô hình tất định.

Sau khi AIE Model fix → QA re-check toàn bộ checklist → nếu tất cả `[x]` thì Approve/Merge PR.

> Chi tiết kết quả chạy: [QA_Testing_Report.md](QA_Testing_Report.md) · Phân tích lỗi: [Error_Analysis.md](Error_Analysis.md) · Kế hoạch: [QA_Testing_Plan.md](QA_Testing_Plan.md)
