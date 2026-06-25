import os

from dotenv import load_dotenv
from openai import OpenAI

from src.llm.base import BaseLLMClient


load_dotenv()


class OpenAIClient(BaseLLMClient):
    def __init__(self) -> None:
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    def generate(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=prompt,
            temperature=0,
        )
        return response.output_text


if __name__ == "__main__":
    client = OpenAIClient()
    print(client.generate('Return ONLY this JSON: {"status":"ok"}'))