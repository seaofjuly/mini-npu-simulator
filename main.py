import time
import json


def mac(pattern, filt):
    n = len(pattern)
    total = 0.0
    for i in range(n):
        for j in range(n):
            total += pattern[i][j] * filt[i][j]
    return total


def flatten(matrix):
    flat = []
    for row in matrix:
        for value in row:
            flat.append(value)
    return flat


def mac_flat(pattern_flat, filter_flat):
    total = 0.0
    for k in range(len(pattern_flat)):
        total += pattern_flat[k] * filter_flat[k]
    return total

def measure_mac_ms(pattern, filt, repeat=10):
    mac(pattern, filt)
    total_time = 0.0
    for i in range(repeat):
        start = time.perf_counter()
        mac(pattern, filt)
        end = time.perf_counter()
        total_time += end - start
    return total_time / repeat * 1000


def make_matrix(n):
    matrix = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append(0.0)
        matrix.append(row)
    return matrix


def get_value(matrix, row, col):
    return matrix[row][col]


def set_value(matrix, row, col, value):
    matrix[row][col] = value


def generate_cross(n):
    matrix = make_matrix(n)
    mid = n // 2
    for k in range(n):
        set_value(matrix, mid, k, 1.0)
        set_value(matrix, k, mid, 1.0)
    return matrix


def generate_x(n):
    matrix = make_matrix(n)
    for k in range(n):
        set_value(matrix, k, k, 1.0)
        set_value(matrix, k, n - 1 - k, 1.0)
    return matrix


EPSILON = 1e-9
LABEL_MAP = {"+": "Cross", "cross": "Cross", "x": "X"}


def judge(score_a, score_b, label_a="A", label_b="B"):
    if abs(score_a - score_b) < EPSILON:
        return "UNDECIDED"
    elif score_a > score_b:
        return label_a
    else:
        return label_b


def normalize_label(raw):
    key = raw.strip().lower()
    return LABEL_MAP.get(key)


def read_row(n):
    while True:
        line = input()
        parts = line.split()
        row = []
        try:
            for p in parts:
                row.append(float(p))
            if len(row) == n:
                break
            print(f"입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요.")
        except ValueError:
            print(f"입력 형식 오류: 각 줄에 {n}개의 숫자를 공백으로 구분해 입력하세요.")
    return row


def read_matrix(title, n):
    print(f"{title} ({n}줄 입력, 공백 구분)")
    matrix = []
    for i in range(n):
        row = read_row(n)
        matrix.append(row)
    return matrix


def print_section(title):
    print()
    print("#" + "-" * 39)
    print(f"# {title}")
    print("#" + "-" * 39)


def print_performance_table(sizes):
    print(f"{'크기':<8}{'평균 시간(ms)':>14}{'연산 횟수':>10}")
    print("-" * 36)
    for n in sizes:
        pattern = generate_cross(n)
        ms = measure_mac_ms(pattern, pattern)
        size_text = f"{n}×{n}"
        print(f"{size_text:<8}{ms:>14.4f}{n * n:>10}")


def measure_flat_ms(pattern_flat, filter_flat, repeat=10):
    mac_flat(pattern_flat, filter_flat)
    total_time = 0.0
    for i in range(repeat):
        start = time.perf_counter()
        mac_flat(pattern_flat, filter_flat)
        end = time.perf_counter()
        total_time += end - start
    return total_time / repeat * 1000


def print_compare_table(sizes):
    print(f"{'크기':<8}{'2D(ms)':>10}{'1D(ms)':>10}{'1D/2D':>8}")
    print("-" * 36)
    for n in sizes:
        pattern = generate_cross(n)
        pattern_flat = flatten(pattern)
        ms_2d = measure_mac_ms(pattern, pattern)
        ms_1d = measure_flat_ms(pattern_flat, pattern_flat)
        size_text = f"{n}×{n}"
        print(f"{size_text:<8}{ms_2d:>10.4f}{ms_1d:>10.4f}{ms_1d / ms_2d:>8.2f}")


def select_mode():
    while True:
        print()
        print("[모드 선택]")
        print()
        print("1. 사용자 입력 (3x3)")
        print("2. data.json 분석")
        choice = input("선택: ").strip()
        if choice == "1" or choice == "2":
            return choice
        print("⚠️ 잘못된 입력입니다. 1 또는 2를 입력하세요.")


def run_user_mode():
    print_section("[1] 필터 입력")
    filter_a = read_matrix("필터 A", 3)
    print()
    filter_b = read_matrix("필터 B", 3)

    print()
    print("✓ 필터 저장 완료")
    print("필터 A:", filter_a)
    print("필터 B:", filter_b)

    print_section("[2] 패턴 입력")
    pattern = read_matrix("패턴", 3)
    print("패턴:", pattern)

    print_section("[3] MAC 결과")
    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)
    print("A 점수:", score_a)
    print("B 점수:", score_b)
    time_ms = (measure_mac_ms(pattern, filter_a) + measure_mac_ms(pattern, filter_b)) / 2
    print(f"연산 시간(평균/10회): {time_ms:.4f} ms")
    result = judge(score_a, score_b)
    if result == "UNDECIDED":
        print("판정: 판정 불가 (|A-B| < 1e-9)")
    else:
        print("판정:", result)

    print_section("[4] 성능 분석 (평균/10회)")
    print_performance_table([3])


def check_matrix(matrix, n):
    if len(matrix) != n:
        return f"크기 불일치 (줄 수 {len(matrix)}, 기대 {n})"
    for row in matrix:
        if len(row) != n:
            return f"크기 불일치 (칸 수 {len(row)}, 기대 {n})"
    return None


def fail(reason):
    print(f"FAIL: {reason}")
    return False, reason


def analyze_pattern(key, item, filters):
    print(f"--- {key} ---")

    parts = key.split("_")
    if len(parts) != 3 or parts[0] != "size" or not parts[1].isdigit():
        return fail("키 형식 오류 (size_N_idx 형태가 아님)")
    n = int(parts[1])

    if "input" not in item or "expected" not in item:
        return fail("스키마 오류 (input 또는 expected 누락)")

    expected = normalize_label(item["expected"])
    if expected is None:
        return fail(f"알 수 없는 expected 라벨 '{item['expected']}'")

    size_key = f"size_{n}"
    if size_key not in filters:
        return fail(f"{size_key} 필터가 없음")
    group = filters[size_key]
    if "cross" not in group or "x" not in group:
        return fail(f"{size_key} 필터에 cross 또는 x가 없음")

    problem = check_matrix(item["input"], n)
    if problem is not None:
        return fail(f"패턴 {problem}")

    cross_score = mac(item["input"], group["cross"])
    x_score = mac(item["input"], group["x"])
    result = judge(cross_score, x_score, "Cross", "X")
    print("Cross 점수:", cross_score)
    print("X 점수:", x_score)
    if result == expected:
        print(f"판정: {result} | expected: {expected} | PASS")
        return True, ""
    elif result == "UNDECIDED":
        print(f"판정: {result} | expected: {expected} | FAIL (동점 규칙)")
        return False, "동점(UNDECIDED) 처리 규칙에 따라 FAIL"
    else:
        print(f"판정: {result} | expected: {expected} | FAIL")
        return False, f"판정 {result}이(가) expected {expected}와 다름"


def run_json_mode(path="data.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    filters = data["filters"]
    patterns = data["patterns"]

    print_section("[1] 필터 로드")
    for size_key in filters:
        labels = []
        for raw in filters[size_key]:
            labels.append(normalize_label(raw))
        print(f"✓ {size_key} 필터 로드 완료 ({', '.join(labels)})")

    print_section("[2] 패턴 분석 (라벨 정규화 적용)")
    total = 0
    passed = 0
    failures = []
    for key in patterns:
        total += 1
        ok, reason = analyze_pattern(key, patterns[key], filters)
        if ok:
            passed += 1
        else:
            failures.append((key, reason))

    print_section("[3] 성능 분석 (평균/10회)")
    print_performance_table([3, 5, 13, 25])
    print()
    print("[보너스] 2차원 vs 1차원 배열 비교 (동일 입력, 10회 평균)")
    print_compare_table([3, 5, 13, 25])

    print_section("[4] 결과 요약")
    print(f"총 테스트: {total}개")
    print(f"통과: {passed}개")
    print(f"실패: {len(failures)}개")
    if len(failures) > 0:
        print()
        print("실패 케이스:")
        for name, reason in failures:
                print(f"- {name}: {reason}")


def main():
    print("=== Mini NPU Simulator ===")
    choice = select_mode()
    if choice == "1":
        run_user_mode()
    else:
        run_json_mode()


main()



