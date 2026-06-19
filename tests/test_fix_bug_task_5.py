import json

def test_stopwords_exist_in_vocab():
    
    with open("data/stopwords/custom.txt", encoding="utf-8") as f:
        stopwords = set(line.strip() for line in f if line.strip())

    with open("models/vocab/pos_vocab.json", encoding="utf-8") as f:
        pos_vocab = json.load(f)

    overlap = stopwords.intersection(pos_vocab.keys())

    assert len(overlap) > 0
