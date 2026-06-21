from pyvi import ViTokenizer
from collections import Counter

def tokenize(text):
    """
    Tokenize sử package pyvi
    """
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