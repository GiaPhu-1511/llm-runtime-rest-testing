import csv
import json
from collections import Counter
from pathlib import Path

BASELINE = Path("outputs/baseline/execution_results.json")
FEEDBACK = Path("outputs/feedback/execution_results.json")
SUMMARY_JSON = Path("outputs/results_summary.json")
SUMMARY_CSV = Path("outputs/results_summary.csv")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def success_rate(results):
    if not results:
        return 0.0

    success = sum(1 for r in results if r["success"])

    return success / len(results)


def success_count(results):
    return sum(1 for r in results if r["success"])


def average_response_time(results):
    times = [
        r["response_time_ms"]
        for r in results
        if r.get("response_time_ms") is not None
    ]

    if not times:
        return 0.0

    return sum(times) / len(times)


def status_code_distribution(results):
    return dict(
        sorted(
            Counter(str(r.get("actual_status")) for r in results).items()
        )
    )


def build_summary(baseline, feedback):
    baseline_rate = success_rate(baseline)
    feedback_rate = success_rate(feedback)

    return {
        "total_cases": len(set(
            [r["operation_uid"] for r in baseline]
            + [r["operation_uid"] for r in feedback]
        )),
        "baseline_success_count": success_count(baseline),
        "feedback_success_count": success_count(feedback),
        "baseline_success_rate": baseline_rate,
        "feedback_success_rate": feedback_rate,
        "improvement_rate": feedback_rate - baseline_rate,
        "average_response_time_baseline": average_response_time(baseline),
        "average_response_time_feedback": average_response_time(feedback),
        "status_code_distribution_baseline": status_code_distribution(baseline),
        "status_code_distribution_feedback": status_code_distribution(feedback),
    }


def export_json(summary):
    SUMMARY_JSON.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def export_csv(summary):
    rows = [
        ("total_cases", summary["total_cases"], ""),
        ("success_count", summary["baseline_success_count"], summary["feedback_success_count"]),
        ("success_rate", summary["baseline_success_rate"], summary["feedback_success_rate"]),
        ("improvement_rate", "", summary["improvement_rate"]),
        ("average_response_time_ms", summary["average_response_time_baseline"], summary["average_response_time_feedback"]),
    ]

    status_codes = sorted(
        set(summary["status_code_distribution_baseline"])
        | set(summary["status_code_distribution_feedback"])
    )

    for status_code in status_codes:
        rows.append((
            f"status_code_{status_code}",
            summary["status_code_distribution_baseline"].get(status_code, 0),
            summary["status_code_distribution_feedback"].get(status_code, 0),
        ))

    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "baseline", "feedback"])
        writer.writerows(rows)


def print_summary(summary):
    print("========== RESULTS ==========")
    print(f"Total cases                    : {summary['total_cases']}")
    print(f"Baseline success count         : {summary['baseline_success_count']}")
    print(f"Feedback success count         : {summary['feedback_success_count']}")
    print(f"Baseline success rate          : {summary['baseline_success_rate']:.2%}")
    print(f"Feedback success rate          : {summary['feedback_success_rate']:.2%}")
    print(f"Improvement rate               : {summary['improvement_rate']:.2%}")
    print(f"Avg response time baseline     : {summary['average_response_time_baseline']:.2f} ms")
    print(f"Avg response time feedback     : {summary['average_response_time_feedback']:.2f} ms")
    print("Baseline status distribution   :", summary["status_code_distribution_baseline"])
    print("Feedback status distribution   :", summary["status_code_distribution_feedback"])
    print(f"Saved JSON                     : {SUMMARY_JSON}")
    print(f"Saved CSV                      : {SUMMARY_CSV}")


def main():

    baseline = load(BASELINE)
    feedback = load(FEEDBACK)

    summary = build_summary(baseline, feedback)

    export_json(summary)
    export_csv(summary)
    print_summary(summary)


if __name__ == "__main__":
    main()
