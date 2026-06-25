import csv
from pathlib import Path

from src.models import Operation


DEFAULT_DATASET = Path("datasets/pilot/pilot_operations.csv")


def to_bool(value: str) -> bool:
    return str(value).lower() == "true"


def load_operations(
    csv_path: str | Path = DEFAULT_DATASET,
) -> list[Operation]:

    path = Path(csv_path)

    operations = []

    with path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            operations.append(
                Operation(
                    operation_uid=row["operation_uid"],
                    api_name=row["api_name"],
                    method=row["method"],
                    path=row["path"],
                    operation_id=row["operation_id"],
                    summary=row["summary"],
                    description=row["description"],
                    parameters_count=int(row["parameters_count"]),
                    has_request_body=to_bool(row["has_request_body"]),
                    response_codes=row["response_codes"],
                )
            )

    return operations


if __name__ == "__main__":

    operations = load_operations()

    print(f"Loaded {len(operations)} operations")
    print(operations[0])