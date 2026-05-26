from dotenv import load_dotenv  
from os import getenv
load_dotenv()
CACHE_TTL_SECONDS = int(getenv("CACHE_TTL_SECONDS", 3600))
WEATHER_API_KEY = getenv("WEATHER_API_KEY", "312f5712e6b047058f2200626252611")
EXCHANGE_RATE_API_KEY = getenv("EXCHANGE_RATE_API_KEY", "b2d71961ebe71a300a02e73d03b6ebc8")
WEATHER_API_URL = getenv("WEATHER_API_URL", "http://api.weatherapi.com/v1/current.json")
EXCHANGE_RATE_API_URL = getenv("EXCHANGE_RATE_API_URL", "https://data.fixer.io/api/latest")
MODEL_NAME = getenv("MODEL_NAME", "openai.gpt-oss-20b")