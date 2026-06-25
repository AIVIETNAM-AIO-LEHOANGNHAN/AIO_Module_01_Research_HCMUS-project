# QA Testing Report — Task 7 (A/B Testing) · branch `feat/A-B-test`

- **Reviewer:** Tâm (QA/QC) · **Date:** 2026-06-22
- **Runner:** `pytest 9.1.1`, Python 3.13.14, Windows 10
- **Verdict:** ❌ **FAIL / NOT APPROVED** (2 critical blockers)

---

## 1. Test execution summary

| Suite | Result |
|-------|--------|
| `tests/test_experiment.py` (Task 7 — new) | **11 passed** |
| `tests/test_classifier.py` (isolated) | **4 failed, 14 passed** |
| Full suite `python -m pytest tests/` | **10 failed, 26 passed** (order-dependent — see §4) |

## 2. A/B experiment result (reproduced by QA)
`python -m experiments.run_experiment` on `data/test/cleaned.csv` (2000 rows) — numbers identical to the committed `results_*.csv` (✅ reproducible, not stale):

| Metric | A — no stopword removal | B — stopword removal | Δ (B − A) |
|--------|------------------------:|---------------------:|----------:|
| Accuracy | 0.518 | 0.555 | +0.037 |
| Precision (weighted) | 0.665 | 0.677 | +0.012 |
| Recall (weighted) | 0.518 | 0.555 | +0.037 |
| F1 (weighted) | 0.380 | 0.462 | +0.082 |

### Error direction (QA error-mining)
| Config | Errors / 2000 | Neg→Pos | Pos→Neg |
|--------|--------------:|--------:|--------:|
| A (no removal) | 964 (48.2%) | **954** | 10 |
| B (removal) | 890 (44.5%) | 860 | 30 |

**QA reading:** The experiment is **fair and reproducible** (E1–E4 pass), but both configs sit at ~chance accuracy and the model labels **almost every negative review "Positive"** (954/964 errors in A). The +0.082 F1 "win" for stopword removal is measured on top of a fundamentally broken classifier, so the conclusion *"lọc stopwords hiệu quả hơn"* is **not yet defensible**.

## 3. Reproducibility / runnability defects
| ID | Observed |
|----|----------|
| QA-E2 | `python experiments/run_experiment.py` → `ModuleNotFoundError: No module named 'models'` (no sys.path bootstrap). |
| QA-E3 | With path fixed, crashes on Windows cp1252 console at `print("=== BẢNG SO SÁNH ===")` **before** writing `results_comparison.csv` and the chart. Completes only with `PYTHONIOENCODING=utf-8`. |
| QA-E1 | No `seed=42` (spec). Model is deterministic so results reproduce, but the spec requirement is unmet and undocumented. |
| QA-E10 | `matplotlib` imported but absent from `requirements.txt`. |

## 4. Test-suite hygiene (order dependence)
Running the full suite yields **10 failed** vs only 4 in isolation. Extra failures come from `tests/test_build_vocab.py`, whose `build_vocab()` call is hard-coded to write `models/vocab/{pos,neg}_vocab.json` (QA-B5). The tiny fixture + `min_freq=5` empties the committed vocab (`{}`), so later tests that read it fail. **Also**: `test_build_vocab.py` itself has 3 failing tests (monkeypatches the renamed `load_stopwords` → `load_words`). QA restored the vocab via `git checkout` after the run.

## 5. Findings → Issues

| ID | Sev | Location | Title | Assignee |
|----|-----|----------|-------|----------|
| QA-E4 | 🔴 CRITICAL | `models/classifier.py` (negation) | A/B result built on near-random classifier (48% err, Neg→Pos bias) | AIE Model |
| QA-B5 | 🔴 CRITICAL | `models/build_vocab.py` / `tests/test_build_vocab.py` | `build_vocab` overwrites committed vocab; non-hermetic suite | AIE Model |
| QA-E2 | 🟠 HIGH | `experiments/run_experiment.py:1` | Script unrunnable from repo root (no path bootstrap) | AIE Model |
| QA-E3 | 🟠 HIGH | `experiments/run_experiment.py:47` | Windows cp1252 crash before 2/3 outputs written | AIE Model |
| QA-E1 | 🟠 HIGH | `experiments/run_experiment.py` | `seed=42` not set (spec) | AIE Model |
| QA-E5 | 🟡 MED | `run_experiment.py` (to_csv) | Outputs to CWD, not via `paths.py` | AIE Model |
| QA-E6 | 🟡 MED | `run_experiment.py:15-17` | Only weighted metrics; class collapse hidden | AIE Model |
| QA-E7 | 🟡 MED | `run_experiment.py:11` | Silent label mapping (≠'1' → Negative) | AIE Data |
| QA-E9 | 🟡 MED | `build_vocab.py` + experiment | Shared vocab built without stopword removal → tests only inference-time removal | AIE Model |
| QA-E10 | 🟡 MED | `requirements.txt` | `matplotlib` undeclared | AIE Data |
| QA-E8 | 🟢 LOW | `run_experiment.py:123` | `plt.show()` blocks headless | AIE Model |

(Per-line rationale is inline in `experiments/run_experiment.py` as `# [QA-E..]` comments.)

## 6. Completion-criteria check (Task 7)
| Criterion | Status |
|-----------|--------|
| `run_experiment.py` runs for both modes | ⚠️ runs only with PYTHONPATH + UTF-8 stdout (QA-E2/E3) |
| `results_comparison.csv` + chart exported | ✅ present & reproducible |
| Insight note on why B better/worse | ❌ `docs/Experimental_Results.md` missing |
| `docs/Experimental_Results.md` updated | ❌ missing |
| QA confirms fairness & result | ⚠️ fairness ✅, result ❌ not trustworthy (QA-E4) |

## 7. Re-check plan
1. Fix QA-E4 (negation in classifier) → re-run A/B; accuracy must be meaningfully > 0.5 and Neg→Pos bias gone.
2. Fix QA-E2/E3 so `python -m experiments.run_experiment` runs clean on Windows and writes all 3 outputs.
3. Add `docs/Experimental_Results.md` with the insight + the fairness/scope note (QA-E9).
4. Fix QA-B5 so the suite is hermetic; target `python -m pytest tests/` = 0 failed.
5. QA re-validates the checklist → Approve/Merge only when all `[x]`.
