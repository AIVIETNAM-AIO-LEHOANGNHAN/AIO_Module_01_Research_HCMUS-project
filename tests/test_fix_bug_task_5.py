import json

def test_stopwords_exist_in_vocab():
    with open("data/stopwords/custom.txt", encoding="utf-8") as f:
        stopwords = set(line.strip() for line in f if line.strip())

    with open("models/vocab/pos_vocab.json", encoding="utf-8") as f:
        pos_vocab = json.load(f)

    with open("models/vocab/neg_vocab.json", encoding="utf-8") as f:
        neg_vocab = json.load(f)

    pos_overlap = stopwords.intersection(pos_vocab.keys())
    neg_overlap = stopwords.intersection(neg_vocab.keys())

    assert len(pos_overlap) > 0 or len(neg_overlap) > 0
