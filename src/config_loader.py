from pathlib import Path
import yaml


CONFIG_PATH = Path("config/experiment.yaml")


def load_config():
    with CONFIG_PATH.open(
        "r",
        encoding="utf-8"
    ) as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    config = load_config()

    print(config)