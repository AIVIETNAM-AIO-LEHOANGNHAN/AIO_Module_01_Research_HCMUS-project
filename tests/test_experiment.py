"""
QA — Task 7 (A/B Testing) verification suite.

Covers the three required strategies against `experiments/run_experiment.py`:
  1. Functional Testing      — evaluate_model() returns the 4 metrics, in range, on real data.
  2. Data Validation Testing — the test set fed to the experiment is clean/binary/non-leaking.
  3. Experiment Validation   — the A/B comparison is FAIR (same data, only the flag differs)
                               and REPRODUCIBLE (identical numbers across runs), and the
                               committed results_*.csv match a fresh computation.

Run: python -m pytest tests/test_experiment.py -v
"""
import csv
from pathlib import Path

import pandas as pd
import pytest

from experiments.run_experiment import evaluate_model
from models.classifier import Classifier
from scripts.paths import (
    TEST_CLEANED,
    POS_VOCAB,
    NEG_VOCAB,
    STOPWORDS_CUSTOM,
    STOPWORDS_PROTECTED,
    PROJECT_ROOT,
)

METRIC_KEYS = ("accuracy", "precision", "recall", "f1")


def _clf(use_removal):
    return Classifier(
        pos_count=POS_VOCAB,
        neg_count=NEG_VOCAB,
        use_stopwords_retrieval=use_removal,
        stopwords=STOPWORDS_CUSTOM,
        negative_words=STOPWORDS_PROTECTED,
    )


@pytest.fixture(scope="module")
def metrics_a():
    return evaluate_model(_clf(False), TEST_CLEANED)


@pytest.fixture(scope="module")
def metrics_b():
    return evaluate_model(_clf(True), TEST_CLEANED)


# === 1. FUNCTIONAL TESTING ====================================================

def test_evaluate_model_returns_all_metrics(metrics_a):
    assert set(metrics_a) == set(METRIC_KEYS), f"Missing metrics: {set(METRIC_KEYS) - set(metrics_a)}"


def test_metrics_in_valid_range(metrics_a, metrics_b):
    for m in (metrics_a, metrics_b):
        for k in METRIC_KEYS:
            assert 0.0 <= m[k] <= 1.0, f"{k}={m[k]} out of [0,1]"


def test_evaluate_model_accepts_classifier_and_path():
    # Signature contract from the spec: evaluate_model(classifier, test_data).
    out = evaluate_model(_clf(False), TEST_CLEANED)
    assert isinstance(out, dict)


# === 2. DATA VALIDATION TESTING ===============================================

def test_test_set_schema_and_labels():
    df = pd.read_csv(TEST_CLEANED)
    assert list(df.columns) == ["text", "label"]
    assert set(df["label"].unique()) <= {0, 1}, "non-binary labels in the experiment test set"
    assert df.isnull().sum().sum() == 0, "null values in the experiment test set"


def test_no_train_test_leakage_for_experiment():
    from scripts.paths import TRAIN_CLEANED

    train = set(pd.read_csv(TRAIN_CLEANED)["text"].astype(str))
    test = set(pd.read_csv(TEST_CLEANED)["text"].astype(str))
    assert not (train & test), "Train/Test overlap invalidates the A/B evaluation"


# === 3. EXPERIMENT VALIDATION TESTING =========================================

def test_reproducible_same_numbers_twice():
    first = evaluate_model(_clf(False), TEST_CLEANED)
    second = evaluate_model(_clf(False), TEST_CLEANED)
    assert first == second, "evaluate_model is not reproducible across runs"


def test_both_configs_use_same_test_set():
    n = len(pd.read_csv(TEST_CLEANED))
    a = _clf(False).predict_batch(pd.read_csv(TEST_CLEANED)["text"].astype(str).tolist())
    b = _clf(True).predict_batch(pd.read_csv(TEST_CLEANED)["text"].astype(str).tolist())
    assert len(a) == len(b) == n, "Configs evaluated different sample counts — unfair"


def test_configs_differ_only_by_stopword_flag():
    a, b = _clf(False), _clf(True)
    assert (a.pos_count, a.neg_count, a.stopwords, a.negative_words) == (
        b.pos_count, b.neg_count, b.stopwords, b.negative_words
    )
    assert a.use_stopwords_retrieval != b.use_stopwords_retrieval


def test_stopword_removal_has_measurable_effect(metrics_a, metrics_b):
    # If A and B are identical the A/B test measures nothing.
    assert metrics_a != metrics_b, "Stopword removal changed no metric — no A/B signal"


# === 4. RESULTS-FILE INTEGRITY (committed artifacts match a fresh run) ========

def _read_value_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return {row["Metric"]: float(row["Value"]) for row in csv.DictReader(f)}


@pytest.mark.parametrize(
    "fname,use_removal",
    [("results_raw.csv", False), ("results_cleaned.csv", True)],
)
def test_committed_results_match_recomputation(fname, use_removal):
    path = PROJECT_ROOT / fname
    if not path.exists():
        pytest.skip(f"{fname} not present")
    committed = _read_value_csv(path)
    fresh = evaluate_model(_clf(use_removal), TEST_CLEANED)
    for k in METRIC_KEYS:
        assert committed[k] == pytest.approx(fresh[k], abs=1e-3), (
            f"{fname}: committed {k}={committed[k]} != recomputed {fresh[k]} "
            "(stale results file)"
        )
