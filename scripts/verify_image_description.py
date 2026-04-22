from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from llm_api import ask_image


DEFAULT_PROMPT = "解析一下这张图表达了什么"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Send one image to llm_api and optionally verify expected keywords in the answer.",
    )
    parser.add_argument("image_path", help="Path to the image file")
    parser.add_argument(
        "--prompt",
        default=DEFAULT_PROMPT,
        help=f"Question to ask about the image. Default: {DEFAULT_PROMPT}",
    )
    parser.add_argument(
        "--context-text",
        help="Optional extra text context passed along with the image",
    )
    parser.add_argument(
        "--expect",
        action="append",
        default=[],
        help="Expected keyword in the answer. Can be passed multiple times.",
    )
    parser.add_argument("--model", help="Override the default model")
    parser.add_argument("--base-url", help="Override the default base URL")
    parser.add_argument("--api-key", help="Override the API key")
    parser.add_argument("--reasoning-effort", help="Override the default reasoning effort")
    parser.add_argument(
        "--no-web-search",
        action="store_true",
        help="Disable web_search for this request",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = ask_image(
        args.image_path,
        prompt=args.prompt,
        context_text=args.context_text,
        model=args.model,
        base_url=args.base_url,
        api_key=args.api_key,
        reasoning_effort=args.reasoning_effort,
        web_search=False if args.no_web_search else None,
    )

    print(result.answer)

    missing = [
        keyword
        for keyword in args.expect
        if keyword.strip() and keyword.lower() not in result.answer.lower()
    ]
    if missing:
        print("\n[verification]", file=sys.stderr)
        print(f"Missing expected keywords: {', '.join(missing)}", file=sys.stderr)
        return 1

    if args.expect:
        print("\n[verification]")
        print("All expected keywords were found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
