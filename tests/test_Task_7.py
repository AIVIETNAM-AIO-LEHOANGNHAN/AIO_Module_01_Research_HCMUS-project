import pytest
from models.classifier import Classifier
from scripts.paths import (
    POS_VOCAB,
    NEG_VOCAB,
    STOPWORDS_CUSTOM,
    STOPWORDS_PROTECTED,
)

@pytest.fixture
def classifier():
    return Classifier(
        pos_count=POS_VOCAB,
        neg_count=NEG_VOCAB,
        use_stopwords_retrieval=False,
        stopwords=STOPWORDS_CUSTOM,
        negative_words=STOPWORDS_PROTECTED,
    )

def test_rat_tot(classifier):
    result = classifier.predict("rất tốt")
    print(f"'rất tốt' -> {result}")

def test_qua_hay(classifier):
    result = classifier.predict("quá hay")
    print(f"'quá hay' -> {result}")

def test_rat_do(classifier):
    result = classifier.predict("rất dở")
    print(f"'rất dở' -> {result}")

def test_khong_tot(classifier):
    result = classifier.predict("không tốt")
    print(f"'không tốt' -> {result}")

def test_khong_do(classifier):
    result = classifier.predict("không dở")
    print(f"'không dở' -> {result}")
