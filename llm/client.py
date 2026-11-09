import os
from typing import Optional
from dotenv import load_dotenv
from groq import Groq
from groq.types.chat import ChatCompletionMessage, ChatCompletionMessageParam


load_dotenv()
LLM_API_KEY = os.getenv("GROQ_API_KEY")

if not LLM_API_KEY:
    raise ValueError("GROQ_API_KEY is not set")


class LLMClient:
    def __init__(self, model: str = "openai/gpt-oss-20b"):
        self.client = Groq(api_key=LLM_API_KEY)
        self.model = model

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        messages: Optional[list[ChatCompletionMessageParam]] = None,
    ) -> ChatCompletionMessage:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
                *(messages or []),
            ],
            response_format={"type": "json_object"},
        )
        return response.choices[0].message
