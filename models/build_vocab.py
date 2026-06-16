from collections import Counter
import pandas as pd
from utils.text_utils import tokenize, load_stopwords
import json
import os

def build_vocab(data_path):
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    vocab_dir = os.path.join(current_dir, "vocab")
    os.makedirs(vocab_dir, exist_ok=True)
    pos_counter = Counter()
    neg_counter = Counter()
    pos_file_path = os.path.join(vocab_dir, "pos_counter.json")
    neg_file_path = os.path.join(vocab_dir, "neg_counter.json")

    data = pd.read_csv(data_path)
    for _, row in data.iterrows():
        tokens = tokenize(str(row['text']))
        stopwords = load_stopwords(r'data\stopwords\custom.txt')
        cleaned_words = [token for token in tokens if token not in stopwords]
        token_freq = Counter(cleaned_words)
        
        if row['label'] == 1:
            pos_counter += token_freq
        elif row['label'] == 0:
            neg_counter += token_freq

    with open(pos_file_path, "w", encoding="utf-8") as f:
        json.dump(pos_counter, f, ensure_ascii=False, indent=4)

    with open(neg_file_path, "w", encoding="utf-8") as f:
        json.dump(neg_counter, f, ensure_ascii=False, indent=4)

    return True

# Test
# build_vocab(r"data\train\cleaned.csv")