from __future__ import annotations

from typing import Any

import requests

from llm_api.errors import RequestError, ResponseFormatError


def send_payload(
    *,
    payload: dict[str, Any],
    api_key: str,
    base_url: str,
    timeout: tuple[float, float],
) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            base_url,
            headers=headers,
            json=payload,
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.exceptions.Timeout as exc:
        raise RequestError("请求超时，请稍后重试") from exc
    except requests.exceptions.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else "unknown"
        raise RequestError(f"远端返回 HTTP 错误，status={status_code}") from exc
    except requests.exceptions.RequestException as exc:
        raise RequestError(f"请求失败：{exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise ResponseFormatError("响应不是合法 JSON") from exc

    if not isinstance(data, dict):
        raise ResponseFormatError("响应 JSON 顶层结构必须是对象")

    return data
