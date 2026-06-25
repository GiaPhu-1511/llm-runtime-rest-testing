import os
import time

from dotenv import load_dotenv
from google import genai

from src.config_loader import load_config
from src.llm.base import BaseLLMClient

load_dotenv()


class GeminiClient(BaseLLMClient):

    def __init__(self):

        config = load_config()["llm"]

        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

        self.model = config["model"]
        self.temperature = config.get("temperature", 0.0)
        self.max_output_tokens = config.get("max_output_tokens", 2048)

    def generate(self, prompt: str) -> str:

        for attempt in range(5):

            try:

                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config={
                        "temperature": self.temperature,
                        "max_output_tokens": self.max_output_tokens,
                    },
                )

                return response.text

            except Exception as e:

                if "503" in str(e) or "UNAVAILABLE" in str(e):

                    print(f"Gemini busy. Retry {attempt + 1}/5")

                    time.sleep(5)

                    continue

                raise

        raise RuntimeError("Gemini unavailable after 5 retries.")


if __name__ == "__main__":

    client = GeminiClient()

    print(
        client.generate(
            'Return ONLY {"status":"ok"}'
        )
    )