# Research Context for Task 3: Vietnamese Stopwords

Project topic: Analyze the impact of stopword removal on Vietnamese text classification.

## Dataset

- UIT-VSFC Vietnamese Students' Feedback Corpus.
- Binary sentiment: `1` = Positive, `0` = Negative.
- Neutral samples are removed.

## Task 3 goal

- Build a customized Vietnamese stopwords list for sentiment classification.
- Use `data/stopwords/raw.txt` from [stopwords/vietnamese-stopwords](https://github.com/stopwords/vietnamese-stopwords) as baseline.
- Create `data/stopwords/custom.txt` as the project stopwords list.
- Create `data/stopwords/protected.txt` for sentiment-critical words.

## Important rule

Do not remove negation or sentiment-bearing words:

`không`, `chưa`, `chẳng`, `chả`, `đừng`, `rất`, `quá`, `hơi`, `tốt`, `tệ`, `kém`, `hay`, `dở`, `nên`, `cần`.

## Research rationale

1. **Is word segmentation necessary for Vietnamese sentiment classification?** — `docs/research/2301.00418_is_word_segmentation_necessary_for_vietnamese_sentiment_classification.pdf`
2. **Vietnamese Sentiment Analysis: An Overview and Comparative Study of Fine-tuning Pretrained Language Models** — `docs/research/vietnamese_sentiment_analysis_overview_comparative_study_finetuning_pretrained_language_models.pdf`
3. **Stopword baseline** — [vietnamese-stopwords](https://github.com/stopwords/vietnamese-stopwords)
4. **Stopword removal is experimental** — must not be assumed to always improve results.

## Experiment variants

| Variant | Description |
|---------|-------------|
| Baseline | No stopword removal |
| Raw stopwords | Remove from `data/stopwords/raw.txt` |
| Custom stopwords | Remove from `data/stopwords/custom.txt` |

## Project layout

```text
data/
├── train/
│   ├── raw.csv
│   └── cleaned.csv
├── test/
│   ├── raw.csv
│   └── cleaned.csv
├── stopwords/
│   ├── raw.txt
│   ├── custom.txt
│   └── protected.txt
├── qa_sample_50.csv
└── README_DATA.md

scripts/
├── paths.py
├── task1_prepare_data.py
├── task2_preprocess_text.py
└── task3_build_stopwords.py

docs/
├── research_context.md
├── Stopwords_Rationale.md
└── research/
    ├── 2301.00418_is_word_segmentation_necessary_for_vietnamese_sentiment_classification.pdf
    └── vietnamese_sentiment_analysis_overview_comparative_study_finetuning_pretrained_language_models.pdf
```
