import sys
sys.path.insert(0, 'd:/Researching-Agent')
from app.config import settings
print(f"Provider : {settings.provider}")
print(f"Base URL : {settings.base_url}")
print(f"Model    : {settings.model}")
print(f"API key  : {'SET (' + settings.api_key[:8] + '...)' if settings.api_key else 'NOT SET'}")
print(f"Tavily   : {'SET' if settings.tavily_api_key else 'NOT SET'}")
