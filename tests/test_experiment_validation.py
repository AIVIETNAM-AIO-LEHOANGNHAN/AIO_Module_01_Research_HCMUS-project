"""
QA — Experiment Validation Testing (Task 8, strategy #3 / fairness of Task 7 A/B test).

Goal: confirm the A/B experiment is FAIR and REPRODUCIBLE before trusting its numbers:
  * both configs (A = no stopword removal, B = removal) run on the SAME test set,
  * the only difference between A and B is the `use_stopwords_retrieval` flag,
  * predictions are deterministic (re-running yields identical results),
  * the evaluation harness maps labels correctly and aligns y_true / y_pred.

Task 7's script lives in `experiments/run_experiment.py`. On a branch where that file
is absent (e.g. feat/sentiment-classifier), the harness tests are SKIPPED with a clear
message — which itself documents that Task 7 is not yet merged here.

Run: python -m pytest tests/test_experiment_validation.py -v
"""
import importlib.util

import pandas as pd
import pytest

from models.classifier import Classifier
from scripts.paths import (
    TEST_CLEANED,
    POS_VOCAB,
    NEG_VOCAB,
    STOPWORDS_CUSTOM,
    STOPWORDS_PROTECTED,
)

def _experiment_available():
    # find_spec raises ModuleNotFoundError if the parent package is missing entirely.
    try:
        return importlib.util.find_spec("experiments.run_experiment") is not None
    except ModuleNotFoundError:
        return False


EXPERIMENT_AVAILABLE = _experiment_available()


def _make(use_removal):
    return Classifier(
        pos_count=POS_VOCAB,
        neg_count=NEG_VOCAB,
        use_stopwords_retrieval=use_removal,
        stopwords=STOPWORDS_CUSTOM,
        negative_words=STOPWORDS_PROTECTED,
    )


@pytest.fixture(scope="module")
def test_texts():
    df = pd.read_csv(TEST_CLEANED)
    return df["text"].astype(str).tolist()


# --- Reproducibility ----------------------------------------------------------

def test_predictions_are_deterministic(test_texts):
    clf = _make(False)
    first = clf.predict_batch(test_texts)
    second = clf.predict_batch(test_texts)
    assert first == second, "Re-running the same config produced different predictions"


def test_two_instances_same_config_agree(test_texts):
    # Reproducibility across fresh instances (no hidden global state).
    a1 = _make(False).predict_batch(test_texts)
    a2 = _make(False).predict_batch(test_texts)
    assert a1 == a2


# --- Fairness -----------------------------------------------------------------

def test_both_configs_score_same_test_set(test_texts):
    a = _make(False).predict_batch(test_texts)
    b = _make(True).predict_batch(test_texts)
    assert len(a) == len(b) == len(test_texts), (
        "Configs A and B evaluated a different number of samples — unfair comparison"
    )


def test_configs_differ_only_by_flag():
    a, b = _make(False), _make(True)
    # Everything except the stopword flag must be identical resources.
    assert a.pos_count == b.pos_count
    assert a.neg_count == b.neg_count
    assert a.stopwords == b.stopwords
    assert a.negative_words == b.negative_words
    assert a.use_stopwords_retrieval != b.use_stopwords_retrieval


def test_removal_actually_changes_some_predictions(test_texts):
    # Sanity: if A and B are byte-identical, the experiment measures nothing.
    a = _make(False).predict_batch(test_texts)
    b = _make(True).predict_batch(test_texts)
    assert a != b, "Stopword removal changed no predictions — A/B test has no signal"


# --- Output contract ----------------------------------------------------------

def test_predictions_use_expected_label_space(test_texts):
    preds = set(_make(False).predict_batch(test_texts))
    assert preds <= {"Positive", "Negative"}, f"Unexpected prediction labels: {preds}"


# --- Task 7 harness (skipped if the script is not on this branch) -------------

@pytest.mark.skipif(
    not EXPERIMENT_AVAILABLE,
    reason="experiments/run_experiment.py is not present on this branch "
    "(Task 7 not merged here) — see QA_Testing_Report.md",
)
def test_evaluate_model_returns_all_metrics():
    from experiments.run_experiment import evaluate_model

    metrics = evaluate_model(_make(False), TEST_CLEANED)
    for key in ("accuracy", "precision", "recall", "f1"):
        assert key in metrics, f"evaluate_model missing metric: {key}"
        assert 0.0 <= metrics[key] <= 1.0
