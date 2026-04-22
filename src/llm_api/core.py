from __future__ import annotations

from pathlib import Path

from llm_api.config.settings import (
    DEFAULT_TIMEOUT,
    build_payload,
    build_payload_from_content,
    load_project_config,
    resolve_api_key,
    resolve_base_url,
    resolve_model,
    resolve_reasoning_effort,
    resolve_web_search,
)
from llm_api.config.input_support import (
    build_input_image_item,
    build_input_text_item,
    read_text_file,
)
from llm_api.models import AskResult
from llm_api.parsing.responses import parse_ask_result
from llm_api.transport.client import send_payload


def ask(
    question: str,
    *,
    model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    reasoning_effort: str | None = "medium",
    web_search: bool | None = None,
    timeout: tuple[float, float] = DEFAULT_TIMEOUT,
) -> AskResult:
    return ask_text(
        question,
        model=model,
        base_url=base_url,
        api_key=api_key,
        reasoning_effort=reasoning_effort,
        web_search=web_search,
        timeout=timeout,
    )


def ask_text(
    text: str,
    *,
    model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    reasoning_effort: str | None = "medium",
    web_search: bool | None = None,
    timeout: tuple[float, float] = DEFAULT_TIMEOUT,
) -> AskResult:
    cleaned_text = (text or "").strip()
    if not cleaned_text:
        raise ValueError("text 不能为空")

    project_config = load_project_config()
    resolved_model = resolve_model(model, config=project_config)
    resolved_base_url = resolve_base_url(base_url, config=project_config)
    resolved_api_key = resolve_api_key(api_key, config=project_config)
    resolved_reasoning_effort = resolve_reasoning_effort(reasoning_effort, config=project_config)
    resolved_web_search = resolve_web_search(web_search, config=project_config)

    payload = build_payload(
        question=cleaned_text,
        model=resolved_model,
        reasoning_effort=resolved_reasoning_effort,
        web_search=resolved_web_search,
    )
    data = send_payload(
        payload=payload,
        api_key=resolved_api_key,
        base_url=resolved_base_url,
        timeout=timeout,
    )
    return parse_ask_result(data)


def ask_text_file(
    path: str | Path,
    *,
    prompt: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    reasoning_effort: str | None = "medium",
    web_search: bool | None = None,
    timeout: tuple[float, float] = DEFAULT_TIMEOUT,
) -> AskResult:
    text = read_text_file(path)
    content_items = [build_input_text_item(text)]
    if prompt:
        cleaned_prompt = prompt.strip()
        if cleaned_prompt:
            content_items.append(build_input_text_item(cleaned_prompt))
    return _ask_from_content_items(
        content_items=content_items,
        model=model,
        base_url=base_url,
        api_key=api_key,
        reasoning_effort=reasoning_effort,
        web_search=web_search,
        timeout=timeout,
    )


def ask_image(
    path: str | Path,
    *,
    prompt: str,
    context_text: str | None = None,
    model: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    reasoning_effort: str | None = "medium",
    web_search: bool | None = None,
    timeout: tuple[float, float] = DEFAULT_TIMEOUT,
) -> AskResult:
    cleaned_prompt = (prompt or "").strip()
    if not cleaned_prompt:
        raise ValueError("ask_image 的 prompt 不能为空")

    content_items = [
        build_input_image_item(path),
        build_input_text_item(cleaned_prompt),
    ]
    cleaned_context = (context_text or "").strip()
    if cleaned_context:
        content_items.append(build_input_text_item(cleaned_context))
    return _ask_from_content_items(
        content_items=content_items,
        model=model,
        base_url=base_url,
        api_key=api_key,
        reasoning_effort=reasoning_effort,
        web_search=web_search,
        timeout=timeout,
    )


def _ask_from_content_items(
    *,
    content_items: list[dict],
    model: str | None,
    base_url: str | None,
    api_key: str | None,
    reasoning_effort: str | None,
    web_search: bool | None,
    timeout: tuple[float, float],
) -> AskResult:
    project_config = load_project_config()
    resolved_model = resolve_model(model, config=project_config)
    resolved_base_url = resolve_base_url(base_url, config=project_config)
    resolved_api_key = resolve_api_key(api_key, config=project_config)
    resolved_reasoning_effort = resolve_reasoning_effort(reasoning_effort, config=project_config)
    resolved_web_search = resolve_web_search(web_search, config=project_config)

    payload = build_payload_from_content(
        content_items=content_items,
        model=resolved_model,
        reasoning_effort=resolved_reasoning_effort,
        web_search=resolved_web_search,
    )
    data = send_payload(
        payload=payload,
        api_key=resolved_api_key,
        base_url=resolved_base_url,
        timeout=timeout,
    )
    return parse_ask_result(data)
