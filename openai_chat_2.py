from openai import OpenAI

from system_prompt import SYSTEM_PROMPT
from text_processor_impl import text_processor

DEFAULT_MODEL = "openai.gpt-oss-20b"


def main():
    client = OpenAI()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            reply = text_processor.get_answer(client, messages, DEFAULT_MODEL)
        except Exception as error:
            print(f"Assistant: Error: {error}")
            continue

        print(f"Assistant: {reply}")


if __name__ == "__main__":
    main()
