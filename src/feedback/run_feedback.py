import json
from pathlib import Path

from src.llm.factory import get_llm_client
from src.response_parser import parse_llm_response

INPUT_FILE = Path("outputs/feedback/feedback_prompts.json")
OUTPUT_FILE = Path("outputs/feedback/refined_tests.json")


def main():
    prompts = json.loads(INPUT_FILE.read_text(encoding="utf-8"))

    llm = get_llm_client()
    results = []

    for item in prompts[:3]:
        uid = item["operation_uid"]
        print(f"Refining: {uid}")

        try:
            response = llm.generate(item["feedback_prompt"])
            refined_test = parse_llm_response(response)

            results.append({
                "operation_uid": uid,
                "feedback_prompt": item["feedback_prompt"],
                "refined_test": refined_test,
            })

        except Exception as e:
            print(f"FAILED: {uid}")
            print(e)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"\nSaved {len(results)} refined tests")
    print(OUTPUT_FILE)


if __name__ == "__main__":
    main()