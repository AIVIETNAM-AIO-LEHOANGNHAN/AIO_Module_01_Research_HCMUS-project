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

TEXT = {
    "vi": {
        "page_title": "Demo Phân loại Cảm xúc",
        "app_title": "Bộ phân loại cảm xúc với Stopwords",
        "caption": "AIO_2026_Research_HCMUS - Demo phân loại cảm xúc văn bản",
        "sidebar_header": "Điều khiển",
        "language": "Ngôn ngữ",
        "remove_stopwords": "Loại bỏ Stopwords",
        "upload": "Upload CSV để Batch Test",
        "single_predict": "Dự đoán câu đơn",
        "input_label": "Nhập câu cần phân tích",
        "input_placeholder": "Ví dụ: giảng viên dạy rất nhiệt tình nhưng cần nói chậm hơn",
        "empty_input": "Nhập một câu để xem kết quả prediction.",
        "prediction": "Dự đoán",
        "score": "Điểm",
        "token_title": "Token Visualization",
        "token_empty": "Nhập câu ở bên trái để xem token.",
        "total": "Tổng",
        "removed": "Xóa",
        "remaining": "Còn",
        "reason_on": (
            "Lý do: loại stopwords giúp giảm bớt các từ lặp lại ít mang sắc thái, "
            "để điểm số tập trung hơn vào token có ý nghĩa."
        ),
        "reason_off": (
            "Lý do: giữ stopwords để đối chiếu với cấu hình gốc và xem việc lọc từ "
            "có làm thay đổi kết quả hay không."
        ),
        "batch_test": "Batch Test",
        "batch_hint": "Upload CSV có 2 cột text và label ở sidebar để chạy Batch Test.",
        "preview": "Xem trước",
        "run_batch": "Chạy đánh giá Batch",
        "batch_results": "Kết quả Batch",
        "batch_empty": "Kết quả batch test sẽ hiển thị tại đây.",
        "batch_better": "Loại stopwords giúp cải thiện độ chính xác.",
        "batch_equal": "Không có sự khác biệt về độ chính xác.",
        "batch_worse": "Loại stopwords làm giảm độ chính xác.",
        "missing_cols": "CSV thiếu cột",
    },
    "en": {
        "page_title": "Stopwords Sentiment Demo",
        "app_title": "Stopwords Sentiment Classifier",
        "caption": "AIO_2026_Research_HCMUS - Text sentiment classification demo",
        "sidebar_header": "Controls",
        "language": "Language",
        "remove_stopwords": "Remove Stopwords",
        "upload": "Upload CSV for Batch Test",
        "single_predict": "Single Predict",
        "input_label": "Enter a sentence to analyze",
        "input_placeholder": "Example: the lecturer is very enthusiastic but should speak more slowly",
        "empty_input": "Enter a sentence to see the prediction.",
        "prediction": "Prediction",
        "score": "Score",
        "token_title": "Token Visualization",
        "token_empty": "Enter a sentence on the left to inspect tokens.",
        "total": "Total",
        "removed": "Removed",
        "remaining": "Left",
        "reason_on": (
            "Reason: removing stopwords reduces repetitive low-sentiment words, "
            "so the score focuses more on meaningful tokens."
        ),
        "reason_off": (
            "Reason: keeping stopwords preserves the baseline configuration and "
            "makes the effect of filtering easier to compare."
        ),
        "batch_test": "Batch Test",
        "batch_hint": "Upload a CSV with text and label columns in the sidebar to run Batch Test.",
        "preview": "Preview",
        "run_batch": "Run Batch Evaluation",
        "batch_results": "Batch Results",
        "batch_empty": "Batch results will appear here.",
        "batch_better": "Removing stopwords improves accuracy.",
        "batch_equal": "There is no accuracy difference.",
        "batch_worse": "Removing stopwords reduces accuracy.",
        "missing_cols": "CSV is missing column(s)",
    },
}


def tr(lang, key):
    return TEXT[lang][key]


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


def inject_styles():
    st.markdown(
        """
        <style>
        :root {
            --accent-green: #1F6F4A;
            --accent-green-soft: rgba(31, 111, 74, 0.16);
            --accent-gold: #D6A21F;
            --accent-gold-soft: rgba(214, 162, 31, 0.18);
            --positive: #22C55E;
            --negative: #EF4444;
            --panel-border: rgba(148, 163, 184, 0.30);
            --panel-fill: rgba(148, 163, 184, 0.08);
        }
        h1, h2, h3 {
            letter-spacing: 0;
        }
        div[data-testid="stMetric"] {
            background: var(--panel-fill);
            border: 1px solid var(--panel-border);
            border-radius: 8px;
            padding: 12px 14px;
        }
        .prediction-wrap {
            display: grid;
            grid-template-columns: minmax(180px, 1fr) minmax(160px, 0.7fr);
            gap: 14px;
            margin: 14px 0 6px;
        }
        .prediction-box {
            border-radius: 8px;
            padding: 16px 18px;
            border: 1px solid var(--panel-border);
            background: var(--panel-fill);
        }
        .prediction-box:first-child {
            border-left: 5px solid var(--accent-green);
        }
        .prediction-box:last-child {
            border-left: 5px solid var(--accent-gold);
        }
        .prediction-label {
            font-size: 0.85rem;
            font-weight: 700;
            opacity: 0.82;
            margin-bottom: 6px;
        }
        .prediction-value {
            font-size: clamp(2.4rem, 4vw, 4rem);
            line-height: 1;
            font-weight: 900;
        }
        .score-value {
            color: var(--accent-gold);
            font-size: clamp(2.1rem, 3vw, 3.2rem);
            line-height: 1;
            font-weight: 850;
        }
        .positive-text {
            color: var(--positive);
        }
        .negative-text {
            color: var(--negative);
        }
        .side-title {
            font-size: 1rem;
            font-weight: 800;
            margin: 4px 0 10px;
            padding-left: 10px;
            border-left: 4px solid var(--accent-green);
        }
        .small-note {
            color: inherit;
            opacity: 0.78;
            font-size: 0.88rem;
            line-height: 1.45;
            margin-top: 8px;
        }
        .legend-row {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin: 10px 0 8px;
        }
        .legend-chip {
            border-radius: 999px;
            padding: 4px 9px;
            font-size: 0.78rem;
            border: 1px solid rgba(15, 23, 42, 0.12);
            white-space: nowrap;
        }
        .token-wrap {
            display: flex;
            flex-wrap: wrap;
            gap: 7px;
            line-height: 2.25;
            margin-bottom: 14px;
        }
        .token-chip {
            padding: 4px 9px;
            border-radius: 6px;
            font-size: 0.86rem;
            max-width: 100%;
            overflow-wrap: anywhere;
        }
        .empty-side {
            color: inherit;
            opacity: 0.72;
            font-size: 0.9rem;
            line-height: 1.45;
        }
        @media (max-width: 900px) {
            .prediction-wrap {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def validate_vocab_files():
    # QA/QC [S10 | Medium]: Only the 4 vocab JSONs are validated here. The lexicon
    # files (negators/intensifiers/critique) are NOT checked, and load_words()
    # returns an empty set silently if one is missing -> negation/intensifier/
    # critique scoring is silently disabled with no UI warning. Validate lexicons too.
    required_files = [EXP_A_POS, EXP_A_NEG, EXP_B_POS, EXP_B_NEG]
    missing = [path for path in required_files if not path.exists()]
    if missing:
        names = "\n".join(str(path) for path in missing)
        raise FileNotFoundError(f"Missing vocab files:\n{names}")


def token_styles():
    return {
        "stopword": "background:#e5e7eb;color:#6b7280;text-decoration:line-through;",
        "negator": "background:#fed7aa;color:#9a3412;",
        "intensifier": "background:#e9d5ff;color:#6b21a8;",
        "critique": "background:#fef3c7;color:#92400e;",
        "positive": "background:#bbf7d0;color:#166534;",
        "negative": "background:#fecaca;color:#991b1b;",
        "normal": "background:#f8fafc;color:#334155;",
    }


def analyze_tokens(text, classifier, remove_stopwords):
    # QA/QC [S11 | Low]: This tokenizes the WHOLE preprocessed text once, but
    # Classifier.get_score() first splits on [,.!?;] then tokenizes each segment.
    # For sentences with punctuation the tokens shown here (and the counts below)
    # can differ from the tokens actually scored. Align both paths for consistency.
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


def render_prediction(score, label, lang):
    label_class = "positive-text" if label == "Positive" else "negative-text"
    st.markdown(
        f"""
        <div class="prediction-wrap">
            <div class="prediction-box">
                <div class="prediction-label">{html.escape(tr(lang, "prediction"))}</div>
                <div class="prediction-value {label_class}">{html.escape(label)}</div>
            </div>
            <div class="prediction-box">
                <div class="prediction-label">{html.escape(tr(lang, "score"))}</div>
                <div class="score-value">{round(score, 4)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_color_legend():
    labels = [
        ("Stopword", "stopword"),
        ("Negator", "negator"),
        ("Intensifier", "intensifier"),
        ("Critique", "critique"),
        ("Positive", "positive"),
        ("Negative", "negative"),
        ("Normal", "normal"),
    ]
    styles = token_styles()
    parts = ["<div class='legend-row'>"]
    for label, kind in labels:
        parts.append(
            f"<span class='legend-chip' style='{styles[kind]}'>{html.escape(label)}</span>"
        )
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def render_stopword_reason(remove_stopwords, lang):
    # QA/QC [N3 | Low - dead code]: The early return when stopwords are OFF makes the
    # `else tr(lang, "reason_off")` branch unreachable, so "reason_off" never renders
    # (the OFF explanation is never shown). Either drop the early return to show
    # reason_off, or remove the dead else-branch and the unused "reason_off" string.
    if not remove_stopwords:
        return

    text = tr(lang, "reason_on") if remove_stopwords else tr(lang, "reason_off")
    st.markdown(f"<div class='small-note'>{html.escape(text)}</div>", unsafe_allow_html=True)


def render_token_view(tokens):
    styles = token_styles()
    parts = ["<div class='token-wrap'>"]
    for item in tokens:
        token = html.escape(item["token"])
        style = styles[item["type"]]
        parts.append(f"<span class='token-chip' style='{style}'>{token}</span>")
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def evaluate_batch(df):
    if "label" not in df.columns and "labels" in df.columns:
        df = df.rename(columns={"labels": "label"})

    required_cols = {"text", "label"}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        raise ValueError(f"CSV is missing column(s): {', '.join(sorted(missing))}")

    # QA/QC [S8 | Medium - spec]: Label handling now validates {0,1} and raises a
    # clear error (good - no more silent crash). But spec Task 10 Step 4 says to
    # CONVERT text labels "Positive"/"Negative" -> 1/0; this astype(int) still
    # rejects text labels instead of mapping them. Accept {"Positive":1,"Negative":0}
    # too so the documented CSV format works.
    df = df[["text", "label"]].copy()
    df["label"] = df["label"].astype(int)
    invalid_labels = set(df["label"].unique()) - {0, 1}
    if invalid_labels:
        raise ValueError("Column label only accepts 0 (Negative) and 1 (Positive)")

    # QA/QC [S12 | Low - cross-task]: This app decides labels with a FIXED 2.0
    # threshold (via predict_batch), while Task 9's pipeline SEARCHES for a best
    # threshold across 9 values. They agree only because the search picked 2.0; if
    # vocab/data change, the two deliverables will disagree. Consider reading the
    # searched best threshold from docs/threshold_results.csv for consistency.
    clf_a = load_classifier("exp_a", False)
    clf_b = load_classifier("exp_b", True)

    y_true = df["label"].tolist()
    texts = df["text"].astype(str).tolist()

    pred_a_text = clf_a.predict_batch(texts)
    pred_b_text = clf_b.predict_batch(texts)
    pred_a = [1 if label == "Positive" else 0 for label in pred_a_text]
    pred_b = [1 if label == "Positive" else 0 for label in pred_b_text]

    metric_rows = []
    for name, preds in [("Exp A", pred_a), ("Exp B", pred_b)]:
        metric_rows.append(
            {
                "experiment": name,
                "accuracy": round(accuracy_score(y_true, preds), 4),
                "precision": round(precision_score(y_true, preds, zero_division=0), 4),
                "recall": round(recall_score(y_true, preds, zero_division=0), 4),
                "f1": round(f1_score(y_true, preds, zero_division=0), 4),
            }
        )

    prediction_df = pd.DataFrame(
        {
            "stt": range(1, len(df) + 1),
            "text": texts,
            "label": y_true,
            "label_name": ["Positive" if value == 1 else "Negative" for value in y_true],
            "exp_a_prediction": pred_a_text,
            "exp_a_correct": ["Đúng" if pred == true else "Sai" for pred, true in zip(pred_a, y_true)],
            "exp_b_prediction": pred_b_text,
            "exp_b_correct": ["Đúng" if pred == true else "Sai" for pred, true in zip(pred_b, y_true)],
        }
    )

    return pd.DataFrame(metric_rows), prediction_df


def render_token_panel(tokens, remove_stopwords, lang):
    st.markdown(
        f"<div class='side-title'>{html.escape(tr(lang, 'token_title'))}</div>",
        unsafe_allow_html=True,
    )

    if tokens:
        render_token_view(tokens)
        total_tokens = len(tokens)
        removed_tokens = sum(1 for item in tokens if item["removed"])
        remaining_tokens = total_tokens - removed_tokens

        c1, c2, c3 = st.columns(3)
        c1.metric(tr(lang, "total"), total_tokens)
        c2.metric(tr(lang, "removed"), removed_tokens)
        c3.metric(tr(lang, "remaining"), remaining_tokens)
    else:
        st.markdown(
            f"<div class='empty-side'>{html.escape(tr(lang, 'token_empty'))}</div>",
            unsafe_allow_html=True,
        )

    render_color_legend()
    render_stopword_reason(remove_stopwords, lang)


def render_batch_results(uploaded_file, lang):
    st.markdown(
        f"<div class='side-title'>{html.escape(tr(lang, 'batch_results'))}</div>",
        unsafe_allow_html=True,
    )

    if uploaded_file is None:
        st.markdown(
            f"<div class='empty-side'>{html.escape(tr(lang, 'batch_empty'))}</div>",
            unsafe_allow_html=True,
        )
        return

    try:
        df = pd.read_csv(uploaded_file)
        with st.expander(tr(lang, "preview"), expanded=False):
            st.dataframe(df.head(), width="stretch", hide_index=True)

        if not st.button(tr(lang, "run_batch")):
            return

        metrics_df, prediction_df = evaluate_batch(df)
    except Exception as exc:
        st.error(str(exc))
        return

    st.dataframe(metrics_df, width="stretch", hide_index=True)

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
        color_discrete_map={"Exp A": "#1f6f4a", "Exp B": "#d6a21f"},
        barmode="group",
        text="value",
    )
    fig.update_layout(
        yaxis_range=[0, 1],
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend_title_text="",
        margin=dict(l=4, r=4, t=12, b=4),
        height=280,
    )
    st.plotly_chart(fig, width="stretch")

    acc_a = metrics_df.loc[metrics_df["experiment"] == "Exp A", "accuracy"].iloc[0]
    acc_b = metrics_df.loc[metrics_df["experiment"] == "Exp B", "accuracy"].iloc[0]

    if acc_b > acc_a:
        st.success(tr(lang, "batch_better"))
    elif acc_b == acc_a:
        st.warning(tr(lang, "batch_equal"))
    else:
        st.error(tr(lang, "batch_worse"))

    st.markdown(
        "<div class='side-title'>Dự đoán từng câu</div>",
        unsafe_allow_html=True,
    )
    st.dataframe(prediction_df, width="stretch", hide_index=True)

    csv_data = prediction_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "Tải kết quả dự đoán",
        data=csv_data,
        file_name="batch_predictions.csv",
        mime="text/csv",
    )


def render_main_input(classifier, remove_stopwords, lang):
    st.header(tr(lang, "single_predict"))
    text = st.text_area(
        tr(lang, "input_label"),
        height=120,
        placeholder=tr(lang, "input_placeholder"),
    )

    tokens = []
    if text.strip():
        score = classifier.get_score(text)
        # QA/QC [S9 | Medium]: The 2.0 threshold is hardcoded here, duplicating the
        # exact rule inside Classifier.predict(). Single-predict and batch decide the
        # label via two different code paths. Prefer classifier.predict(text) so the
        # decision threshold lives in one place and cannot drift.
        label = "Positive" if score >= 2.0 else "Negative"
        render_prediction(score, label, lang)
        tokens = analyze_tokens(text, classifier, remove_stopwords)
    else:
        st.info(tr(lang, "empty_input"))

    return tokens


def main():
    st.set_page_config(
        page_title="Stopwords Sentiment Demo",
        layout="wide",
    )
    inject_styles()

    try:
        validate_vocab_files()
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    # QA/QC [N2 | Low - dead i18n]: lang is hardcoded to "vi" and there is no language
    # selector widget, so the entire "en" translation block in TEXT (and the
    # "language" key) is dead code. Either add a st.sidebar.selectbox/radio to set
    # `lang`, or remove the unused "en" half to avoid drift.
    lang = "vi"
    # QA/QC [N4 | Low - consistency]: Hardcoded VN string bypasses the tr() i18n
    # system (see also "Dự đoán từng câu" and "Tải kết quả dự đoán" in render_batch
    # _results). Use tr(lang, "sidebar_header") so all UI text flows through TEXT.
    st.sidebar.header("Điều khiển")

    remove_stopwords = st.sidebar.toggle(tr(lang, "remove_stopwords"), value=False)
    uploaded_file = st.sidebar.file_uploader(tr(lang, "upload"), type=["csv"])
    st.sidebar.caption(
        "File CSV gồm 2 cột: `text` và `label`. "
        "Cột `label` chỉ nhận 0 = Negative, 1 = Positive."
    )

    exp_name = "exp_b" if remove_stopwords else "exp_a"
    classifier = load_classifier(exp_name, remove_stopwords)

    main_col, side_col = st.columns([0.60, 0.40], gap="large")

    with main_col:
        st.title(tr(lang, "app_title"))
        st.caption(tr(lang, "caption"))
        tokens = render_main_input(classifier, remove_stopwords, lang)

    with side_col:
        render_token_panel(tokens, remove_stopwords, lang)
        render_batch_results(uploaded_file, lang)


if __name__ == "__main__":
    main()
