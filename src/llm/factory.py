from src.config_loader import load_config

from src.llm.ollama_client import OllamaClient


def get_llm_client():
    config = load_config()

    provider = config.get("llm", {}).get("provider", "ollama").lower()

    if provider == "ollama":
        return OllamaClient()

    raise ValueError(
        "This project version only supports Ollama as the LLM provider. "
        f"Unsupported provider: {provider}"
    )
