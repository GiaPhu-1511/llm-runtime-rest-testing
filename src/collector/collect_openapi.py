import json
from pathlib import Path
from urllib.request import Request, urlopen

OUTPUT_DIR = Path("datasets/openapi")
RAW_DIR = Path("datasets/raw")

SELECTED_APIS = {
    "spotify": {
        "url": "https://api.apis.guru/v2/specs/spotify.com/1.0.0/openapi.json",
        "max_operations": 88,
    },
    "sendgrid": {
        "url": "https://api.apis.guru/v2/specs/sendgrid.com/1.0.0/openapi.json",
        "max_operations": 120,
    },
}


def download_json(url: str) -> dict:
    req = Request(url, headers={"User-Agent": "llm-runtime-rest-testing"})
    with urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def count_operations(spec: dict) -> int:
    methods = {"get", "post", "put", "delete", "patch", "head", "options"}
    count = 0

    for path_item in spec.get("paths", {}).values():
        if not isinstance(path_item, dict):
            continue

        for method in path_item:
            if method.lower() in methods:
                count += 1

    return count


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    inventory_rows = [
        "api_name,source_file,openapi_version,total_operations,max_selected_operations,status\n"
    ]

    for api_name, api_info in SELECTED_APIS.items():
        url = api_info["url"]
        max_operations = api_info["max_operations"]

        print(f"Downloading {api_name}...")

        try:
            spec = download_json(url)
            operations = count_operations(spec)

            api_dir = OUTPUT_DIR / api_name
            api_dir.mkdir(parents=True, exist_ok=True)

            output_file = api_dir / "openapi.json"
            output_file.write_text(
                json.dumps(spec, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

            openapi_version = spec.get("openapi") or spec.get("swagger") or "unknown"

            inventory_rows.append(
                f"{api_name},{output_file},{openapi_version},{operations},{max_operations},downloaded\n"
            )

            print(
                f"OK: {api_name} "
                f"({operations} operations, max selected={max_operations})"
            )

        except Exception as e:
            inventory_rows.append(
                f'{api_name},,,0,{max_operations},"failed: {str(e)}"\n'
            )
            print(f"FAILED: {api_name} - {e}")

    inventory_file = RAW_DIR / "api_inventory.csv"
    inventory_file.write_text("".join(inventory_rows), encoding="utf-8")

    print("\nDone.")
    print(f"Inventory saved to {inventory_file}")


if __name__ == "__main__":
    main()