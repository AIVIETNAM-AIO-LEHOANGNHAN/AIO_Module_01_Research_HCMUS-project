# QA/QC Checklist — Task 7 (A/B Testing) & Task 8 (Quality Gate)

- **Branch under review:** `feat/sentiment-classifier`
- **Reviewer (QA/QC):** Tâm (QA/QC, AIO Conquer 2026)
- **Date:** 2026-06-22
- **Scope:** Giai đoạn 2 — từ điển, logic phân loại, và thí nghiệm A/B (Task 7), cổng kiểm soát chất lượng (Task 8).
- **Verdict:** ❌ **NOT APPROVED / BLOCKED** — see [QA_Testing_Report.md](QA_Testing_Report.md) and [Error_Analysis.md](Error_Analysis.md).

> Status legend: `[x]` đạt · `[ ]` chưa đạt · `[~]` đạt một phần / có rủi ro

---

## 0. Deliverables present on this branch (gate check)

| # | Required artifact (Task 7 / 8) | Present on `feat/sentiment-classifier`? | Status |
|---|--------------------------------|------------------------------------------|--------|
| 0.1 | `experiments/run_experiment.py` | ❌ Only on `feat/A-B-test` (not merged here) | [ ] |
| 0.2 | `results_raw.csv`, `results_cleaned.csv`, `results_comparison.csv` | ❌ Only on `feat/A-B-test` | [ ] |
| 0.3 | Comparison chart (`results_comparison_chart.png`) | ❌ Only on `feat/A-B-test` | [ ] |
| 0.4 | `docs/Experimental_Results.md` (Task 7 analysis) | ❌ Missing on all branches | [ ] |
| 0.5 | `docs/QA_Testing_Plan.md` | ✅ Created by this review | [x] |
| 0.6 | `docs/QA_Testing_Report.md` | ✅ Created by this review | [x] |
| 0.7 | `docs/Error_Analysis.md` (≥20 cases) | ✅ Created by this review | [x] |
| 0.8 | `app.py` (Streamlit dashboard / E2E) | ❌ File is empty | [ ] |

**QA note:** Task 7's experiment code is on a *separate, unmerged branch*. A reviewer checking out `feat/sentiment-classifier` alone cannot reproduce Task 7. **These branches must be merged (or rebased) before approval.**

---

## 1. Functional Testing — `tokenize()` and `predict()`

| # | Test case | Expected | Result | Finding |
|---|-----------|----------|--------|---------|
| F1 | `predict("hay")` (single positive) | Positive | ✅ PASS | — |
| F2 | `predict("dở")` (single negative) | Negative | ✅ PASS | — |
| F3 | `predict("dạy hay nhưng dở")` (mixed → tie) | Negative | ❌ **FAIL** → Positive | [QA-C6](#critical) |
| F4 | `predict("hay tốt đẹp")` | Positive | ✅ PASS | — |
| F5 | `predict("dở tệ chán")` | Negative | ✅ PASS | — |
| F6 | `predict_batch([...])` returns list aligned 1:1 | list len = N | ✅ PASS | — |
| F7 | `predict()` with default `negative_words=None` | should not crash | ❌ **risk** — `open(None)` raises uncaught `TypeError` | [QA-C3](#high) |
| F8 | Punctuation stripped consistently train vs predict | consistent | ❌ **FAIL** (train strips, predict doesn't) | [QA-C4](#high) |
| F9 | vocab/stopwords loaded once, not per-call | efficient | ❌ re-read on every `predict()` | [QA-C5](#high) |

- [ ] **Functional Testing PASSED** — 2 failing + 2 design defects.

## 2. Data Validation Testing — corpora & artifacts

| # | Test case | Expected | Result | Finding |
|---|-----------|----------|--------|---------|
| D1 | Train/Test columns = `[text, label]` | ✅ | ✅ PASS | — |
| D2 | No null values | ✅ | ✅ PASS | — |
| D3 | UTF-8 decodable text | ✅ | ✅ PASS (BOM present, see note) | [QA-D1](#medium) |
| D4 | Labels ∈ {0,1} | ✅ | ✅ PASS | — |
| D5 | Class balance 20–80% | ✅ | ✅ PASS | — |
| D6 | No fully duplicated rows | ✅ | ✅ PASS | — |
| D7 | No Train/Test leakage | ✅ | ✅ PASS | — |
| D8 | Vocab JSON valid + non-empty + counts ≥ 5 | ✅ | ✅ PASS *(after restore)* | [QA-B5](#critical) |
| D9 | Stopword files load as non-empty sets | ✅ | ✅ PASS | — |
| D10 | Protected words not also in removal list | ✅ | ✅ PASS | — |
| D11 | Vocab built **without** stopword removal (polluted) | clean | ❌ stopwords leak into vocab | [QA-B2](#medium) |

- [~] **Data Validation PASSED with risks** — D8 only passes because QA restored the vocab files that the test suite corrupts (QA-B5). D11 weakens the A/B isolation.

## 3. Experiment Validation Testing — fairness & reproducibility (Task 7)

| # | Test case | Expected | Result | Finding |
|---|-----------|----------|--------|---------|
| E1 | Predictions deterministic across runs | identical | ✅ PASS | — |
| E2 | Fresh instances, same config agree | identical | ✅ PASS | — |
| E3 | A and B evaluate the SAME test set | same N | ✅ PASS | — |
| E4 | A and B differ ONLY by stopword flag | ✅ | ✅ PASS | — |
| E5 | Removal actually changes ≥1 prediction | non-empty signal | ✅ PASS | — |
| E6 | Predictions ∈ {Positive, Negative} | ✅ | ✅ PASS | — |
| E7 | `seed=42` set as spec requires | seed fixed | ❌ no seed in `run_experiment.py` | [QA-E1](#medium) |
| E8 | Output paths reproducible (use `paths.py`) | ✅ | ❌ writes to CWD | [QA-E2](#low) |
| E9 | Model accuracy is meaningfully > chance | > ~0.5 | ❌ A=0.518 / B=0.555 (near random) | [QA-C6](#critical) |

- [ ] **Experiment Validation PASSED** — the experiment is *fair and reproducible*, but the **result it measures is not trustworthy** because the classifier is near-random (driven by the QA-C6 negation bug).

## 4. Edge Case Testing (from test plan docx)

| # | Case | Expected | Result | Finding |
|---|------|----------|--------|---------|
| EC1 | Empty string `""` | Negative (documented default) | ✅ PASS | [QA-C7](#medium) |
| EC2 | Only stopwords `"và là của trong"` | Negative | ❌ **FAIL** → Positive | [QA-B2](#medium) |
| EC3 | Negation `"không hay"` | Negative | ✅ PASS | — |
| EC4 | Double negation `"không không tốt"` | Positive (spec) | ❌ **FAIL** → Negative | [QA-C6](#critical) |
| EC5 | Negation chain `"không chẳng tốt"` | Positive (spec) | ❌ **FAIL** | [QA-C6](#critical) |
| EC6 | Noise punctuation `"!!! hay ???"` | Positive | ❌ **FAIL** | [QA-C4](#high) |

- [ ] **Edge Case Testing PASSED.**

## 5. Test-suite hygiene (Manual Review)

| # | Check | Result | Finding |
|---|-------|--------|---------|
| H1 | Tests are hermetic (no side effects on tracked files) | ❌ `test_build_vocab` overwrites committed vocab | [QA-B5](#critical) |
| H2 | Suite result independent of test order | ❌ 4 fail isolated / 13 fail together | [QA-B5](#critical) |
| H3 | Tests assert spec, not buggy behaviour | ✅ (functional tests encode correct spec) | — |
| H4 | `tests/test_build_vocab.py` is green & up to date | ❌ 3/7 fail: monkeypatch stale `load_stopwords` + use-before-assign | [QA-H1](#medium) |

---

## 6. Severity summary

| Severity | Count | IDs |
|----------|-------|-----|
| 🔴 CRITICAL | 2 | QA-B5, QA-C6 |
| 🟠 HIGH | 5 | QA-C3, QA-C4, QA-C5, QA-B1, QA-H1 |
| 🟡 MEDIUM | 6 | QA-C1, QA-C7, QA-B2, QA-B4, QA-D1, QA-E1 |
| 🟢 LOW | 4 | QA-C2, QA-T1, QA-B3, QA-E2 |

## 7. Approval decision

> Theo hướng dẫn QA/QC (AIO Conquer 2026): *"Ưu tiên đúng lỗi quan trọng. Sai yêu cầu, thiếu logic và thiếu bằng chứng luôn phải được xử lý trước các lỗi về hình thức."*

❌ **Giai đoạn 2 KHÔNG được Approve.** Blockers phải xử lý trước khi re-check:
1. **QA-C6** — sửa logic phủ định (đang khiến mô hình gần như random, ~48% sai).
2. **QA-B5** — `build_vocab` ghi đè artifact đã commit; test không hermetic.
3. **0.1–0.4 / 0.8** — merge Task 7 (`experiments/`, results, chart) + viết `docs/Experimental_Results.md`; bổ sung `app.py`.

Sau khi AIE Model fix → QA re-check toàn bộ checklist → nếu tất cả `[x]` thì Approve/Merge.
