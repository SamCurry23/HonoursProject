
import time
from config import MODELS, RATE_LIMIT_DELAY


class ModelManager:
    

    def __init__(self):
        self.clients = {}
        self._load_clients()

    def _load_clients(self):
        if MODELS["gpt"]["enabled"]:
            try:
                from api.openai_client import OpenAIClient
                self.clients["gpt"] = OpenAIClient()
                print(f"  ✓ Loaded {MODELS['gpt']['name']}")
            except Exception as e:
                print(f"  ✗ Failed to load GPT client: {e}")

        if MODELS["gemini"]["enabled"]:
            try:
                from api.gemini_client import GeminiClient
                self.clients["gemini"] = GeminiClient()
                print(f"  ✓ Loaded {MODELS['gemini']['name']}")
            except Exception as e:
                print(f"  ✗ Failed to load Gemini client: {e}")

        if MODELS["claude"]["enabled"]:
            try:
                from api.claude_client import ClaudeClient
                self.clients["claude"] = ClaudeClient()
                print(f"  ✓ Loaded {MODELS['claude']['name']}")
            except Exception as e:
                print(f"  ✗ Failed to load Claude client: {e}")

        if not self.clients:
            raise RuntimeError(
                "No models are available. "
                "Please set at least one API key in your .env file."
            )

    def get_enabled_models(self) -> list[str]:
        return list(self.clients.keys())

    def query(self, model_key: str, prompt: str) -> dict:
        
        if model_key not in self.clients:
            return {"response": "", "success": False, "error": "Model not loaded"}
        result = self.clients[model_key].query(prompt)
        time.sleep(RATE_LIMIT_DELAY)
        return result

    def query_all(self, prompt: str) -> dict[str, dict]:
        
        results = {}
        for key in self.clients:
            results[key] = self.query(key, prompt)
        return results
