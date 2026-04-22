import os
import json
import requests

# =========================
# 基础配置
# =========================

# 你的 Responses API 地址
BASE_URL = "https://api.example.com/v1/responses"

# 模型名称
MODEL = "gpt-5.4"

# 参考你当前 codex 配置中的 model_reasoning_effort
# 可选值通常包括：
# none / minimal / low / medium / high / xhigh
MODEL_REASONING_EFFORT = "medium"

# 是否启用内置 web_search 工具
# 这里按你的要求，最终版默认开启
ENABLE_WEB_SEARCH = True

# 工具调用策略：
# auto = 由模型自行决定是否使用工具
# 这里按你的要求固定为 auto
TOOL_CHOICE = "auto"


# =========================
# 工具函数
# =========================

def get_api_key() -> str:
    """
    从环境变量读取 API Key。

    运行脚本前，请先在终端设置：
        export OPENAI_API_KEY="你的key"

    如果没有设置，会直接报错，避免请求发出去才发现问题。
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("请先设置环境变量 OPENAI_API_KEY")
    return api_key


def normalize_reasoning_effort(effort: str) -> str:
    """
    对 reasoning effort 做简单规范化。
    如果传入值不在允许范围内，就退回到 medium。

    这样做的好处是：
    - 你以后改配置时，不容易因为拼错字符串导致请求异常
    - 保留和 codex 配置一致的使用习惯
    """
    allowed = {"none", "minimal", "low", "medium", "high", "xhigh"}
    effort = (effort or "medium").lower()
    return effort if effort in allowed else "medium"


def build_payload(question: str) -> dict:
    """
    构造 Responses API 的请求体。

    这里保留了：
    - model
    - reasoning.effort
    - input
    - web_search 工具
    - tool_choice = auto

    说明：
    1. input 使用 Responses API 推荐的结构化格式
    2. web_search 配置会始终带上
    3. tool_choice 固定为 auto，不做额外判断逻辑
    """
    payload = {
        "model": MODEL,
        "reasoning": {
            "effort": normalize_reasoning_effort(MODEL_REASONING_EFFORT)
        },
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": question
                    }
                ]
            }
        ]
    }

    if ENABLE_WEB_SEARCH:
        payload["tools"] = [
            {
                "type": "web_search"
            }
        ]
        payload["tool_choice"] = TOOL_CHOICE

    return payload


def send_request(payload: dict, timeout=(10, 180)) -> dict:
    """
    发送 HTTP 请求到 Responses API，并返回解析后的 JSON。

    timeout 说明：
    - 第一个数字 10：连接超时 10 秒
    - 第二个数字 180：读取超时 180 秒

    之所以把读取超时设得更长，是因为 reasoning 打开后，
    服务端有时会慢一些。
    """
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
    }

    response = requests.post(
        BASE_URL,
        headers=headers,
        json=payload,
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def extract_output_text(data: dict) -> str:
    """
    从 Responses API 返回中提取最终文本答案。

    Responses API 的结果通常在：
        data["output"][...]["content"][...]["text"]

    这里做了遍历式提取，兼容性更好。
    如果未来响应里有多个文本块，也能拼接起来。
    """
    texts = []

    for item in data.get("output", []):
        if item.get("type") != "message":
            continue

        for content in item.get("content", []):
            if content.get("type") == "output_text":
                text = content.get("text", "")
                if text:
                    texts.append(text)

    return "\n".join(texts).strip()


def extract_reasoning_info(data: dict) -> dict:
    """
    提取 reasoning 相关信息，方便你在终端里确认当前请求使用了什么 effort。
    """
    reasoning = data.get("reasoning", {}) or {}
    return {
        "effort": reasoning.get("effort"),
        "summary": reasoning.get("summary"),
    }


def extract_usage_info(data: dict) -> dict:
    """
    提取 token 使用情况。

    这里保留常用的几项：
    - input_tokens
    - output_tokens
    - reasoning_tokens
    - total_tokens

    方便你日后观察：
    - 问题长短
    - 推理成本
    - 总消耗
    """
    usage = data.get("usage", {}) or {}
    output_details = usage.get("output_tokens_details", {}) or {}

    return {
        "input_tokens": usage.get("input_tokens", 0),
        "output_tokens": usage.get("output_tokens", 0),
        "reasoning_tokens": output_details.get("reasoning_tokens", 0),
        "total_tokens": usage.get("total_tokens", 0),
    }


def ask(question: str) -> dict:
    """
    对外暴露的主调用函数。

    输入：
        question: 你要问模型的问题

    输出：
        一个字典，包含：
        - answer: 模型文本回答
        - reasoning: reasoning 信息
        - usage: token 用量
        - raw: 原始响应 JSON（调试用）
    """
    payload = build_payload(question)
    data = send_request(payload)

    return {
        "answer": extract_output_text(data),
        "reasoning": extract_reasoning_info(data),
        "usage": extract_usage_info(data),
        "raw": data,
    }


# =========================
# 主程序示例
# =========================

if __name__ == "__main__":
    # 这里放一个默认测试问题。
    # 你后续只需要改这个 question 即可。
    question = "请联网搜索 MSFT 股票当前的收盘价，并告诉我这是哪一天的收盘价。"

    try:
        result = ask(question)

        print("=== QUESTION ===")
        print(question)

        print("\n=== ANSWER ===")
        print(result["answer"] or "[empty]")

        print("\n=== REASONING ===")
        print(json.dumps(result["reasoning"], ensure_ascii=False, indent=2))

        print("\n=== USAGE ===")
        print(json.dumps(result["usage"], ensure_ascii=False, indent=2))

        # 如果你后续要排查问题，可以打开下面两行查看完整返回
        # print("\n=== RAW RESPONSE ===")
        # print(json.dumps(result["raw"], ensure_ascii=False, indent=2))

    except Exception as e:
        print("ERROR:", type(e).__name__, str(e))
