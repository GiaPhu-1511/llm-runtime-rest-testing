import csv
import json
from pathlib import Path

PILOT_OPERATIONS = Path("datasets/pilot/pilot_operations.csv")
BASELINE_TESTS = Path("outputs/baseline/generated_tests.json")
BASELINE_RESULTS = Path("outputs/baseline/execution_results.json")
FEEDBACK_RESULTS = Path("outputs/feedback/execution_results.json")
SUMMARY_JSON = Path("outputs/results_summary.json")
SUMMARY_CSV = Path("outputs/results_summary.csv")
FAULT_CANDIDATES_CSV = Path("outputs/fault_candidates.csv")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_pilot_operations(path: Path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def rate(numerator, denominator):
    if denominator == 0:
        return 0.0

    return numerator / denominator


def status_match_rate(results):
    return rate(sum(1 for r in results if r.get("success")), len(results))


def parse_response_codes(raw_codes):
    if not raw_codes:
        return set()

    return {
        code.strip()
        for code in raw_codes.split("|")
        if code.strip()
    }


def status_to_code(value):
    if value is None:
        return ""

    return str(value)


def operation_map(operations):
    return {
        operation["operation_uid"]: {
            "method": operation["method"],
            "path": operation["path"],
            "documented_response_codes": parse_response_codes(
                operation["response_codes"]
            ),
        }
        for operation in operations
    }


def covered_operations(generated_tests):
    return {
        item["operation_uid"]
        for item in generated_tests
        if item.get("generated_test") is not None
    }


def is_fault_candidate(result, operation):
    actual_status = result.get("actual_status")
    actual_code = status_to_code(actual_status)
    documented_codes = operation["documented_response_codes"]

    return (
        actual_status is not None
        and (
            int(actual_status) >= 500
            or actual_code not in documented_codes
        )
    )


def build_fault_candidates(results, operations_by_uid, source_phase):
    candidates = []

    for result in results:
        uid = result["operation_uid"]
        operation = operations_by_uid.get(uid)

        if not operation or not is_fault_candidate(result, operation):
            continue

        candidates.append(
            {
                "operation_uid": uid,
                "method": operation["method"],
                "path": operation["path"],
                "documented_response_codes": "|".join(
                    sorted(operation["documented_response_codes"])
                ),
                "actual_status": result.get("actual_status"),
                "response_body_preview": result.get("response_body_preview"),
                "source_phase": source_phase,
            }
        )

    return candidates


def build_summary(operations, generated_tests, baseline_results, feedback_results):
    operations_by_uid = operation_map(operations)
    covered = covered_operations(generated_tests)
    baseline_status_rate = status_match_rate(baseline_results)
    feedback_status_rate = status_match_rate(feedback_results)
    fault_candidates = (
        build_fault_candidates(baseline_results, operations_by_uid, "baseline")
        + build_fault_candidates(feedback_results, operations_by_uid, "feedback")
    )
    total_execution_results = len(baseline_results) + len(feedback_results)

    return {
        "rq1_endpoint_coverage": {
            "total_operations": len(operations),
            "covered_operations": len(covered),
            "endpoint_coverage_rate": rate(len(covered), len(operations)),
        },
        "rq2_fault_detection": {
            "fault_candidates_count": len(fault_candidates),
            "fault_candidate_rate": rate(
                len(fault_candidates),
                total_execution_results,
            ),
        },
        "secondary_runtime_feedback_metrics": {
            "baseline_status_match_rate": baseline_status_rate,
            "feedback_status_match_rate": feedback_status_rate,
            "status_match_improvement": (
                feedback_status_rate - baseline_status_rate
            ),
        },
        "fault_candidates": fault_candidates,
    }


def export_json(summary):
    exportable_summary = dict(summary)
    exportable_summary.pop("fault_candidates", None)

    SUMMARY_JSON.write_text(
        json.dumps(exportable_summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def export_csv(summary):
    coverage = summary["rq1_endpoint_coverage"]
    faults = summary["rq2_fault_detection"]
    secondary = summary["secondary_runtime_feedback_metrics"]

    rows = [
        ("total_operations", coverage["total_operations"]),
        ("covered_operations", coverage["covered_operations"]),
        ("endpoint_coverage_rate", coverage["endpoint_coverage_rate"]),
        ("fault_candidates_count", faults["fault_candidates_count"]),
        ("fault_candidate_rate", faults["fault_candidate_rate"]),
        ("baseline_status_match_rate", secondary["baseline_status_match_rate"]),
        ("feedback_status_match_rate", secondary["feedback_status_match_rate"]),
        ("status_match_improvement", secondary["status_match_improvement"]),
    ]

    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        writer.writerows(rows)


def export_fault_candidates(fault_candidates):
    fieldnames = [
        "operation_uid",
        "method",
        "path",
        "documented_response_codes",
        "actual_status",
        "response_body_preview",
        "source_phase",
    ]

    with FAULT_CANDIDATES_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(fault_candidates)


def print_summary(summary):
    coverage = summary["rq1_endpoint_coverage"]
    faults = summary["rq2_fault_detection"]
    secondary = summary["secondary_runtime_feedback_metrics"]

    print("========== RQ1 Endpoint Coverage ==========")
    print(f"Total operations        : {coverage['total_operations']}")
    print(f"Covered operations      : {coverage['covered_operations']}")
    print(f"Endpoint coverage rate  : {coverage['endpoint_coverage_rate']:.2%}")

    print("\n========== RQ2 Fault Detection ==========")
    print(f"Fault candidates count  : {faults['fault_candidates_count']}")
    print(f"Fault candidate rate    : {faults['fault_candidate_rate']:.2%}")

    print("\n========== Secondary Runtime Feedback Metrics ==========")
    print(f"Baseline status match rate : {secondary['baseline_status_match_rate']:.2%}")
    print(f"Feedback status match rate : {secondary['feedback_status_match_rate']:.2%}")
    print(f"Status match improvement   : {secondary['status_match_improvement']:.2%}")

    print(f"\nSaved JSON              : {SUMMARY_JSON}")
    print(f"Saved CSV               : {SUMMARY_CSV}")
    print(f"Saved fault candidates  : {FAULT_CANDIDATES_CSV}")


def main():

    operations = load_pilot_operations(PILOT_OPERATIONS)
    generated_tests = load_json(BASELINE_TESTS)
    baseline_results = load_json(BASELINE_RESULTS)
    feedback_results = load_json(FEEDBACK_RESULTS)

    summary = build_summary(
        operations,
        generated_tests,
        baseline_results,
        feedback_results,
    )

    export_json(summary)
    export_csv(summary)
    export_fault_candidates(summary["fault_candidates"])
    print_summary(summary)


if __name__ == "__main__":
    main()
