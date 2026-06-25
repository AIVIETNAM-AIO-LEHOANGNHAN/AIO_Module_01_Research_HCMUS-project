from utils.text_utils import tokenize, load_words
from scripts.paths import STOPWORDS_CUSTOM, TRAIN_CLEANED, STOPWORDS_PROTECTED, POS_VOCAB, NEG_VOCAB
import json

class Classifier:
    def __init__(self, pos_count, neg_count, use_stopwords_retrieval = False, stopwords = None, negative_words = None):
        self.pos_count = pos_count
        self.neg_count = neg_count
        self.use_stopwords_retrieval = use_stopwords_retrieval
        self.stopwords = stopwords
        self.negative_words = negative_words
        
        with open(self.pos_count, 'r', encoding='utf-8') as file:
            self.pos_vocab = json.load(file)

        with open(self.neg_count, 'r', encoding='utf-8') as file:
            self.neg_vocab = json.load(file)

    def predict(self, text):
        tokens = tokenize(text)
        stopwords = load_words(self.stopwords)
        negative_words = load_words(self.negative_words)
        if self.use_stopwords_retrieval:
            tokens = [token for token in tokens if token not in stopwords]

        score = 0
        negative = 1
        for token in tokens:
            if token in self.pos_vocab.keys():
                score += negative
            
            elif token in self.neg_vocab.keys():
                score -= negative

            if token in negative_words:
                negative = -1
            else:
                negative = 1

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
    print("POS FILE:", POS_VOCAB)
    
