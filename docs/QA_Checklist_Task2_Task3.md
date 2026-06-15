# QA Checklist — Task 2 & Task 3
**Branch:** `feat/preprocessing-stopwords`
**Reviewer:** QA Role
**Review Date:** 2026-06-11
**QA Standards:** Based on `HƯỚNG DẪN THIẾT LẬP KẾ HOẠCH KIỂM THỬ CHO QA_QC.docx`

---

## Phạm vi kiểm thử (Scope)

| In scope | Out of scope |
|----------|--------------|
| Task 2: `scripts/task2_preprocess_text.py` | Model training/evaluation |
| Task 3: `scripts/task3_build_stopwords.py` | Task 1 data sourcing |
| `data/train/cleaned.csv`, `data/test/cleaned.csv` | Dashboard/Streamlit |
| `data/stopwords/{raw,custom,protected}.txt` | CI/CD pipeline |
| `docs/Stopwords_Rationale.md` | |

---

## Môi trường kiểm thử (Test Environment)

- Python 3.13 (Windows 10)
- Libraries: `pandas`, `re`, `pathlib`, `urllib`
- Dataset: UIT-VSFC (8000 train / 2000 test rows)
- All tests run manually against committed files in `feat/preprocessing-stopwords`

---

## Task 2 — Viết mã nguồn tiền xử lý

### Functional Testing

| # | Test Case | Expected | Actual | Status | Notes |
|---|-----------|----------|--------|--------|-------|
| T2-01 | `clean_text("Thầy Dạy Tốt!!!")` | `"thầy dạy tốt!!!"` | `"thầy dạy tốt!!!"` | ✅ PASS | Lowercase correct |
| T2-02 | `clean_text("  khoảng trắng thừa  ")` | `"khoảng trắng thừa"` | `"khoảng trắng thừa"` | ✅ PASS | Strip works |
| T2-03 | `clean_text("@#$% emoji 👍🔥")` | `"emoji"` | `"emoji"` | ✅ PASS | Special chars removed |
| T2-04 | `clean_text(None)` | `""` | `""` | ✅ PASS | Null handled |
| T2-05 | `clean_text("")` | `""` | `""` | ✅ PASS | Empty string safe |
| T2-06 | `clean_text("giảng_viên tốt")` | `"giảng viên tốt"` | `"giảng viên tốt"` | ✅ PASS | Underscore normalized |
| T2-07 | `clean_text("không hiểu gì")` | `"không hiểu gì"` | `"không hiểu gì"` | ✅ PASS | Vietnamese preserved |
| T2-08 | `clean_text("85% đúng")` | Should preserve "%" or note removal | `"85 đúng"` | ⚠️ WARN | `%` stripped, loses numerical context |
| T2-09 | Script runs on both train + test | No exceptions | No exceptions | ✅ PASS | Both files processed |
| T2-10 | `.apply()` used for column processing | Yes | `df["text"].apply(clean_text)` | ✅ PASS | Per spec |

### Data Validation Testing

| # | Check | Expected | Actual | Status |
|---|-------|----------|--------|--------|
| DV2-01 | Uppercase chars in `train/cleaned.csv` | 0 rows | 0 rows | ✅ PASS |
| DV2-02 | Empty text rows in `train/cleaned.csv` | 0 rows | 0 rows | ✅ PASS |
| DV2-03 | Null/NaN rows in `train/cleaned.csv` | 0 rows | 0 rows | ✅ PASS |
| DV2-04 | Label values are `{0, 1}` | `{0, 1}` | `{'0', '1'}` | ✅ PASS |
| DV2-05 | Row count integrity (train raw vs cleaned) | ≤ 8000 | 8000 = 8000 | ✅ PASS |
| DV2-06 | Row count integrity (test raw vs cleaned) | ≤ 2000 | 2000 = 2000 | ✅ PASS |
| DV2-07 | Encoding of output files | UTF-8-sig | UTF-8-sig | ✅ PASS |
| DV2-08 | `train/cleaned.csv` != `train/raw.csv` | Some diff | 31 rows differ | ⚠️ WARN | Raw data was already lowercase (see F2-01 below) |

### Checklist Tiêu chí hoàn thành (Task 2 Spec)

| # | Tiêu chí | Status | Ghi chú |
|---|---------|--------|---------|
| C2-01 | Code viết trong `data/preprocess.py` | ❌ FAIL | File nằm ở `scripts/task2_preprocess_text.py`, **không phải** `data/preprocess.py` như spec yêu cầu |
| C2-02 | Script chạy không lỗi trên tập mẫu | ✅ PASS | |
| C2-03 | File `train_cleaned.csv` và `test_cleaned.csv` được tạo | ⚠️ WARN | Output là `data/train/cleaned.csv` / `data/test/cleaned.csv` — tên file khác spec (`train_cleaned.csv`) nhưng cấu trúc thư mục tốt hơn |
| C2-04 | Hàm `clean_text()` xử lý lowercase và xóa khoảng trắng | ✅ PASS | |
| C2-05 | Xử lý dòng trống (null/NaN) | ✅ PASS | `dropna()` + filter `!= ""` |
| C2-06 | Script chạy được trên cả train và test | ✅ PASS | |
| C2-07 | Code được comment rõ ràng | ✅ PASS | Docstrings đầy đủ trên tất cả hàm |

### Findings — Task 2

#### [F2-01] ⚠️ MEDIUM — `raw.csv` đã được lower-case từ trước khi commit

**Mô tả:** File `data/train/raw.csv` đã ở dạng lowercase hoàn toàn. Chỉ có 31/8000 dòng khác nhau giữa raw và cleaned (do loại ký tự đặc biệt như `%`, `&`, `>`). Điều này có nghĩa là "raw" data thực chất đã được tiền xử lý trước đó, không phải dữ liệu thô thực sự.

**Tác động:** Không thể verify rằng pipeline preprocessing hoạt động đúng trên dữ liệu thô thực tế (uppercase, emoji, HTML entities...). QA không thể đánh giá đầy đủ hiệu quả của Task 2.

**Khuyến nghị:** Commit file raw gốc thực sự từ Hugging Face (chưa qua bất kỳ xử lý nào), hoặc giải thích tại sao raw.csv đã được clean sẵn.

#### [F2-02] ⚠️ MEDIUM — Percentage signs và ký tự số học bị xóa

**Mô tả:** `%`, `>`, `<`, `&` không nằm trong `ALLOWED_PUNCTUATION`. Ví dụ: "85% thời gian" → "85 thời gian", "> 30%" → "30".

**Tác động:** Ngữ nghĩa số liệu bị mất. Tuy nhiên, đây là dữ liệu cảm xúc (sentiment), số % ít ảnh hưởng đến label.

**File:** `scripts/task2_preprocess_text.py:20`

#### [F2-03] ⚠️ MINOR — Thiếu comment giải thích `ALLOWED_PUNCTUATION`

**Mô tả:** Biến `ALLOWED_PUNCTUATION = r".,?!:;\-'\"()"` không có comment giải thích tại sao những ký tự này được giữ lại và tại sao `%`, `&`, `>` bị loại bỏ.

**File:** `scripts/task2_preprocess_text.py:20`

#### [F2-04] ✅ INFO — Spec path deviation acceptable

**Mô tả:** Spec yêu cầu `data/preprocess.py` nhưng code ở `scripts/task2_preprocess_text.py`. Cấu trúc `scripts/` tốt hơn về mặt tổ chức project. Cần xác nhận với Leader/PM.

---

## Task 3 — Xây dựng danh sách từ dừng

### Functional Testing

| # | Test Case | Expected | Actual | Status | Notes |
|---|-----------|----------|--------|--------|-------|
| T3-01 | Protected words NOT in `custom.txt` (exact) | 0 violations | 0 violations | ✅ PASS | |
| T3-02 | No duplicates in `custom.txt` | 0 | 0 | ✅ PASS | |
| T3-03 | `custom.txt` is sorted | Sorted | Sorted alphabetically | ✅ PASS | |
| T3-04 | `remove_stopwords("giảng viên không nhiệt tình")` | "không" preserved | "không" preserved | ✅ PASS | Protected word stays |
| T3-05 | Multi-word stopword matching | Removed from text | NOT removed | ❌ FAIL | See F3-01 CRITICAL below |
| T3-06 | One word per line in `custom.txt` | Yes | Yes | ✅ PASS | |
| T3-07 | `load_stopwords()` importable by pipeline | Yes | Yes | ✅ PASS | Function exported |

### Data Validation Testing

| # | Check | Expected | Actual | Status |
|---|-------|----------|--------|--------|
| DV3-01 | `protected.txt` words absent from `custom.txt` | 0 violations | 0 violations | ✅ PASS |
| DV3-02 | `không` absent from `custom.txt` | Not present | Not present | ✅ PASS |
| DV3-03 | `chưa` absent from `custom.txt` | Not present | Not present | ✅ PASS |
| DV3-04 | `rất` absent from `custom.txt` | Not present | Not present | ✅ PASS |
| DV3-05 | Row count: `raw.txt` ≥ `custom.txt` | raw > custom | 1938 > 1799 | ✅ PASS |
| DV3-06 | `custom.txt` entry count matches Rationale | 1799 | 1799 | ✅ PASS |
| DV3-07 | `chả`,`chẳng`,`dở`,`hơi`,`kém`,`tệ`,`đừng` in `raw.txt` | Should be there | NOT in raw.txt | ⚠️ WARN | See F3-03 |

### Checklist Tiêu chí hoàn thành (Task 3 Spec)

| # | Tiêu chí | Status | Ghi chú |
|---|---------|--------|---------|
| C3-01 | `data/stopwords.txt` chứa danh sách từ dừng sạch | ✅ PASS | File ở `data/stopwords/custom.txt` — tên/path khác spec nhưng có lý do tổ chức |
| C3-02 | Đã lọc bỏ các từ phủ định | ✅ PASS | protected.txt đúng 15 từ |
| C3-03 | Có `docs/Stopwords_Rationale.md` | ✅ PASS | Đầy đủ nội dung |
| C3-04 | Định dạng `.txt` mỗi từ 1 dòng | ✅ PASS | |
| C3-05 | Lưu trong thư mục `data/` | ✅ PASS | |
| C3-06 | Demo lọc từ trên câu ví dụ | ✅ PASS | Có trong Rationale section 7 |

### Findings — Task 3

#### [F3-01] ❌ CRITICAL — `remove_stopwords()` không thể match multi-word entries

**Mô tả:** `remove_stopwords()` tokenize văn bản bằng `text.split()` (space-based, cho ra từng syllable riêng lẻ). Nhưng `custom.txt` chứa **1438/1799 entries là multi-word** (ví dụ: `"bao giờ"`, `"cho nên"`, `"bao nhiêu"`, `"ai nấy"`). Vì tokenization chỉ tạo ra single tokens, các multi-word entries KHÔNG BAO GIỜ match được trong quá trình remove.

**Bằng chứng:**
```
custom.txt total:    1799 entries
  Single-word:        361 entries  ← Only these 20% actually work
  Multi-word:        1438 entries  ← 80% are DEAD, never removed
```

**Ví dụ lỗi:**
```python
stopwords = load_stopwords()  # chứa "cho nên"
remove_stopwords("cần cho nên phải sửa", stopwords)
# Output: "cần cho nên phải sửa"   ← "cho nên" KHÔNG bị xóa
# Thực tế "cho" bị xóa (là single token), "nên" được bảo vệ
# → Output thực: "cần nên phải sửa"  (vô nghĩa)
```

**Tác động:** 80% stopwords list vô dụng. Pipeline downstream nhận được văn bản chưa được lọc đúng. Kết quả thí nghiệm so sánh "with/without stopwords" sẽ không chính xác.

**Khuyến nghị:** Sử dụng **word segmentation** (VnCoreNLP / underthesea) để tách "bao giờ" thành 1 token trước khi filter, HOẶC chỉ giữ single-word entries trong `custom.txt`, HOẶC dùng regex-based phrase matching.

**File:** `scripts/task3_build_stopwords.py:104-106`

---

#### [F3-02] ⚠️ MEDIUM — `contains_any_token()` gây OVER-REMOVAL từ raw list

**Mô tả:** Hàm `contains_any_token()` loại bỏ bất kỳ entry nào trong `raw.txt` có chứa protected token. Kết quả: **131/139 entries bị loại** là **multi-word phrases** như `"cho nên"` (= therefore), `"bằng không"` (= otherwise), `"chưa bao giờ"` (= never).

Những phrases này là **stopwords hợp lệ** (không mang cảm xúc), nhưng bị loại chỉ vì một token trong phrase là protected. Ví dụ:
- `"cho nên"` bị loại vì `"nên"` protected → nhưng `"nên"` trong "cho nên" là liên từ, KHÔNG phải sentiment word
- `"bằng không"` bị loại vì `"không"` protected → nhưng "bằng không" = "otherwise"

**Tác động:** Thực tế thấp vì multi-word entries không bao giờ match (F3-01), nhưng logic sai về mặt nguyên tắc và sẽ gây ra lỗi khi F3-01 được sửa.

**File:** `scripts/task3_build_stopwords.py:81-89`

---

#### [F3-03] ⚠️ MINOR — 7 protected words không có trong `raw.txt`

**Mô tả:** Các từ `chả`, `chẳng`, `dở`, `hơi`, `kém`, `tệ`, `đừng` trong `protected.txt` KHÔNG có trong baseline `raw.txt`. Chúng không cần được "bảo vệ" vì chưa bao giờ bị đưa vào danh sách stopwords.

**Ảnh hưởng:** Hiện không gây lỗi. Nhưng nếu `raw.txt` được cập nhật trong tương lai và thêm các từ này, `protected.txt` sẽ đảm bảo an toàn. Đây là **defensive programming** — chấp nhận được nhưng cần ghi chú trong Rationale.

**File:** `data/stopwords/protected.txt`

---

#### [F3-04] ⚠️ MINOR — `download_raw_stopwords()` không kiểm tra response validity

**Mô tả:** Hàm `download_raw_stopwords()` download URL và ghi thẳng vào file mà không kiểm tra HTTP status code hoặc content validity. Nếu URL trả về 404 hoặc redirect page, file `raw.txt` sẽ bị ghi đè bằng HTML/error content.

**File:** `scripts/task3_build_stopwords.py:58-65`

---

## Tổng kết đánh giá QA

### Task 2 — Preprocessing

| Hạng mục | Kết quả |
|---------|---------|
| Code quality | ✅ Tốt — functions modular, docstrings đầy đủ |
| Functional correctness | ✅ Đúng — clean_text() hoạt động chính xác |
| Data integrity | ✅ Đạt — cleaned files sạch, không null/uppercase |
| Spec compliance | ⚠️ Một số deviation về tên file/path |
| Evidence of preprocessing | ⚠️ raw.csv đã clean sẵn — pipeline chưa được kiểm chứng đầy đủ |
| **Verdict** | **⚠️ CONDITIONAL PASS** |

### Task 3 — Stopwords

| Hạng mục | Kết quả |
|---------|---------|
| Protected words safety | ✅ Đúng — không có protected word trong custom.txt |
| Documentation | ✅ Rationale đầy đủ và rõ ràng |
| File format | ✅ Đúng format |
| `remove_stopwords()` correctness | ❌ **CRITICAL BUG** — 80% entries không hoạt động |
| `contains_any_token()` logic | ⚠️ Over-removal trên multi-word phrases |
| **Verdict** | **❌ FAIL — cần sửa F3-01 trước khi approve** |

---

## Hành động cần thực hiện (Action Items)

| ID | Priority | Assignee | Action |
|----|----------|----------|--------|
| A1 | 🔴 CRITICAL | Dev | Sửa `remove_stopwords()` để hỗ trợ multi-word matching (F3-01) |
| A2 | 🟡 MEDIUM | Dev | Xem xét lại `contains_any_token()` logic — chỉ bảo vệ single-token matches (F3-02) |
| A3 | 🟡 MEDIUM | Dev | Giải thích hoặc commit raw.csv thực sự chưa xử lý (F2-01) |
| A4 | 🟢 MINOR | Dev | Thêm comment giải thích `ALLOWED_PUNCTUATION` và việc loại `%` (F2-02, F2-03) |
| A5 | 🟢 MINOR | Dev | Thêm HTTP status check trong `download_raw_stopwords()` (F3-04) |
| A6 | 🟢 MINOR | Dev | Ghi chú trong Rationale về 7 protected words không có trong raw.txt (F3-03) |
| A7 | 🔵 INFO | PM/Leader | Xác nhận file path spec: `data/preprocess.py` vs `scripts/task2_preprocess_text.py` |

---

*QA sign-off: Task 2 ⚠️ CONDITIONAL PASS | Task 3 ❌ FAIL (pending A1)*
