from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from llm_api import ask


class AskIntegrationTests(unittest.TestCase):
    def test_ask_returns_structured_result(self) -> None:
        response = mock.Mock()
        response.raise_for_status.return_value = None
        response.json.return_value = {
            "output": [
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": "你好，世界"}],
                }
            ],
            "reasoning": {"effort": "medium", "summary": None},
            "usage": {
                "input_tokens": 5,
                "output_tokens": 6,
                "total_tokens": 11,
                "output_tokens_details": {"reasoning_tokens": 2},
            },
        }

        with mock.patch("llm_api.transport.client.requests.post", return_value=response) as mock_post:
            result = ask(
                "你好",
                api_key="key",
                base_url="https://example.com/v1/responses",
            )

        self.assertEqual(result.answer, "你好，世界")
        self.assertEqual(result.reasoning.effort, "medium")
        self.assertEqual(result.usage.total_tokens, 11)
        sent_payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(sent_payload["input"][0]["content"][0]["text"], "你好")


if __name__ == "__main__":
    unittest.main()
