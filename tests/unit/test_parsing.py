from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from llm_api.parsing.responses import (
    extract_output_text,
    extract_reasoning_info,
    extract_usage_info,
    parse_ask_result,
)


SAMPLE_RESPONSE = {
    "output": [
        {
            "type": "message",
            "content": [
                {"type": "output_text", "text": "第一段"},
                {"type": "output_text", "text": "第二段"},
            ],
        }
    ],
    "reasoning": {
        "effort": "medium",
        "summary": [{"type": "summary_text", "text": "简要说明"}],
    },
    "usage": {
        "input_tokens": 10,
        "output_tokens": 20,
        "total_tokens": 40,
        "output_tokens_details": {"reasoning_tokens": 5},
    },
}


class ParsingTests(unittest.TestCase):
    def test_extract_output_text_joins_multiple_blocks(self) -> None:
        self.assertEqual(extract_output_text(SAMPLE_RESPONSE), "第一段\n第二段")

    def test_extract_reasoning_info(self) -> None:
        reasoning = extract_reasoning_info(SAMPLE_RESPONSE)
        self.assertEqual(reasoning.effort, "medium")
        self.assertIsInstance(reasoning.summary, list)

    def test_extract_usage_info(self) -> None:
        usage = extract_usage_info(SAMPLE_RESPONSE)
        self.assertEqual(usage.input_tokens, 10)
        self.assertEqual(usage.output_tokens, 20)
        self.assertEqual(usage.reasoning_tokens, 5)
        self.assertEqual(usage.total_tokens, 40)

    def test_parse_ask_result(self) -> None:
        result = parse_ask_result(SAMPLE_RESPONSE)
        self.assertEqual(result.answer, "第一段\n第二段")
        self.assertEqual(result.usage.total_tokens, 40)
        self.assertEqual(result.raw, SAMPLE_RESPONSE)


if __name__ == "__main__":
    unittest.main()
