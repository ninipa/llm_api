from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from llm_api.errors import ConfigurationError

DEFAULT_BASE_URL = "https://api.example.com/v1/responses"
DEFAULT_MODEL = "gpt-5.4"
DEFAULT_REASONING_EFFORT = "medium"
DEFAULT_TIMEOUT = (10.0, 180.0)
DEFAULT_WEB_SEARCH = True
PROJECT_CONFIG_FILENAME = ".llm_api.json"
ALLOWED_REASONING_EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh"}


def find_project_config_path(start_dir: str | Path | None = None) -> Path | None:
    current = Path(start_dir or Path.cwd()).resolve()
    for candidate_dir in (current, *current.parents):
        candidate = candidate_dir / PROJECT_CONFIG_FILENAME
        if candidate.exists():
            return candidate
    return None


def load_project_config(config_path: str | Path | None = None) -> dict[str, Any]:
    resolved_path = Path(config_path) if config_path else find_project_config_path()
    if resolved_path is None:
        return {}
    try:
        payload = json.loads(resolved_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"项目配置文件不是合法 JSON：{resolved_path}") from exc
    if not isinstance(payload, dict):
        raise ConfigurationError(f"项目配置文件顶层结构必须是对象：{resolved_path}")
    return payload


def resolve_api_key(api_key: str | None, *, config: dict[str, Any] | None = None) -> str:
    value = (api_key or os.getenv("OPENAI_API_KEY") or _config_str(config, "api_key") or "").strip()
    if not value:
        raise ConfigurationError("缺少 API key，请设置 OPENAI_API_KEY、项目配置文件中的 api_key，或显式传入 api_key")
    return value


def resolve_base_url(base_url: str | None, *, config: dict[str, Any] | None = None) -> str:
    value = (base_url or os.getenv("OPENAI_BASE_URL") or _config_str(config, "base_url") or DEFAULT_BASE_URL).strip()
    if not value:
        raise ConfigurationError("base_url 不能为空")
    return value


def resolve_model(model: str | None, *, config: dict[str, Any] | None = None) -> str:
    value = (model or os.getenv("OPENAI_MODEL") or _config_str(config, "model") or DEFAULT_MODEL).strip()
    if not value:
        raise ConfigurationError("model 不能为空")
    return value


def normalize_reasoning_effort(effort: str | None) -> str:
    value = (effort or DEFAULT_REASONING_EFFORT).strip().lower()
    return value if value in ALLOWED_REASONING_EFFORTS else DEFAULT_REASONING_EFFORT


def resolve_reasoning_effort(reasoning_effort: str | None, *, config: dict[str, Any] | None = None) -> str:
    env_value = os.getenv("OPENAI_REASONING_EFFORT")
    return normalize_reasoning_effort(reasoning_effort or env_value or _config_str(config, "reasoning_effort"))


def resolve_web_search(web_search: bool | None, *, config: dict[str, Any] | None = None) -> bool:
    if web_search is not None:
        return bool(web_search)
    env_value = os.getenv("OPENAI_WEB_SEARCH")
    if env_value is not None:
        return _parse_bool(env_value, source="OPENAI_WEB_SEARCH")
    if config is not None and "web_search" in config:
        return _parse_bool(config["web_search"], source="project config")
    return DEFAULT_WEB_SEARCH


def build_payload(
    *,
    question: str,
    model: str,
    reasoning_effort: str,
    web_search: bool,
) -> dict:
    return build_payload_from_content(
        content_items=[
            {
                "type": "input_text",
                "text": question,
            }
        ],
        model=model,
        reasoning_effort=reasoning_effort,
        web_search=web_search,
    )


def build_payload_from_content(
    *,
    content_items: list[dict[str, Any]],
    model: str,
    reasoning_effort: str,
    web_search: bool,
) -> dict:
    payload = {
        "model": model,
        "reasoning": {"effort": normalize_reasoning_effort(reasoning_effort)},
        "input": [
            {
                "role": "user",
                "content": content_items,
            }
        ],
    }

    if web_search:
        payload["tools"] = [{"type": "web_search"}]
        payload["tool_choice"] = "auto"

    return payload


def _config_str(config: dict[str, Any] | None, key: str) -> str | None:
    if config is None or key not in config or config[key] is None:
        return None
    value = config[key]
    if not isinstance(value, str):
        raise ConfigurationError(f"项目配置中的 {key} 必须是字符串")
    return value


def _parse_bool(value: Any, *, source: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"1", "true", "yes", "on"}:
            return True
        if lowered in {"0", "false", "no", "off"}:
            return False
    raise ConfigurationError(f"{source} 中的布尔值不合法：{value!r}")
