import html
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

PROJECT_ROOT_PATH = Path(__file__).resolve().parent
if str(PROJECT_ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT_PATH))

from models.classifier import Classifier
from scripts.paths import PROJECT_ROOT
from utils.text_utils import preprocess, tokenize


VOCAB_ROOT = PROJECT_ROOT / "models" / "vocab"

EXP_A_POS = VOCAB_ROOT / "exp_a" / "pos_vocab.json"
EXP_A_NEG = VOCAB_ROOT / "exp_a" / "neg_vocab.json"
EXP_B_POS = VOCAB_ROOT / "exp_b" / "pos_vocab.json"
EXP_B_NEG = VOCAB_ROOT / "exp_b" / "neg_vocab.json"


@st.cache_resource
def load_classifier(exp_name, remove_stopwords):
    if exp_name == "exp_a":
        return Classifier(
            pos_vocab_path=EXP_A_POS,
            neg_vocab_path=EXP_A_NEG,
            remove_stopwords=remove_stopwords,
        )

    return Classifier(
        pos_vocab_path=EXP_B_POS,
        neg_vocab_path=EXP_B_NEG,
        remove_stopwords=remove_stopwords,
    )


def validate_vocab_files():
    required_files = [EXP_A_POS, EXP_A_NEG, EXP_B_POS, EXP_B_NEG]
    missing = [path for path in required_files if not path.exists()]
    if missing:
        names = "\n".join(str(path) for path in missing)
        raise FileNotFoundError(f"Missing vocab files:\n{names}")


def analyze_tokens(text, classifier, remove_stopwords):
    clean_text = preprocess(text)
    tokens = tokenize(clean_text)
    analyzed = []

    for token in tokens:
        token_type = "normal"
        removed = False

        if remove_stopwords and token in classifier.stopwords:
            token_type = "stopword"
            removed = True
        elif token in classifier.negators:
            token_type = "negator"
        elif token in classifier.intensifiers:
            token_type = "intensifier"
        elif token in classifier.critique_words:
            token_type = "critique"
        elif token in classifier.pos_vocab:
            token_type = "positive"
        elif token in classifier.neg_vocab:
            token_type = "negative"

        analyzed.append(
            {
                "token": token,
                "type": token_type,
                "removed": removed,
            }
        )

    return analyzed


def render_token_view(tokens):
    styles = {
        "stopword": "background:#e5e7eb;color:#6b7280;text-decoration:line-through;",
        "negator": "background:#fed7aa;color:#9a3412;",
        "intensifier": "background:#e9d5ff;color:#6b21a8;",
        "critique": "background:#fef3c7;color:#92400e;",
        "positive": "background:#bbf7d0;color:#166534;",
        "negative": "background:#fecaca;color:#991b1b;",
        "normal": "background:#f8fafc;color:#334155;",
    }

    parts = ["<div style='display:flex;flex-wrap:wrap;gap:8px;line-height:2.4;'>"]
    for item in tokens:
        token = html.escape(item["token"])
        style = styles[item["type"]]
        parts.append(
            "<span style='padding:4px 10px;border-radius:6px;"
            f"font-size:14px;{style}'>{token}</span>"
        )
    parts.append("</div>")

    st.markdown("".join(parts), unsafe_allow_html=True)


def evaluate_batch(df):
    required_cols = {"text", "label"}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(f"CSV is missing column(s): {', '.join(sorted(missing))}")

    clf_a = load_classifier("exp_a", False)
    clf_b = load_classifier("exp_b", True)

    y_true = df["label"].astype(int).tolist()
    texts = df["text"].astype(str).tolist()

    pred_a_text = clf_a.predict_batch(texts)
    pred_b_text = clf_b.predict_batch(texts)
    pred_a = [1 if label == "Positive" else 0 for label in pred_a_text]
    pred_b = [1 if label == "Positive" else 0 for label in pred_b_text]

    rows = []
    for name, preds in [("Exp A", pred_a), ("Exp B", pred_b)]:
        rows.append(
            {
                "experiment": name,
                "accuracy": round(accuracy_score(y_true, preds), 4),
                "precision": round(precision_score(y_true, preds, zero_division=0), 4),
                "recall": round(recall_score(y_true, preds, zero_division=0), 4),
                "f1": round(f1_score(y_true, preds, zero_division=0), 4),
            }
        )

    return pd.DataFrame(rows)


def show_single_predict(classifier, remove_stopwords):
    st.header("Single Predict")

    text = st.text_area(
        "Nhập câu cần phân tích",
        height=120,
        placeholder="Ví dụ: giảng viên dạy rất nhiệt tình nhưng cần nói chậm hơn",
    )

    if not text.strip():
        st.info("Nhập một câu để xem kết quả phân tích.")
        return

    score = classifier.get_score(text)
    label = "Positive" if score >= 2.0 else "Negative"

    col1, col2 = st.columns(2)
    col1.metric("Prediction", label)
    col2.metric("Score", round(score, 4))

    tokens = analyze_tokens(text, classifier, remove_stopwords)
    total_tokens = len(tokens)
    removed_tokens = sum(1 for item in tokens if item["removed"])
    remaining_tokens = total_tokens - removed_tokens

    st.subheader("Token Visualization")
    render_token_view(tokens)

    c1, c2, c3 = st.columns(3)
    c1.metric("Tổng token", total_tokens)
    c2.metric("Token bị xóa", removed_tokens)
    c3.metric("Token còn lại", remaining_tokens)


def show_batch_test(uploaded_file):
    st.header("Batch Test")

    if uploaded_file is None:
        st.info("Upload CSV có 2 cột text và label để chạy Batch Test.")
        return

    try:
        df = pd.read_csv(uploaded_file)

        st.subheader("Preview")
        st.dataframe(df.head(), width="stretch")

        if not st.button("Chay danh gia Batch"):
            return

        metrics_df = evaluate_batch(df)

        st.subheader("Metrics Comparison")
        st.dataframe(metrics_df, width="stretch")

        chart_df = metrics_df.melt(
            id_vars="experiment",
            value_vars=["accuracy", "precision", "recall", "f1"],
            var_name="metric",
            value_name="value",
        )
        fig = px.bar(
            chart_df,
            x="metric",
            y="value",
            color="experiment",
            barmode="group",
            text="value",
        )
        fig.update_layout(yaxis_range=[0, 1])
        st.plotly_chart(fig, width="stretch")

        acc_a = metrics_df.loc[metrics_df["experiment"] == "Exp A", "accuracy"].iloc[0]
        acc_b = metrics_df.loc[metrics_df["experiment"] == "Exp B", "accuracy"].iloc[0]

        if acc_b > acc_a:
            st.success("Loại stopwords giúp cải thiện độ chính xác.")
        elif acc_b == acc_a:
            st.warning("Không có sự khác biệt về độ chính xác.")
        else:
            st.error("Loại stopwords làm giảm độ chính xác.")
    except Exception as exc:
        st.error(str(exc))


def main():
    st.set_page_config(
        page_title="Stopwords Sentiment Demo",
        layout="wide",
    )

    st.title("Stopwords Sentiment Classifier")
    st.caption("AIO_2026_Research_HCMUS - Demo phân loại cảm xúc văn bản")

    try:
        validate_vocab_files()
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    st.sidebar.header("Điều khiển")
    remove_stopwords = st.sidebar.toggle("Loại bỏ Stopwords", value=False)
    uploaded_file = st.sidebar.file_uploader("Upload CSV để Batch Test", type=["csv"])

    exp_name = "exp_b" if remove_stopwords else "exp_a"
    classifier = load_classifier(exp_name, remove_stopwords)

    show_single_predict(classifier, remove_stopwords)
    st.divider()
    show_batch_test(uploaded_file)


if __name__ == "__main__":
    main()
