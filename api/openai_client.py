

from api.base_client import BaseModelClient
from config import OPENAI_API_KEY, MODELS, REQUEST_TIMEOUT


class OpenAIClient(BaseModelClient):
    def __init__(self):
        cfg = MODELS["gpt"]
        super().__init__(cfg["name"])
        self.model_id = cfg["model_id"]

        from openai import OpenAI
        self._client = OpenAI(api_key=OPENAI_API_KEY, timeout=REQUEST_TIMEOUT)

    def _call_api(self, prompt: str) -> str:
        response = self._client.chat.completions.create(
            model=self.model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=512,
            temperature=0.0,  
        )
        return response.choices[0].message.content.strip()
