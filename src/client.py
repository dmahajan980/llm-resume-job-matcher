import os
from types import SimpleNamespace
from typing import Optional

import httpx
from dotenv import load_dotenv


load_dotenv()
GROK_API_KEY = os.getenv("GROK_API_KEY")

if not GROK_API_KEY:
    raise ValueError("GROK_API_KEY is not set")


class LLMClient:
    def __init__(self, model: str = "grok-4.3"):
        self.model = model

    def chat(
        self,
        system_prompt: str,
        user_prompt: Optional[str] = None,
        messages: Optional[list[dict[str, str]]] = None,
    ) -> SimpleNamespace:
        guarded_user_prompt = (
            f"""
        <unsafe_user_prompt>
        {user_prompt}
        </unsafe_user_prompt>
        """
            if user_prompt
            else None
        )

        response = httpx.post(
            "https://api.x.ai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROK_API_KEY}"},
            json={
                "model": self.model,
                "temperature": 0,
                "reasoning_effort": "none",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    *(
                        [{"role": "user", "content": guarded_user_prompt}]
                        if guarded_user_prompt
                        else []
                    ),
                    *(messages or []),
                ],
            },
            timeout=120,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"].get("content")
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
        )
