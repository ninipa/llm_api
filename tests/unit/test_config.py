from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from llm_api.config.input_support import (
    build_input_image_item,
    build_unsupported_image_file_message,
    build_unsupported_text_file_message,
    get_supported_image_file_extensions,
    get_supported_text_file_extensions,
    read_text_file,
    validate_image_file_path,
    validate_text_file_path,
)
from llm_api.config.settings import (
    DEFAULT_BASE_URL,
    PROJECT_CONFIG_FILENAME,
    build_payload,
    build_payload_from_content,
    find_project_config_path,
    load_project_config,
    resolve_api_key,
    resolve_base_url,
    resolve_model,
    resolve_reasoning_effort,
    resolve_web_search,
)
from llm_api.errors import ConfigurationError


class ConfigTests(unittest.TestCase):
    def test_default_base_url_uses_placeholder_endpoint(self) -> None:
        self.assertEqual(DEFAULT_BASE_URL, "https://api.example.com/v1/responses")
        self.assertNotIn("intelalloc", DEFAULT_BASE_URL)

    def test_invalid_reasoning_effort_falls_back_to_medium(self) -> None:
        self.assertEqual(resolve_reasoning_effort("bad-value"), "medium")

    def test_env_reasoning_effort_is_used_when_argument_is_none(self) -> None:
        with mock.patch.dict(os.environ, {"OPENAI_REASONING_EFFORT": "high"}, clear=False):
            self.assertEqual(resolve_reasoning_effort(None), "high")

    def test_build_payload_includes_web_search(self) -> None:
        payload = build_payload(
            question="你好",
            model="gpt-5.4",
            reasoning_effort="medium",
            web_search=True,
        )
        self.assertEqual(payload["model"], "gpt-5.4")
        self.assertEqual(payload["reasoning"]["effort"], "medium")
        self.assertEqual(payload["input"][0]["content"][0]["text"], "你好")
        self.assertEqual(payload["tools"], [{"type": "web_search"}])
        self.assertEqual(payload["tool_choice"], "auto")

    def test_build_payload_can_disable_web_search(self) -> None:
        payload = build_payload(
            question="你好",
            model="gpt-5.4",
            reasoning_effort="medium",
            web_search=False,
        )
        self.assertNotIn("tools", payload)
        self.assertNotIn("tool_choice", payload)

    def test_build_payload_from_content_supports_image_and_text(self) -> None:
        payload = build_payload_from_content(
            content_items=[
                {"type": "input_image", "image_url": "data:image/png;base64,abc", "detail": "high"},
                {"type": "input_text", "text": "请识别图片内容"},
            ],
            model="gpt-5.4",
            reasoning_effort="medium",
            web_search=False,
        )
        self.assertEqual(payload["input"][0]["content"][0]["type"], "input_image")
        self.assertEqual(payload["input"][0]["content"][1]["text"], "请识别图片内容")

    def test_missing_api_key_raises_configuration_error(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ConfigurationError):
                resolve_api_key(None)

    def test_load_project_config_returns_empty_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch("pathlib.Path.cwd", return_value=Path(tmpdir)):
                self.assertEqual(load_project_config(), {})

    def test_find_project_config_path_searches_parent_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            nested = root / "a" / "b"
            nested.mkdir(parents=True)
            config_path = root / PROJECT_CONFIG_FILENAME
            config_path.write_text('{"model":"gpt-5.4"}', encoding="utf-8")
            self.assertEqual(find_project_config_path(nested), config_path.resolve())

    def test_load_project_config_reads_json_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / PROJECT_CONFIG_FILENAME
            config_path.write_text('{"model":"gpt-5.4","web_search":false}', encoding="utf-8")
            self.assertEqual(load_project_config(config_path), {"model": "gpt-5.4", "web_search": False})

    def test_load_project_config_rejects_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / PROJECT_CONFIG_FILENAME
            config_path.write_text("{bad json}", encoding="utf-8")
            with self.assertRaises(ConfigurationError):
                load_project_config(config_path)

    def test_config_value_is_used_when_env_absent(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True):
            config = {
                "api_key": "cfg-key",
                "base_url": "https://cfg.example/v1/responses",
                "model": "cfg-model",
                "reasoning_effort": "high",
                "web_search": False,
            }
            self.assertEqual(resolve_api_key(None, config=config), "cfg-key")
            self.assertEqual(resolve_base_url(None, config=config), "https://cfg.example/v1/responses")
            self.assertEqual(resolve_model(None, config=config), "cfg-model")
            self.assertEqual(resolve_reasoning_effort(None, config=config), "high")
            self.assertFalse(resolve_web_search(None, config=config))

    def test_env_overrides_project_config(self) -> None:
        config = {
            "api_key": "cfg-key",
            "base_url": "https://cfg.example/v1/responses",
            "model": "cfg-model",
            "reasoning_effort": "high",
            "web_search": False,
        }
        with mock.patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "env-key",
                "OPENAI_BASE_URL": "https://env.example/v1/responses",
                "OPENAI_MODEL": "env-model",
                "OPENAI_REASONING_EFFORT": "low",
                "OPENAI_WEB_SEARCH": "true",
            },
            clear=True,
        ):
            self.assertEqual(resolve_api_key(None, config=config), "env-key")
            self.assertEqual(resolve_base_url(None, config=config), "https://env.example/v1/responses")
            self.assertEqual(resolve_model(None, config=config), "env-model")
            self.assertEqual(resolve_reasoning_effort(None, config=config), "low")
            self.assertTrue(resolve_web_search(None, config=config))

    def test_explicit_argument_overrides_env_and_config(self) -> None:
        config = {"api_key": "cfg-key", "model": "cfg-model", "web_search": False}
        with mock.patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "env-key", "OPENAI_MODEL": "env-model", "OPENAI_WEB_SEARCH": "false"},
            clear=True,
        ):
            self.assertEqual(resolve_api_key("arg-key", config=config), "arg-key")
            self.assertEqual(resolve_model("arg-model", config=config), "arg-model")
            self.assertTrue(resolve_web_search(True, config=config))

    def test_invalid_config_bool_raises_configuration_error(self) -> None:
        with self.assertRaises(ConfigurationError):
            resolve_web_search(None, config={"web_search": "maybe"})

    def test_supported_text_extensions_come_from_config(self) -> None:
        self.assertEqual(
            get_supported_text_file_extensions(),
            (
                ".txt",
                ".md",
                ".json",
                ".command",
                ".log",
                ".sh",
                ".csh",
                ".zsh",
                ".yaml",
                ".yml",
                ".toml",
                ".html",
                ".htm",
            ),
        )

    def test_supported_image_extensions_come_from_config(self) -> None:
        self.assertEqual(
            get_supported_image_file_extensions(),
            (".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tiff", ".tif"),
        )

    def test_text_file_validation_is_case_insensitive(self) -> None:
        path = validate_text_file_path("example.JSON")
        self.assertEqual(path.name, "example.JSON")

    def test_image_file_validation_is_case_insensitive(self) -> None:
        path = validate_image_file_path("example.PNG")
        self.assertEqual(path.name, "example.PNG")

    def test_text_file_rejects_unsupported_extension(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, build_unsupported_text_file_message()):
            validate_text_file_path("sample.docx")

    def test_image_file_rejects_unsupported_extension(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, build_unsupported_image_file_message()):
            validate_image_file_path("sample.heic")

    def test_read_text_file_reads_supported_file(self) -> None:
        with mock.patch("pathlib.Path.read_text", return_value="hello") as mock_read_text:
            text = read_text_file("sample.md")
        self.assertEqual(text, "hello")
        mock_read_text.assert_called_once_with(encoding="utf-8")

    def test_build_input_image_item_rejects_unsupported_extension(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, build_unsupported_image_file_message()):
            build_input_image_item("sample.pdf")


if __name__ == "__main__":
    unittest.main()
