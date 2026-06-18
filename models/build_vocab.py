from collections import Counter
import pandas as pd
from utils.text_utils import tokenize, load_stopwords
import json
import os
import regex as re
from scripts.paths import STOPWORDS_CUSTOM, TRAIN_CLEANED

def filter_min_freq(vocab, min_freq):
    for key in list(vocab.keys()):
        if vocab[key] < min_freq:
            del vocab[key]

def build_vocab(data_path):
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    vocab_dir = os.path.join(current_dir, "vocab")
    os.makedirs(vocab_dir, exist_ok=True)
    pos_counter = Counter()
    neg_counter = Counter()
    pos_file_path = os.path.join(vocab_dir, "pos_vocab.json")
    neg_file_path = os.path.join(vocab_dir, "neg_vocab.json")

    data = pd.read_csv(data_path)
    for _, row in data.iterrows():
        text = str(row['text'])
        # Remove punctuation and number inside input text
        text = re.sub(r'[\p{P}\p{N}+]', '', text)
        tokens = tokenize(text)
        stopwords = load_stopwords(STOPWORDS_CUSTOM)
        cleaned_words = [token for token in tokens if token not in stopwords]
        token_freq = Counter(cleaned_words)
        
        if row['label'] == 1:
            pos_counter += token_freq
        elif row['label'] == 0:
            neg_counter += token_freq

    filter_min_freq(pos_counter, 5)
    filter_min_freq(neg_counter, 5)
    
    with open(pos_file_path, "w", encoding="utf-8") as f:
        json.dump(pos_counter, f, ensure_ascii=False, indent=4)

    with open(neg_file_path, "w", encoding="utf-8") as f:
        json.dump(neg_counter, f, ensure_ascii=False, indent=4)

    return True

# Test
if __name__ == "__main__":
    build_vocab(TRAIN_CLEANED)