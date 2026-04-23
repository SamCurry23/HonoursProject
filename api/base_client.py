
 
import time
import random
from abc import ABC, abstractmethod
from config import MAX_RETRIES, RATE_LIMIT_DELAY
 
 
class BaseModelClient(ABC):
    
 
    def __init__(self, model_name: str):
        self.model_name = model_name
 
    @abstractmethod
    def _call_api(self, prompt: str) -> str:
        
        pass
 
    def query(self, prompt: str) -> dict:
        
        last_error = None
 
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response_text = self._call_api(prompt)
                return {"response": response_text, "success": True, "error": None}
 
            except Exception as exc:
                last_error = str(exc)
                error_lower = last_error.lower()
 
                
                if any(k in error_lower for k in ("rate", "429", "quota", "limit")):
                    wait = RATE_LIMIT_DELAY * (2 ** (attempt - 1)) + random.uniform(0, 1)
                    print(f"  [Rate limit] {self.model_name} – waiting {wait:.1f}s "
                          f"(attempt {attempt}/{MAX_RETRIES})")
                    time.sleep(wait)
 
                
                elif any(k in error_lower for k in ("500", "502", "503", "529", "timeout", "overload")):
                    wait = RATE_LIMIT_DELAY * (2 ** attempt) 
                    print(f"  [Server error] {self.model_name} – waiting {wait:.1f}s "
                          f"(attempt {attempt}/{MAX_RETRIES})")
                    time.sleep(wait)
 
                
                else:
                    print(f"  [Error] {self.model_name}: {last_error}")
                    break
 
        return {"response": "", "success": False, "error": last_error}
 
    def is_available(self) -> bool:
        
        result = self.query("Reply with the single word: OK")
        return result["success"]
