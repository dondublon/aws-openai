import json

from openai import OpenAI

from system_prompt import SYSTEM_PROMPT
from tools import TOOL_FUNCTIONS, tools as TOOLS
from travel_policy_matcher import get_policy_matcher

DEFAULT_MODEL = "openai.gpt-oss-20b"


def ensure_system_prompt(messages):
    if messages and messages[0].get("role") == "system":
        return

    messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})


def execute_tool_call(tool_name, arguments_json, call_id):
    arguments = json.loads(arguments_json)
    result = TOOL_FUNCTIONS[tool_name](**arguments)
    return {
        "role": "tool",
        "tool_call_id": call_id,
        "content": str(result),
    }


def maybe_answer_from_policy(messages):
    if not messages:
        return None

    last_message = messages[-1]
    if last_message.get("role") != "user":
        return None

    matcher = get_policy_matcher()
    if matcher is None:
        return None

    answer = matcher.get_answer(last_message.get("content") or "")
    if answer:
        messages.append({"role": "assistant", "content": answer})
    return answer


def run_agent_turn(client, messages, model=DEFAULT_MODEL):
    ensure_system_prompt(messages)

    policy_answer = maybe_answer_from_policy(messages)
    if policy_answer:
        return policy_answer

    first_response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )
    first_message = first_response.choices[0].message
    messages.append(first_message.model_dump(exclude_none=True))

    if not first_message.tool_calls:
        return first_message.content or ""

    tool_replies = []
    for tool_call in first_message.tool_calls:
        tool_message = execute_tool_call(
            tool_name=tool_call.function.name,
            arguments_json=tool_call.function.arguments,
            call_id=tool_call.id,
        )
        messages.append(tool_message)
        tool_replies.append(f'{tool_message["content"]} (tool)')

    return "\n".join(tool_replies)


def main():
    client = OpenAI()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            reply = run_agent_turn(client, messages)
        except Exception as error:
            print(f"Assistant: Error: {error}")
            continue

        print(f"Assistant: {reply}")


if __name__ == "__main__":
    main()