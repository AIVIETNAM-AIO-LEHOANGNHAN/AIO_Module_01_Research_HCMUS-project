# [QA-E2 | HIGH] No sys.path bootstrap. Running `python experiments/run_experiment.py` from the
#   repo root raises `ModuleNotFoundError: No module named 'models'` (the tests only work because
#   tests/conftest.py inserts PROJECT_ROOT). Task 7 criterion "Script chạy thành công" fails out of
#   the box. Fix: add a bootstrap (insert project root into sys.path) or run as `python -m
#   experiments.run_experiment` and document it.
# [QA-E10 | MEDIUM] `matplotlib` is imported here but is NOT in requirements.txt (only pandas,
#   scikit-learn, datasets, pyvi). A fresh env cannot run this script. Add matplotlib.
from models.classifier import Classifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from scripts.paths import STOPWORDS_CUSTOM, TEST_CLEANED, STOPWORDS_PROTECTED, POS_VOCAB, NEG_VOCAB
import pandas as pd
import matplotlib.pyplot as plt

# [QA-E1 | HIGH/spec] Task 7 explicitly requires a fixed `seed=42` for reproducibility. No seed is
#   set anywhere in this script. The rule-based model happens to be deterministic (QA verified
#   identical numbers across runs), so results ARE reproducible in practice — but the spec
#   requirement is unmet and there is no note explaining WHY a seed is unnecessary. Either set a
#   seed or document the determinism argument in Experimental_Results.md.
def evaluate_model(classifier, test_data):
    df = pd.read_csv(test_data)
    text_list = df['text'].tolist()
    y_pred = classifier.predict_batch(text_list)
    # [QA-E7 | MEDIUM] Label mapping is silent: any value != '1' (e.g. '1.0', stray ' 2', NaN) maps
    #   to 'Negative' with no validation. Assert labels are in {'0','1'} first, or map explicitly
    #   and raise on anything unexpected — otherwise mislabeled rows quietly inflate the negative class.
    y_true = ['Positive' if str(label).strip() == '1' else 'Negative' for label in df['label'].tolist()]

    # [QA-E6 | MEDIUM] average='weighted' with no `zero_division` arg. The model predicts almost
    #   everything "Positive" (QA measured 954/964 errors are Neg->Pos), so one class can have no
    #   predictions -> sklearn emits UndefinedMetricWarning and the weighted figure hides the
    #   collapse. Report PER-CLASS precision/recall (and set zero_division=0 explicitly) so the
    #   degenerate behaviour is visible instead of averaged away.
    return {
        'accuracy': round(accuracy_score(y_true, y_pred), 3),
        'precision': round(precision_score(y_true, y_pred, average='weighted', labels=['Positive', 'Negative']), 3),
        'recall': round(recall_score(y_true, y_pred, average='weighted', labels=['Positive', 'Negative']), 3),
        'f1': round(f1_score(y_true, y_pred, average='weighted', labels=['Positive', 'Negative']), 3),
    }

# Test
if __name__ == "__main__":
    # [QA-E4 | CRITICAL/validity] The headline result this script produces is built on a classifier
    #   that is near-random: A (no removal) acc=0.518/F1=0.380, B (removal) acc=0.555/F1=0.462 on a
    #   binary task. QA error-mining: config A makes 964/2000 errors and 954 of them are Neg->Pos
    #   (the model labels almost every negative review "Positive"). Root cause is the negation bug in
    #   classifier.py (sign-flip + single-token negation) plus tie->Negative. The experiment PROCESS
    #   is fair and reproducible, but the conclusion "lọc stopwords hiệu quả hơn" (+0.082 F1) is NOT
    #   trustworthy until the classifier is fixed and accuracy is meaningfully above chance.
    # [QA-E9 | MEDIUM/fairness] Both configs share ONE vocab built WITHOUT stopword removal
    #   (build_vocab does not strip stopwords). So this A/B only tests "remove stopwords at inference
    #   time", not the research hypothesis "build/train with vs without stopwords". State this scope
    #   limit explicitly, or also compare a vocab built on the stopword-removed corpus.
    clf_1 = Classifier(
        pos_count= POS_VOCAB,
        neg_count= NEG_VOCAB,
        use_stopwords_retrieval = False,
        stopwords= STOPWORDS_CUSTOM,
        negative_words= STOPWORDS_PROTECTED,
    )

    clf_2 = Classifier(
        pos_count= POS_VOCAB,
        neg_count= NEG_VOCAB,
        use_stopwords_retrieval = True,
        stopwords= STOPWORDS_CUSTOM,
        negative_words= STOPWORDS_PROTECTED,
    )

    # [QA-E5 | MEDIUM] Output paths are bare filenames -> written to the CURRENT WORKING DIRECTORY,
    #   not a fixed location. Run from a different folder and the files scatter; run from repo root
    #   and results_*.csv land at the top level (committed there now). Use scripts/paths.py to write
    #   into a stable results/ dir for reproducibility.
    raw_metrics = evaluate_model(clf_1,TEST_CLEANED)
    df_metrics = pd.DataFrame(list(raw_metrics.items()), columns=['Metric', 'Value'])
    df_metrics.to_csv('results_raw.csv', index=False)

    cleaned_metrics = evaluate_model(clf_2,TEST_CLEANED)
    df_metrics = pd.DataFrame(list(cleaned_metrics.items()), columns=['Metric', 'Value'])
    df_metrics.to_csv('results_cleaned.csv', index=False)

    # [QA-E3 | HIGH] This print + the SƠ ĐỒ below crash on Windows' default cp1252 console with
    #   UnicodeEncodeError ('Ả'). Critically, results_comparison.csv (line below) and the chart
    #   are written AFTER this print, so on the documented env (VS Code/Windows) the script dies
    #   here and TWO of the three required deliverables are never produced. Fix: at top of script do
    #   `sys.stdout.reconfigure(encoding='utf-8')`, or write files BEFORE printing.
    # Bước 3: Tổng hợp và Trực quan hóa
    print("\n=== BẢNG SO SÁNH ===")
    comparison_df = pd.DataFrame({
        'Metric': ['Accuracy', 'Precision', 'Recall', 'F1-Score'],
        'Raw (no stopwords)': [
            raw_metrics['accuracy'],
            raw_metrics['precision'],
            raw_metrics['recall'],
            raw_metrics['f1']
        ],
        'Cleaned (with stopwords)': [
            cleaned_metrics['accuracy'],
            cleaned_metrics['precision'],
            cleaned_metrics['recall'],
            cleaned_metrics['f1']
        ],
        'Delta': [
            cleaned_metrics['accuracy'] - raw_metrics['accuracy'],
            cleaned_metrics['precision'] - raw_metrics['precision'],
            cleaned_metrics['recall'] - raw_metrics['recall'],
            cleaned_metrics['f1'] - raw_metrics['f1']
        ]
    })
    print(comparison_df.to_string(index=False))
    
    # Lưu bảng so sánh
    comparison_df.to_csv('results_comparison.csv', index=False)
    
    # Vẽ biểu đồ cột
    metrics = ['Accuracy', 'F1-Score']
    raw_values = [raw_metrics['accuracy'], raw_metrics['f1']]
    cleaned_values = [cleaned_metrics['accuracy'], cleaned_metrics['f1']]
    x = range(len(metrics))
    width = 0.35
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    bars1 = ax1.bar([i - width/2 for i in x], raw_values, width, label='Raw (no stopwords)', color='steelblue')
    bars2 = ax1.bar([i + width/2 for i in x], cleaned_values, width, label='Cleaned (with stopwords)', color='coral')
    
    ax1.set_ylabel('Score')
    ax1.set_title('So sánh hiệu suất mô hình - Delta giữa hai cấu hình')
    ax1.set_xticks(x)
    ax1.set_xticklabels(metrics)
    ax1.legend(loc='upper left')
    ax1.set_ylim(0, 1)
    
    # Thêm giá trị trên các cột
    for bar in bars1:
        height = bar.get_height()
        ax1.annotate(f'{height:.3f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)
    
    for bar in bars2:
        height = bar.get_height()
        ax1.annotate(f'{height:.3f}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=9)
    
    # Vẽ đường nối các cột để thấy delta
    for i, (raw, cleaned) in enumerate(zip(raw_values, cleaned_values)):
        ax1.plot([i - width/2, i + width/2], [raw, cleaned], 'k--', alpha=0.5)
        delta = cleaned - raw
        color = 'green' if delta >= 0 else 'red'
        ax1.annotate(f'Δ={delta:+.3f}',
                    xy=((i - width/2 + i + width/2) / 2, (raw + cleaned) / 2),
                    xytext=(0, 10),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=10, color=color, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('results_comparison_chart.png', dpi=300, bbox_inches='tight')
    print("\nBiểu đồ đã được lưu vào: results_comparison_chart.png")
    # [QA-E8 | LOW] plt.show() blocks in headless/CI runs (no display) and serves no purpose once
    #   the figure is saved. Guard it or remove for automated reproducibility.
    plt.show()