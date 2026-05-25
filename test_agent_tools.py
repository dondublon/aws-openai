import json
import unittest

from agent_tools import execute_tool_call, get_exchange_rate, get_weather


class AgentToolsTests(unittest.TestCase):
    def test_get_weather_returns_stubbed_payload(self):
        result = get_weather("Paris")

        self.assertEqual(result["city"], "Paris")
        self.assertIn("temp", result)
        self.assertIn("status", result)

    def test_get_exchange_rate_returns_stubbed_payload(self):
        result = get_exchange_rate("usd", "ils")

        self.assertEqual(result["base_currency"], "USD")
        self.assertEqual(result["target_currency"], "ILS")
        self.assertEqual(result["rate"], 3.65)

    def test_execute_tool_call_returns_tool_message(self):
        tool_message = execute_tool_call(
            tool_name="get_exchange_rate",
            arguments_json=json.dumps(
                {"base_currency": "USD", "target_currency": "EUR"}
            ),
            call_id="call-123",
        )

        self.assertEqual(tool_message["role"], "tool")
        self.assertEqual(tool_message["tool_call_id"], "call-123")
        self.assertEqual(
            json.loads(tool_message["content"])["target_currency"],
            "EUR",
        )

    def test_execute_tool_call_returns_error_for_unknown_tool(self):
        tool_message = execute_tool_call(
            tool_name="missing_tool",
            arguments_json="{}",
            call_id="call-404",
        )

        self.assertEqual(tool_message["role"], "tool")
        self.assertIn("Unknown tool", tool_message["content"])


if __name__ == "__main__":
    unittest.main()
