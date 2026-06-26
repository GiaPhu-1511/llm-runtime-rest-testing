import ollama

from src.config_loader import load_config
from src.llm.base import BaseLLMClient


class OllamaClient(BaseLLMClient):

    def __init__(self):
        config = load_config()["llm"]

        self.model = config.get("model", "qwen2.5:7b")
        self.temperature = config.get("temperature", 0.0)

    def generate(self, prompt: str) -> str:
        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": self.temperature,
            },
        )

        return response["message"]["content"]


if __name__ == "__main__":
    client = OllamaClient()
    print(client.generate('Return ONLY this JSON: {"status":"ok"}'))
