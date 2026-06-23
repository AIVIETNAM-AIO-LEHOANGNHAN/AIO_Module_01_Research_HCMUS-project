from utils.text_utils import tokenize, load_words
from scripts.paths import STOPWORDS_CUSTOM, TRAIN_CLEANED, STOPWORDS_PROTECTED, POS_VOCAB, NEG_VOCAB
import json

class Classifier:
    # [QA-C1 | MEDIUM] Param `use_stopwords_retrieval` is mis-named: the feature REMOVES
    #   stopwords, not retrieves them. Task 7 spec mandates the name `use_stopwords_removal`.
    #   Rename for spec compliance + readability.
    # [QA-C2 | LOW] `pos_count`/`neg_count` are file PATHS to vocab JSON, not counts. Misleading
    #   names (e.g. `pos_vocab_path`). See also QA-C5 (loaded on every call).
    def __init__(self, pos_count, neg_count, use_stopwords_retrieval = False, stopwords = None, negative_words = None):
        self.pos_count = pos_count
        self.neg_count = neg_count
        self.use_stopwords_retrieval = use_stopwords_retrieval
        self.stopwords = stopwords
        self.negative_words = negative_words

    def predict(self, text):
        tokens = tokenize(text)
        stopwords = load_words(self.stopwords)
        # [QA-C3 | HIGH] If negative_words is None (the constructor default), load_words(None)
        #   calls open(None) -> raises TypeError, which is NOT caught (load_words only catches
        #   FileNotFoundError). So `Classifier(pos, neg).predict("x")` crashes. Either default to
        #   an empty set or guard for None.
        negative_words = load_words(self.negative_words)
        # [QA-C4 | HIGH] train/predict PREPROCESSING MISMATCH: build_vocab.py strips punctuation
        #   and digits (regex \p{P}\p{N}) before tokenizing, but predict() does not. Tokens like
        #   "hay!" or "tốt." never match the vocab keys. Apply the SAME cleaning here.
        if self.use_stopwords_retrieval:
            tokens = [token for token in tokens if token not in stopwords]

        # [QA-C5 | HIGH/PERF] Both vocab files are re-read from disk + JSON-parsed on EVERY
        #   predict() call. predict_batch() of N rows => 2*N disk reads (full test set = 4000 reads).
        #   Load once in __init__ and reuse.
        with open(self.pos_count, 'r', encoding='utf-8') as file:
            pos_vocab = json.load(file)

        with open(self.neg_count, 'r', encoding='utf-8') as file:
            neg_vocab = json.load(file)

        # [QA-C6 | CRITICAL] NEGATION LOGIC IS BROKEN — root cause of the ~48% test-set error rate
        #   (all errors observed are Negative->Positive). Two defects:
        #   (a) `score -= negative`: when `negative == -1` (after a negator), a NEGATIVE-vocab word
        #       contributes +1 instead of -1, flipping sentiment the wrong way.
        #       e.g. "nhưng dở": "nhưng" sets negative=-1, then "dở" does score-=(-1)=+1.
        #   (b) `negative` is reset to 1 after EVERY non-negator token, so negation only ever
        #       affects the single immediately-following token and cannot span ("không rất tệ").
        #   Recommend: apply negator to a forward window of vocab words, and only ever invert
        #   POSITIVE contributions to negative (negation of "tốt" -> negative; do not turn an
        #   already-negative word positive).
        score = 0
        negative = 1
        for token in tokens:
            if token in pos_vocab.keys():
                score += negative

            elif token in neg_vocab.keys():
                score -= negative

            if token in negative_words:
                negative = -1
            else:
                negative = 1

        # [QA-C7 | MEDIUM] Tie/neutral handling: score == 0 silently maps to "Negative", and there
        #   is no "Neutral" class. Empty/unknown/stopword-only inputs all become Negative by
        #   default. This biases metrics and hides genuine neutrals. Document or add a Neutral band.
        if score <= 0:
            result = "Negative"
        else:
            result = "Positive"
        return result

    def predict_batch(self, list_of_texts):
        results = [self.predict(text) for text in list_of_texts]
        return results
    
# Test with predict and predict_batch
if __name__ == "__main__":
    test_classifier = Classifier(
        pos_count= POS_VOCAB,
        neg_count= NEG_VOCAB,
        use_stopwords_retrieval = False,
        stopwords= STOPWORDS_CUSTOM,
        negative_words= STOPWORDS_PROTECTED,
    )
    # Input
    text = "dạy quá chán"
    list_of_text = [
        "dạy rất hay",
        "dở",
        "không khó hiểu",
    ]

    # Test không có từ dừng
    test_classifier.use_stopwords_retrieval = False
    print("Test khi không có từ dừng")
    print(test_classifier.predict(text))
    print(test_classifier.predict_batch(list_of_text))

    # Test có từ dừng
    test_classifier.use_stopwords_retrieval = True
    print("Test khi có từ dừng")
    print(test_classifier.predict(text))
    print(test_classifier.predict_batch(list_of_text))