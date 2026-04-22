from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from llm_api.core import ask_image, ask_text, ask_text_file


class CoreTests(unittest.TestCase):
    def test_ask_text_rejects_empty_text(self) -> None:
        with self.assertRaises(ValueError):
            ask_text("   ", api_key="key", base_url="https://example.com/v1/responses")

    def test_ask_text_file_reads_file_and_uses_prompt(self) -> None:
        with mock.patch("llm_api.core.read_text_file", return_value='{"ok": true}') as mock_read_text_file:
            with mock.patch("llm_api.core.send_payload", return_value={"output": [], "usage": {}, "reasoning": {}}) as mock_send_payload:
                ask_text_file(
                    "sample.json",
                    prompt="解释一下",
                    api_key="key",
                    base_url="https://example.com/v1/responses",
                )

        mock_read_text_file.assert_called_once_with("sample.json")
        content = mock_send_payload.call_args.kwargs["payload"]["input"][0]["content"]
        self.assertEqual(content[0]["text"], '{"ok": true}')
        self.assertEqual(content[1]["text"], "解释一下")

    def test_ask_image_requires_prompt(self) -> None:
        with self.assertRaises(ValueError):
            ask_image("sample.png", prompt="  ", api_key="key", base_url="https://example.com/v1/responses")

    def test_ask_image_builds_image_and_text_content(self) -> None:
        with mock.patch("llm_api.core.build_input_image_item", return_value={"type": "input_image", "image_url": "data:image/png;base64,abc", "detail": "high"}):
            with mock.patch("llm_api.core.send_payload", return_value={"output": [], "usage": {}, "reasoning": {}}) as mock_send_payload:
                ask_image(
                    "sample.png",
                    prompt="识别图片",
                    context_text="这是截图",
                    api_key="key",
                    base_url="https://example.com/v1/responses",
                )

        content = mock_send_payload.call_args.kwargs["payload"]["input"][0]["content"]
        self.assertEqual(content[0]["type"], "input_image")
        self.assertEqual(content[1]["text"], "识别图片")
        self.assertEqual(content[2]["text"], "这是截图")


if __name__ == "__main__":
    unittest.main()
