import json

# 1. Hàm load dữ liệu từ các file của bạn
def load_data(file_path, is_json=False):
    if is_json:
        with open(file_path, 'r', encoding='utf-8') as f:
            return set(json.load(f).keys()) # Lấy danh sách từ (keys)
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            return set(line.strip() for line in f if line.strip())

# 2. Định nghĩa đường dẫn tới các file
# Bạn hãy điều chỉnh đường dẫn cho khớp với thư mục thực tế của bạn
vocab_pos = load_data('models/vocab/exp_b/pos_vocab.json', is_json=True)
vocab_neg = load_data('models/vocab/exp_b/neg_vocab.json', is_json=True)
negators = load_data('data/lexicon/negators.txt')
intensifiers = load_data('data/lexicon/intensifiers.txt')
critique = load_data('data/lexicon/critique_words.txt')

# 3. Kiểm tra trùng lặp
all_rules = negators.union(intensifiers, critique)
overlap_pos = vocab_pos.intersection(all_rules)
overlap_neg = vocab_neg.intersection(all_rules)

# 4. Xuất kết quả
print("--- CÁC TỪ BỊ TRÙNG LẶP ---")
print(f"Trùng với pos_vocab: {overlap_pos}")
print(f"Trùng với neg_vocab: {overlap_neg}")

if not overlap_pos and not overlap_neg:
    print("Tuyệt vời! Không có sự trùng lặp dữ liệu.")
else:
    print("\nLời khuyên: Hãy xóa các từ này khỏi file pos_vocab/neg_vocab để tránh nhiễu.")
