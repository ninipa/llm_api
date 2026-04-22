from __future__ import annotations

import io
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from llm_api.cli.main import main
from llm_api.models import AskResult, ReasoningInfo, UsageInfo


class CliTests(unittest.TestCase):
    def test_default_cli_prints_answer_only(self) -> None:
        fake_result = AskResult(
            answer="答案文本",
            reasoning=ReasoningInfo(effort="medium", summary=None),
            usage=UsageInfo(input_tokens=1, output_tokens=2, reasoning_tokens=0, total_tokens=3),
            raw={"ok": True},
        )
        stdout = io.StringIO()

        with mock.patch("llm_api.cli.main.ask", return_value=fake_result):
            with redirect_stdout(stdout):
                exit_code = main(["ask", "你好"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue().strip(), "答案文本")

    def test_cli_can_use_text_file_mode(self) -> None:
        fake_result = AskResult(
            answer="文本文件答案",
            reasoning=ReasoningInfo(effort="medium", summary=None),
            usage=UsageInfo(input_tokens=1, output_tokens=2, reasoning_tokens=0, total_tokens=3),
            raw={"ok": True},
        )
        stdout = io.StringIO()

        with mock.patch("llm_api.cli.main.ask_text_file", return_value=fake_result) as mock_ask_text_file:
            with redirect_stdout(stdout):
                exit_code = main(["ask", "--text-file", "sample.json", "--prompt", "解释一下"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue().strip(), "文本文件答案")
        mock_ask_text_file.assert_called_once()

    def test_cli_can_use_image_file_mode(self) -> None:
        fake_result = AskResult(
            answer="图片答案",
            reasoning=ReasoningInfo(effort="medium", summary=None),
            usage=UsageInfo(input_tokens=1, output_tokens=2, reasoning_tokens=0, total_tokens=3),
            raw={"ok": True},
        )
        stdout = io.StringIO()

        with mock.patch("llm_api.cli.main.ask_image", return_value=fake_result) as mock_ask_image:
            with redirect_stdout(stdout):
                exit_code = main(["ask", "--image-file", "sample.png", "--prompt", "识别图片"])

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout.getvalue().strip(), "图片答案")
        mock_ask_image.assert_called_once()

    def test_cli_can_show_usage(self) -> None:
        fake_result = AskResult(
            answer="答案文本",
            reasoning=ReasoningInfo(effort="medium", summary=None),
            usage=UsageInfo(input_tokens=1, output_tokens=2, reasoning_tokens=0, total_tokens=3),
            raw={"ok": True},
        )
        stdout = io.StringIO()

        with mock.patch("llm_api.cli.main.ask", return_value=fake_result):
            with redirect_stdout(stdout):
                exit_code = main(["ask", "你好", "--show-usage"])

        self.assertEqual(exit_code, 0)
        output = stdout.getvalue()
        self.assertIn("答案文本", output)
        self.assertIn('"total_tokens": 3', output)

    def test_cli_returns_error_when_question_is_missing(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        with mock.patch("sys.stdin.isatty", return_value=True):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main(["ask"])

        self.assertEqual(exit_code, 1)
        self.assertIn("缺少问题文本", stderr.getvalue())

    def test_cli_rejects_conflicting_inputs(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            exit_code = main(["ask", "你好", "--text-file", "sample.md"])
        self.assertEqual(exit_code, 1)
        self.assertIn("不能同时使用", stderr.getvalue())

    def test_cli_requires_prompt_for_image_file(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            exit_code = main(["ask", "--image-file", "sample.png"])
        self.assertEqual(exit_code, 1)
        self.assertIn("必须提供 --prompt", stderr.getvalue())

    def test_cli_rejects_context_without_image_file(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            exit_code = main(["ask", "--text-file", "sample.md", "--context-text", "ctx"])
        self.assertEqual(exit_code, 1)
        self.assertIn("--context-text 只允许与 --image-file 一起使用", stderr.getvalue())

    def test_cli_can_show_config(self) -> None:
        stdout = io.StringIO()
        with mock.patch("llm_api.cli.main.find_project_config_path", return_value=Path("/tmp/.llm_api.json")):
            with mock.patch("llm_api.cli.main.load_project_config", return_value={"model": "gpt-5.4"}):
                with redirect_stdout(stdout):
                    exit_code = main(["ask", "--show-config"])
        self.assertEqual(exit_code, 0)
        output = stdout.getvalue()
        self.assertIn("/tmp/.llm_api.json", output)
        self.assertIn('"model": "gpt-5.4"', output)


if __name__ == "__main__":
    unittest.main()
