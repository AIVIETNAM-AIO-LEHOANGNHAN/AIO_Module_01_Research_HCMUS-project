"""
Task 2: Tiền xử lý văn bản.

Input : data/train/raw.csv, data/test/raw.csv
Output: data/train/cleaned.csv, data/test/cleaned.csv
"""

import re
import sys
from pathlib import Path

import pandas as pd

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from paths import TEST_CLEANED, TEST_RAW, TRAIN_CLEANED, TRAIN_RAW

# QA [F2-02/F2-03]: % > < & are NOT in ALLOWED_PUNCTUATION and will be stripped.
# "85% đúng" → "85 đúng", "turnitindotcom > 30%" → "turnitindotcom 30".
# For sentiment classification this is acceptable, but document the decision explicitly.
ALLOWED_PUNCTUATION = r".,?!:;\-'\"()"
SPECIAL_CHAR_PATTERN = re.compile(
    rf"[^\w\s{re.escape(ALLOWED_PUNCTUATION)}]",
    flags=re.UNICODE,
)


def clean_text(text: str) -> str:
    """Lowercase, loại ký tự đặc biệt thừa, chuẩn hóa khoảng trắng."""
    if pd.isna(text):
        return ""

    text = str(text).lower().strip()
    text = SPECIAL_CHAR_PATTERN.sub(" ", text)
    text = text.replace("_", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Làm sạch dataframe: bỏ null, clean text, bỏ dòng rỗng."""
    df = df.copy()
    df = df.dropna(subset=["text", "label"])
    df["text"] = df["text"].apply(clean_text)
    df = df[df["text"] != ""].reset_index(drop=True)
    df["label"] = df["label"].astype(int)
    return df


def preprocess_file(input_path: Path, output_path: Path) -> pd.DataFrame:
    """Đọc CSV, tiền xử lý và ghi ra file cleaned."""
    # QA [F2-01]: raw.csv was committed already lowercase with no emoji — only 31/8000
    # rows differ between raw and cleaned (special char removal only). Verify that
    # truly raw data from Hugging Face would flow through this function correctly
    # before claiming the preprocessing pipeline is validated end-to-end.
    df = pd.read_csv(input_path, encoding="utf-8-sig")
    cleaned = preprocess_dataframe(df)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned.to_csv(output_path, index=False, encoding="utf-8-sig")
    return cleaned


def main() -> None:
    train_df = preprocess_file(TRAIN_RAW, TRAIN_CLEANED)
    test_df = preprocess_file(TEST_RAW, TEST_CLEANED)

    print("Done Task 2.")
    print(f"Train: {len(train_df)} rows -> {TRAIN_CLEANED}")
    print(f"Test : {len(test_df)} rows -> {TEST_CLEANED}")


if __name__ == "__main__":
    main()
