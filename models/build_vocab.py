import json
import os
import pandas as pd
from collections import Counter

from utils.text_utils import preprocess, tokenize, load_words
from scripts.paths import STOPWORDS_CUSTOM, TRAIN_CLEANED



# 1. FILTER LOW FREQUENCY WORDS

def filter_by_frequency(counter, min_freq=2):
    """
    Giữ lại các từ xuất hiện >= min_freq
    """
    return Counter({
        word: freq
        for word, freq in counter.items()
        if freq >= min_freq
    })



# 2. REMOVE NEUTRAL WORDS 

def remove_neutral_words(pos_counter, neg_counter, threshold=0.7, output_dir="vocab"):
    """
    Loại bỏ các từ xuất hiện giống nhau ở cả positive và negative
    → vì đây là từ "trung tính"
    """

    # tìm từ xuất hiện ở cả 2 phía
    common_words = set(pos_counter.keys()) & set(neg_counter.keys())

    neutral_words = []

    for word in common_words:
        pos_freq = pos_counter[word]
        neg_freq = neg_counter[word]

        ratio = min(pos_freq, neg_freq) / max(pos_freq, neg_freq)

        # nếu xuất hiện gần như cân bằng → coi là neutral
        if ratio >= threshold:
            neutral_words.append(word)


    # lưu file debug
  
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "removed_neutral_words.txt"), "w", encoding="utf-8") as f:
        for word in sorted(neutral_words):
            f.write(word + "\n")

    # xóa khỏi vocab

    for word in neutral_words:
        del pos_counter[word]
        del neg_counter[word]

    print(f"Removed {len(neutral_words)} neutral words")

    return pos_counter, neg_counter



# 3. TEXT PROCESSING PIPELINE

def process_text(text, remove_stopwords=False, stopwords_set=None):
    """
    preprocess → tokenize → optional stopwords removal
    """

    text = preprocess(text)
    tokens = tokenize(text)

    if remove_stopwords and stopwords_set:
        tokens = [t for t in tokens if t not in stopwords_set]

    return tokens



# 4. BUILD VOCAB (CORE FUNCTION)

def build_vocab(
    data_path,
    output_dir,
    remove_stopwords=False,
    min_freq=2,
    neutral_threshold=0.7
):

    print("\n[STEP 1] Loading data...")

    # -------------------------
    # load stopwords
    # -------------------------
    stopwords = load_words(STOPWORDS_CUSTOM) if remove_stopwords else set()

    # -------------------------
    # load dataset
    # -------------------------
    data = pd.read_csv(data_path)

    print("[STEP 2] Processing text...")

    # tạo cột tokens
    data["tokens"] = data["text"].apply(
        lambda x: process_text(x, remove_stopwords, stopwords)
    )

    # -------------------------
    # split theo label
    # -------------------------
    pos_tokens = data[data["label"] == 1]["tokens"].sum()
    neg_tokens = data[data["label"] == 0]["tokens"].sum()

    print("[STEP 3] Building counters...")

    pos_counter = filter_by_frequency(Counter(pos_tokens), min_freq)
    neg_counter = filter_by_frequency(Counter(neg_tokens), min_freq)

    print("[STEP 4] Removing neutral words...")

    pos_counter, neg_counter = remove_neutral_words(
        pos_counter,
        neg_counter,
        threshold=neutral_threshold,
        output_dir=output_dir
    )

    # -------------------------
    # save vocab
    # -------------------------
    print("[STEP 5] Saving vocab...")

    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "pos_vocab.json"), "w", encoding="utf-8") as f:
        json.dump(pos_counter, f, ensure_ascii=False, indent=4)

    with open(os.path.join(output_dir, "neg_vocab.json"), "w", encoding="utf-8") as f:
        json.dump(neg_counter, f, ensure_ascii=False, indent=4)

    print(f"Done! Vocab saved to: {output_dir}")

    return pos_counter, neg_counter


# 5. EXPERIMENT RUNNER

def run_experiments():

    current_dir = os.path.dirname(os.path.abspath(__file__))

    experiments = [
        {"name": "exp_a", "remove_stopwords": False},
        {"name": "exp_b", "remove_stopwords": True}
    ]

    for exp in experiments:
        print(f"\n==============================")
        print(f"Running {exp['name']}")
        print(f"==============================")

        build_vocab(
            data_path=TRAIN_CLEANED,
            output_dir=os.path.join(current_dir, "vocab", exp["name"]),
            remove_stopwords=exp["remove_stopwords"]
        )



# 6. ENTRY POINT

if __name__ == "__main__":
    run_experiments()