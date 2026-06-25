import json
from pathlib import Path

BASELINE_TESTS_FILE = Path("outputs/baseline/generated_tests.json")
EXECUTION_RESULTS_FILE = Path("outputs/baseline/execution_results.json")
OUTPUT_FILE = Path("outputs/feedback/feedback_prompts.json")


def build_feedback_prompt(test_case: dict, execution_result: dict) -> str:
    generated = test_case["generated_test"]

    return f"""
You are an expert REST API tester.

A previous LLM-generated REST API test was executed and produced runtime feedback.

Your task:
Generate ONE improved REST API test request for the same operation.

Return ONLY valid JSON. Do not include markdown.

Required JSON format:
{{
  "operation_uid": "{test_case["operation_uid"]}",
  "method": "{generated["method"]}",
  "path": "{generated["path"]}",
  "query_params": {{}},
  "headers": {{}},
  "body": null,
  "expected_status": null,
  "test_intent": "positive | negative | boundary | error"
}}

Original generated test:
{json.dumps(generated, indent=2, ensure_ascii=False)}

Runtime feedback:
- Expected status: {execution_result["expected_status"]}
- Actual status: {execution_result["actual_status"]}
- Response body: {execution_result["response_body_preview"]}
- Error: {execution_result["error"]}

Guidelines:
- Use the runtime feedback to improve the test.
- If the server requires authorization, generate a negative/authentication test and set expected_status to 401.
- Do not invent undocumented paths.
- Return exactly one JSON object.
""".strip()


def main():
    baseline_tests = json.loads(
        BASELINE_TESTS_FILE.read_text(encoding="utf-8")
    )

    execution_results = json.loads(
        EXECUTION_RESULTS_FILE.read_text(encoding="utf-8")
    )

    result_by_uid = {
        item["operation_uid"]: item
        for item in execution_results
    }

    feedback_prompts = []

    for test_case in baseline_tests:
        uid = test_case["operation_uid"]
        execution_result = result_by_uid[uid]

        prompt = build_feedback_prompt(test_case, execution_result)

        feedback_prompts.append(
            {
                "operation_uid": uid,
                "feedback_prompt": prompt,
            }
        )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(feedback_prompts, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Saved {len(feedback_prompts)} feedback prompts")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()