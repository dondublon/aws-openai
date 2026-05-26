from openai import OpenAI

from agent_tools import TOOLS, execute_tool_call
from travel_policy_matcher import get_policy_matcher

DEFAULT_MODEL = "openai.gpt-oss-20b"


def maybe_answer_from_policy(messages):
    if not messages:
        return None

    last_message = messages[-1]

    matcher = get_policy_matcher()
    if matcher is None:
        return None

    answer = matcher.get_answer(last_message.get("content") or "")
    if answer:
        messages.append({"role": "assistant", "content": answer})
    return answer


def run_agent_turn(client, messages, model=DEFAULT_MODEL):
    policy_answer = maybe_answer_from_policy(messages)
    if policy_answer:
        return policy_answer

    while True:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        message = response.choices[0].message
        messages.append(message.model_dump(exclude_none=True))

        if not message.tool_calls:
            return message.content or ""

        for tool_call in message.tool_calls:
            messages.append(
                execute_tool_call(
                    tool_name=tool_call.function.name,
                    arguments_json=tool_call.function.arguments,
                    call_id=tool_call.id,
                )
            )


def main():
    client = OpenAI()
    messages = []

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