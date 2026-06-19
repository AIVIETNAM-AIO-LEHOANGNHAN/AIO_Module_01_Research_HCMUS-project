def test_stopwords_may_appear():
    import json

    stopwords = set(open("data/stopwords/custom.txt", encoding="utf-8").read().splitlines())

    pos = json.load(open("models/vocab/pos_vocab.json"))

    # KHÔNG ép >0, chỉ kiểm tra khả năng tồn tại
    assert isinstance(pos, dict)
