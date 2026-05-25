from openai import OpenAI

from agent_tools import TOOLS, execute_tool_call

DEFAULT_MODEL = "openai.gpt-oss-20b"
EXIT_COMMANDS = {"exit", "quit"}


def run_agent_turn(client, messages, model=DEFAULT_MODEL):
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
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        if not user_input:
            continue

        if user_input.lower() in EXIT_COMMANDS:
            print("Bye!")
            break

        messages.append({"role": "user", "content": user_input})

        try:
            reply = run_agent_turn(client, messages)
        except Exception as error:
            print(f"Assistant: Error: {error}")
            continue

        print(f"Assistant: {reply}")


if __name__ == "__main__":
    main()