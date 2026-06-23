# QA Testing Report — Giai đoạn 2 (Task 7 & Task 8)

- **Branch:** `feat/sentiment-classifier` · **Reviewer:** Tâm (QA/QC) · **Date:** 2026-06-22
- **Runner:** `pytest 9.1.1`, Python 3.13.14, Windows 10
- **Overall verdict:** ❌ **FAIL / NOT APPROVED** (2 critical blockers)

---

## 1. Test execution summary

### 1.1 Per-module (hermetic / isolated runs)
| Module | Result |
|--------|--------|
| `tests/test_classifier.py` | **4 failed, 14 passed** |
| `tests/test_data_validation.py` | **18 passed** |
| `tests/test_experiment_validation.py` | **6 passed, 1 skipped** (Task 7 harness absent) |

### 1.2 Full-suite run (`python -m pytest tests/`)
```
13 failed, 47 passed, 1 skipped
```
> ⚠️ **The suite result is order-dependent.** In isolation only the 4 known functional tests fail.
> Run together, **9 extra tests fail** because `tests/test_build_vocab.py` calls `build_vocab()`,
> which is hard-coded to write `models/vocab/{pos,neg}_vocab.json` (ignoring its tmp fixture). The
> tiny fixture + `min_freq=5` leaves the committed vocab empty (`{}`, 2 bytes), so every later test
> that reads the vocab fails. **This is finding [QA-B5] and is itself a release blocker.**
> QA restored the vocab via `git checkout -- models/vocab/*.json` after the run.

## 2. Functional Testing — failures (from `test_classifier.py`)
| Test | Expected | Actual | Root cause |
|------|----------|--------|-----------|
| `test_mixed_sentiment_score_zero` (`"dạy hay nhưng dở"`) | Negative | Positive | QA-C6 negation flip |
| `test_only_stopwords` (`"và là của trong"`) | Negative | Positive | QA-B2 stopwords in vocab |
| `test_double_negation_expected_behavior` (`"không không tốt"`) | Positive | Negative | QA-C6 no multi-negation |
| `test_mixed_noise_and_vocab` (`"@@ dạy hay ## nhưng dở !!"`) | Negative | Positive | QA-C6 + QA-C4 punctuation |

## 3. Experiment Validation — Task 7 A/B measurement (reproduced by QA)
Ran `evaluate_model` (from `feat/A-B-test:experiments/run_experiment.py`) against `data/test/cleaned.csv` (2000 rows):

| Metric | Config A — no stopword removal | Config B — stopword removal | Δ (B − A) |
|--------|-------------------------------:|----------------------------:|----------:|
| Accuracy | 0.518 | 0.555 | +0.037 |
| Precision (weighted) | 0.665 | 0.677 | +0.012 |
| Recall (weighted) | 0.518 | 0.555 | +0.037 |
| F1 (weighted) | 0.380 | 0.462 | +0.082 |

**QA reading:**
- The A/B test is **fair and reproducible** (deterministic; same test set; only the flag differs) — `test_experiment_validation.py` confirms E1–E6 pass.
- **But the numbers are not trustworthy as a research result.** Both configs sit at ~chance accuracy on a binary task. Direct error mining (config A) showed **964 / 2000 = 48.2% error**, and *every* sampled error was Negative→Positive — a systematic bias caused by the broken negation logic (QA-C6). The +0.082 F1 "win" for stopword removal is measured on top of a fundamentally broken classifier, so the conclusion "lọc stopwords tốt hơn" is **not yet defensible**.
- Spec gap: `run_experiment.py` does **not** set `seed=42` (QA-E1) and writes CSVs to CWD instead of via `scripts/paths.py` (QA-E2).

## 4. Findings → Issues (assign to AIE Model / AIE Data)

| ID | Sev | File:Line | Title | Assignee |
|----|-----|-----------|-------|----------|
| QA-C6 | 🔴 CRITICAL | `models/classifier.py:46-58` | Negation logic flips negative words positive; no multi-token negation | AIE Model |
| QA-B5 | 🔴 CRITICAL | `models/build_vocab.py:14-25` | `build_vocab` overwrites committed vocab; tests not hermetic | AIE Model |
| QA-C3 | 🟠 HIGH | `models/classifier.py:18` | `predict` crashes when `negative_words=None` (uncaught TypeError) | AIE Model |
| QA-C4 / QA-B1 | 🟠 HIGH | `classifier.py` vs `build_vocab.py` | Train/predict preprocessing mismatch (punctuation/digits) | AIE Model |
| QA-C5 | 🟠 HIGH | `models/classifier.py` | Vocab/stopwords re-read from disk every `predict()` call | AIE Model |
| QA-B2 | 🟡 MED | `models/build_vocab.py` | Vocab built without stopword removal → polluted signal | AIE Data |
| QA-E1 | 🟡 MED | `experiments/run_experiment.py` | `seed=42` not set (spec) | AIE Model |
| QA-D1 | 🟡 MED | `data/*/*.csv` | UTF-8 **BOM** present at file start | AIE Data |
| QA-H1 | 🟠 HIGH | `tests/test_build_vocab.py` | 3/7 tests fail: monkeypatch stale `load_stopwords` (renamed `load_words`); `pos_vocab` used before assignment | AIE Model |
| QA-C1/C2/C7, T1, B3/B4, E2 | 🟢 LOW | various | Naming, magic numbers, tie→Negative default, unused import | — |

(Full per-line rationale is inline in the source as `# [QA-..]` comments.)

## 5. Completion-criteria check (Task 7 & 8)
| Criterion | Status |
|-----------|--------|
| `run_experiment.py` runs for both modes | ⚠️ runs, **but only on `feat/A-B-test`** |
| `results_comparison.csv` + chart exported | ⚠️ only on `feat/A-B-test` |
| Insight note on why B better/worse | ❌ `docs/Experimental_Results.md` missing |
| `docs/Experimental_Results.md` updated | ❌ missing |
| `docs/QA_Testing_Report.md` | ✅ this file |
| `docs/Error_Analysis.md` ≥20 cases | ✅ [Error_Analysis.md](Error_Analysis.md) |
| All checklist `[x]` | ❌ multiple `[ ]` |
| QA Approve / Merge final PR | ❌ **withheld** |

## 6. Re-check plan
After AIE Model fixes QA-C6 and QA-B5 (and Task 7 is merged with `Experimental_Results.md`):
1. `python -m pytest tests/ -v` must be **0 failed** and **order-independent**.
2. Re-run A/B; accuracy must be meaningfully > 0.5 and the negation edge cases must pass.
3. Re-mine errors; error rate target < 25% before the stopword conclusion is accepted.
4. QA re-validates the checklist → Approve only when all `[x]`.
