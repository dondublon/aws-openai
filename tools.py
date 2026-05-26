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
            "description": "Get exchange rate for a currency from one currency to another",
            "parameters": {
                "type": "object",
                "properties": {
                    "from_currency": {
                        "type": "string",
                        "description": "three letter currency code to convert from, like USD or EUR"
                    },
                    "to_currency": {
                        "type": "string",
                        "description": "three letter currency code to convert to, like USD or EUR"
                    }
                },
                "required": ["from_currency", "to_currency"]
            }
        }
    }
]

TOOL_FUNCTIONS={
    "get_current_weather":get_current_weather,
    "get_exchange_rate":get_exchange_rate
}


