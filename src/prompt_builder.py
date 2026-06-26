from src.models import Operation


def build_baseline_prompt(operation: Operation) -> str:
    return f"""
You are an expert REST API tester.

Generate ONE executable REST API test request for the following OpenAPI operation.

Return ONLY valid JSON. Do not include markdown.

Required JSON format:
{{
  "operation_uid": "{operation.operation_uid}",
  "method": "{operation.method}",
  "path": "{operation.path}",
  "query_params": {{}},
  "headers": {{}},
  "body": null,
  "expected_status": null,
  "test_intent": "positive | negative | boundary | error"
}}

Operation:
- API name: {operation.api_name}
- Method: {operation.method}
- Path: {operation.path}
- Operation ID: {operation.operation_id}
- Summary: {operation.summary}
- Description: {operation.description}
- Number of parameters: {operation.parameters_count}
- Has request body: {operation.has_request_body}
- Documented response codes: {operation.response_codes}

Guidelines:
- Use realistic values when possible.
- Cover edge cases or error codes if the operation description suggests them.
- Do not invent undocumented paths.
- Return exactly one JSON object.
""".strip()


if __name__ == "__main__":
    from src.data_loader import load_operations

    ops = load_operations("datasets/pilot/pilot_operations.csv")
    prompt = build_baseline_prompt(ops[0])

    print(prompt)
