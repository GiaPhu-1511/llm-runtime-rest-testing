import json
import re


def parse_llm_response(text: str) -> dict:
    """
    Parse JSON returned by an LLM.
    Supports:
    - pure JSON
    - Markdown code blocks (```json ... ```)
    """

    text = text.strip()

    # Remove Markdown code fences
    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    return json.loads(text.strip())


if __name__ == "__main__":

    sample = """
{
    "status": "ok"
}
"""

    print(parse_llm_response(sample))