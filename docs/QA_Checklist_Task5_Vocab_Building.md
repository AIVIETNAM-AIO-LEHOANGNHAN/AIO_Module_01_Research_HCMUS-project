# QA Checklist — Task 5 (KAN-13): Build Vocabulary
**Branch:** `feat/model-vocab-building`
**Base:** `develop`
**Reviewer:** QA Role
**Review Date:** 2026-06-17
**Automated tests:** `tests/test_text_utils.py`, `tests/test_build_vocab.py`

---

## Phạm vi kiểm thử (Scope)

| In scope | Out of scope |
|----------|--------------|
| `utils/text_utils.py` | Model inference / scoring |
| `models/build_vocab.py` | Streamlit app |
| `models/vocab/{pos,neg}_counter.json` | Task 6 rule-based classifier |
| `data/stopwords/custom.txt` (input) | CI/CD pipeline |

---

## Môi trường kiểm thử

```bash
py -m pip install -r requirements.txt pytest
py -m pytest tests/ -v
```

- Python 3.10+
- Libraries: `pandas`, `pyvi`, `pytest`
- Dataset: `data/train/cleaned.csv` (8000 rows)

---

## Task 5 — Functional Testing

| # | Test Case | Expected | Actual (branch) | Status | Notes |
|---|-----------|----------|-----------------|--------|-------|
| T5-01 | `load_stopwords("data/stopwords/custom.txt")` trả về set không rỗng | set, >1500 entries | ~1930 entries | ✅ PASS | |
| T5-02 | Protected words không có trong `custom.txt` | 0 overlap | 0 overlap | ✅ PASS | Khớp quyết định team (comment PR) |
| T5-03 | `tokenize("giảng viên nhiệt tình")` giữ compound với `_` | `giảng_viên`, `nhiệt_tình` | `giảng_viên`, `nhiệt_tình` (space) | ✅ PASS | |
| T5-04 | `tokenize()` dùng `ViTokenizer.tokenize()` (spec) | Dùng API chuẩn | Dùng API chuẩn | ✅ PASS |  |
| T5-05 | `build_vocab()` chạy trên `train/cleaned.csv` | Không exception | Không exception | ✅ PASS | |
| T5-06 | Output file names theo spec | `pos_vocab.json`, `neg_vocab.json` | `pos_vocab.json`, `neg_vocab.json` | ✅ PASSL |  |
| T5-07 | Label routing: label=1 → pos, label=0 → neg | Đúng counter | Đúng | ✅ PASS | |
| T5-08 | `min_freq >= 5` lọc noise | Không có token freq < 5 | Không có token freq < 5 | ✅ PASS |  |
| T5-09 | Sentiment words (`rất`, `tốt`, `kém`, `không`) có trong vocab | Có trong pos/neg | Có | ✅ PASS | Nhờ custom.txt đã loại protected |
| T5-10 | Stopwords trong `custom.txt` bị loại khỏi vocab | Không xuất hiện | Cần spot-check | ⚠️ WARN | VD: `và`, `của` không nên có |

---

## Data Validation Testing

| # | Check | Expected | Actual | Status |
|---|-------|----------|--------|--------|
| DV5-01 | Protected ∩ custom = ∅ | 0 | 0 | ✅ PASS |
| DV5-02 | `pos_counter.json` hợp lệ JSON UTF-8 | Yes | Yes | ✅ PASS |
| DV5-03 | `neg_counter.json` hợp lệ JSON UTF-8 | Yes | Yes | ✅ PASS |
| DV5-04 | Không có punctuation trong vocab | 0 keys | `,`: 2817, `.`: 3846 (pos) | ❌ FAIL | Dấu câu bị đếm như từ |
| DV5-05 | Compound words dùng `_` | 100% | 0% (dùng space) | ❌ FAIL | Xem T5-03 |
| DV5-06 | pos + neg có từ mang sentiment | có `tốt`, `rất`… | có | ✅ PASS |
| DV5-07 | Vocab size hợp lý sau min_freq | nhỏ hơn hiện tại | pos: 1265, neg: 2315 (chưa lọc) | ❌ FAIL | Chưa có min_freq |

---

## Non-Functional / Code Quality

| # | Check | Expected | Actual | Status |
|---|-------|----------|--------|--------|
| NF5-01 | Dùng `scripts/paths.py` cho đường dẫn | Path cross-platform | Hardcode `r'data\stopwords\custom.txt'` | ❌ FAIL | Chỉ chạy đúng trên Windows |
| NF5-02 | `load_stopwords` không gọi trong vòng lặp row | 1 lần | Mỗi row (8000 lần) | ❌ FAIL | Performance |
| NF5-03 | Tái sử dụng logic Task 3 `remove_stopwords()` | Nên dùng chung | Token filter thủ công | ⚠️ WARN | Multi-word stopwords có thể lọc sai |
| NF5-04 | Docstring / comment rõ ràng | Có | Typo "sử ddungjpackage" | ⚠️ WARN | |
| NF5-05 | Import thừa `Counter` trong text_utils | Không | Có | ⚠️ WARN | Minor |

---

## Tiêu chí hoàn thành (Jira KAN-13)

| # | Tiêu chí | Status | Ghi chú |
|---|---------|--------|---------|
| C5-01 | `build_vocab.py` chạy ổn trên train | ⚠️ WARN | Chạy được nhưng thiếu entry point |
| C5-02 | `pos_vocab.json` & `neg_vocab.json` trong `models/vocab/` | ❌ FAIL | Tên file khác spec |
| C5-03 | `tokenize()` modularized tại `utils/text_utils.py` | ✅ PASS | File tồn tại |
| C5-04 | QA verify: không garbage, compound có `_` | ❌ FAIL | Có punctuation; compound dùng space |

---

## Findings Summary

### [F5-01] 🔴 CRITICAL — Compound words bị tách bằng space thay vì `_`

**File:** `utils/text_utils.py`

**Mô tả:** Hàm `tokenize()` gọi `spacy_tokenize` rồi `replace('_', ' ')`, làm mất format compound theo PyVi. Vocab output: `"giảng viên"` thay vì `"giảng_viên"`.

**Khuyến nghị:** Dùng `ViTokenizer.tokenize(text).split()` hoặc giữ nguyên token từ `spacy_tokenize` (không replace).

---

### [F5-02] 🔴 CRITICAL — Chưa lọc `min_freq`

**File:** `models/build_vocab.py`

**Mô tả:** Spec yêu cầu chỉ giữ từ xuất hiện ≥ 5 lần. Hiện vocab chứa nhiều noise (freq=1).

**Khuyến nghị:** Sau khi build counter, filter: `{k: v for k, v in counter.items() if v >= min_freq}`.

---

### [F5-03] 🟠 MAJOR — Punctuation trong vocabulary

**File:** `models/build_vocab.py`, output JSON

**Mô tả:** `,` và `.` là top tokens trong `pos_counter.json` (2817 và 3846 lần).

**Khuyến nghị:** Loại token chỉ gồm punctuation hoặc filter sau tokenize.

---

### [F5-04] 🟠 MAJOR — Hardcoded path & load stopwords trong loop

**File:** `models/build_vocab.py` line 20

**Khuyến nghị:** Dùng `STOPWORDS_CUSTOM` từ `scripts/paths.py`; load stopwords một lần trước vòng lặp.

---

### [F5-05] 🟡 MINOR — Tên output file & entry point

**Khuyến nghị:** Đổi tên theo spec hoặc cập nhật Jira; thêm `main()` gọi `build_vocab(TRAIN_CLEANED)`.

---

## Chạy automated tests

```bash
# Tất cả tests
py -m pytest tests/ -v

# Chỉ text utils
py -m pytest tests/test_text_utils.py -v

# Chỉ vocab (cần file JSON đã generate)
py -m pytest tests/test_build_vocab.py -v
```

**Kỳ vọng hiện tại:** Một số test sẽ **FAIL** cho đến khi dev fix F5-01 → F5-03. Đây là behavior mong muốn của QA gate.

---

## Verdict

| Mức | Số finding |
|-----|------------|
| 🔴 Critical | 2 |
| 🟠 Major | 2 |
| 🟡 Minor | 1 |

**Recommendation:** **Request Changes** — fix F5-01, F5-02, F5-03 trước khi merge vào `develop`.
