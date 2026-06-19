import json
from utils.text_utils import load_stopwords


def test_stopwords_exist_in_vocab():
    stopwords = load_stopwords(
        "data/stopwords/custom.txt"
    )
  
    with open(
        "models/vocab/pos_vocab.json",
        encoding="utf-8"
    ) as f:
        pos_vocab = json.load(f)

    overlap = stopwords.intersection(
        pos_vocab.keys()
    )

    # Ít nhất phải có một stopword xuất hiện
    assert len(overlap) > 0
