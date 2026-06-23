from collections import Counter
import pandas as pd
from utils.text_utils import tokenize
import json
import os
import regex as re
from scripts.paths import STOPWORDS_CUSTOM, TRAIN_CLEANED

def filter_min_freq(vocab, min_freq):
    for key in list(vocab.keys()):
        if vocab[key] < min_freq:
            del vocab[key]

def build_vocab(data_path):

    # [QA-B5 | CRITICAL] Output directory is hard-coded to models/vocab/ relative to THIS file and
    #   ignores any caller intent. tests/test_build_vocab.py calls build_vocab() with a tiny tmp_path
    #   fixture, so the unit test OVERWRITES the committed pos_vocab.json / neg_vocab.json. With
    #   min_freq=5 and ~10 rows the result is `{}` (empty). Effects observed by QA:
    #     1. Running the full pytest suite corrupts tracked model artifacts (git shows them modified
    #        and emptied).
    #     2. Order-dependent failures: every test that runs AFTER test_build_vocab sees empty vocab
    #        (13 failed when run together vs 4 in isolation).
    #   Fix: accept an `output_dir` parameter (default models/vocab/) so tests write to tmp_path and
    #   never touch version-controlled files. Make build_vocab() pure w.r.t. its inputs.
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
        # [QA-B1 | HIGH] This cleaning is applied at TRAIN time only. predict() (classifier.py)
        #   does NOT apply it -> train/predict mismatch (see QA-C4). Move cleaning into a shared
        #   helper in utils.text_utils and call it from BOTH paths.
        text = re.sub(r'[\p{P}\p{N}+]', '', text)
        tokens = tokenize(text)
        token_freq = Counter(tokens)

        # [QA-B2 | MEDIUM] Vocab is built WITHOUT stopword removal, so common stopwords
        #   ("và", "là", "của", "trong"...) enter both vocabs and become sentiment signals.
        #   This is why test_only_stopwords fails (pure-stopword input scores Positive). It also
        #   means config A vs B (Task 7) is NOT a clean isolation of the stopword variable: the
        #   shared vocab is already polluted. Consider building vocab on the cleaned/no-stopword
        #   corpus for config B, or excluding stopwords here.
        if row['label'] == 1:
            pos_counter += token_freq
        elif row['label'] == 0:
            neg_counter += token_freq
        # [QA-B3 | LOW] Rows whose label is neither 0 nor 1 are silently dropped (no count, no
        #   warning). Add an else-branch that logs/raises so malformed labels are caught.

    # [QA-B4 | MEDIUM] min_freq=5 is hard-coded (magic number). A word appearing in BOTH pos and
    #   neg vocab keeps a count in each with no net-signal handling -> ambiguous tokens add noise.
    #   Make the threshold a parameter and consider removing tokens dominant in both classes.
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