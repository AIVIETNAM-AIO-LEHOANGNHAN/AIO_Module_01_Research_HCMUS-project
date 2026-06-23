"""
QA — Data Validation Testing (Task 8, strategy #1).

Verifies that the Train/Test corpora and the generated vocab/stopword artifacts are
clean, correctly formatted and safe to feed into the classifier. These tests check
*properties of the data*, not classifier behaviour.

Run: python -m pytest tests/test_data_validation.py -v
"""
import json

import pandas as pd
import pytest

from scripts.paths import (
    TRAIN_CLEANED,
    TEST_CLEANED,
    POS_VOCAB,
    NEG_VOCAB,
    STOPWORDS_CUSTOM,
    STOPWORDS_PROTECTED,
)
from utils.text_utils import load_words

DATASETS = [("train", TRAIN_CLEANED), ("test", TEST_CLEANED)]


@pytest.fixture(scope="module", params=DATASETS, ids=[d[0] for d in DATASETS])
def dataset(request):
    name, path = request.param
    df = pd.read_csv(path)
    return name, df


# --- Schema / encoding --------------------------------------------------------

def test_has_expected_columns(dataset):
    _, df = dataset
    assert list(df.columns) == ["text", "label"], (
        f"Expected columns ['text','label'], got {list(df.columns)}"
    )


def test_no_null_values(dataset):
    name, df = dataset
    nulls = df.isnull().sum().to_dict()
    assert df.isnull().sum().sum() == 0, f"[{name}] null values present: {nulls}"


def test_text_is_utf8_decodable(dataset):
    # If pandas read it with encoding errors the strings would already be mojibake;
    # re-encoding to utf-8 must round-trip without error.
    name, df = dataset
    for value in df["text"].astype(str):
        value.encode("utf-8")  # raises if not encodable


# --- Label integrity ----------------------------------------------------------

def test_labels_are_binary(dataset):
    name, df = dataset
    bad = set(df["label"].unique()) - {0, 1}
    assert not bad, f"[{name}] unexpected label values: {bad}"


def test_classes_not_severely_imbalanced(dataset):
    # QA guardrail: a wildly imbalanced split would make Task 7 accuracy misleading.
    name, df = dataset
    ratio = df["label"].mean()  # fraction of positives
    assert 0.2 <= ratio <= 0.8, f"[{name}] positive ratio {ratio:.2f} is heavily skewed"


# --- Duplicates ---------------------------------------------------------------

def test_no_fully_duplicated_rows(dataset):
    name, df = dataset
    dupes = int(df.duplicated().sum())
    # Reported (not always fatal) — flag for QA review.
    assert dupes == 0, f"[{name}] {dupes} fully duplicated (text,label) rows found"


def test_no_train_test_leakage():
    train = pd.read_csv(TRAIN_CLEANED)
    test = pd.read_csv(TEST_CLEANED)
    overlap = set(train["text"].astype(str)) & set(test["text"].astype(str))
    assert not overlap, (
        f"Train/Test leakage: {len(overlap)} identical texts in both splits "
        "— invalidates the Task 7 evaluation."
    )


# --- Vocab artifacts ----------------------------------------------------------

@pytest.mark.parametrize("path", [POS_VOCAB, NEG_VOCAB], ids=["pos_vocab", "neg_vocab"])
def test_vocab_is_valid_nonempty_json(path):
    with open(path, "r", encoding="utf-8") as f:
        vocab = json.load(f)
    assert isinstance(vocab, dict) and len(vocab) > 0, f"{path} is empty or not a dict"
    assert all(isinstance(v, int) and v >= 0 for v in vocab.values()), (
        "vocab counts must be non-negative integers"
    )


def test_min_freq_threshold_respected():
    # build_vocab filters counts < 5; surviving entries must all be >= 5.
    for path in (POS_VOCAB, NEG_VOCAB):
        with open(path, "r", encoding="utf-8") as f:
            vocab = json.load(f)
        below = {k: v for k, v in vocab.items() if v < 5}
        assert not below, f"{path} has entries below min_freq=5: {list(below)[:5]}"


# --- Stopword resources -------------------------------------------------------

def test_stopword_files_load_as_nonempty_sets():
    for path in (STOPWORDS_CUSTOM, STOPWORDS_PROTECTED):
        words = load_words(path)
        assert isinstance(words, set) and len(words) > 0, f"{path} loaded empty"


def test_protected_words_not_in_stopword_removal_list():
    # A "protected" (negation) word that is ALSO in the removal list would be stripped
    # before it can flip sentiment — defeating its purpose. Flag any overlap.
    stop = load_words(STOPWORDS_CUSTOM)
    protected = load_words(STOPWORDS_PROTECTED)
    overlap = stop & protected
    assert not overlap, (
        f"Protected/negation words also in removal list (will be stripped): {overlap}"
    )
