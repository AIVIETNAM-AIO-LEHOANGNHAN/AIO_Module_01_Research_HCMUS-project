import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

PROJECT_ROOT_PATH = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT_PATH))

from models.build_vocab import build_vocab
from models.classifier import Classifier
from utils.text_utils import load_words
from scripts.paths import (
    PROJECT_ROOT,
    TRAIN_CLEANED,
    TEST_CLEANED,
    DOCS_DIR,
    NEGATORS,
    INTENSIFIERS,
    CRITIQUE_WORDS,
)
VOCAB_ROOT = PROJECT_ROOT / "models" / "vocab"

EXP_A_DIR = VOCAB_ROOT / "exp_a"
EXP_B_DIR = VOCAB_ROOT / "exp_b"

EXP_A_POS = EXP_A_DIR / "pos_vocab.json"
EXP_A_NEG = EXP_A_DIR / "neg_vocab.json"
EXP_B_POS = EXP_B_DIR / "pos_vocab.json"
EXP_B_NEG = EXP_B_DIR / "neg_vocab.json"

THRESHOLDS = [-2, -1, -0.5, 0, 0.5, 1, 1.5, 2, 3]
def validate_inputs():
    required_files = [
        TRAIN_CLEANED,
        TEST_CLEANED,
        NEGATORS,
        INTENSIFIERS,
        CRITIQUE_WORDS,
    ]

    missing = [path for path in required_files if not path.exists()]

    if missing:
        names = "\n".join(str(path) for path in missing)
        raise FileNotFoundError(f"Missing required files:\n{names}")

    return True
def step_build_vocab():
    # QA/QC [S4 | Low - spec]: build_vocab() reports progress via print() (terminal
    # only). Spec Step 1 asks for progress ON the Streamlit UI. Consider passing a
    # status callback or wrapping calls with st.status() to surface progress in-app.
    EXP_A_DIR.mkdir(parents=True, exist_ok=True)
    EXP_B_DIR.mkdir(parents=True, exist_ok=True)

    build_vocab(
        data_path=TRAIN_CLEANED,
        output_dir=EXP_A_DIR,
        remove_stopwords=False,
    )

    build_vocab(
        data_path=TRAIN_CLEANED,
        output_dir=EXP_B_DIR,
        remove_stopwords=True,
    )

    return {
        "exp_a": [EXP_A_POS, EXP_A_NEG],
        "exp_b": [EXP_B_POS, EXP_B_NEG],
    }
    
def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def step_clean_vocab():
    rules = (
        load_words(NEGATORS)
        | load_words(INTENSIFIERS)
        | load_words(CRITIQUE_WORDS)
    )

    vocab_files = [
        EXP_A_POS,
        EXP_A_NEG,
        EXP_B_POS,
        EXP_B_NEG,
    ]

    rows = []

    for path in vocab_files:
        if not path.exists():
            raise FileNotFoundError(f"Vocab file not found: {path}")

        vocab = read_json(path)
        before = len(vocab)

        cleaned = {
            word: freq
            for word, freq in vocab.items()
            if word not in rules
        }

        after = len(cleaned)
        write_json(path, cleaned)

        rows.append({
            "file": str(path.relative_to(VOCAB_ROOT)),
            "before": before,
            "after": after,
            "removed": before - after,
        })

    return pd.DataFrame(rows)
def load_experiment_classifiers():
    clf_a = Classifier(
        pos_vocab_path=EXP_A_POS,
        neg_vocab_path=EXP_A_NEG,
        remove_stopwords=False,
    )

    clf_b = Classifier(
        pos_vocab_path=EXP_B_POS,
        neg_vocab_path=EXP_B_NEG,
        remove_stopwords=True,
    )

    return clf_a, clf_b
def evaluate_thresholds(classifier, test_df, exp_name):
    y_true = test_df["label"].tolist()
    scores = [classifier.get_score(text) for text in test_df["text"]]

    rows = []
    best_accuracy = -1
    best_threshold = None
    best_y_pred = None

    for threshold in THRESHOLDS:
        y_pred = [1 if score >= threshold else 0 for score in scores]

        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)

        rows.append({
            "experiment": exp_name,
            "threshold": threshold,
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        })

        # QA/QC [S2 | Medium - analysis]: "Best" is chosen by ACCURACY alone. The
        # task's stated goal was to fix over-prediction of Positive (FP~703) by
        # balancing precision/recall. Empirically the best-accuracy threshold is 2.0,
        # where exp_a STILL has FP=731 (confusion [[269,731],[64,936]]) - i.e.
        # optimizing accuracy does not address the stated goal; the real gain comes
        # from stopword removal (exp_b FP=351). Select by F1 (or report the P/R
        # trade-off) to match the objective stated in the task.
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_threshold = threshold
            best_y_pred = y_pred

    matrix = confusion_matrix(y_true, best_y_pred).tolist()

    return rows, {
        "experiment": exp_name,
        "best_threshold": best_threshold,
        "best_accuracy": round(best_accuracy, 4),
        "confusion_matrix": matrix,
    }


def step_run_experiment():
    test_df = pd.read_csv(TEST_CLEANED)

    if "text" not in test_df.columns or "label" not in test_df.columns:
        raise ValueError("TEST_CLEANED must contain text and label columns")

    clf_a, clf_b = load_experiment_classifiers()

    rows_a, best_a = evaluate_thresholds(clf_a, test_df, "exp_a")
    rows_b, best_b = evaluate_thresholds(clf_b, test_df, "exp_b")

    results_df = pd.DataFrame(rows_a + rows_b)

    return results_df, best_a, best_b
def step_export_results(results_df):
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    output_path = DOCS_DIR / "threshold_results.csv"
    results_df.to_csv(output_path, index=False)

    return output_path
def run_all_pipeline():
    validate_inputs()
    step_build_vocab()
    clean_stats = step_clean_vocab()
    results_df, best_a, best_b = step_run_experiment()
    output_path = step_export_results(results_df)

    return {
        "clean_stats": clean_stats,
        "results": results_df,
        "best_a": best_a,
        "best_b": best_b,
        "output_path": output_path,
    }


def show_results(results):
    clean_stats = results["clean_stats"]
    results_df = results["results"]
    best_a = results["best_a"]
    best_b = results["best_b"]
    output_path = results["output_path"]

    st.subheader("Clean Vocab Stats")
    st.dataframe(clean_stats, width="stretch")

    st.subheader("Threshold Search Results")
    st.dataframe(results_df, width="stretch")

    improvement = best_b["best_accuracy"] - best_a["best_accuracy"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Exp A Best Accuracy", best_a["best_accuracy"])
    col2.metric("Exp B Best Accuracy", best_b["best_accuracy"])
    col3.metric("Improvement", round(improvement, 4))

    st.subheader("Confusion Matrix")
    # QA/QC [S3 | Low]: Rendered as a raw nested list with no TN/FP/FN/TP labels,
    # which is hard to interpret. Render as a labeled 2x2 table (rows=actual,
    # cols=predicted) so reviewers can read FP/FN directly.
    st.write("Exp A", best_a["confusion_matrix"])
    st.write("Exp B", best_b["confusion_matrix"])

    with open(output_path, "rb") as f:
        st.download_button(
            "Download threshold_results.csv",
            data=f,
            file_name="threshold_results.csv",
            mime="text/csv",
        )


def main():
    st.set_page_config(
        page_title="End-to-End Pipeline",
        layout="wide",
    )

    st.title("Pipeline End-to-End")
    st.caption("Build vocab -> Clean vocab -> Run experiment -> Export CSV")

    if "pipeline_results" not in st.session_state:
        st.session_state.pipeline_results = None

    st.sidebar.header("Pipeline Controls")

    if st.sidebar.button("Chạy toàn bộ Pipeline"):
        # QA/QC [S1 | Medium - spec]: A single global spinner hides per-step status.
        # The spec requires each of the 4 steps to show "đang chạy / hoàn thành / lỗi".
        # Wrap each step (build/clean/experiment/export) in its own st.status() so a
        # failure is attributable to a specific step, not the whole run.
        try:
            with st.spinner("Đang chạy toàn bộ pipeline..."):
                st.session_state.pipeline_results = run_all_pipeline()
            st.success("Pipeline completed successfully")
        except Exception as e:
            st.error(str(e))

    if st.sidebar.button("Step 1: Build Vocab"):
        try:
            validate_inputs()
            with st.spinner("Đang build vocab..."):
                step_build_vocab()
            st.success("Build vocab completed")
        except Exception as e:
            st.error(str(e))

    if st.sidebar.button("Step 2: Clean Vocab"):
        try:
            with st.spinner("Đang clean vocab..."):
                clean_stats = step_clean_vocab()
            st.success("Clean vocab completed")
            st.dataframe(clean_stats, width="stretch")
        except Exception as e:
            st.error(str(e))

    if st.sidebar.button("Step 3: Run Experiment + Export"):
        try:
            with st.spinner("Đang chạy experiment..."):
                results_df, best_a, best_b = step_run_experiment()
                output_path = step_export_results(results_df)

            st.session_state.pipeline_results = {
                "clean_stats": pd.DataFrame(),
                "results": results_df,
                "best_a": best_a,
                "best_b": best_b,
                "output_path": output_path,
            }

            st.success("Experiment completed")
        except Exception as e:
            st.error(str(e))

    if st.session_state.pipeline_results:
        show_results(st.session_state.pipeline_results)
    else:
        st.info("Chọn một nút ở sidebar để bắt đầu.")


if __name__ == "__main__":
    main()
