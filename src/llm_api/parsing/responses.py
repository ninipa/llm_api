from __future__ import annotations

from typing import Any

from llm_api.models import AskResult, ReasoningInfo, UsageInfo


def extract_output_text(data: dict[str, Any]) -> str:
    texts: list[str] = []
    for item in data.get("output", []):
        if item.get("type") != "message":
            continue
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                text = content.get("text", "")
                if text:
                    texts.append(text)
    return "\n".join(texts).strip()


def extract_reasoning_info(data: dict[str, Any]) -> ReasoningInfo:
    reasoning = data.get("reasoning", {}) or {}
    return ReasoningInfo(
        effort=reasoning.get("effort"),
        summary=reasoning.get("summary"),
    )


def extract_usage_info(data: dict[str, Any]) -> UsageInfo:
    usage = data.get("usage", {}) or {}
    output_details = usage.get("output_tokens_details", {}) or {}
    return UsageInfo(
        input_tokens=int(usage.get("input_tokens", 0) or 0),
        output_tokens=int(usage.get("output_tokens", 0) or 0),
        reasoning_tokens=int(output_details.get("reasoning_tokens", 0) or 0),
        total_tokens=int(usage.get("total_tokens", 0) or 0),
    )


def parse_ask_result(data: dict[str, Any]) -> AskResult:
    return AskResult(
        answer=extract_output_text(data),
        reasoning=extract_reasoning_info(data),
        usage=extract_usage_info(data),
        raw=data,
    )
