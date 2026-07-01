"""
Bản sao trung thực của models/classifier.py & utils/text_utils.py trên
origin/main (commit đã được QA review ở Task 7), dùng riêng cho Task 11.

Không sửa models/classifier.py / utils/text_utils.py tại chỗ vì các file đó
đang được app.py và pipeline/run_pipeline.py trên nhánh này dùng với logic
khác (negation-window, intensifier, critique-word, vocab tách exp_a/exp_b).
File này giữ nguyên logic của origin/main để phân tích lỗi đúng với bản mà
nhóm đã cập nhật trên GitHub.
"""
import json

from pyvi import ViTokenizer


def tokenize_main(text):
    """Tokenize giống hệt origin/main: không lowercase, không strip dấu câu/số."""
    if text:
        return ViTokenizer.spacy_tokenize(text)[0]
    return []


def load_words_main(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        print(f"Cảnh báo: Không tìm thấy file stopwords tại '{file_path}'")
        return set()


class MainClassifier:
    """Sao chép nguyên logic Classifier trên origin/main."""

    def __init__(self, pos_count, neg_count, use_stopwords_retrieval=False,
                 stopwords=None, negative_words=None):
        self.pos_count = pos_count
        self.neg_count = neg_count
        self.use_stopwords_retrieval = use_stopwords_retrieval
        self.stopwords = stopwords
        self.negative_words = negative_words

        with open(self.pos_count, "r", encoding="utf-8") as f:
            self.pos_vocab = json.load(f)
        with open(self.neg_count, "r", encoding="utf-8") as f:
            self.neg_vocab = json.load(f)

    def get_score(self, text):
        tokens = tokenize_main(text)
        stopwords = load_words_main(self.stopwords)
        negative_words = load_words_main(self.negative_words)

        if self.use_stopwords_retrieval:
            tokens = [t for t in tokens if t not in stopwords]

        score = 0
        negative = 1
        for token in tokens:
            if token in self.pos_vocab.keys():
                score += negative
            elif token in self.neg_vocab.keys():
                score -= negative

            negative = -1 if token in negative_words else 1

        return score

    def predict(self, text):
        score = self.get_score(text)
        return "Positive" if score > 0 else "Negative"

    def predict_batch(self, texts):
        return [self.predict(t) for t in texts]
