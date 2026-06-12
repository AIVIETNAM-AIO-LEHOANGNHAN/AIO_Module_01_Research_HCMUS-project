"""
Task 3: Xây dựng danh sách stopwords tiếng Việt.

Input :
  - data/stopwords/raw.txt
  - data/stopwords/protected.txt
Output:
  - data/stopwords/custom.txt
  - docs/Stopwords_Rationale.md
"""

import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from paths import (
    BASELINE_STOPWORDS_URL,
    DOCS_DIR,
    STOPWORDS_CUSTOM,
    STOPWORDS_DIR,
    STOPWORDS_PROTECTED,
    STOPWORDS_RAW,
)

RATIONALE_PATH = DOCS_DIR / "Stopwords_Rationale.md"

JUNK_WORDS = {
    "introduction",
    "amen",
    "alô",
    "a lô",
    "a ha",
}


def load_word_list(path: Path) -> set[str]:
    """Đọc danh sách từ txt, mỗi dòng một entry."""
    if not path.exists():
        return set()

    words: set[str] = set()
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        word = normalize_entry(line)
        if word:
            words.add(word)
    return words


def normalize_entry(text: str) -> str:
    """Chuẩn hóa một dòng: lowercase + gộp khoảng trắng thừa."""
    return " ".join(str(text).strip().lower().split())


def download_raw_stopwords(
    url: str = BASELINE_STOPWORDS_URL,
    output_path: Path = STOPWORDS_RAW,
) -> None:
    """Tải baseline stopwords từ GitHub nếu chưa có."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "AIO-Module-01/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status != 200:
                raise urllib.error.HTTPError(
                    url, response.status, "Unexpected HTTP status", response.headers, None
                )
            content = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to download stopwords from {url}") from exc

    if not content.strip() or content.lstrip().startswith("<"):
        raise ValueError(f"Invalid stopwords content from {url}")

    output_path.write_text(content, encoding="utf-8")


def load_raw_stopwords(path: Path = STOPWORDS_RAW) -> set[str]:
    """Đọc baseline stopwords và lọc token meta không phù hợp."""
    words: set[str] = set()
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        word = normalize_entry(line)
        if not word or word.startswith("#"):
            continue
        if "_" in word or word in JUNK_WORDS:
            continue
        words.add(word)
    return words


def is_protected_entry(entry: str, protected_words: set[str]) -> bool:
    """Chỉ loại entry one-word trùng protected; giữ cụm multi-word."""
    return len(entry.split()) == 1 and entry in protected_words


def build_stopwords(raw_stopwords: set[str], protected_words: set[str]) -> tuple[set[str], set[str]]:
    """Tạo stopwords chính thức, loại entry one-word trùng protected token."""
    removed = {w for w in raw_stopwords if is_protected_entry(w, protected_words)}
    stopwords = raw_stopwords - removed
    return stopwords, removed


def split_stopword_entries(stopwords: set[str]) -> tuple[list[str], set[str]]:
    """Tách entry multi-word (ưu tiên dài trước) và single-word."""
    multi_word = sorted((w for w in stopwords if " " in w), key=len, reverse=True)
    single_word = {w for w in stopwords if " " not in w}
    return multi_word, single_word


def save_word_list(words: set[str], path: Path) -> None:
    """Ghi danh sách từ, mỗi dòng một entry."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(sorted(words)) + "\n", encoding="utf-8-sig")


def load_stopwords(path: Path = STOPWORDS_CUSTOM) -> set[str]:
    """Đọc stopwords đã build — dùng lại ở pipeline huấn luyện."""
    return load_word_list(path)


def remove_stopwords(
    text: str,
    stopwords: set[str],
    protected_words: set[str] | None = None,
) -> str:
    """Loại stopwords khỏi câu (hỗ trợ cụm multi-word, bảo vệ protected tokens)."""
    if not text or not stopwords:
        return text.strip() if text else ""

    if protected_words is None:
        protected_words = load_word_list(STOPWORDS_PROTECTED)

    multi_word, single_word = split_stopword_entries(stopwords)
    single_word -= protected_words
    safe_multi = [
        phrase
        for phrase in multi_word
        if not any(token in protected_words for token in phrase.split())
    ]

    padded = f" {normalize_entry(text)} "

    for phrase in safe_multi:
        needle = f" {phrase} "
        while needle in padded:
            padded = padded.replace(needle, " ")

    tokens = padded.split()
    filtered = [token for token in tokens if token not in single_word]
    return re.sub(r"\s+", " ", " ".join(filtered)).strip()


def demo_incorrect_removal(sentence: str, protected_word: str) -> dict[str, str]:
    """Demo hậu quả nếu xóa nhầm từ phủ định/cảm xúc."""
    return {
        "original": sentence,
        "incorrect": remove_stopwords(sentence, {protected_word}),
        "protected_word": protected_word,
    }


def write_rationale(
    path: Path,
    raw_count: int,
    raw_stopwords: set[str],
    stopwords: set[str],
    protected_words: set[str],
    removed_entries: set[str],
) -> None:
    """Tạo tài liệu giải thích lý do dùng custom stopwords."""
    protected_preview = ", ".join(f"`{w}`" for w in sorted(protected_words))
    protected_not_in_raw = sorted(protected_words - raw_stopwords)
    not_in_raw_preview = ", ".join(f"`{w}`" for w in protected_not_in_raw)
    multi_word, single_word = split_stopword_entries(stopwords)

    content = f"""# Stopwords Rationale

## 1. Mục tiêu

Xây dựng danh sách stopwords tiếng Việt **tùy chỉnh cho phân loại cảm xúc nhị phân**
trên corpus phản hồi sinh viên UIT-VSFC.

## 2. Nguồn baseline

- Repository: [stopwords/vietnamese-stopwords](https://github.com/stopwords/vietnamese-stopwords)
- File gốc: `data/stopwords/raw.txt`
- Số entry baseline (sau lọc meta): **{raw_count}**
- File dùng trong project: `data/stopwords/custom.txt`

## 3. Vì sao không xóa stopwords máy móc?

Các từ trong `data/stopwords/protected.txt`:

{protected_preview}

Ví dụ: `giảng viên dạy chưa tốt` — nếu xóa `chưa` → `giảng viên dạy tốt` (**đảo nghĩa**).

Một số protected words ({not_in_raw_preview}) **không có trong baseline** `raw.txt`; vẫn giữ trong `protected.txt` để phòng khi baseline được cập nhật sau này.

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
| `data/stopwords/raw.txt` | {raw_count} |
| `data/stopwords/protected.txt` | {len(protected_words)} |
| `data/stopwords/custom.txt` | {len(stopwords)} |
| Entry bị loại (protected one-word) | {len(removed_entries)} |
| Single-word trong `custom.txt` | {len(single_word)} |
| Multi-word trong `custom.txt` | {len(multi_word)} |

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
"""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> None:
    STOPWORDS_DIR.mkdir(parents=True, exist_ok=True)

    if not STOPWORDS_RAW.exists():
        print(f"Downloading baseline -> {STOPWORDS_RAW}")
        download_raw_stopwords()

    raw_stopwords = load_raw_stopwords()
    protected_words = load_word_list(STOPWORDS_PROTECTED)
    stopwords, removed_entries = build_stopwords(raw_stopwords, protected_words)

    save_word_list(stopwords, STOPWORDS_CUSTOM)
    write_rationale(
        RATIONALE_PATH,
        raw_count=len(raw_stopwords),
        raw_stopwords=raw_stopwords,
        stopwords=stopwords,
        protected_words=protected_words,
        removed_entries=removed_entries,
    )

    print("Done Task 3.")
    print(f"Raw stopwords : {len(raw_stopwords)}")
    print(f"Protected     : {len(protected_words)}")
    print(f"Custom list   : {len(stopwords)} -> {STOPWORDS_CUSTOM}")
    print(f"Removed       : {len(removed_entries)} entries")
    print("Demo: see docs/Stopwords_Rationale.md section 7")


if __name__ == "__main__":
    main()
