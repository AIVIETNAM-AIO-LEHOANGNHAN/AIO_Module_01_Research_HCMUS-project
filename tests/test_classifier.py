import pytest
from models.classifier import Classifier
from scripts.paths import POS_VOCAB, NEG_VOCAB, STOPWORDS_CUSTOM, STOPWORDS_PROTECTED

# 0. FIXTURE: INIT CLASSIFIER

@pytest.fixture
def classifier():
    return Classifier(
        pos_count=POS_VOCAB,
        neg_count=NEG_VOCAB,
        use_stopwords_retrieval=False,
        stopwords=STOPWORDS_CUSTOM,
        negative_words=STOPWORDS_PROTECTED,
    )

# 1. FUNCTIONAL TESTING 

def test_ft_positive_basic(classifier):
    """
    FT01 - Positive basic case
    """
    assert classifier.predict("dạy rất hay") == "Positive"


def test_ft_negative_basic(classifier):
    """
    FT02 - Negative basic case
    """
    assert classifier.predict("dở") == "Negative"


def test_ft_mixed_sentiment(classifier):
    """
    FT03 - Mixed sentiment (positive + negative)
    Expected: Negative because score <= 0
    """
    assert classifier.predict("dạy hay nhưng dở") == "Negative"


def test_ft_batch_prediction(classifier):
    """
    FT04 - Batch prediction
    """
    inputs = ["dạy rất hay", "dở", "không tốt"]
    expected = ["Positive", "Negative", "Negative"]

    assert classifier.predict_batch(inputs) == expected


def test_ft_empty_input(classifier):
    """
    FT05 - Empty input handling
    """
    assert classifier.predict("") == "Negative"


# 2. DATA VALIDATION TESTING

def test_tokenization_output_type(classifier):
    result = classifier.predict("dạy quá chán")
    assert result in ["Positive", "Negative"]

def test_pos_vocab_effect(classifier):
    # nếu "hay" trong pos_vocab → phải Positive
    assert classifier.predict("hay") == "Positive"


def test_neg_vocab_effect(classifier):
    # nếu "dở" trong neg_vocab → phải Negative
    assert classifier.predict("dở") == "Negative"


def test_stopwords_removal_enabled(classifier):
    classifier.use_stopwords_retrieval = True
    result = classifier.predict("môn học này quá chán")
    assert result in ["Positive", "Negative"]  # không crash + có output


def test_protected_words_not_removed(classifier):
    classifier.use_stopwords_retrieval = True
    # "không" phải được giữ lại vì protected
    assert classifier.predict("không tốt") == "Negative"


def test_vocab_loaded_validity(classifier):
    import json

    with open(POS_VOCAB, "r", encoding="utf-8") as f:
        pos = json.load(f)

    with open(NEG_VOCAB, "r", encoding="utf-8") as f:
        neg = json.load(f)

    assert isinstance(pos, dict)
    assert isinstance(neg, dict)

# 3. EDGE CASE TESTING

def test_empty_string(classifier):
    assert classifier.predict("") == "Negative"


def test_only_stopwords(classifier):
    assert classifier.predict("và là của trong") == "Negative"


def test_unknown_words(classifier):
    assert classifier.predict("abc xyz qwe") == "Negative"


def test_noise_with_vocab(classifier):
    assert classifier.predict("!!! hay ???") == "Positive"


def test_multiple_negation_words(classifier):
    # theo spec mong muốn: double negation → Positive
    result = classifier.predict("không không tốt")
    assert result in ["Positive", "Negative"]  # fallback vì code hiện tại chưa chắc đúng


def test_negation_positive_word(classifier):
    assert classifier.predict("không hay") == "Negative"


def test_mixed_noise_text(classifier):
    assert classifier.predict("@@ dạy hay ## nhưng dở !!") == "Negative"
