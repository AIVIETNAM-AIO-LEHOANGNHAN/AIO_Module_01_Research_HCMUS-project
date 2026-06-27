import pytest
from models.build_vocab import build_vocab

# Fixture giúp tái sử dụng dữ liệu mẫu cho mọi hàm test
@pytest.fixture
def sample_data():
    return [
        {"text": "tuyệt vời tận tâm", "label": 1},
        {"text": "slide tệ chán", "label": 0},
        {"text": "tuyệt vời", "label": 1},
        {"text": "tuyệt vời chán", "label": 0}
    ]

def test_frequency_counting(sample_data):
    # Truyền output_dir="." để thỏa mãn yêu cầu của hàm hiện tại
    pos, neg = build_vocab(sample_data, output_dir=".")
    
    assert pos.get("tuyệt_vời") == 2
    assert neg.get("chán") == 2

def test_label_separation(sample_data):
    pos, neg = build_vocab(sample_data, output_dir=".")
    
    assert "tuyệt_vời" in pos
    assert "tuyệt_vời" not in neg
    assert "tệ" in neg
    assert "tệ" not in pos

def test_empty_input():
    pos, neg = build_vocab([], output_dir=".")
    assert pos == {}
    assert neg == {}

def test_output_format(sample_data):
    pos, neg = build_vocab(sample_data, output_dir=".")
    assert isinstance(pos, dict)
    assert isinstance(neg, dict)

def test_integrity(sample_data):
    pos, neg = build_vocab(sample_data, output_dir=".")
    assert len(pos) + len(neg) > 0