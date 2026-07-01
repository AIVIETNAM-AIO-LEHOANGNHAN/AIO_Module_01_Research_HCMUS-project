"""
Task 11 — Sinh 2000 câu KHÓ (hard cases) để stress-test classifier trong
pipeline/run_pipeline.py.

Mỗi câu được sinh từ template nên nhãn thật (label) biết chắc theo cấu trúc,
nhưng câu được thiết kế để "bẫy" mô hình rule-based theo đúng các pattern lỗi
đã phát hiện ở error_analysis_report.md:

  - Phủ định đảo chiều (không + từ tích cực -> Negative)
  - Phủ định kép (không hề + từ tiêu cực -> Positive)
  - Câu nhượng bộ "tuy ... nhưng ..." (nghĩa nằm ở vế sau "nhưng")
  - Câu phê bình dùng từ góp ý (nên/cần/bổ sung -> Negative)
  - Bẫy từ trung tính (câu chê nhưng chứa từ học thuật trung tính)

Đầu ra: data/test/hard_cases_2000.csv  (cột: text,label)
Nhãn: 0 = Negative, 1 = Positive. Cân bằng 1000 / 1000.
"""
import csv
import random
from pathlib import Path

from scripts.paths import DATA_DIR

SEED = 42
TARGET_PER_TEMPLATE = 200  # 5 template neg + 5 template pos = 2000 câu

OUT_PATH = DATA_DIR / "test" / "hard_cases_2000.csv"

# ---------------------------------------------------------------------------
# Từ vựng thành phần
# ---------------------------------------------------------------------------
SUBJECTS = [
    "thầy", "cô", "giảng viên", "bài giảng", "môn học này",
    "cách giảng dạy", "nội dung môn học", "phần lý thuyết",
    "slide bài giảng", "giáo trình", "phương pháp dạy", "cách truyền đạt",
]

SUBJECTS_PERSON = ["thầy", "cô", "giảng viên"]

POS_WORDS = [
    "hay", "dễ hiểu", "hấp dẫn", "nhiệt tình", "tận tâm", "cuốn hút",
    "rõ ràng", "sinh động", "bổ ích", "hữu ích", "thú vị", "chi tiết",
    "tâm huyết", "dễ tiếp thu",
]

NEG_WORDS = [
    "chán", "khó hiểu", "nhàm chán", "tệ", "dở", "sơ sài", "lộn xộn",
    "mơ hồ", "hời hợt", "rời rạc", "khô khan", "lan man", "khó theo dõi",
    "buồn ngủ",
]

INTENSIFIERS = ["rất", "quá", "cực kỳ", "khá", "hơi", "vô cùng"]

NEGATORS = ["không", "chưa", "chẳng", "không hề"]

CRITIQUE_OPEN = ["nên", "cần"]
IMPROVE_PHRASES = [
    "bổ sung thêm ví dụ minh họa",
    "cải thiện cách trình bày",
    "cập nhật lại giáo trình",
    "thêm nhiều bài tập thực hành",
    "giảng chậm và kỹ hơn",
    "tương tác với sinh viên nhiều hơn",
    "sắp xếp nội dung logic hơn",
    "đầu tư hơn cho phần thực hành",
]

NEUTRAL_ISSUE = [
    "còn sơ sài và thiếu chiều sâu",
    "chưa bám sát thực tế",
    "còn nặng lý thuyết",
    "thiếu tính ứng dụng",
    "chưa được đầu tư đúng mức",
    "còn nhiều chỗ chưa hợp lý",
    "chưa tạo được hứng thú",
    "còn khá dàn trải",
]

# opener để tăng số biến thể (giữ nghĩa nguyên vẹn)
OPENERS = ["", "nhìn chung", "nói chung", "thật sự", "theo em", "nói thật"]

POS_TAIL = [
    "rất đáng để học",
    "em học được nhiều điều",
    "khiến em thêm yêu môn học",
    "tiết học trôi qua rất nhanh",
    "em mong có thêm nhiều buổi như vậy",
    "thực sự xứng đáng thời gian bỏ ra",
]


def cap(s):
    return s[0].upper() + s[1:] if s else s


def build_negative(rng):
    """5 template cho câu Negative (label = 0)."""
    templates = []

    # N1 — phủ định từ tích cực: "thầy dạy không hay"
    def n1():
        subj = rng.choice(SUBJECTS_PERSON)
        neg = rng.choice(["không", "chẳng"])
        pos = rng.choice(POS_WORDS)
        verb = rng.choice(["dạy", "giảng", "truyền đạt"])
        return f"{subj} {verb} {neg} {pos} ."

    # N2 — nhượng bộ pos->neg: "tuy nhiệt tình nhưng dạy rất khó hiểu"
    def n2():
        pos = rng.choice(POS_WORDS)
        intens = rng.choice(INTENSIFIERS)
        neg = rng.choice(NEG_WORDS)
        return f"tuy {pos} nhưng dạy {intens} {neg} ."

    # N3 — câu góp ý/phê bình: "cách dạy nên cải thiện cách trình bày"
    def n3():
        opener = rng.choice(OPENERS)
        subj = rng.choice(SUBJECTS)
        crit = rng.choice(CRITIQUE_OPEN)
        imp = rng.choice(IMPROVE_PHRASES)
        head = f"{opener} {subj}".strip()
        return f"{head} {crit} {imp} ."

    # N4 — chê thẳng có mức độ: "bài giảng quá nhàm chán"
    def n4():
        subj = rng.choice(SUBJECTS)
        intens = rng.choice(INTENSIFIERS)
        neg = rng.choice(NEG_WORDS)
        return f"{subj} {intens} {neg} ."

    # N5 — bẫy từ trung tính: "nội dung môn học còn sơ sài và thiếu chiều sâu"
    def n5():
        opener = rng.choice(OPENERS)
        subj = rng.choice(SUBJECTS)
        issue = rng.choice(NEUTRAL_ISSUE)
        head = f"{opener} {subj}".strip()
        return f"{head} {issue} ."

    for gen in (n1, n2, n3, n4, n5):
        seen = set()
        made = 0
        attempts = 0
        while made < TARGET_PER_TEMPLATE and attempts < TARGET_PER_TEMPLATE * 60:
            attempts += 1
            sent = cap(gen())
            if sent not in seen:
                seen.add(sent)
                templates.append((sent, 0))
                made += 1
    return templates


def build_positive(rng):
    """5 template cho câu Positive (label = 1)."""
    templates = []

    # P1 — phủ định từ tiêu cực: "bài giảng không hề nhàm chán"
    def p1():
        subj = rng.choice(SUBJECTS)
        neg = rng.choice(["không hề", "chẳng hề", "không"])
        negw = rng.choice(NEG_WORDS)
        tail = rng.choice(["", "chút nào", "một chút nào"])
        base = f"{subj} {neg} {negw}"
        return (f"{base} {tail} .").replace("  ", " ")

    # P2 — nhượng bộ neg->pos: "tuy hơi khó nhưng rất bổ ích"
    def p2():
        neg = rng.choice(NEG_WORDS)
        intens = rng.choice(INTENSIFIERS)
        pos = rng.choice(POS_WORDS)
        return f"tuy hơi {neg} nhưng {intens} {pos} ."

    # P3 — khen thẳng có mức độ: "thầy giảng cực kỳ dễ hiểu"
    def p3():
        subj = rng.choice(SUBJECTS_PERSON)
        verb = rng.choice(["giảng", "dạy", "truyền đạt"])
        intens = rng.choice(INTENSIFIERS)
        pos = rng.choice(POS_WORDS)
        return f"{subj} {verb} {intens} {pos} ."

    # P4 — khen kèm đuôi tích cực: "bài giảng rất hấp dẫn, em học được nhiều điều"
    def p4():
        subj = rng.choice(SUBJECTS)
        intens = rng.choice(["rất", "cực kỳ", "vô cùng"])
        pos = rng.choice(POS_WORDS)
        tail = rng.choice(POS_TAIL)
        return f"{subj} {intens} {pos} , {tail} ."

    # P5 — khen nhẹ: "nhìn chung cách truyền đạt khá cuốn hút"
    def p5():
        opener = rng.choice(OPENERS)
        subj = rng.choice(SUBJECTS)
        deg = rng.choice(["khá", "tương đối", "nhìn chung là", "thật sự"])
        pos = rng.choice(POS_WORDS)
        head = f"{opener} {subj}".strip()
        return f"{head} {deg} {pos} ."

    for gen in (p1, p2, p3, p4, p5):
        seen = set()
        made = 0
        attempts = 0
        while made < TARGET_PER_TEMPLATE and attempts < TARGET_PER_TEMPLATE * 60:
            attempts += 1
            sent = cap(gen())
            if sent not in seen:
                seen.add(sent)
                templates.append((sent, 1))
                made += 1
    return templates


def main():
    rng = random.Random(SEED)

    rows = build_negative(rng) + build_positive(rng)
    rng.shuffle(rows)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "label"])
        writer.writerows(rows)

    n_pos = sum(1 for _, y in rows if y == 1)
    n_neg = sum(1 for _, y in rows if y == 0)
    print(f"Đã sinh {len(rows)} câu -> {OUT_PATH}")
    print(f"  Positive (1): {n_pos}")
    print(f"  Negative (0): {n_neg}")


if __name__ == "__main__":
    main()
