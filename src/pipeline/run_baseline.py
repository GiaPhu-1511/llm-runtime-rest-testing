import json
import re
import time
from pathlib import Path

from src.data_loader import load_operations
from src.prompt_builder import build_baseline_prompt
from src.llm.factory import get_llm_client
from src.response_parser import parse_llm_response

OUTPUT_DIR = Path("outputs/baseline")
OUTPUT_FILE = OUTPUT_DIR / "generated_tests.json"
DEFAULT_QUOTA_RETRY_DELAY_SECONDS = 60
MAX_QUOTA_RETRIES = 3


def is_quota_error(error):
    message = str(error)
    return "429" in message or "RESOURCE_EXHAUSTED" in message


def get_retry_delay_seconds(error):
    message = str(error)

    retry_delay = getattr(error, "retry_delay", None)
    if retry_delay is not None:
        seconds = getattr(retry_delay, "seconds", None)
        if seconds is not None:
            return max(int(seconds), 1)

    patterns = [
        r"retry_delay\s*\{\s*seconds:\s*(\d+)",
        r"retryDelay['\"]?\s*:\s*['\"]?(\d+)s",
    ]

    for pattern in patterns:
        match = re.search(pattern, message)
        if match:
            return max(int(match.group(1)), 1)

    return DEFAULT_QUOTA_RETRY_DELAY_SECONDS


def save_results(results):
    OUTPUT_FILE.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    operations = load_operations()

    llm = get_llm_client()

    results = []

    for operation in operations:

        print(f"Generating: {operation.operation_uid}")

        prompt = build_baseline_prompt(operation)
        quota_retries = 0

        while True:

            try:
                response = llm.generate(prompt)

                generated_test = parse_llm_response(response)

                results.append(
                    {
                        "operation_uid": operation.operation_uid,
                        "prompt": prompt,
                        "generated_test": generated_test,
                    }
                )

                save_results(results)
                break

            except Exception as e:
                if is_quota_error(e):
                    quota_retries += 1

                    if quota_retries > MAX_QUOTA_RETRIES:
                        print(f"FAILED: {operation.operation_uid}")
                        print(e)
                        results.append(
                            {
                                "operation_uid": operation.operation_uid,
                                "prompt": prompt,
                                "generated_test": None,
                                "error_type": "quota_exceeded",
                                "error_message": str(e),
                            }
                        )
                        save_results(results)
                        break

                    retry_delay = get_retry_delay_seconds(e)
                    print(
                        f"Quota exhausted for {operation.operation_uid}. "
                        f"Retry {quota_retries}/{MAX_QUOTA_RETRIES} "
                        f"in {retry_delay} seconds."
                    )
                    time.sleep(retry_delay)
                    continue

                print(f"FAILED: {operation.operation_uid}")
                print(e)
                save_results(results)
                break

    print(f"\nSaved {len(results)} tests")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()
