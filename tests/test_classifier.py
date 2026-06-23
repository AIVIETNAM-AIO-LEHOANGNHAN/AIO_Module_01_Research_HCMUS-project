import pytest
from models.classifier import Classifier
from scripts.paths import POS_VOCAB, NEG_VOCAB, STOPWORDS_CUSTOM, STOPWORDS_PROTECTED

# FIXTURE

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

def test_positive_single_token(classifier):
    assert classifier.predict("hay") == "Positive"


def test_negative_single_token(classifier):
    assert classifier.predict("dở") == "Negative"


# [QA-TEST | FAIL] This test FAILS on the current code (returns "Positive"). The comment claims
#   hay(+1)+dở(-1)=0, but "nhưng" is treated as a negator, flipping dở's contribution to +1
#   (see QA-C6). The TEST is correct; the CODE is wrong. Do not "fix" the test — fix the negation.
def test_mixed_sentiment_score_zero(classifier):
    # hay (+1) + dở (-1) => score <= 0
    assert classifier.predict("dạy hay nhưng dở") == "Negative"


def test_multiple_positive_words(classifier):
    assert classifier.predict("hay tốt đẹp") == "Positive"


def test_multiple_negative_words(classifier):
    assert classifier.predict("dở tệ chán") == "Negative"


def test_empty_input(classifier):
    assert classifier.predict("") == "Negative"


def test_batch_prediction(classifier):
    inputs = ["hay", "dở", "không tốt"]
    expected = ["Positive", "Negative", "Negative"]
    assert classifier.predict_batch(inputs) == expected

# 2. DATA VALIDATION TESTING 

def test_vocab_files_are_valid_json():
    import json

    with open(POS_VOCAB, "r", encoding="utf-8") as f:
        pos = json.load(f)

    with open(NEG_VOCAB, "r", encoding="utf-8") as f:
        neg = json.load(f)

    assert isinstance(pos, dict)
    assert isinstance(neg, dict)


def test_stopwords_toggle_does_not_crash(classifier):
    classifier.use_stopwords_retrieval = True
    assert classifier.predict("môn học này quá chán") in ["Positive", "Negative"]


def test_protected_words_still_effective(classifier):
    classifier.use_stopwords_retrieval = True
    assert classifier.predict("không tốt") == "Negative"

# 3. EDGE CASE TESTING 

# [QA-TEST | FAIL] FAILS (returns "Positive"). Stopwords leaked into the vocab (QA-B2) so a
#   pure-stopword sentence scores positive. Test is correct; fix vocab construction.
def test_only_stopwords(classifier):
    assert classifier.predict("và là của trong") == "Negative"


def test_unknown_words(classifier):
    assert classifier.predict("abc xyz qwe") == "Negative"


def test_noise_punctuation(classifier):
    assert classifier.predict("!!! hay ???") == "Positive"


def test_negation_simple(classifier):
    # không + hay => Negative
    assert classifier.predict("không hay") == "Negative"


# [QA-TEST | FAIL] FAILS (returns "Negative"). Double negation is not supported: `negative` is
#   reset every token, so only the last negator (still -1) applies once and "tốt" scores -1.
#   See QA-C6. Test encodes the intended spec; code does not meet it.
def test_double_negation_expected_behavior(classifier):
    # không không tốt => expected Positive (spec)
    result = classifier.predict("không không tốt")
    assert result == "Positive"


def test_negation_chain(classifier):
    # không chẳng tốt => expected Positive
    result = classifier.predict("không chẳng tốt")
    assert result == "Positive"


# [QA-TEST | FAIL] FAILS (returns "Positive"). Same negation flip as QA-C6 ("nhưng" turns "dở"
#   positive); punctuation tokens also not stripped at predict time (QA-C4).
def test_mixed_noise_and_vocab(classifier):
    assert classifier.predict("@@ dạy hay ## nhưng dở !!") == "Negative"

# 4. STOPWORDS BEHAVIOR 

def test_stopwords_on_off_consistency(classifier):
    text = "môn học hay"

    classifier.use_stopwords_retrieval = False
    result_off = classifier.predict(text)

    classifier.use_stopwords_retrieval = True
    result_on = classifier.predict(text)

    # sentiment should NOT change due to stopwords removal
    assert result_off == result_on
