from tool_functions import get_current_weather, get_exchange_rate


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name"
                    }
                },
                "required": ["city"]
            }
        }
    },
     {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "Get exchange rate from one country or currency to another",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_country": {
                        "type": "string",
                        "description": "Country name or three letter currency code to convert from"
                    },
                    "to_country": {
                        "type": "string",
                        "description": "Country name or three letter currency code to convert to"
                    }
                },
                "required": ["from_country", "to_country"]
            }
        }
    }
]

TOOL_FUNCTIONS={
    "get_current_weather":get_current_weather,
    "get_exchange_rate":get_exchange_rate
}


