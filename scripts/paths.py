"""Shared data paths for project scripts."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"

TRAIN_DIR = DATA_DIR / "train"
TEST_DIR = DATA_DIR / "test"
STOPWORDS_DIR = DATA_DIR / "stopwords"

TRAIN_RAW = TRAIN_DIR / "raw.csv"
TRAIN_CLEANED = TRAIN_DIR / "cleaned.csv"
TEST_RAW = TEST_DIR / "raw.csv"
TEST_CLEANED = TEST_DIR / "cleaned.csv"

STOPWORDS_RAW = STOPWORDS_DIR / "raw.txt"
STOPWORDS_CUSTOM = STOPWORDS_DIR / "custom.txt"
STOPWORDS_PROTECTED = STOPWORDS_DIR / "protected.txt"

QA_SAMPLE = DATA_DIR / "qa_sample_50.csv"
README_DATA = DATA_DIR / "README_DATA.md"

BASELINE_STOPWORDS_URL = (
    "https://raw.githubusercontent.com/stopwords/vietnamese-stopwords/"
    "master/vietnamese-stopwords.txt"
)
