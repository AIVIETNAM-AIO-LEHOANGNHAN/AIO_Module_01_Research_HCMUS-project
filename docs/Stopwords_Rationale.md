# Stopwords Rationale

## 1. Mục tiêu

Xây dựng danh sách stopwords tiếng Việt **tùy chỉnh cho phân loại cảm xúc nhị phân**
trên corpus phản hồi sinh viên UIT-VSFC.

## 2. Nguồn baseline

- Repository: [stopwords/vietnamese-stopwords](https://github.com/stopwords/vietnamese-stopwords)
- File gốc: `data/stopwords/raw.txt`
- Số entry baseline (sau lọc meta): **1938**
- File dùng trong project: `data/stopwords/custom.txt`

## 3. Vì sao không xóa stopwords máy móc?

Các từ trong `data/stopwords/protected.txt`:

`chưa`, `chả`, `chẳng`, `cần`, `dở`, `hay`, `hơi`, `không`, `kém`, `nên`, `quá`, `rất`, `tệ`, `tốt`, `đừng`

Ví dụ: `giảng viên dạy chưa tốt` — nếu xóa `chưa` → `giảng viên dạy tốt` (**đảo nghĩa**).

Một số protected words (`chả`, `chẳng`, `dở`, `hơi`, `kém`, `tệ`, `đừng`) **không có trong baseline** `raw.txt`; vẫn giữ trong `protected.txt` để phòng khi baseline được cập nhật sau này.

Xem thêm `docs/research_context.md` và papers trong `docs/research/`.

## 4. Quy trình build

Script `scripts/task3_build_stopwords.py`:

1. Đọc `data/stopwords/raw.txt`
2. Đọc `data/stopwords/protected.txt`
3. Loại **entry one-word** trùng protected token (giữ nguyên cụm multi-word như `cho nên`, `chưa bao giờ`)
4. Ghi `data/stopwords/custom.txt`

`remove_stopwords()` xóa cụm multi-word trước (ưu tiên dài, bỏ qua cụm chứa protected token), sau đó xóa single-word (trừ protected).

## 5. Thống kê

| File | Số entry |
|------|----------|
| `data/stopwords/raw.txt` | 1938 |
| `data/stopwords/protected.txt` | 15 |
| `data/stopwords/custom.txt` | 1930 |
| Entry bị loại (protected one-word) | 8 |
| Single-word trong `custom.txt` | 361 |
| Multi-word trong `custom.txt` | 1569 |

## 6. Biến thí nghiệm

| Variant | Mô tả |
|---------|-------|
| Baseline | Không loại stopwords |
| Raw stopwords | Loại từ `raw.txt` trực tiếp |
| Custom stopwords | Loại từ `custom.txt` (có bảo vệ protected words) |

## 7. Demo QA

```python
from scripts.task3_build_stopwords import demo_incorrect_removal, load_stopwords, remove_stopwords

print(demo_incorrect_removal("giảng viên dạy chưa tốt", "chưa"))

stopwords = load_stopwords()
sample = "giảng viên không nhiệt tình , thầy dạy rất chậm ."
print(remove_stopwords(sample, stopwords))

# Multi-word stopword (vd. "bao giờ")
print(remove_stopwords("không biết bao giờ mới xong", stopwords))
```
