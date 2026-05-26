from dotenv import load_dotenv  
from os import getenv
from pathlib import Path
load_dotenv()
CACHE_TTL_SECONDS = int(getenv("CACHE_TTL_SECONDS", 3600))
WEATHER_API_KEY = getenv("WEATHER_API_KEY", "312f5712e6b047058f2200626252611")
EXCHANGE_RATE_API_KEY = getenv("EXCHANGE_RATE_API_KEY", "b2d71961ebe71a300a02e73d03b6ebc8")
WEATHER_API_URL = getenv("WEATHER_API_URL", "http://api.weatherapi.com/v1/current.json")
EXCHANGE_RATE_API_URL = getenv("EXCHANGE_RATE_API_URL", "https://data.fixer.io/api/latest")
MODEL_NAME = getenv("MODEL_NAME", "openai.gpt-oss-20b")
BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
TRAVEL_POLICY_FILE = KNOWLEDGE_DIR / "travel_policy.txt"
TRAVEL_POLICY_EMBEDDINGS_PATH = getenv(
    "TRAVEL_POLICY_EMBEDDINGS_PATH",
    str(KNOWLEDGE_DIR / "travel_policy_embeddings.json"),
)
EMBEDDING_MODEL = getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
EMBEDDING_MIN_SIMILARITY = float(getenv("EMBEDDING_MIN_SIMILARITY", "0.65"))