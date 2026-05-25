import json


def get_weather(city: str) -> dict:
    return {
        "city": city,
        "temp": 22,
        "status": "sunny",
    }


def get_exchange_rate(base_currency: str, target_currency: str) -> dict:
    base_currency = base_currency.upper()
    target_currency = target_currency.upper()

    rates = {
        ("USD", "ILS"): 3.65,
        ("USD", "EUR"): 0.92,
        ("EUR", "ILS"): 3.98,
        ("ILS", "USD"): 0.27,
    }

    rate = rates.get((base_currency, target_currency), 1.0)
    return {
        "base_currency": base_currency,
        "target_currency": target_currency,
        "rate": rate,
    }


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name",
                    }
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_exchange_rate",
            "description": "Get exchange rate between two currencies",
            "parameters": {
                "type": "object",
                "properties": {
                    "base_currency": {
                        "type": "string",
                        "description": "Base currency code like USD",
                    },
                    "target_currency": {
                        "type": "string",
                        "description": "Target currency code like ILS",
                    },
                },
                "required": ["base_currency", "target_currency"],
            },
        },
    },
]

TOOL_FUNCTIONS = {
    "get_weather": get_weather,
    "get_exchange_rate": get_exchange_rate,
}


def execute_tool_call(tool_name: str, arguments_json: str, call_id: str) -> dict:
    try:
        arguments = json.loads(arguments_json)
        result = TOOL_FUNCTIONS[tool_name](**arguments)
    except KeyError:
        result = {"error": f"Unknown tool: {tool_name}"}
    except (TypeError, json.JSONDecodeError) as error:
        result = {"error": f"Invalid arguments for {tool_name}: {error}"}
    except Exception as error:
        result = {"error": f"Tool execution failed for {tool_name}: {error}"}

    return {
        "role": "tool",
        "tool_call_id": call_id,
        "content": json.dumps(result),
    }
