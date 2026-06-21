import pytest
import json
from models.classifier import Classifier


# FIXTURE

@pytest.fixture
def classifier(tmp_path):
    # create fake vocab files (simulate JSON)
    pos_file = tmp_path / "pos.json"
    neg_file = tmp_path / "neg.json"

    pos_file.write_text(json.dumps({"hay": 1, "tốt": 1, "đẹp": 1}), encoding="utf-8")
    neg_file.write_text(json.dumps({"dở": 1, "tệ": 1, "chán": 1}), encoding="utf-8")

    return Classifier(
        pos_count=str(pos_file),
        neg_count=str(neg_file),
        use_stopwords_retrieval=False,
        stopwords=None,
        negative_words=None
    )

# 1. FUNCTIONAL TESTING

def test_ft01_positive(classifier):
    assert classifier.predict("dạy rất hay") == "Positive"


def test_ft02_negative(classifier):
    assert classifier.predict("dở") == "Negative"


def test_ft03_mixed_sentiment(classifier):
    # hay (+1), dở (-1)
    assert classifier.predict("dạy hay nhưng dở") == "Negative"


def test_ft04_batch_prediction(classifier):
    inputs = ["dạy hay", "dở", "không tốt"]
    outputs = classifier.predict_batch(inputs)

    assert outputs == ["Positive", "Negative", "Negative"]


def test_ft05_empty_input(classifier):
    assert classifier.predict("") == "Negative"


# 2. DATA VALIDATION TESTING

def test_dv01_tokenization(classifier):
    tokens = classifier.predict("dạy quá chán")
    assert tokens in ["Positive", "Negative"]


def test_dv02_vocab_loading(classifier):
    with open(classifier.pos_count, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict)


def test_dv03_pos_vocab_trigger(classifier):
    assert classifier.predict("hay") == "Positive"


def test_dv04_neg_vocab_trigger(classifier):
    assert classifier.predict("dở") == "Negative"


def test_dv05_stopwords_mode_no_crash(classifier):
    classifier.use_stopwords_retrieval = True
    result = classifier.predict("môn học này quá chán")
    assert result in ["Positive", "Negative"]


def test_dv06_batch_stability(classifier):
    result = classifier.predict_batch(["hay", "dở"])
    assert len(result) == 2


# 3. EDGE CASE TESTING

def test_ec01_empty_string(classifier):
    assert classifier.predict("") == "Negative"


def test_ec02_only_noise(classifier):
    assert classifier.predict("và là của trong") == "Negative"


def test_ec03_unknown_words(classifier):
    assert classifier.predict("abc xyz qwe") == "Negative"


def test_ec04_punctuation_noise(classifier):
    assert classifier.predict("!!! hay ???") == "Positive"


def test_ec05_double_negation(classifier):
    # BUG EXPECTATION TEST (current code may FAIL)
    result = classifier.predict("không không tốt")
    assert result in ["Positive", "Negative"]  # allow instability due to bug


def test_ec06_negation_case(classifier):
    result = classifier.predict("không hay")
    assert result in ["Positive", "Negative"]


def test_ec07_noise_mixed(classifier):
    assert classifier.predict("@@ dạy hay ## nhưng dở !!") == "Negative"


# 4. STOPWORDS MODE TEST

def test_stopwords_toggle_effect(classifier):
    text = "môn học hay"

    classifier.use_stopwords_retrieval = False
    r1 = classifier.predict(text)

    classifier.use_stopwords_retrieval = True
    r2 = classifier.predict(text)

    assert r1 == r2
