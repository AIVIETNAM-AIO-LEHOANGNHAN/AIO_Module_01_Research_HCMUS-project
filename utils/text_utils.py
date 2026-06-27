from pyvi import ViTokenizer
import regex as re


def tokenize(text):
    """
    Tokenize sử dụng PyVi
    """
    if not text:
        return []

    return ViTokenizer.tokenize(text).split()


def load_words(file_path):
    """
    Đọc file txt (mỗi dòng 1 từ)
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return set(
                line.strip()
                for line in f
                if line.strip()
            )

    except FileNotFoundError:

        print(
            f"Không tìm thấy file: {file_path}"
        )

        return set()


def preprocess(text):
    """
    Tiền xử lý văn bản trước khi tokenize
    """

    text = str(text).lower()

    # bỏ dấu câu và số
    text = re.sub(r'[\p{P}\p{N}]', ' ', text)

    # chuẩn hóa khoảng trắng
    text = re.sub(r'\s+', ' ', text)

    return text.strip()
