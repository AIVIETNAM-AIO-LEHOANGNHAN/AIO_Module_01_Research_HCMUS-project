import pandas as pd
import os
import sys

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

from models.classifier import Classifier
from scripts.paths import TEST_CLEANED, DOCS_DIR


# ======================================================
# 1. EVALUATE MODEL (FIX THRESHOLD = 0)
# ======================================================
def evaluate_model(classifier, test_path):
    """
    Đánh giá model theo rule:
    score > 0 => Positive
    else => Negative
    """

    df = pd.read_csv(TEST_CLEANED)

    y_true = df["label"]

    # predict label từ model
    y_pred_text = classifier.predict_batch(df["text"])

    # convert string → binary
    y_pred = [1 if label == "Positive" else 0 for label in y_pred_text]

    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist()
    }


# ======================================================
# 2. FIND BEST THRESHOLD
# ======================================================
def find_best_threshold(classifier, test_path, exp_name):
    """
    Thay vì cố định score > 0,
    ta thử nhiều threshold để tìm ngưỡng tốt nhất
    """

    df = pd.read_csv(test_path)

    y_true = df["label"].tolist()

    # lấy raw sentiment score
    scores = [classifier.get_score(text) for text in df["text"]]

    thresholds = [-2, -1, -0.5, 0, 0.5, 1, 1.5, 2, 3]

    results = []

    best_acc = 0
    best_threshold = 0

    print(f"\n{'='*60}")
    print(f"THRESHOLD SEARCH - {exp_name}")
    print(f"{'='*60}")

    for threshold in thresholds:

        # predict theo threshold
        y_pred = [1 if s >= threshold else 0 for s in scores]

        acc = accuracy_score(y_true, y_pred)

        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)

        results.append({
            "experiment": exp_name,
            "threshold": threshold,
            "accuracy": round(acc, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4)
        })

        # cập nhật best
        if acc > best_acc:
            best_acc = acc
            best_threshold = threshold

    return results, best_threshold, best_acc


# ======================================================
# 3. COMPARE EXPERIMENTS
# ======================================================
def print_and_save(results_a, results_b):
    """
    So sánh Exp A vs Exp B tại threshold cố định (1.5)
    và lưu file CSV
    """

    print("\n================= COMPARISON (threshold = 2.0) =================")

    # lấy kết quả threshold = 2.0
    res_a = next(r for r in results_a if r["threshold"] == 2.0)
    res_b = next(r for r in results_b if r["threshold"] == 2.0)

    print(f"{'Metric':<15} | {'Exp A':<10} | {'Exp B':<10}")
    print("-" * 45)

    for metric in ["accuracy", "precision", "recall", "f1"]:
        print(f"{metric:<15} | {res_a[metric]:<10} | {res_b[metric]:<10}")

    # -------------------------
    # save file
    # -------------------------
    os.makedirs(DOCS_DIR, exist_ok=True)

    pd.DataFrame(results_a + results_b).to_csv(
        os.path.join(DOCS_DIR, "threshold_results.csv"),
        index=False
    )

    print(f"\nSaved → {DOCS_DIR}/threshold_results.csv")


# ======================================================
# 4. MAIN EXPERIMENT
# ======================================================
if __name__ == "__main__":

    # -------------------------
    # Load models
    # -------------------------
    clf_a = Classifier(
        pos_vocab_path="models/vocab/exp_a/pos_vocab.json",
        neg_vocab_path="models/vocab/exp_a/neg_vocab.json",
        remove_stopwords=False
    )

    clf_b = Classifier(
        pos_vocab_path="models/vocab/exp_b/pos_vocab.json",
        neg_vocab_path="models/vocab/exp_b/neg_vocab.json",
        remove_stopwords=True
    )

    # -------------------------
    # Evaluate default model
    # -------------------------
    metrics_a = evaluate_model(clf_a, TEST_CLEANED)
    metrics_b = evaluate_model(clf_b, TEST_CLEANED)

    # -------------------------
    # Threshold search
    # -------------------------
    results_a, best_thr_a, best_acc_a = find_best_threshold(
        clf_a, TEST_CLEANED, "exp_a"
    )

    results_b, best_thr_b, best_acc_b = find_best_threshold(
        clf_b, TEST_CLEANED, "exp_b"
    )

    # -------------------------
    # Compare + save
    # -------------------------
    print_and_save(results_a, results_b)