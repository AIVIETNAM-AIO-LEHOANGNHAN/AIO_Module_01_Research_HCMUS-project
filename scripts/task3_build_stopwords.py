"""
Task 3: Xây dựng danh sách stopwords tiếng Việt.

Input :
  - data/stopwords/raw.txt
  - data/stopwords/protected.txt
Output:
  - data/stopwords/custom.txt
  - docs/Stopwords_Rationale.md
"""

import sys
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
    # QA [F3-04]: HTTP status is not checked. If the URL returns a 404 or redirect,
    # the raw.txt will be overwritten with HTML/error content silently.
    # Fix: check response.status == 200 before writing.
    with urllib.request.urlopen(url, timeout=30) as response:
        output_path.write_text(response.read().decode("utf-8"), encoding="utf-8")


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


def contains_any_token(phrase: str, token_set: set[str]) -> bool:
    """Kiểm tra phrase có chứa token thuộc token_set không."""
    return any(token in token_set for token in phrase.split())


def build_stopwords(raw_stopwords: set[str], protected_words: set[str]) -> tuple[set[str], set[str]]:
    """Tạo stopwords chính thức, loại entry chứa protected token."""
    # QA [F3-02]: contains_any_token causes OVER-REMOVAL of multi-word phrases.
    # 131 phrases like "cho nên" (therefore), "bằng không" (otherwise), "chưa bao giờ"
    # (never) are removed because they contain a protected single token — even though
    # the protected token ("nên", "không", "chưa") carries NO sentiment meaning in those
    # compound phrases. Consider restricting protection to single-token entries only:
    #   removed = {w for w in raw_stopwords if w in protected_words}
    # (This is safe today because multi-word entries are never matched anyway — see F3-01)
    removed = {w for w in raw_stopwords if contains_any_token(w, protected_words)}
    stopwords = raw_stopwords - removed
    return stopwords, removed


def save_word_list(words: set[str], path: Path) -> None:
    """Ghi danh sách từ, mỗi dòng một entry."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(sorted(words)) + "\n", encoding="utf-8-sig")


def load_stopwords(path: Path = STOPWORDS_CUSTOM) -> set[str]:
    """Đọc stopwords đã build — dùng lại ở pipeline huấn luyện."""
    return load_word_list(path)


def remove_stopwords(text: str, stopwords: set[str]) -> str:
    """Loại stopwords khỏi câu (tokenize theo khoảng trắng)."""
    # QA [F3-01] CRITICAL: text.split() produces single syllable/word tokens.
    # custom.txt contains 1438/1799 multi-word entries (e.g. "bao giờ", "cho nên",
    # "bao nhiêu"). These NEVER match because each token is a single word.
    # Only the 361 single-word entries actually have any effect.
    # Fix options:
    #   (a) Apply Vietnamese word segmentation (underthesea/VnCoreNLP) before this call
    #       so "bao giờ" becomes one token, OR
    #   (b) Filter custom.txt to single-word entries only, OR
    #   (c) Use regex phrase-matching for multi-word entries.
    # Until fixed, 80% of the stopwords list is dead code.
    return " ".join(token for token in text.split() if token.lower() not in stopwords)


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
    stopwords: set[str],
    protected_words: set[str],
    removed_entries: set[str],
) -> None:
    """Tạo tài liệu giải thích lý do dùng custom stopwords."""
    protected_preview = ", ".join(f"`{w}`" for w in sorted(protected_words))

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

Xem thêm `docs/research_context.md` và papers trong `docs/research/`.

## 4. Quy trình build

Script `scripts/task3_build_stopwords.py`:

1. Đọc `data/stopwords/raw.txt`
2. Đọc `data/stopwords/protected.txt`
3. Loại entry chứa protected token
4. Ghi `data/stopwords/custom.txt`

## 5. Thống kê

| File | Số entry |
|------|----------|
| `data/stopwords/raw.txt` | {raw_count} |
| `data/stopwords/protected.txt` | {len(protected_words)} |
| `data/stopwords/custom.txt` | {len(stopwords)} |
| Entry bị loại (protected overlap) | {len(removed_entries)} |

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
