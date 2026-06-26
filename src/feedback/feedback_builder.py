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
- The runtime execution result is the ground truth.
- You MUST update expected_status to exactly match the observed actual_status unless there is strong evidence that the runtime failed unexpectedly.
- Preserve method, path, parameters and body whenever possible.
- Only modify:
  - expected_status
  - test_intent
  - headers (if authentication is needed)
- Do NOT keep the previous expected_status if it contradicts runtime feedback.
- If actual_status is 401, the refined test should expect 401.
- If actual_status is 403, the refined test should expect 403.
- If actual_status is another documented status code for this operation, prefer that actual status.
- Do not hardcode authorization failures to 401; learn from the actual runtime status.
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
