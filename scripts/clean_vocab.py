import json
import os

def load_rules(file_path):
    """Nạp các từ luật từ file .txt"""
    if not os.path.exists(file_path):
        print(f"Cảnh báo: Không tìm thấy file {file_path}")
        return set()
    with open(file_path, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f if line.strip())

def clean_vocab(vocab_path, rules_set):
    """Loại bỏ các từ nằm trong rules_set khỏi vocab_path"""
    if not os.path.exists(vocab_path):
        print(f"Lỗi: Không tìm thấy file {vocab_path}")
        return

    with open(vocab_path, 'r', encoding='utf-8') as f:
        vocab = json.load(f)
    
    # Lọc từ: chỉ giữ lại những từ KHÔNG có trong tập luật
    cleaned_vocab = {word: score for word, score in vocab.items() if word not in rules_set}
    
    # Ghi lại file sau khi đã lọc
    with open(vocab_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_vocab, f, ensure_ascii=False, indent=4)
    
    print(f"Đã dọn dẹp: {vocab_path} | Giảm từ {len(vocab)} xuống {len(cleaned_vocab)} từ.")

# --- CẤU HÌNH ĐƯỜNG DẪN ---
# Nạp tất cả các bộ luật của bạn
all_rules = (
    load_rules('data/lexicon/negators.txt') | 
    load_rules('data/lexicon/intensifiers.txt') | 
    load_rules('data/lexicon/critique_words.txt')
)

# Danh sách các file cần dọn dẹp (bao gồm cả exp_a và exp_b)
files_to_clean = [
    'models/vocab/exp_a/pos_vocab.json',
    'models/vocab/exp_a/neg_vocab.json',
    'models/vocab/exp_b/pos_vocab.json',
    'models/vocab/exp_b/neg_vocab.json'
]

if __name__ == "__main__":
    print(f"Bắt đầu dọn dẹp với {len(all_rules)} từ luật...")
    for path in files_to_clean:
        clean_vocab(path, all_rules)
    print("Hoàn tất dọn dẹp dữ liệu!")