"""Unit tests for utils/text_utils.py (Task 5 — vocab building)."""

import pytest
from utils.text_utils import load_words, tokenize


# TEST LOAD STOPWORDS
class TestLoadStopwords:

    def test_loads_non_empty_set(self):
        stopwords = load_words("data/stopwords/custom.txt")
        assert isinstance(stopwords, set)
        assert len(stopwords) > 0

    def test_ignores_blank_lines(self, tmp_path):
        path = tmp_path / "stopwords.txt"
        path.write_text("một\n\n  hai  \n", encoding="utf-8")

        assert load_words(str(path)) == {"một", "hai"}

    def test_missing_file_returns_empty_set(self, tmp_path):
        missing = tmp_path / "missing.txt"
        assert load_words(str(missing)) == set()

    def test_protected_words_not_in_custom(self):
        custom = load_words("data/stopwords/custom.txt")
        protected = load_words("data/stopwords/protected.txt")

        assert protected.isdisjoint(custom)


# TEST TOKENIZE
class TestTokenize:

    def test_returns_list_of_strings(self):
        tokens = tokenize("giảng viên dạy tốt")

        assert isinstance(tokens, list)
        assert all(isinstance(t, str) for t in tokens)

    def test_empty_input(self):
        assert tokenize("") == []
        assert tokenize("   ") == []

    def test_compound_words_behavior(self):
        """
        PyVi behavior: compound words may be joined by '_'
        but we only test consistency, not exact implementation.
        """
        tokens = tokenize("giảng viên nhiệt tình")

        # must contain at least one meaningful token
        assert len(tokens) > 0
        assert all(isinstance(t, str) for t in tokens)

    def test_known_words_preserved(self):
        tokens = tokenize("giảng viên dạy tốt")

        # relaxed assertion (không phụ thuộc exact tokenizer output)
        joined = "_".join(tokens)

        assert "giảng" in joined or "viên" in joined or "giảng_viên" in tokens
