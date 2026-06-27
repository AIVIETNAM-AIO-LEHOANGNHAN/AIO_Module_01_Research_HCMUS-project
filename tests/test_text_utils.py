import json

def check_vocabulary_overlap(pos_path, neg_path):
   
    with open(pos_path, 'r', encoding='utf-8') as f:
        pos_vocab = json.load(f)
    with open(neg_path, 'r', encoding='utf-8') as f:
        neg_vocab = json.load(f)
    
    pos_set = set(pos_vocab.keys())
    neg_set = set(neg_vocab.keys())
    
    overlap = pos_set.intersection(neg_set)
    
    print(f"--- Phân tích trùng lặp từ vựng ---")
    print(f"Số lượng từ Pos: {len(pos_set)}")
    print(f"Số lượng từ Neg: {len(neg_set)}")
    print(f"Số lượng từ trùng nhau: {len(overlap)}")
    
    return overlap

def analyze_and_export_overlap(pos_path, neg_path, output_file='overlap_words.txt'):
    # Load dữ liệu
    with open(pos_path, 'r', encoding='utf-8') as f:
        pos_vocab = json.load(f)
    with open(neg_path, 'r', encoding='utf-8') as f:
        neg_vocab = json.load(f)
    
    pos_set = set(pos_vocab.keys())
    neg_set = set(neg_vocab.keys())
    
    # Tìm giao điểm
    overlap = pos_set.intersection(neg_set)
    
    # In ra thông tin tổng quát
    print(f"--- Phân tích trùng lặp từ vựng ---")
    print(f"Số lượng từ Pos: {len(pos_set)}")
    print(f"Số lượng từ Neg: {len(neg_set)}")
    print(f"Số lượng từ trùng nhau: {len(overlap)}")
    
    # Xuất ra file
    with open(output_file, 'w', encoding='utf-8') as f:
        for word in sorted(list(overlap)):
            f.write(f"{word}\n")
    print(f"Danh sách từ trùng đã được xuất ra: '{output_file}'")
    
    return overlap


pos_p = 'models/vocab/exp_b/pos_vocab.json'
neg_p = 'models/vocab/exp_b/neg_vocab.json'

analyze_and_export_overlap(pos_p, neg_p, output_file='docs/overlap_words.txt')