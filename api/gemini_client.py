
 
from google import genai
from google.genai import types
from api.base_client import BaseModelClient
from config import GEMINI_API_KEY, MODELS
 
 
SYSTEM_INSTRUCTION = (
    "You are a helpful assistant. Answer questions directly and completely. "
    "Do not add preamble or meta-commentary. Just answer the question."
)
 
 
class GeminiClient(BaseModelClient):
    def __init__(self):
        cfg = MODELS["gemini"]
        super().__init__(cfg["name"])
        self.model_id = cfg["model_id"]
        self._client = genai.Client(api_key=GEMINI_API_KEY)
 
    def _call_api(self, prompt: str) -> str:
        response = self._client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.0,
                max_output_tokens=2048,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                safety_settings=[
                    types.SafetySetting(
                        category="HARM_CATEGORY_HARASSMENT",
                        threshold="BLOCK_NONE",
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_HATE_SPEECH",
                        threshold="BLOCK_NONE",
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        threshold="BLOCK_NONE",
                    ),
                    types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT",
                        threshold="BLOCK_NONE",
                    ),
                ],
            ),
        )
 
        try:
            if response.text:
                return response.text.strip()
        except Exception:
            pass
        try:
            for candidate in response.candidates:
                for part in candidate.content.parts:
                    if hasattr(part, "text") and part.text:
                        return part.text.strip()
        except Exception:
            pass
 
        return ""