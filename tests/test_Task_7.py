from models.classifier import Classifier
from scripts.paths import (
    POS_VOCAB,
    NEG_VOCAB,
    STOPWORDS_CUSTOM,
    STOPWORDS_PROTECTED,
)

classifier = Classifier(
    pos_count=POS_VOCAB,
    neg_count=NEG_VOCAB,
    use_stopwords_retrieval=False,
    stopwords=STOPWORDS_CUSTOM,
    negative_words=STOPWORDS_PROTECTED,
)

print("Pos vocab:", len(classifier.pos_vocab))
print("Neg vocab:", len(classifier.neg_vocab))
