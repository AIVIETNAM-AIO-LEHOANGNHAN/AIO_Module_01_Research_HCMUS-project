"""
Task 11 — Stress-test pipeline/run_pipeline.py trên 2000 câu KHÓ.

Script này TÁI SỬ DỤNG chính các hàm của pipeline/run_pipeline.py
(step_build_vocab, step_clean_vocab, load_experiment_classifiers,
evaluate_thresholds) nhưng thay tập test bằng data/test/hard_cases_2000.csv,
để kiểm tra pipeline chạy đúng và xem classifier xử lý câu khó ra sao.

Chạy:  python -m scripts.task11_run_pipeline_hardtest
Đầu ra:
  - docs/hard_cases_threshold_results.csv   (threshold search trên câu khó)
  - docs/hard_cases_errors.csv              (danh sách câu khó bị đoán sai)
  - in ra console: accuracy tốt nhất + confusion matrix + lỗi theo template
"""
import pandas as pd
from sklearn.metrics import confusion_matrix

from scripts.paths import DATA_DIR, DOCS_DIR
from pipeline.run_pipeline import (
    validate_inputs,
    step_build_vocab,
    step_clean_vocab,
    load_experiment_classifiers,
    evaluate_thresholds,
    THRESHOLDS,
)

HARD_PATH = DATA_DIR / "test" / "hard_cases_2000.csv"


def best_row(rows):
    return max(rows, key=lambda r: r["accuracy"])


def errors_at_threshold(clf, df, threshold):
    """Trả về DataFrame các câu bị đoán sai tại 1 threshold."""
    recs = []
    for text, y_true in zip(df["text"], df["label"]):
        score = clf.get_score(text)
        y_pred = 1 if score >= threshold else 0
        if y_pred != y_true:
            recs.append({
                "text": text,
                "label_true": y_true,
                "label_pred": y_pred,
                "score": round(score, 3),
                "error_type": "False Positive" if y_true == 0 else "False Negative",
            })
    return pd.DataFrame(recs)


def main():
    print("=" * 64)
    print("TASK 11 — STRESS TEST run_pipeline.py TRÊN 2000 CÂU KHÓ")
    print("=" * 64)

    # 1) Chạy đúng các bước chuẩn bị của pipeline (build + clean vocab)
    validate_inputs()
    print("\n[1/4] Build vocab (exp_a / exp_b) từ train...")
    step_build_vocab()
    print("[2/4] Clean vocab (loại rule words)...")
    step_clean_vocab()

    # 2) Nạp tập câu khó
    hard_df = pd.read_csv(HARD_PATH)
    if "text" not in hard_df.columns or "label" not in hard_df.columns:
        raise ValueError("hard_cases_2000.csv phải có cột text và label")
    print(f"[3/4] Nạp {len(hard_df)} câu khó từ {HARD_PATH.name}")

    # 3) Dùng đúng classifier của pipeline, đánh giá trên câu khó
    clf_a, clf_b = load_experiment_classifiers()
    print("[4/4] Đánh giá threshold search trên câu khó...\n")

    rows_a, best_a = evaluate_thresholds(clf_a, hard_df, "exp_a")
    rows_b, best_b = evaluate_thresholds(clf_b, hard_df, "exp_b")

    results_df = pd.DataFrame(rows_a + rows_b)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(DOCS_DIR / "hard_cases_threshold_results.csv", index=False)

    # 4) Báo cáo
    def report(name, best, clf):
        thr = best["best_threshold"]
        cm = best["confusion_matrix"]  # [[TN, FP], [FN, TP]]
        tn, fp = cm[0]
        fn, tp = cm[1]
        print(f"--- {name.upper()} (best threshold = {thr}) ---")
        print(f"  Accuracy       : {best['best_accuracy']}")
        print(f"  Confusion [[TN,FP],[FN,TP]] = {cm}")
        print(f"  False Positive : {fp}  (Neg bị đoán Positive)")
        print(f"  False Negative : {fn}  (Pos bị đoán Negative)")
        return thr

    thr_a = report("exp_a (giữ stopwords)", best_a, clf_a)
    print()
    thr_b = report("exp_b (loại stopwords)", best_b, clf_b)

    print(f"\nĐộ chênh accuracy (B - A): {round(best_b['best_accuracy'] - best_a['best_accuracy'], 4)}")

    # 5) Xuất danh sách câu sai (theo exp_b tại threshold tốt nhất) + phân bố lỗi
    err_a = errors_at_threshold(clf_a, hard_df, thr_a)
    err_b = errors_at_threshold(clf_b, hard_df, thr_b)
    err_b.to_csv(DOCS_DIR / "hard_cases_errors.csv", index=False)

    print("\n--- Phân bố lỗi trên câu khó ---")
    print(f"  Exp A: {len(err_a)}/{len(hard_df)} sai "
          f"(FP={sum(err_a['error_type']=='False Positive')}, "
          f"FN={sum(err_a['error_type']=='False Negative')})")
    print(f"  Exp B: {len(err_b)}/{len(hard_df)} sai "
          f"(FP={sum(err_b['error_type']=='False Positive')}, "
          f"FN={sum(err_b['error_type']=='False Negative')})")

    print("\nĐã lưu:")
    print(f"  {DOCS_DIR / 'hard_cases_threshold_results.csv'}")
    print(f"  {DOCS_DIR / 'hard_cases_errors.csv'}")
    print("\nPIPELINE HARD-TEST HOÀN TẤT ✓")


if __name__ == "__main__":
    main()
