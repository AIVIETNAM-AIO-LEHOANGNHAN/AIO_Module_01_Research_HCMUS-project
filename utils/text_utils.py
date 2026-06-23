from pyvi import ViTokenizer
from collections import Counter

# [QA-T1 | LOW] Unused import: `Counter` is imported but never used in this module. Remove.
def tokenize(text):
    """
    Tokenize sử package pyvi
    """
    # [QA-T2 | MEDIUM] `if text:` treats whitespace-only strings ("   ") as truthy and passes them
    #   to ViTokenizer, but None / "" return []. Behaviour is OK for "" but inconsistent for
    #   whitespace. Prefer `if text and text.strip():` and accept only str (non-str input such as
    #   NaN floats from pandas will raise inside pyvi — guard or cast at the caller).
    if text:
        tokens = ViTokenizer.spacy_tokenize(text)[0]
        return tokens
    else:
        return list()

def load_words(file_path):
    """
    Đọc file text chứa words (mỗi từ một dòng) và trả về một set.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            stopwords = set(
                line.strip() for line in lines if line.strip()
            )
            
            return stopwords
            
    except FileNotFoundError:
        print(f"Cảnh báo: Không tìm thấy file stopwords tại '{file_path}'")
        return set()