import csv
import json
from pathlib import Path

RAW_DIR = Path("datasets/raw")
INVENTORY_FILE = RAW_DIR / "api_inventory.csv"
OUTPUT_FILE = RAW_DIR / "operations_all.csv"

HTTP_METHODS = {"get", "post", "put", "delete", "patch", "head", "options"}


def load_inventory() -> dict:
    result = {}

    with INVENTORY_FILE.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["status"] != "downloaded":
                continue

            result[row["api_name"]] = {
                "source_file": Path(row["source_file"]),
            }

    return result


def make_operation_uid(api_name: str, method: str, path: str) -> str:
    clean_path = (
        path.replace("/", "_")
        .replace("{", "")
        .replace("}", "")
        .replace("-", "_")
    )
    return f"{api_name}_{method.upper()}{clean_path}"


def extract_operations(api_name: str, spec: dict) -> list[dict]:
    rows = []
    paths = spec.get("paths", {})

    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue

        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS:
                continue

            if not isinstance(operation, dict):
                continue

            method_upper = method.upper()

            rows.append(
                {
                    "operation_uid": make_operation_uid(api_name, method_upper, path),
                    "api_name": api_name,
                    "method": method_upper,
                    "path": path,
                    "operation_id": operation.get("operationId", ""),
                    "summary": operation.get("summary", ""),
                    "description": operation.get("description", ""),
                    "parameters_count": len(operation.get("parameters", [])),
                    "has_request_body": "requestBody" in operation,
                    "response_codes": "|".join(operation.get("responses", {}).keys()),
                    "source_file": "",
                }
            )

    return rows


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    inventory = load_inventory()
    all_rows = []

    for api_name, info in inventory.items():
        source_file = info["source_file"]

        print(f"Extracting ALL operations from {api_name}...")

        spec = json.loads(source_file.read_text(encoding="utf-8"))
        rows = extract_operations(api_name, spec)

        for row in rows:
            row["source_file"] = str(source_file)

        all_rows.extend(rows)

        print(f"OK: {api_name} extracted {len(rows)} operations")

    fieldnames = [
        "operation_uid",
        "api_name",
        "method",
        "path",
        "operation_id",
        "summary",
        "description",
        "parameters_count",
        "has_request_body",
        "response_codes",
        "source_file",
    ]

    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print("\nDone.")
    print(f"Saved {len(all_rows)} operations to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()