import json
import re

from scripts.paths import (
    POS_VOCAB, NEG_VOCAB, STOPWORDS_CUSTOM,
    NEGATORS, INTENSIFIERS, CRITIQUE_WORDS
)

from utils.text_utils import preprocess, tokenize, load_words


class Classifier:
    """
    Rule-based sentiment classifier for Vietnamese text.
    Uses:
    - Positive / Negative vocabulary
    - Negation handling
    - Intensifiers (rất, hơi, quá)
    - Critique words (nên, cần, thiếu, ít)
    """

    def __init__(self,
                 pos_vocab_path=POS_VOCAB,
                 neg_vocab_path=NEG_VOCAB,
                 stopwords_path=STOPWORDS_CUSTOM,
                 negators_path=NEGATORS,
                 intensifiers_path=INTENSIFIERS,
                 critique_words_path=CRITIQUE_WORDS,
                 remove_stopwords=False):

        # -------------------------
        # 1. LOAD VOCABULARY
        # -------------------------
        self.pos_vocab = self._load_vocab(pos_vocab_path)
        self.neg_vocab = self._load_vocab(neg_vocab_path)

        # -------------------------
        # 2. LOAD LEXICONS
        # -------------------------
        self.stopwords = load_words(stopwords_path)
        self.negators = load_words(negators_path)
        self.intensifiers = load_words(intensifiers_path)
        self.critique_words = load_words(critique_words_path)

        self.remove_stopwords = remove_stopwords

        # -------------------------
        # 3. RULE WEIGHTS
        # -------------------------
        self.intensity_weight ={
            "cực_kỳ": 2.0,
            "siêu": 2.0,
            "vô_cùng": 2.0,
            "hết_sức": 2.0,
            "cực": 2.0,
            "rất": 1.5,
            "quá": 1.5,
            "thực_sự": 1.5,
            "khá": 0.8,
            "tương_đối": 0.8,
            "hơi": 0.5,
            "có_vẻ": 0.5,
            "một_chút": 0.5,
            "dường_như": 0.5
        }

        self.critique_weight = {
            "thiếu": -1,
            "ít": -1,
            "nên": -0.5,
            "cần": -0.5,
            "đề_nghị": -0.5,
            "cải_thiện": -0.5,
            "bổ_sung": -0.5,
            "xem_xét": -0.5,
            "thay_đổi": -0.5,
            "mong": -0.2,
            "muốn": -0.2
        }
        

    # ======================================================
    # LOAD VOCAB HELPER
    # ======================================================
    def _load_vocab(self, path):
        with open(path, "r", encoding="utf-8") as f:
            return set(json.load(f).keys())

    # ======================================================
    # MAIN SCORING FUNCTION (CORE LOGIC)
    # ======================================================
    def _score_tokens(self, tokens):
        """
        Tính điểm cảm xúc cho 1 đoạn token
        """

        score = 0.0
        negation_window = 0
        intensity = 1.0

        for token in tokens:

            # -------------------------
            # 1. NEGATION (phủ định)
            # -------------------------
            if token in self.negators:
                negation_window = 2
                continue

            # -------------------------
            # 2. INTENSIFIER
            # -------------------------
            if token in self.intensifiers:
                intensity *= self.intensity_weight.get(token, 1.0)
                continue

            # -------------------------
            # 3. CRITIQUE WORDS
            # -------------------------
            if token in self.critique_words:
                score += self.critique_weight.get(token, 0)
                intensity = 1.0
                continue

            # -------------------------
            # 4. SENTIMENT WORDS
            # -------------------------
            value = 0

            if token in self.pos_vocab:
                value = 1
            elif token in self.neg_vocab:
                value = -1

            # apply negation
            if value != 0:

                if negation_window > 0:
                    value *= -1

                score += value * intensity

                # reset intensity after use
                intensity = 1.0

            # reduce negation scope
            if negation_window > 0:
                negation_window -= 1

        return score

    # ======================================================
    # TEXT LEVEL SCORING
    # ======================================================
    def get_score(self, text):
        """
        Trả về tổng điểm sentiment của cả câu
        """

        # 1. clean text
        text = preprocess(text)

        # 2. split câu
        segments = re.split(r"[,.!?;]", text)

        total_score = 0.0

        for segment in segments:

            tokens = tokenize(segment.strip())

            # optional stopwords removal
            if self.remove_stopwords:
                tokens = [
                    t for t in tokens
                    if t not in self.stopwords
                ]

            # score từng đoạn
            total_score += self._score_tokens(tokens)

        return total_score

    # ======================================================
    # PREDICTION
    # ======================================================
    def predict(self, text):
        score = self.get_score(text)
        return "Positive" if score > 0 else "Negative"

    def predict_batch(self, texts):
        return [self.predict(t) for t in texts]


# ======================================================
# TEST FUNCTION
# ======================================================
def test():
    model = Classifier(remove_stopwords=False)

    samples = [
        "dạy rất hay",
        "dở",
        "không tốt",
        "rất tệ",
        "nên cải thiện slide",
        "giảng viên rất nhiệt tình"
    ]

    print("\n--- SENTIMENT TEST ---")
    for text in samples:
        print(f"{text} -> {model.predict(text)}")


if __name__ == "__main__":
    test()