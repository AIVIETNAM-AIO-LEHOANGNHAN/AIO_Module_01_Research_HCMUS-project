import os
from pathlib import Path

# Cấu trúc thư mục gốc
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DOCS_DIR = PROJECT_ROOT / "docs"
MODELS_DIR = PROJECT_ROOT / "models"


# Đường dẫn Dữ liệu
TRAIN_DIR = DATA_DIR / "train"
TEST_DIR = DATA_DIR / "test"
STOPWORDS_DIR = DATA_DIR / "stopwords"
STOPWORDS_CUSTOM = DATA_DIR / "stopwords" / "custom.txt"
STOPWORDS_PROTECTED = DATA_DIR / "stopwords" / "protected.txt"
TRAIN_CLEANED = TRAIN_DIR / "cleaned.csv"
TEST_CLEANED = TEST_DIR / "cleaned.csv"

# Đường dẫn Từ điển (Lexicon)
LEXICON_DIR = DATA_DIR / "lexicon"
NEGATORS = LEXICON_DIR / "negators.txt"
INTENSIFIERS = LEXICON_DIR / "intensifiers.txt"
CRITIQUE_WORDS = LEXICON_DIR / "critique_words.txt"

# Tự động lấy tên thí nghiệm từ biến môi trường, mặc định là "exp_a"
EXP_NAME = os.getenv("EXP_NAME", "exp_a")

# Cấu trúc Vocab động theo thí nghiệm
VOCAB_DIR = MODELS_DIR / "vocab" / EXP_NAME
POS_VOCAB = VOCAB_DIR / "pos_vocab.json"
NEG_VOCAB = VOCAB_DIR / "neg_vocab.json"

# URLs và tài nguyên khác
BASELINE_STOPWORDS_URL = (
    "https://raw.githubusercontent.com/stopwords/vietnamese-stopwords/"
    "master/vietnamese-stopwords.txt"
)