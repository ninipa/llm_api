from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class ReasoningInfo:
    effort: str | None
    summary: Any

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class UsageInfo:
    input_tokens: int
    output_tokens: int
    reasoning_tokens: int
    total_tokens: int

    def to_dict(self) -> dict[str, int]:
        return asdict(self)


@dataclass(slots=True)
class AskResult:
    answer: str
    reasoning: ReasoningInfo
    usage: UsageInfo
    raw: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "answer": self.answer,
            "reasoning": self.reasoning.to_dict(),
            "usage": self.usage.to_dict(),
            "raw": self.raw,
        }
