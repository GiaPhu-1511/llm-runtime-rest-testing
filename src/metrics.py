import json
from pathlib import Path

BASELINE = Path("outputs/baseline/execution_results.json")
FEEDBACK = Path("outputs/feedback/execution_results.json")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def success_rate(results):
    if not results:
        return 0.0

    success = sum(1 for r in results if r["success"])

    return success / len(results)


def main():

    baseline = load(BASELINE)
    feedback = load(FEEDBACK)

    baseline_rate = success_rate(baseline)
    feedback_rate = success_rate(feedback)

    print("========== RESULTS ==========")
    print(f"Baseline success rate : {baseline_rate:.2%}")
    print(f"Feedback success rate : {feedback_rate:.2%}")
    print(f"Improvement           : {(feedback_rate-baseline_rate):.2%}")


if __name__ == "__main__":
    main()