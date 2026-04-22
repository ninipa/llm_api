from __future__ import annotations

import argparse
import json
import sys

from llm_api import ask, ask_image, ask_text_file
from llm_api.config import PROJECT_CONFIG_FILENAME, find_project_config_path, load_project_config
from llm_api.errors import LlmApiError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="llm-api", description="OpenAI-compatible LLM client CLI")
    subparsers = parser.add_subparsers(dest="command")

    ask_parser = subparsers.add_parser("ask", help="发起一次单轮提问")
    ask_parser.add_argument("question", nargs="?", help="问题文本；如果不提供则尝试从 stdin 读取")
    ask_parser.add_argument("--text-file", help="读取文本文件后发送，目前支持部分 text file 扩展名")
    ask_parser.add_argument("--image-file", help="发送图片文件，目前支持部分 image file 扩展名")
    ask_parser.add_argument("--prompt", help="图片输入时必填；文本文件输入时可选")
    ask_parser.add_argument("--context-text", help="图片输入时可选的额外文本上下文")
    ask_parser.add_argument("--model", help="覆盖默认 model")
    ask_parser.add_argument("--base-url", help="覆盖默认 base_url")
    ask_parser.add_argument("--api-key", help="显式传入 API key")
    ask_parser.add_argument("--reasoning-effort", help="覆盖默认 reasoning_effort")
    ask_parser.add_argument("--no-web-search", action="store_true", help="关闭 web_search")
    ask_parser.add_argument("--show-config", action="store_true", help=f"显示当前解析到的配置来源与默认值（包含 {PROJECT_CONFIG_FILENAME}）")
    ask_parser.add_argument("--show-usage", action="store_true", help="输出 usage 信息")
    ask_parser.add_argument("--show-reasoning", action="store_true", help="输出 reasoning 信息")
    ask_parser.add_argument("--show-raw", action="store_true", help="输出原始响应 JSON")
    ask_parser.set_defaults(handler=handle_ask)

    return parser


def _read_question(question: str | None) -> str:
    if question and question.strip():
        return question.strip()

    if not sys.stdin.isatty():
        text = sys.stdin.read().strip()
        if text:
            return text

    raise ValueError("缺少问题文本，请通过参数传入或从 stdin 提供内容")


def _validate_input_mode(args: argparse.Namespace) -> None:
    sources = [
        bool((args.question or "").strip()),
        bool(args.text_file),
        bool(args.image_file),
    ]
    if sum(sources) > 1:
        raise ValueError("question、--text-file、--image-file 不能同时使用")
    if args.image_file and not (args.prompt or "").strip():
        raise ValueError("使用 --image-file 时必须提供 --prompt")
    if args.context_text and not args.image_file:
        raise ValueError("--context-text 只允许与 --image-file 一起使用")


def handle_ask(args: argparse.Namespace) -> int:
    _validate_input_mode(args)
    if args.show_config:
        _print_resolved_config(args)
        return 0

    if args.image_file:
        result = ask_image(
            args.image_file,
            prompt=args.prompt,
            context_text=args.context_text,
            model=args.model,
            base_url=args.base_url,
            api_key=args.api_key,
            reasoning_effort=args.reasoning_effort,
            web_search=False if args.no_web_search else None,
        )
    elif args.text_file:
        result = ask_text_file(
            args.text_file,
            prompt=args.prompt,
            model=args.model,
            base_url=args.base_url,
            api_key=args.api_key,
            reasoning_effort=args.reasoning_effort,
            web_search=False if args.no_web_search else None,
        )
    else:
        question = _read_question(args.question)
        result = ask(
            question,
            model=args.model,
            base_url=args.base_url,
            api_key=args.api_key,
            reasoning_effort=args.reasoning_effort,
            web_search=False if args.no_web_search else None,
        )

    print(result.answer)

    if args.show_usage:
        print("\n[usage]")
        print(json.dumps(result.usage.to_dict(), ensure_ascii=False, indent=2))

    if args.show_reasoning:
        print("\n[reasoning]")
        print(json.dumps(result.reasoning.to_dict(), ensure_ascii=False, indent=2))

    if args.show_raw:
        print("\n[raw]")
        print(json.dumps(result.raw, ensure_ascii=False, indent=2))

    return 0


def _print_resolved_config(args: argparse.Namespace) -> None:
    config_path = find_project_config_path()
    project_config = load_project_config()
    payload = {
        "project_config_path": str(config_path) if config_path else None,
        "project_config": project_config,
        "cli_overrides": {
            "model": args.model,
            "base_url": args.base_url,
            "api_key": "[provided]" if args.api_key else None,
            "reasoning_effort": args.reasoning_effort,
            "web_search": False if args.no_web_search else None,
        },
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "handler"):
        parser.print_help(sys.stderr)
        return 2

    try:
        return args.handler(args)
    except (LlmApiError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
