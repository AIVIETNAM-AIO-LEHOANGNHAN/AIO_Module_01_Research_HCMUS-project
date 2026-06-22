from models.classifier import Classifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from scripts.paths import STOPWORDS_CUSTOM, TEST_CLEANED, STOPWORDS_PROTECTED, POS_VOCAB, NEG_VOCAB
import pandas as pd
import matplotlib.pyplot as plt

def evaluate_model(classifier, test_data):
    df = pd.read_csv(test_data)
    text_list = df['text'].tolist()
    y_pred = classifier.predict_batch(text_list)
    y_true = ['Positive' if str(label).strip() == '1' else 'Negative' for label in df['label'].tolist()]

    return {
        'accuracy': round(accuracy_score(y_true, y_pred), 3),
        'precision': round(precision_score(y_true, y_pred, average='weighted', labels=['Positive', 'Negative']), 3),
        'recall': round(recall_score(y_true, y_pred, average='weighted', labels=['Positive', 'Negative']), 3),
        'f1': round(f1_score(y_true, y_pred, average='weighted', labels=['Positive', 'Negative']), 3),
    }

# Test
if __name__ == "__main__":
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

    raw_metrics = evaluate_model(clf_1,TEST_CLEANED)
    df_metrics = pd.DataFrame(list(raw_metrics.items()), columns=['Metric', 'Value'])
    df_metrics.to_csv('results_raw.csv', index=False)

    cleaned_metrics = evaluate_model(clf_2,TEST_CLEANED)
    df_metrics = pd.DataFrame(list(cleaned_metrics.items()), columns=['Metric', 'Value'])
    df_metrics.to_csv('results_cleaned.csv', index=False)

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
    plt.show()