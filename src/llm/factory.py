from src.config_loader import load_config

from src.llm.gemini_client import GeminiClient
from src.llm.ollama_client import OllamaClient
from src.llm.openai_client import OpenAIClient


def get_llm_client():
    config = load_config()

    provider = config["llm"]["provider"].lower()

    if provider == "gemini":
        return GeminiClient()

    if provider == "openai":
        return OpenAIClient()

    if provider == "ollama":
        return OllamaClient()

    raise ValueError(f"Unsupported LLM provider: {provider}")
