import os
import json
from typing import Optional
import httpx
from pydantic import BaseModel, Field, ValidationError

class FormattedPost(BaseModel):
    tweet_text: str = Field(..., description="The formatted post text, max 280 chars.")
    source_row_id: str = Field(..., description="The ID of the row this text belongs to.")

class LLMService:
    def __init__(self):
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = httpx.Client(timeout=30.0)

    def format_post(self, raw_text: str, row_id: str) -> Optional[FormattedPost]:
        # Build prompt
        system_prompt = (
            "You are a helpful assistant that rewrites social media posts. "
            "Preserve all facts, do not add new information, keep the tone friendly, and ensure the output is a valid JSON matching the schema."
        )
        user_prompt = f"Rewrite the following text for a tweet (max 280 chars):\n\n{raw_text}"
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0,
            "response_format": {"type": "json_object"},
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        try:
            response = self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            json_str = data["choices"][0]["message"]["content"]
            return FormattedPost.parse_raw(json_str)
        except Exception as e:
            # If the LLM request fails (e.g., missing API key, 401, network error),
            # fall back to returning the raw text unchanged. This keeps the pipeline
            # deterministic and allows guardrails to run on the original content.
            print(f"[WARN] LLM call failed ({e}). Falling back to raw text.")
            return FormattedPost(tweet_text=raw_text, source_row_id=row_id)

