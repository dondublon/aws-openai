import importlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import patch


class _ImportSafeResponse:
    def __init__(self):
        self.output = []
        self.output_text = ""
        self.usage = SimpleNamespace(input_tokens=0, output_tokens=0, total_tokens=0)


class _ImportSafeClient:
    class responses:
        @staticmethod
        def create(**kwargs):
            return _ImportSafeResponse()


class _FakeMessage:
    def __init__(self, content=None, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls

    def model_dump(self, exclude_none=True):
        payload = {"role": "assistant"}
        if self.content is not None:
            payload["content"] = self.content
        if self.tool_calls is not None:
            payload["tool_calls"] = self.tool_calls
        return payload


class _FakeResponse:
    def __init__(self, message):
        self.choices = [SimpleNamespace(message=message)]


class _FakeCompletions:
    def __init__(self, responses):
        self._responses = list(responses)

    def create(self, **kwargs):
        return self._responses.pop(0)


class _FakeChat:
    def __init__(self, responses):
        self.completions = _FakeCompletions(responses)


class _FakeClient:
    def __init__(self, responses):
        self.chat = _FakeChat(responses)


fake_openai_module = types.ModuleType("openai")
fake_openai_module.OpenAI = _ImportSafeClient

with patch.dict(sys.modules, {"openai": fake_openai_module}), patch("builtins.print"):
    openai_chat_2 = importlib.import_module("openai_chat_2")


class OpenAIChat2Tests(unittest.TestCase):
    def test_run_agent_turn_handles_tool_call_and_final_reply(self):
        tool_call = SimpleNamespace(
            id="call-1",
            function=SimpleNamespace(
                name="get_exchange_rate",
                arguments='{"base_currency":"USD","target_currency":"EUR"}',
            ),
        )
        first_response = _FakeResponse(_FakeMessage(content=None, tool_calls=[tool_call]))
        second_response = _FakeResponse(_FakeMessage(content="1 USD is 0.92 EUR", tool_calls=None))
        client = _FakeClient([first_response, second_response])
        messages = [{"role": "user", "content": "Convert 1 USD to EUR"}]

        reply = openai_chat_2.run_agent_turn(client, messages, "test-model")

        self.assertEqual(reply, "1 USD is 0.92 EUR")
        self.assertEqual(messages[-1]["content"], "1 USD is 0.92 EUR")
        self.assertEqual(messages[-2]["role"], "tool")


if __name__ == "__main__":
    unittest.main()
