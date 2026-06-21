"""Unit tests for utils/text_utils.py (Task 5 — vocab building)."""

import pytest

from utils.text_utils import load_words, tokenize


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
        """DV5-01: protected tokens must stay out of custom.txt (Task 3 guarantee)."""
        custom = load_words("data/stopwords/custom.txt")
        protected = load_words("data/stopwords/protected.txt")
        assert protected.isdisjoint(custom)


class TestTokenize:
    def test_returns_list_of_strings(self):
        tokens = tokenize("giảng viên dạy tốt")
        assert isinstance(tokens, list)
        assert all(isinstance(t, str) for t in tokens)

    def test_empty_input(self):
        assert tokenize("") == []

    @pytest.mark.parametrize(
        "text, expected_token",
        [
            ("giảng viên nhiệt tình", "giảng_viên"),
            ("sinh viên học tập", "sinh_viên"),
            ("môn học hay", "môn_học"),
        ],
    )
    def test_compound_words_use_underscore(self, text, expected_token):
        """T5-03 (spec): compound words must use '_' per PyVi tokenize()."""
        tokens = tokenize(text)
        assert expected_token in tokens

    def test_does_not_split_known_compound(self):
        tokens = tokenize("giảng viên dạy nhiệt tình")
        assert "giảng" not in tokens or "viên" not in tokens or "giảng_viên" in tokens
