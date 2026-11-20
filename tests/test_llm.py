import sys
sys.path.insert(0, 'd:/Researching-Agent')

# Reset any cached settings/client
import importlib
import app.config
importlib.reload(app.config)
import app.llm
app.llm._client = None
importlib.reload(app.llm)

from app.config import settings
from app.llm import chat

print(f"Provider : {settings.provider}")
print(f"Base URL : {settings.base_url}")
print(f"Model    : {settings.model}")
print(f"API key  : {'SET (' + settings.api_key[:12] + '...)' if settings.api_key else 'NOT SET'}")
print()
print("Testing LLM call...")
try:
    reply = chat("You are a helpful assistant.", "Reply with just: OK", max_tokens=5)
    print(f"LLM reply: {repr(reply)}")
    print("SUCCESS - LLM is working!")
except Exception as e:
    print(f"FAILED: {e}")
