import time

from config import CACHE_TTL_SECONDS, EXCHANGE_RATE_API_URL, WEATHER_API_KEY, EXCHANGE_RATE_API_KEY,\
    WEATHER_API_URL,WEATHER_API_URL, EXCHANGE_RATE_API_URL   
from logging_config import logger
import requests
def get_current_weather(city: str)->str:
    """Get the current weather in a given city."""
    if not city:
        return "City argument is missing."
    resp = requests.get(WEATHER_API_URL, {"key":WEATHER_API_KEY, "q":city})
    res = f"{city} is wrong city"
    if not resp.status_code == 400:
        resp.raise_for_status()
        data = resp.json()
        res = f"Weather in {data["location"]["name"]}: temperature is {data["current"]["temp_c"]}\u00B0C , {data["current"]["condition"]["text"]},\n\
        speed of wind: {data["current"]["wind_kph"]} kph, Humidity is {data["current"]["humidity"]}%"
    return res


_rates_cache = None
def get_exchange_rate(from_currency: str, to_currency: str)->str:
    global _rates_cache
   
    result = ""
    if not from_currency:
        result += "from_currency argument is missing. "
    if not to_currency:
        result += "to_currency argument is missing. "
    if not result:
        use_cache = False
        if _rates_cache is not None:
            rates_timestamp = _rates_cache["timestamp"]
            rates_age = time.time() - rates_timestamp

            if rates_age < CACHE_TTL_SECONDS:
                use_cache = True
        if use_cache:
            data = _rates_cache
            logger.debug("Using cached exchange rates.")
        else: 
             logger.debug("Fetching new exchange rates.")
             resp = requests.get(EXCHANGE_RATE_API_URL, params={"access_key":EXCHANGE_RATE_API_KEY})
             resp.raise_for_status()
             data = resp.json()
             _rates_cache =data
        rates = data["rates"]    
        rateFrom = rates[from_currency]
        rateTo = rates[to_currency]
        rateFromTo = round(rateTo / rateFrom, 2)
        result = f"The current exchange rate from {from_currency} to {to_currency} is {rateFromTo}."
    return result   

TOOLS = {
    "get_current_weather": get_current_weather,
    "get_exchange_rate": get_exchange_rate  
}