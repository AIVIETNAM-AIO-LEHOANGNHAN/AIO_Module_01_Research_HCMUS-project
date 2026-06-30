# QA/QC Checklist — Task 9 & Task 10

**Branch:** `feat/pipeline-streamlit-app`
**Reviewer:** QA/QC
**Date:** 2026-06-30
**Files under test:** [`pipeline/run_pipeline.py`](pipeline/run_pipeline.py) (Task 9), [`app.py`](app.py) (Task 10)
**Method:** Static review + headless execution of all pipeline steps + empirical reproduction of threshold search and batch-label handling.

> **Note (rebase):** This review was first done against commit `773e8e9`, then rebased onto teammate commits `e98ca6e` / `330b8e0` ("sua lai streamlit UI" / "fix UI 1") which rewrote `app.py` (i18n + two-column layout). Findings were reconciled against that new code: **S13 is already fixed** by their i18n button, and **S8 is downgraded to Medium** (their rewrite now raises a clear error instead of crashing silently). S9 and S2 still apply. The Task-10 criteria table below was validated against the pre-rewrite `app.py`; the UI structure changed but the underlying classifier behavior did not.

---

## Verdict

| Task | Result | Summary |
|------|--------|---------|
| **Task 9 — End-to-end Pipeline** | ✅ **PASS** (with notes) | All 10 acceptance criteria met. Pipeline runs clean end-to-end (18 threshold rows, valid confusion matrices, CSV exported). Notes are improvements, not blockers. |
| **Task 10 — Streamlit UI** | ✅ **PASS** (post-rewrite) | All criteria met. **S8 (batch text-labels)** is the main open gap: the spec says to *convert* `Positive`/`Negative` labels to 1/0, but the code rejects them with a clear error instead. No longer a crash. S13 already fixed by teammate. |

---

## Task 9 — Acceptance Criteria (`pipeline/run_pipeline.py`)

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | `pipeline/run_pipeline.py` exists | ✅ | File present in repo |
| 2 | 4 steps run in order on "Chạy toàn bộ" | ✅ ⚠️ | `run_all_pipeline()` calls validate→build→clean→experiment→export sequentially. **Note S1:** only one global spinner — no per-step status. |
| 3 | Each step runs independently | ✅ | 4 separate sidebar buttons; `step_clean_vocab` guards missing vocab with `FileNotFoundError` |
| 4 | 4 vocab files created after Step 1 | ✅ | Verified: `exp_a/{pos,neg}_vocab.json`, `exp_b/{pos,neg}_vocab.json` regenerated |
| 5 | Vocab count drops after Step 2 | ✅ | Verified live: exp_a/pos 717→696 (−21), exp_a/neg 1341→1314 (−27), exp_b/pos 552→534 (−18), exp_b/neg 1135→1111 (−24) |
| 6 | Threshold table shows 9 rows | ✅ | 9 thresholds × 2 experiments = 18 rows produced |
| 7 | `docs/threshold_results.csv` created | ✅ | File written & re-exported successfully |
| 8 | Download CSV button works | ✅ | `st.download_button` reads file in `rb`, valid `text/csv` mime |
| 9 | No hardcoded paths | ✅ | All paths from `scripts/paths.py`; `VOCAB_ROOT`/`DOCS_DIR` derived from `PROJECT_ROOT` |
| 10 | Step failure halts subsequent steps | ✅ | Steps raise; exceptions propagate up `run_all_pipeline` and are caught in `main()` → run stops |

### Task 9 — Findings

| ID | Severity | Location | Finding |
|----|----------|----------|---------|
| **S1** | Medium (spec) | `run_pipeline.py:264-269` | "Chạy toàn bộ Pipeline" shows a single global spinner. Spec requires each step to show **đang chạy / hoàn thành / lỗi**. Wrap each of the 4 steps in its own `st.status()`/spinner so a failure is attributable to a specific step. |
| **S2** | Medium (analysis) | `run_pipeline.py:164` | "Best threshold" is selected by **accuracy only**. The task's stated motivation was to fix over-prediction of Positive (FP≈703) by balancing precision/recall. Empirically the best-accuracy threshold is 2.0, where **exp_a still has FP=731** — i.e. accuracy optimization does **not** address the stated goal. The real improvement comes from stopword removal (exp_b FP=351), not threshold tuning. Consider selecting by **F1** (or reporting the precision/recall trade-off) to match the stated objective. |
| **S3** | Low (UX) | `run_pipeline.py:237-238` | Confusion matrix is dumped as a raw nested list with no TN/FP/FN/TP labels — hard to read. Render as a labeled 2×2 table. |
| **S4** | Low (spec) | `run_pipeline.py` (build step) | `build_vocab()` reports progress via `print()` → terminal only. Spec Step 1 asks for progress **on the Streamlit UI**. |
| **S5** | Info (logic) | `run_pipeline.py` / `classifier.py` | The clean-vocab premise ("rule words left in vocab get processed twice") is not strictly true: `Classifier._score_tokens` checks negator/intensifier/critique **before** pos/neg vocab and `continue`s, so a rule word in vocab is shadowed and never double-counted. Clean Vocab is still good hygiene (smaller vocab) but is not correctness-critical for scoring. |

---

## Task 10 — Acceptance Criteria (`app.py`)

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | `app.py` at project root | ✅ | Present at root |
| 2 | Header shows project name | ✅ | `app.py:232-233` title + caption |
| 3 | Toggle OFF → Classifier A | ✅ | `exp_name = "exp_a"`, `remove_stopwords=False` |
| 4 | Toggle ON → Classifier B | ✅ | `exp_name = "exp_b"`, `remove_stopwords=True` |
| 5 | Toggle change is fast | ✅ | `@st.cache_resource` keyed by `(exp_name, remove_stopwords)` |
| 6 | Stopword struck-through when toggle ON | ✅ | `analyze_tokens` flags `removed=True`; `render_token_view` applies `line-through` |
| 7 | Stopword normal when toggle OFF | ✅ | Branch only fires when `remove_stopwords` is True |
| 8 | 7 token colors | ✅ | `render_token_view` defines 7 styles (stopword/negator/intensifier/critique/positive/negative/normal) |
| 9 | Token stats correct | ✅ ⚠️ | Counts computed correctly. **Note S11:** token list shown ≠ tokens actually scored (different tokenization paths). |
| 10 | Valid file → runs | ✅ | `pd.read_csv` → preview → `evaluate_batch` |
| 11 | Invalid file (missing column) → error, no crash | ✅ | `evaluate_batch` raises `ValueError`; caught by `try/except` → `st.error` |
| 12 | Metrics table shows 4 metrics | ✅ | accuracy/precision/recall/f1 |
| 13 | Chart: 4 groups × 2 bars | ✅ | `px.bar` melt + `barmode="group"` |
| 14 | Auto conclusion matches data | ✅ | Compares `acc_b` vs `acc_a` → success/warning/error |
| 15 | Empty input no crash | ✅ | `if not text.strip(): return` |

### Task 10 — Findings

| ID | Severity | Location | Finding |
|----|----------|----------|---------|
| **S8** | Medium (spec) *(was High; reduced after teammate rewrite)* | `evaluate_batch` (`astype(int)` + label validation) | Original code crashed silently on text labels. The teammate rewrite now validates `label ∈ {0,1}` and raises a clear `"Column label only accepts 0/1"` error — **no more silent crash**. Remaining gap: Spec Step 4 says to *convert* text labels (`Positive`→1, `Negative`→0); the code still **rejects** them via `astype(int)` instead of mapping. **Fix:** also accept `{"Positive":1,"Negative":0}` so the documented CSV format works. |
| **S9** | Medium (consistency) | `app.py:155` | Decision threshold `2.0` is hardcoded here, duplicating `Classifier.predict()`'s internal `2.0`. Single-predict and batch then use **two different code paths** for the same decision. Call `classifier.predict(text)` instead so the rule lives in one place. |
| **S10** | Medium (robustness) | `app.py:43-48` | `validate_vocab_files()` checks only the 4 vocab JSONs, **not** the lexicon files. `load_words()` returns an empty set silently on a missing lexicon → negation/intensifier/critique scoring is silently disabled with no UI warning. Validate lexicons too (or surface the warning). |
| **S11** | Low (consistency) | `app.py:51-53` | `analyze_tokens` tokenizes the whole preprocessed text, but `get_score` first splits on `[,.!?;]` then tokenizes each segment. For sentences with punctuation the displayed token list/counts can differ from what was actually scored. |
| **S12** | Low (cross-task) | `app.py` vs `run_pipeline.py` | App uses a **fixed** 2.0 threshold; the pipeline **searches** for a best threshold. They agree only because the best happened to be 2.0. If vocab/data change, the two deliverables will disagree on the decision rule. Consider sharing the searched best threshold. |
| ~~**S13**~~ | ✅ Resolved | `app.py` | Button label missing diacritics — **already fixed** in the teammate rewrite (now uses i18n `tr(lang, "run_batch")` = "Chạy đánh giá Batch"). No action needed. |

---

## Data Validation (advisor QA/QC plan — strategy 1)

| Check | Result |
|-------|--------|
| `data/test/cleaned.csv` & `data/train/cleaned.csv` exist | ✅ |
| Label format | ✅ numeric `int64` (1/0) — consistent with `build_vocab` (`label == 1`) and pipeline `evaluate_thresholds` |
| UTF-8 BOM on CSVs | ⚠️ Files start with BOM (`EF BB BF`). Current pandas strips it (columns read as `text`/`label`), so **not a live failure** — but it's version-dependent. Re-saving as UTF-8 (no BOM) or reading with `encoding="utf-8-sig"` removes the risk. |
| Required columns `text`, `label` | ✅ present in both |

---

## Recommended fix priority

1. **S8 (Medium)** — make batch test *accept/convert* `Positive`/`Negative` labels per spec (currently rejects them with a clear error).
2. **S2 (Medium)** — align threshold-selection metric with the stated precision/recall goal (use F1, or document accuracy choice).
3. **S10 (Medium)** — validate lexicons / surface missing-file warnings.
4. **S9, S1 (Medium)** — de-duplicate the 2.0 threshold; add per-step status in "Run all".
5. **S3, S4, S5, S11, S12, S13 (Low/Info)** — polish.

> Inline `# QA/QC [Sx]:` comments have been added at each location above in `pipeline/run_pipeline.py` and `app.py`.
