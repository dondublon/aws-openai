import requests

from config import FIXER_API_URL, FIXER_KEY, WEATHER_API_KEY, WEATHER_API_URL

COUNTRY_TO_CURRENCY = {
    "united states": "USD",
    "usa": "USD",
    "us": "USD",
    "america": "USD",
    "united kingdom": "GBP",
    "uk": "GBP",
    "britain": "GBP",
    "england": "GBP",
    "germany": "EUR",
    "france": "EUR",
    "italy": "EUR",
    "spain": "EUR",
    "netherlands": "EUR",
    "belgium": "EUR",
    "austria": "EUR",
    "ireland": "EUR",
    "portugal": "EUR",
    "greece": "EUR",
    "finland": "EUR",
    "japan": "JPY",
    "china": "CNY",
    "india": "INR",
    "canada": "CAD",
    "australia": "AUD",
    "switzerland": "CHF",
    "sweden": "SEK",
    "norway": "NOK",
    "denmark": "DKK",
    "poland": "PLN",
    "czech republic": "CZK",
    "czechia": "CZK",
    "hungary": "HUF",
    "turkey": "TRY",
    "mexico": "MXN",
    "brazil": "BRL",
    "south korea": "KRW",
    "korea": "KRW",
    "singapore": "SGD",
    "hong kong": "HKD",
    "new zealand": "NZD",
    "south africa": "ZAR",
    "israel": "ILS",
    "uae": "AED",
    "united arab emirates": "AED",
    "saudi arabia": "SAR",
    "russia": "RUB",
    "russian federation": "RUB",
    "ukraine": "UAH",
    "thailand": "THB",
    "indonesia": "IDR",
    "malaysia": "MYR",
    "philippines": "PHP",
    "vietnam": "VND",
    "argentina": "ARS",
    "chile": "CLP",
    "colombia": "COP",
    "egypt": "EGP",
    "romania": "RON",
    "bulgaria": "BGN",
    "croatia": "EUR",
    "iceland": "ISK",
}


def get_current_weather(city: str) -> str:
    if not city:
        return "City argument is missing."
    if not WEATHER_API_KEY:
        return "Weather service is not configured: WEATHER_API_KEY is missing."

    try:
        response = requests.get(
            WEATHER_API_URL,
            params={"key": WEATHER_API_KEY, "q": city},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        return f"Failed to fetch weather: {exc}"

    location = data.get("location", {})
    current = data.get("current", {})
    condition = current.get("condition", {})

    city_name = location.get("name", city.strip())
    temperature = current.get("temp_c")
    weather_text = condition.get("text", "unknown weather")
    wind_speed = current.get("wind_kph")
    humidity = current.get("humidity")

    return (
        f"Weather in {city_name}: temperature is {temperature}°C, "
        f"{weather_text}, wind speed: {wind_speed} kph, humidity: {humidity}%"
    )


def _country_to_currency(country: str) -> str:
    normalized = country.strip().lower()
    if normalized in COUNTRY_TO_CURRENCY:
        return COUNTRY_TO_CURRENCY[normalized]

    code = country.strip().upper()
    if len(code) == 3 and code.isalpha():
        return code

    raise ValueError(f"Unknown country or currency: {country}")


def _units_per_eur(currency: str, rates: dict) -> float:
    if currency == "EUR":
        return 1.0
    if currency not in rates:
        raise ValueError(f"Exchange rate for {currency} is missing in API response.")
    return rates[currency]


def get_exchange_rate(from_country: str, to_country: str) -> str:
    if not FIXER_KEY:
        return "Exchange rate service is not configured: FIXER_KEY is missing."

    from_currency = _country_to_currency(from_country)
    to_currency = _country_to_currency(to_country)

    if from_currency == to_currency:
        return f"1 {from_currency} = 1 {to_currency}"

    symbols = sorted({from_currency, to_currency} - {"EUR"})

    try:
        response = requests.get(
            f"{FIXER_API_URL}/latest",
            params={
                "access_key": FIXER_KEY,
                "base": "EUR",
                "symbols": ",".join(symbols),
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        return f"Failed to fetch exchange rate: {exc}"

    if not data.get("success"):
        error = data.get("error", {})
        message = error.get("info") or error.get("type") or "unknown error"
        return f"Failed to fetch exchange rate: {message}"

    rates = data.get("rates")
    if not isinstance(rates, dict):
        return "Failed to fetch exchange rate: missing rates in API response."

    try:
        from_per_eur = _units_per_eur(from_currency, rates)
        to_per_eur = _units_per_eur(to_currency, rates)
        result = to_per_eur / from_per_eur
    except ValueError as exc:
        return str(exc)

    date = data.get("date", "unknown date")
    return (
        f"1 {from_currency} ({from_country.strip()}) = "
        f"{result} {to_currency} ({to_country.strip()}) on {date}"
    )

TOOLS = {
    "get_current_weather": get_current_weather,
    "get_exchange_rate": get_exchange_rate,
}