import json
from openai import OpenAI

client = OpenAI()

class Functions:
    def get_weather(self, city: str) -> dict:
        return {
            "city": city,
            "temp": 22,
            "status": "sunny",
        }


tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Get weather for a city",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
            },
            "required": ["city"],
        },
    }
]

# noinspection PyTypeChecker
response = client.responses.create(
    model="openai.gpt-oss-20b",
    input="What's the weather in Paris?",
    # input="What's the capital of France?",
    tools=tools,
)

functions = Functions()
final_response = None

for item in response.output:
    if item.type != "function_call":
        continue
    print("item:", item)
    args = json.loads(item.arguments)
    print("args:", args)
    func = getattr(functions, item.name, None)
    result = func(**args)

    # noinspection PyTypeChecker
    final_response = client.responses.create(
        model="openai.gpt-oss-120b",
        previous_response_id=response.id,
        input=[
            {
                "type": "function_call_output",
                "call_id": item.call_id,
                "output": json.dumps(result),
            }
        ],
    )

if final_response:
    final_final_response = final_response
else:
    final_final_response = response

print(final_final_response.output_text)

print("input:", final_final_response.usage.input_tokens)
print("output:", final_final_response.usage.output_tokens)
print("total:", final_final_response.usage.total_tokens)