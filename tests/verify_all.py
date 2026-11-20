import sys
sys.path.insert(0, 'd:/Researching-Agent')
from dotenv import load_dotenv
load_dotenv('d:/Researching-Agent/.env', override=True)

# Reload config fresh
import importlib, app.config, app.llm
importlib.reload(app.config)
app.llm._client = None
importlib.reload(app.llm)

from app.config import settings
from app.llm import chat
from app.tools.search import web_search

print(f"Provider : {settings.provider}")
print(f"Model    : {settings.model}")
print(f"Base URL : {settings.base_url}")
print(f"LLM key  : {'SET (' + settings.api_key[:10] + '...)' if settings.api_key else 'NOT SET'}")
print(f"Tavily   : {'SET (' + settings.tavily_api_key[:10] + '...)' if settings.tavily_api_key else 'NOT SET'}")

print("\n--- Testing LLM (Groq) ---")
try:
    reply = chat("You are helpful.", "Say OK", max_tokens=5)
    print(f"LLM: {reply!r}  ✅")
except Exception as e:
    print(f"LLM FAILED: {e}")

print("\n--- Testing Tavily search ---")
try:
    results = web_search("AI in healthcare", max_results=1)
    print(f"Tavily: {len(results)} result(s) returned  ✅")
    if results:
        print(f"  Title: {results[0]['title'][:60]}")
except Exception as e:
    print(f"Tavily FAILED: {e}")
