import sys
sys.path.insert(0, 'd:/Researching-Agent')
from dotenv import load_dotenv
load_dotenv('d:/Researching-Agent/.env', override=True)
import os

key = os.getenv("TAVILY_API_KEY", "")
print(f"Tavily key: {key!r}")

from tavily import TavilyClient
try:
    client = TavilyClient(api_key=key)
    result = client.search("test query", max_results=1)
    print(f"Tavily OK: {result}")
except Exception as e:
    print(f"Tavily FAILED: {e}")
