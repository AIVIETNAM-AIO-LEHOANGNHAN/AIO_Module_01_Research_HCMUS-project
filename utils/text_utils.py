from pyvi import ViTokenizer
from collections import Counter

def tokenize(text):
    """
    Tokenize sử ddungjpackage pyvi
    """
    raw_tokens = ViTokenizer.spacy_tokenize(text)[0]

    # Remove the '_' inside each token
    tokens = [token.replace('_',' ') for token in raw_tokens]
    return tokens

def load_stopwords(file_path):
    """
    Đọc file text chứa stopwords (mỗi từ một dòng) và trả về một set.
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