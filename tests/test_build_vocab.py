"""Unit tests for models/build_vocab.py (Task 5 — vocab building)."""

import json
from collections import Counter
from pathlib import Path

import pandas as pd
import pytest

from models.build_vocab import build_vocab
from utils.text_utils import load_words


@pytest.fixture
def sample_csv(tmp_path):
    path = tmp_path / "train.csv"
    df = pd.DataFrame(
        {
            "text": [
                "giảng viên dạy rất tốt",
                "giảng viên dạy rất tốt",
                "giảng viên dạy rất tốt",
                "giảng viên dạy rất tốt",
                "giảng viên dạy rất tốt",
                "phòng học kém chất lượng",
                "phòng học kém chất lượng",
                "phòng học kém chất lượng",
                "phòng học kém chất lượng",
                "phòng học kém chất lượng",
            ],
            "label": [1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
        }
    )
    df.to_csv(path, index=False, encoding="utf-8")
    return path


class TestBuildVocab:
    def test_build_vocab_success_and_outputs(self, tmp_path):
        # tạo dữ liệu giả
        csv_path = tmp_path / "train.csv"
        csv_path.write_text(
            "text,label\n"
            "giảng viên dạy tốt,1\n"
            "phòng học rất kém,0\n"
            "giảng viên rất tốt,1\n"
            "phòng học kém chất lượng,0\n",
            encoding="utf-8"
        )
        # ACT
        result = build_vocab(str(csv_path))

        # ASSERT: function chạy OK
        assert result is True

        vocab_dir = tmp_path / "vocab"

        pos_file = vocab_dir / "pos_vocab.json"
        neg_file = vocab_dir / "neg_vocab.json"

        # file phải tồn tại
        assert pos_file.exists()
        assert neg_file.exists()
        
        # ASSERT: nội dung đúng
        pos_vocab = json.loads(pos_file.read_text(encoding="utf-8"))
        neg_vocab = json.loads(neg_file.read_text(encoding="utf-8"))

        # phải có dữ liệu
        assert len(pos_vocab) > 0
        assert len(neg_vocab) > 0

        # kiểm tra logic sentiment
        assert any("tốt" in k for k in pos_vocab.keys())
        assert any("kém" in k for k in neg_vocab.keys())

    
    def test_sentiment_words_preserved_in_vocab(self, sample_csv, monkeypatch, tmp_path):
        """Protected/sentiment tokens (not in custom.txt) must appear in counters."""
        monkeypatch.setattr(
            "models.build_vocab.os.path.dirname",
            lambda _: str(tmp_path),
        )
        monkeypatch.setattr(
            "models.build_vocab.load_stopwords",
            lambda _: load_words("data/stopwords/custom.txt"),
        )
        build_vocab(str(sample_csv))
        pos = json.loads((tmp_path / "vocab" / "pos_vocab.json").read_text(encoding="utf-8"))
        neg = json.loads((tmp_path / "vocab" / "neg_vocab.json").read_text(encoding="utf-8"))
        assert pos.get("rất", 0) >= 5
        assert pos.get("tốt", 0) >= 5
        assert neg.get("kém", 0) >= 5

    def test_label_routing(self, sample_csv, monkeypatch, tmp_path):
        monkeypatch.setattr(
            "models.build_vocab.os.path.dirname",
            lambda _: str(tmp_path),
        )
        monkeypatch.setattr(
            "models.build_vocab.load_stopwords",
            lambda _: set(),
        )
        build_vocab(str(sample_csv))
        pos = json.loads((tmp_path / "vocab" / "pos_vocab.json").read_text(encoding="utf-8"))
        neg = json.loads((tmp_path / "vocab" / "neg_vocab.json").read_text(encoding="utf-8"))
        assert sum(pos.values()) > 0
        assert sum(neg.values()) > 0
        assert "tốt" in pos
        assert "kém" in neg


class TestVocabArtifacts:
    """Validation against committed vocab files on full train set."""

    @pytest.fixture
    def pos_vocab(self):
        path = Path("models/vocab/pos_vocab.json")
        if not path.exists():
            pytest.skip("pos_vocab.json not generated yet")
        return json.loads(path.read_text(encoding="utf-8"))

    @pytest.fixture
    def neg_vocab(self):
        path = Path("models/vocab/neg_vocab.json")
        if not path.exists():
            pytest.skip("neg_vocab.json not generated yet")
        return json.loads(path.read_text(encoding="utf-8"))

    def test_vocab_files_exist(self):
        assert Path("models/vocab/pos_vocab.json").exists()
        assert Path("models/vocab/neg_vocab.json").exists()

    def test_no_punctuation_tokens(self, pos_vocab, neg_vocab):
        """DV5-04: punctuation should not be counted as vocabulary."""
        punct = {",", ".", "!", "?", ":", ";", "-", "'", '"', "(", ")"}
        assert punct.isdisjoint(pos_vocab.keys())
        assert punct.isdisjoint(neg_vocab.keys())

    def test_compound_words_use_underscore(self, pos_vocab, neg_vocab):
        """DV5-05: multi-word PyVi tokens should use '_', not spaces."""
        all_keys = set(pos_vocab) | set(neg_vocab)
        spaced_compounds = [
            w for w in all_keys if " " in w and "_" not in w and len(w.split()) == 2
        ]
        assert spaced_compounds == []

    def test_min_freq_threshold(self, pos_vocab, neg_vocab, min_freq=5):
        """T5-08 (spec): drop tokens with frequency < min_freq."""
        for vocab in (pos_vocab, neg_vocab):
            low_freq = [w for w, c in vocab.items() if c < min_freq]
            assert low_freq == [], f"Found low-frequency tokens: {low_freq[:10]}"
