

import anthropic
from api.base_client import BaseModelClient
from config import ANTHROPIC_API_KEY, MODELS, REQUEST_TIMEOUT


class ClaudeClient(BaseModelClient):
    def __init__(self):
        cfg = MODELS["claude"]
        super().__init__(cfg["name"])
        self.model_id = cfg["model_id"]

        self._client = anthropic.Anthropic(
            api_key=ANTHROPIC_API_KEY,
            timeout=REQUEST_TIMEOUT,
        )

    def _call_api(self, prompt: str) -> str:
        message = self._client.messages.create(
            model=self.model_id,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.content[0].text.strip()
