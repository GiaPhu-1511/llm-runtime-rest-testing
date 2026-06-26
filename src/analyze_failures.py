import csv
import json
from pathlib import Path

BASELINE_RESULTS = Path("outputs/baseline/execution_results.json")
FEEDBACK_RESULTS = Path("outputs/feedback/execution_results.json")
REFINED_TESTS = Path("outputs/feedback/refined_tests.json")
OUTPUT_FILE = Path("outputs/failure_analysis.csv")

FIELDNAMES = [
    "operation_uid",
    "baseline_expected_status",
    "baseline_actual_status",
    "feedback_expected_status",
    "feedback_actual_status",
    "feedback_success",
    "test_intent",
    "response_body_preview",
    "failure_reason",
]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def by_operation_uid(items):
    return {
        item["operation_uid"]: item
        for item in items
    }


def get_test_intent(refined_item):
    if not refined_item:
        return ""

    refined_test = refined_item.get("refined_test") or {}
    return refined_test.get("test_intent", "")


def failure_reason(result):
    if result.get("success"):
        return ""

    actual_status = result.get("actual_status")
    expected_status = result.get("expected_status")
    response_body = result.get("response_body_preview") or ""
    error = result.get("error") or ""
    details = f"{response_body} {error}".lower()

    if actual_status == 401:
        return "Unauthorized (401)"

    if actual_status == 403:
        return "Forbidden (403)"

    if actual_status == 404 or "not found" in details or "invalid path" in details:
        return "Invalid path"

    if expected_status != actual_status:
        return "Wrong expected status"

    return "Other"


def build_rows(baseline_results, feedback_results, refined_tests):
    baseline_by_uid = by_operation_uid(baseline_results)
    refined_by_uid = by_operation_uid(refined_tests)
    rows = []

    for feedback in feedback_results:
        uid = feedback["operation_uid"]
        baseline = baseline_by_uid.get(uid, {})
        refined = refined_by_uid.get(uid)

        rows.append(
            {
                "operation_uid": uid,
                "baseline_expected_status": baseline.get("expected_status"),
                "baseline_actual_status": baseline.get("actual_status"),
                "feedback_expected_status": feedback.get("expected_status"),
                "feedback_actual_status": feedback.get("actual_status"),
                "feedback_success": feedback.get("success"),
                "test_intent": get_test_intent(refined),
                "response_body_preview": feedback.get("response_body_preview"),
                "failure_reason": failure_reason(feedback),
            }
        )

    return rows


def write_csv(rows):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def print_summary(baseline_results, feedback_results):
    baseline_by_uid = by_operation_uid(baseline_results)

    total_improved = 0
    total_unchanged = 0
    total_remaining_failures = 0

    for feedback in feedback_results:
        uid = feedback["operation_uid"]
        baseline = baseline_by_uid.get(uid, {})
        baseline_success = bool(baseline.get("success"))
        feedback_success = bool(feedback.get("success"))

        if not baseline_success and feedback_success:
            total_improved += 1

        if baseline_success == feedback_success:
            total_unchanged += 1

        if not feedback_success:
            total_remaining_failures += 1

    print(f"total improved: {total_improved}")
    print(f"total unchanged: {total_unchanged}")
    print(f"total remaining failures: {total_remaining_failures}")
    print(OUTPUT_FILE)


def main():
    baseline_results = load_json(BASELINE_RESULTS)
    feedback_results = load_json(FEEDBACK_RESULTS)
    refined_tests = load_json(REFINED_TESTS)

    rows = build_rows(baseline_results, feedback_results, refined_tests)
    write_csv(rows)
    print_summary(baseline_results, feedback_results)


if __name__ == "__main__":
    main()
