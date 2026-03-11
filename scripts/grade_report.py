import json
import sys

WEIGHTS = {
    "test_split_vertically": 10,
    "test_split_horizontally": 10,
    "test_split_and_merge_vertically": 10,
    "test_split_and_merge_horizontally": 10,
    "test_rotate_array": 10,
    "test_rotate_array_empty": 5,
    "test_create_array_int_cast": 10,
    "test_create_array_float": 10,
    "test_evaluate_basic_ops": 10,
    "test_evaluate_unary_ops": 10,
    "test_evaluate_errors": 5,
}

MAX_POINTS = sum(WEIGHTS.values())


def main() -> int:
    try:
        with open("report.json", "r", encoding="utf-8") as f:
            report = json.load(f)
    except FileNotFoundError:
        print("report.json not found")
        return 1

    tests = report.get("tests", [])
    earned = 0

    seen = set()

    for test in tests:
        nodeid = test.get("nodeid", "")
        outcome = test.get("outcome", "")
        test_name = nodeid.split("::")[-1]

        if test_name in WEIGHTS:
            seen.add(test_name)
            if outcome == "passed":
                earned += WEIGHTS[test_name]

    print("Test results:")
    for name, points in WEIGHTS.items():
        status = "PASSED" if name in seen and any(
            t.get("nodeid", "").endswith(name) and t.get("outcome") == "passed"
            for t in tests
        ) else "FAILED"
        earned_points = points if status == "PASSED" else 0
        print(f"- {name}: {status} ({earned_points}/{points})")

    print(f"\nTotal: {earned}/{MAX_POINTS}")
    print(f"::notice title=Points::{earned}/{MAX_POINTS}")

    if earned < MAX_POINTS:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
