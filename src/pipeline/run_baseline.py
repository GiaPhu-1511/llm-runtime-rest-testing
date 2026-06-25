import json
from pathlib import Path

from src.data_loader import load_operations
from src.prompt_builder import build_baseline_prompt
from src.llm.factory import get_llm_client
from src.response_parser import parse_llm_response

OUTPUT_DIR = Path("outputs/baseline")
OUTPUT_FILE = OUTPUT_DIR / "generated_tests.json"


def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    operations = load_operations()

    llm = get_llm_client()

    results = []

    for operation in operations[:3]:

        print(f"Generating: {operation.operation_uid}")

        try:
            prompt = build_baseline_prompt(operation)

            response = llm.generate(prompt)

            generated_test = parse_llm_response(response)

            results.append(
                {
                    "operation_uid": operation.operation_uid,
                    "prompt": prompt,
                    "generated_test": generated_test,
                }
            )

        except Exception as e:
            print(f"FAILED: {operation.operation_uid}")
            print(e)
            continue

    OUTPUT_FILE.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nSaved {len(results)} tests")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()