import importlib
import json
import sys
import tempfile
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
fake_logging_config = types.ModuleType("logging_config")
fake_logging_config.logger = SimpleNamespace(
    debug=lambda *args, **kwargs: None,
    info=lambda *args, **kwargs: None,
    warning=lambda *args, **kwargs: None,
    error=lambda *args, **kwargs: None,
)

with patch.dict(
    sys.modules,
    {"openai": fake_openai_module, "logging_config": fake_logging_config},
), patch("builtins.print"):
    openai_chat_2 = importlib.import_module("openai_chat_2")


class OpenAIChat2Tests(unittest.TestCase):
    def test_travel_policy_matcher_returns_best_match_above_threshold(self):
        rows = [
            {"text": "Valid passports are required.", "embedding": [1.0, 0.0]},
            {"text": "Travel insurance is recommended.", "embedding": [0.0, 1.0]},
        ]
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", suffix=".json") as handle:
            json.dump(rows, handle)
            handle.flush()
            embedder = SimpleNamespace(embed=lambda texts: iter(([1.0, 0.0],)))
            matcher = openai_chat_2.TravelPolicyMatcher(
                embeddings_path=handle.name,
                threshold=0.8,
                embedder=embedder,
            )

            reply = matcher.get_answer("Do I need a passport?")

        self.assertEqual(reply, "Valid passports are required.")

    def test_travel_policy_matcher_returns_none_below_threshold(self):
        rows = [
            {"text": "Valid passports are required.", "embedding": [1.0, 0.0]},
            {"text": "Travel insurance is recommended.", "embedding": [0.0, 1.0]},
        ]
        diagonal = 2 ** -0.5
        with tempfile.NamedTemporaryFile("w+", encoding="utf-8", suffix=".json") as handle:
            json.dump(rows, handle)
            handle.flush()
            embedder = SimpleNamespace(embed=lambda texts: iter(([diagonal, diagonal],)))
            matcher = openai_chat_2.TravelPolicyMatcher(
                embeddings_path=handle.name,
                threshold=0.8,
                embedder=embedder,
            )

            reply = matcher.get_answer("Tell me something generic")

        self.assertIsNone(reply)

    def test_run_agent_turn_returns_policy_match_without_model_call(self):
        client = _FakeClient([])
        messages = [{"role": "user", "content": "Do I need a passport?"}]

        with patch.object(
            openai_chat_2,
            "get_policy_matcher",
            return_value=SimpleNamespace(get_answer=lambda query: "Valid passports are required."),
        ):
            reply = openai_chat_2.run_agent_turn(client, messages, "test-model")

        self.assertEqual(reply, "Valid passports are required.")
        self.assertEqual(messages[-1]["role"], "assistant")
        self.assertEqual(messages[-1]["content"], "Valid passports are required.")

    def test_run_agent_turn_falls_back_to_model_when_policy_has_no_match(self):
        response = _FakeResponse(_FakeMessage(content="Use the model fallback", tool_calls=None))
        client = _FakeClient([response])
        messages = [{"role": "user", "content": "How is the weather in Paris?"}]

        with patch.object(
            openai_chat_2,
            "get_policy_matcher",
            return_value=SimpleNamespace(get_answer=lambda query: None),
        ):
            reply = openai_chat_2.run_agent_turn(client, messages, "test-model")

        self.assertEqual(reply, "Use the model fallback")
        self.assertEqual(messages[-1]["content"], "Use the model fallback")

    def test_run_agent_turn_returns_tool_result_when_tool_is_called(self):
        tool_call = SimpleNamespace(
            id="call-1",
            function=SimpleNamespace(
                name="get_exchange_rate",
                arguments='{"from_country":"USD","to_country":"EUR"}',
            ),
        )
        first_response = _FakeResponse(_FakeMessage(content=None, tool_calls=[tool_call]))
        client = _FakeClient([first_response])
        messages = [{"role": "user", "content": "Convert 1 USD to EUR"}]

        with patch.dict(
            openai_chat_2.TOOL_FUNCTIONS,
            {"get_exchange_rate": lambda from_country, to_country: "1 USD = 0.92 EUR"},
        ):
            reply = openai_chat_2.run_agent_turn(client, messages, "test-model")

        self.assertEqual(reply, "1 USD = 0.92 EUR (tool)")
        self.assertEqual(messages[-1]["role"], "tool")
        self.assertEqual(messages[-1]["content"], "1 USD = 0.92 EUR")


if __name__ == "__main__":
    unittest.main()
