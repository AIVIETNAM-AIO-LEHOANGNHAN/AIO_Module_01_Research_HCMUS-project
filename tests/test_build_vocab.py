"""Unit tests for models/build_vocab.py (Task 5 — vocab building)."""

import json
from pathlib import Path

import pandas as pd
import pytest

from models.build_vocab import build_vocab


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

    def test_build_vocab_success_and_outputs(self, sample_csv, tmp_path):
        # ACT
        result = build_vocab(str(sample_csv))

        # ASSERT return
        assert result is True

        vocab_dir = tmp_path / "vocab"
        pos_file = vocab_dir / "pos_vocab.json"
        neg_file = vocab_dir / "neg_vocab.json"

        # file tồn tại
        assert pos_file.exists()
        assert neg_file.exists()

        # load data
        pos_vocab = json.loads(pos_file.read_text(encoding="utf-8"))
        neg_vocab = json.loads(neg_file.read_text(encoding="utf-8"))

        # không rỗng
        assert len(pos_vocab) > 0
        assert len(neg_vocab) > 0

        # logic sentiment
        assert any("tốt" in k for k in pos_vocab.keys())
        assert any("kém" in k for k in neg_vocab.keys())

    def test_label_routing(self, sample_csv, tmp_path):
        build_vocab(str(sample_csv))

        vocab_dir = tmp_path / "vocab"
        pos_vocab = json.loads((vocab_dir / "pos_vocab.json").read_text(encoding="utf-8"))
        neg_vocab = json.loads((vocab_dir / "neg_vocab.json").read_text(encoding="utf-8"))

        assert sum(pos_vocab.values()) > 0
        assert sum(neg_vocab.values()) > 0

        assert "tốt" in pos_vocab
        assert "kém" in neg_vocab

class TestVocabArtifacts:

    def test_vocab_files_exist(self):
        assert Path("models/vocab/pos_vocab.json").exists()
        assert Path("models/vocab/neg_vocab.json").exists()

    def test_no_punctuation_tokens(self):
        pos_vocab = json.loads(Path("models/vocab/pos_vocab.json").read_text(encoding="utf-8"))
        neg_vocab = json.loads(Path("models/vocab/neg_vocab.json").read_text(encoding="utf-8"))

        punct = {",", ".", "!", "?", ":", ";", "-", "'", '"', "(", ")"}

        assert punct.isdisjoint(pos_vocab.keys())
        assert punct.isdisjoint(neg_vocab.keys())

    def test_compound_words_use_underscore(self):
        pos_vocab = json.loads(Path("models/vocab/pos_vocab.json").read_text(encoding="utf-8"))
        neg_vocab = json.loads(Path("models/vocab/neg_vocab.json").read_text(encoding="utf-8"))

        all_keys = set(pos_vocab) | set(neg_vocab)

        spaced_compounds = [
            w for w in all_keys
            if " " in w and "_" not in w and len(w.split()) == 2
        ]

        assert spaced_compounds == []

    def test_min_freq_threshold(self, min_freq=5):
        pos_vocab = json.loads(Path("models/vocab/pos_vocab.json").read_text(encoding="utf-8"))
        neg_vocab = json.loads(Path("models/vocab/neg_vocab.json").read_text(encoding="utf-8"))

        for vocab in (pos_vocab, neg_vocab):
            low_freq = [w for w, c in vocab.items() if c < min_freq]
            assert low_freq == []
