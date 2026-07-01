"""
Task 11 - Error Analysis (dựa trên phiên bản classifier đã cập nhật trên
origin/main, xem scripts/task11_classifier_main.py).

Chạy Classifier (Exp A = giữ stopwords, Exp B = loại stopwords) trên
data/test/cleaned.csv, thu thập các câu dự đoán sai, gắn nhãn error_type
(False Positive / False Negative), phân loại nguyên nhân, và xuất:
  - docs/error_analysis_exp_a.csv
  - docs/error_analysis_exp_b.csv
  - docs/_error_analysis_summary.json (dữ liệu trung gian cho báo cáo)
"""
import json
import re
from collections import Counter

import pandas as pd

from scripts.paths import TEST_CLEANED, DOCS_DIR, STOPWORDS_CUSTOM, STOPWORDS_PROTECTED
from scripts.task11_classifier_main import MainClassifier, load_words_main

POS_VOCAB = "models/vocab/pos_vocab.json"
NEG_VOCAB = "models/vocab/neg_vocab.json"

NEGATIVE_WORDS = load_words_main(STOPWORDS_PROTECTED)
STOPWORDS = load_words_main(STOPWORDS_CUSTOM)

CONTRAST_RE = re.compile(r"\bnhưng\b|\btuy nhiên\b|\btuy\b")


def word_present(text, word):
    return re.search(rf"(?<!\w){re.escape(word)}(?!\w)", text) is not None


def classify_cause(text, label_true, label_pred, score, pos_vocab, neg_vocab):
    t = str(text).lower()
    has_negative_word = any(word_present(t, w) for w in NEGATIVE_WORDS)
    has_contrast = bool(CONTRAST_RE.search(t))

    if label_true == 0 and label_pred == 1:
        # False Positive: gold Negative, model đoán Positive
        if has_contrast:
            return "C2-nhuong_bo (tuy...nhung)"
        if has_negative_word:
            return "C1-negation_1_token_khong_du_pham_vi"
        if score == 0:
            return "C3-neg_vocab_ngheo(score=0,default Negative*)"
        return "C4-pos_vocab_lan_at_khac"
    else:
        # False Negative: gold Positive, model đoán Negative
        if score == 0:
            return "D2-pos_vocab_khong_nhan_ra"
        if has_negative_word and score < 0:
            return "D1-negative_word_lat_dau_qua_tay"
        return "D3-neg_vocab_lan_at_khac"


def run_experiment(exp_name, use_stopwords_retrieval, df):
    clf = MainClassifier(
        pos_count=POS_VOCAB,
        neg_count=NEG_VOCAB,
        use_stopwords_retrieval=use_stopwords_retrieval,
        stopwords=STOPWORDS_CUSTOM,
        negative_words=STOPWORDS_PROTECTED,
    )

    rows = []
    for text, label_true in zip(df["text"], df["label"]):
        score = clf.get_score(text)
        pred = 1 if score > 0 else 0
        if pred != label_true:
            error_type = "False Positive" if label_true == 0 else "False Negative"
            cause = classify_cause(text, label_true, pred, score, clf.pos_vocab, clf.neg_vocab)
            rows.append({
                "text": text,
                "label_true": label_true,
                "label_pred": pred,
                "score": score,
                "error_type": error_type,
                "cause": cause,
            })

    err_df = pd.DataFrame(rows)
    n_total = len(df)
    n_err = len(err_df)
    n_fp = (err_df["error_type"] == "False Positive").sum() if n_err else 0
    n_fn = (err_df["error_type"] == "False Negative").sum() if n_err else 0
    acc = 1 - n_err / n_total

    print(f"\n{exp_name}: total={n_total} errors={n_err} (FP={n_fp}, FN={n_fn}) acc={acc:.4f}")
    return err_df, {"total": n_total, "errors": n_err, "fp": int(n_fp), "fn": int(n_fn), "acc": acc}


def main():
    df = pd.read_csv(TEST_CLEANED)

    err_a, stats_a = run_experiment("exp_a (giu stopwords)", use_stopwords_retrieval=False, df=df)
    err_b, stats_b = run_experiment("exp_b (loai stopwords)", use_stopwords_retrieval=True, df=df)

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    out_cols = ["text", "label_true", "label_pred", "score", "error_type"]
    err_a[out_cols].to_csv(DOCS_DIR / "error_analysis_exp_a.csv", index=False)
    err_b[out_cols].to_csv(DOCS_DIR / "error_analysis_exp_b.csv", index=False)

    set_a = set(err_a["text"])
    set_b = set(err_b["text"])
    both_wrong = set_a & set_b
    only_a_wrong = set_a - set_b   # A sai, B đúng
    only_b_wrong = set_b - set_a  # B sai, A đúng

    cause_counts_a = Counter(err_a["cause"]) if len(err_a) else Counter()
    cause_counts_b = Counter(err_b["cause"]) if len(err_b) else Counter()

    with open(DOCS_DIR / "_error_analysis_summary.json", "w", encoding="utf-8") as f:
        json.dump({
            "stats_a": stats_a,
            "stats_b": stats_b,
            "both_wrong": len(both_wrong),
            "only_a_wrong": len(only_a_wrong),
            "only_b_wrong": len(only_b_wrong),
            "cause_counts_a": dict(cause_counts_a),
            "cause_counts_b": dict(cause_counts_b),
            "examples_only_a_wrong": sorted(only_a_wrong)[:20],
            "examples_both_wrong": sorted(both_wrong)[:20],
            "examples_only_b_wrong": sorted(only_b_wrong)[:20],
        }, f, ensure_ascii=False, indent=2)

    print("\n--- Cause counts A ---")
    for k, v in cause_counts_a.most_common():
        print(f"  {k}: {v}")
    print("--- Cause counts B ---")
    for k, v in cause_counts_b.most_common():
        print(f"  {k}: {v}")

    print(f"\nBoth wrong: {len(both_wrong)}  Only A wrong (B fixed): {len(only_a_wrong)}  Only B wrong: {len(only_b_wrong)}")
    print("\nSaved CSVs to docs/error_analysis_exp_a.csv and docs/error_analysis_exp_b.csv")


if __name__ == "__main__":
    main()
