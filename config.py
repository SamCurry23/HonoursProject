
 
import os
from dotenv import load_dotenv
 
load_dotenv()
 
OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY    = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
 
MODELS = {
    "gpt": {
        "name":       "GPT-4o-mini",
        "model_id":   "gpt-4o-mini",
        "api_key_var": "OPENAI_API_KEY",
        "enabled":    bool(OPENAI_API_KEY),
    },
    "gemini": {
        "name":       "Gemini 2.5 Flash",
        "model_id":   "gemini-2.5-flash",
        "api_key_var": "GEMINI_API_KEY",
        "enabled":    bool(GEMINI_API_KEY),
    },
    "claude": {
        "name":       "Claude Haiku 3",
        "model_id":   "claude-haiku-4-5-20251001",
        "api_key_var": "ANTHROPIC_API_KEY",
        "enabled":    bool(ANTHROPIC_API_KEY),
    },
}
 
RATE_LIMIT_DELAY = 1.5
 
MAX_RETRIES = 3
 
REQUEST_TIMEOUT = 30
 
DOMAINS = ["mathematics", "factual", "logical", "ethics", "creative"]
 
DOMAIN_DISPLAY_NAMES = {
    "mathematics": "Mathematics",
    "factual":     "Factual Accuracy",
    "logical":     "Logical Reasoning",
    "ethics":      "Ethical Reasoning",
    "creative":    "Creative Generation",
}
 
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
DATA_DIR       = os.path.join(BASE_DIR, "data", "questions")
RESULTS_DIR    = os.path.join(BASE_DIR, "results")
WEBSITE_DIR    = os.path.join(BASE_DIR, "website")
 
os.makedirs(RESULTS_DIR, exist_ok=True)