import csv
import random
from pathlib import Path

CONFIG_FILE = Path("config/experiment.yaml")
RAW_DIR = Path("datasets/raw")
PILOT_DIR = Path("datasets/pilot")

INPUT_FILE = RAW_DIR / "operations_all.csv"
EXPERIMENT_FILE = RAW_DIR / "operations.csv"
PILOT_FILE = PILOT_DIR / "pilot_operations.csv"


def load_config() -> dict:
    config = {}

    for line in CONFIG_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if "." in value:
            config[key] = float(value)
        else:
            config[key] = int(value)

    return config


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows to write: {path}")

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    config = load_config()

    seed = config["random_seed"]
    experiment_size = config["experiment_dataset_size"]
    pilot_ratio = config["pilot_ratio"]

    all_rows = read_csv(INPUT_FILE)

    if experiment_size > len(all_rows):
        raise ValueError("experiment_dataset_size is larger than operations_all.csv")

    random.seed(seed)

    experiment_rows = random.sample(all_rows, experiment_size)
    experiment_uids = {row["operation_uid"] for row in experiment_rows}

    for row in all_rows:
        row["selected_for_experiment"] = str(row["operation_uid"] in experiment_uids)

    for row in experiment_rows:
        row["selected_for_experiment"] = "True"

    pilot_size = round(experiment_size * pilot_ratio)
    pilot_rows = random.sample(experiment_rows, pilot_size)
    pilot_uids = {row["operation_uid"] for row in pilot_rows}

    for row in experiment_rows:
        row["selected_for_pilot"] = str(row["operation_uid"] in pilot_uids)

    for row in pilot_rows:
        row["selected_for_pilot"] = "True"

    write_csv(EXPERIMENT_FILE, experiment_rows)
    write_csv(PILOT_FILE, pilot_rows)

    print("Sampling completed.")
    print(f"All operations: {len(all_rows)}")
    print(f"Experiment operations: {len(experiment_rows)} -> {EXPERIMENT_FILE}")
    print(f"Pilot operations: {len(pilot_rows)} -> {PILOT_FILE}")


if __name__ == "__main__":
    main()