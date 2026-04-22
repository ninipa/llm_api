from __future__ import annotations

import base64
import json
import mimetypes
from functools import lru_cache
from pathlib import Path
from typing import Any

from llm_api.errors import ConfigurationError


CONFIG_PATH = Path(__file__).with_name("input_extensions.json")


@lru_cache(maxsize=1)
def load_input_extensions() -> dict[str, tuple[str, ...]]:
    payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {
        "text_file_extensions": tuple(_normalize_extensions(payload["text_file_extensions"])),
        "image_file_extensions": tuple(_normalize_extensions(payload["image_file_extensions"])),
    }


def get_supported_text_file_extensions() -> tuple[str, ...]:
    return load_input_extensions()["text_file_extensions"]


def get_supported_image_file_extensions() -> tuple[str, ...]:
    return load_input_extensions()["image_file_extensions"]


def validate_text_file_path(path: str | Path) -> Path:
    resolved = Path(path)
    suffix = resolved.suffix.lower()
    if suffix not in get_supported_text_file_extensions():
        raise ConfigurationError(build_unsupported_text_file_message())
    return resolved


def validate_image_file_path(path: str | Path) -> Path:
    resolved = Path(path)
    suffix = resolved.suffix.lower()
    if suffix not in get_supported_image_file_extensions():
        raise ConfigurationError(build_unsupported_image_file_message())
    return resolved


def build_unsupported_text_file_message() -> str:
    extensions = ", ".join(get_supported_text_file_extensions())
    return f"该类型输入文件格式不支持。当前支持的 text file 扩展名：{extensions}"


def build_unsupported_image_file_message() -> str:
    extensions = ", ".join(get_supported_image_file_extensions())
    return f"该类型输入文件格式不支持。当前支持的 image file 扩展名：{extensions}"


def read_text_file(path: str | Path) -> str:
    resolved = validate_text_file_path(path)
    return resolved.read_text(encoding="utf-8")


def build_input_text_item(text: str) -> dict[str, str]:
    return {
        "type": "input_text",
        "text": text,
    }


def build_input_image_item(path: str | Path) -> dict[str, str]:
    resolved = validate_image_file_path(path)
    mime_type = mimetypes.guess_type(resolved.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(resolved.read_bytes()).decode("ascii")
    return {
        "type": "input_image",
        "image_url": f"data:{mime_type};base64,{encoded}",
        "detail": "high",
    }


def _normalize_extensions(values: list[Any]) -> list[str]:
    normalized: list[str] = []
    for value in values:
        if not isinstance(value, str):
            raise ConfigurationError("输入扩展名配置文件格式不合法")
        suffix = value.strip().lower()
        if not suffix.startswith("."):
            raise ConfigurationError("输入扩展名必须以 . 开头")
        normalized.append(suffix)
    return normalized
