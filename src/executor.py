import json
import time
from pathlib import Path

import requests

from src.config_loader import load_config


def execute_test(test_case: dict, base_url: str, test_key: str) -> dict:
    generated = test_case[test_key]

    method = generated["method"]
    path = generated["path"]
    url = base_url.rstrip("/") + path

    start = time.time()

    try:
        response = requests.request(
            method=method,
            url=url,
            params=generated.get("query_params") or {},
            headers=generated.get("headers") or {},
            json=generated.get("body"),
            timeout=15,
        )

        elapsed_ms = round((time.time() - start) * 1000, 2)

        return {
            "operation_uid": test_case["operation_uid"],
            "method": method,
            "url": url,
            "expected_status": generated.get("expected_status"),
            "actual_status": response.status_code,
            "response_time_ms": elapsed_ms,
            "response_body_preview": response.text[:500],
            "success": response.status_code == generated.get("expected_status"),
            "error": None,
        }

    except Exception as e:
        elapsed_ms = round((time.time() - start) * 1000, 2)

        return {
            "operation_uid": test_case["operation_uid"],
            "method": method,
            "url": url,
            "expected_status": generated.get("expected_status"),
            "actual_status": None,
            "response_time_ms": elapsed_ms,
            "response_body_preview": "",
            "success": False,
            "error": str(e),
        }


def run_executor(
    input_file: str,
    output_file: str,
    test_key: str,
) -> None:
    config = load_config()
    api_config = config["apis"]

    input_path = Path(input_file)
    output_path = Path(output_file)

    test_cases = json.loads(input_path.read_text(encoding="utf-8"))

    results = []

    for test_case in test_cases:
        api_name = test_case["operation_uid"].split("_")[0]
        base_url = api_config[api_name]["base_url"]

        print(f"Executing: {test_case['operation_uid']}")

        result = execute_test(test_case, base_url, test_key)
        results.append(result)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nSaved {len(results)} execution results")
    print(output_path)


def main():
    run_executor(
        input_file="outputs/baseline/generated_tests.json",
        output_file="outputs/baseline/execution_results.json",
        test_key="generated_test",
    )


if __name__ == "__main__":
    main()