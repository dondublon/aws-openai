import json

from config import MODEL_NAME
from system_prompt import SYSTEM_PROMPT
from text_processor import TextProcessor
from tools import TOOL_FUNCTIONS, tools as TOOLS
from travel_policy_matcher import get_policy_matcher


class TextProcessorImpl(TextProcessor):
    def get_answer(self, client, messages, model=MODEL_NAME):
        self._ensure_system_prompt(messages)

        policy_answer = self._maybe_answer_from_policy(messages)
        if policy_answer:
            return policy_answer

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

        tool_replies = []
        for tool_call in message.tool_calls:
            tool_message = self._execute_tool_call(
                tool_name=tool_call.function.name,
                arguments_json=tool_call.function.arguments,
                call_id=tool_call.id,
            )
            messages.append(tool_message)
            tool_replies.append(f'{tool_message["content"]} (tool)')

        return "\n".join(tool_replies)

    def _ensure_system_prompt(self, messages):
        if messages and messages[0].get("role") == "system":
            return

        messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    def _execute_tool_call(self, tool_name, arguments_json, call_id):
        arguments = json.loads(arguments_json)
        result = TOOL_FUNCTIONS[tool_name](**arguments)
        return {
            "role": "tool",
            "tool_call_id": call_id,
            "content": str(result),
        }

    def _maybe_answer_from_policy(self, messages):
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


text_processor = TextProcessorImpl()
