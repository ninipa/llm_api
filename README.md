# llm_api

`llm_api` 是一个 Python-only 的 OpenAI-compatible LLM client 项目，目标是提供可复用的 shared library 和一个最小可用的 CLI。

## 当前能力
- 共享库入口：`llm_api.ask(...)`
- 新增 typed API：`ask_text(...)`、`ask_text_file(...)`、`ask_image(...)`
- CLI 入口：`llm-api ask ...`
- 支持自定义 `base_url`
- 支持开关 `web_search`
- 返回结构包含 `answer`、`reasoning`、`usage`、`raw`

## 文档导航
- `docs/usage/other_project_integration.md`
  - 另一个 Python 项目接入 `llm_api` 的执行模板
- `docs/usage/README.md`
  - 使用文档目录说明
- `docs/architecture/README.md`
  - 架构文档目录说明
- `docs/decisions/README.md`
  - 设计决策目录说明
- `examples/public_samples/`
  - public 仓库自带的安全示例文件

## 安装
在项目根目录执行：

```bash
pip install -e .
```

## 项目配置文件
当前支持项目级配置文件：

```text
.llm_api.json
```

示例文件可参考：

```text
.llm_api.example.json
```

示例内容：

```json
{
  "api_key": "替换为你的 API key",
  "base_url": "https://api.example.com/v1/responses",
  "model": "gpt-5.4",
  "reasoning_effort": "medium",
  "web_search": true
}
```

当前优先级：

1. CLI 显式参数
2. 环境变量
3. 项目配置文件 `.llm_api.json`
4. 代码默认值

## 环境变量
- `OPENAI_API_KEY`：必填
- `OPENAI_BASE_URL`：可选，用于覆盖默认 OpenAI-compatible endpoint
- `OPENAI_MODEL`：可选，用于覆盖默认模型
- `OPENAI_REASONING_EFFORT`：可选，用于覆盖默认 `reasoning_effort`
- `OPENAI_WEB_SEARCH`：可选，用于覆盖默认 `web_search`

## CLI 用法
最简单的调用：

```bash
llm-api ask "请总结一下什么是向量数据库"
```

读取 public 仓库自带的 JSON 示例并追加 prompt：

```bash
llm-api ask --text-file examples/public_samples/demo_input.json --prompt "这是什么内容，解析一下它的结构并猜测用途"
```

读取 public 仓库自带的 shell 示例并解释作用：

```bash
llm-api ask --text-file examples/public_samples/demo_script.command --prompt "解释这个 shell 脚本的主要步骤"
```

读取图片并识别内容：

```bash
llm-api ask --image-file /path/to/demo.png --prompt "请识别图片中的文字，并说明它展示的内容"
```

用独立脚本验证某张图片的描述是否命中预期关键词：

```bash
python3 scripts/verify_image_description.py /path/to/your_image.png \
  --prompt "解析一下这张图表达了什么" \
  --expect Transaction \
  --expect "Data Link" \
  --expect Physical \
  --expect TX \
  --expect RX
```

给图片补充文本上下文：

```bash
llm-api ask --image-file /path/to/demo.png --prompt "请解释图片里的主要信息" --context-text "这是一张命令行帮助截图"
```

查看当前解析到的项目配置与 CLI 覆盖值：

```bash
llm-api ask --show-config
```

显示 `usage`：

```bash
llm-api ask "请总结一下什么是向量数据库" --show-usage
```

关闭 `web_search`：

```bash
llm-api ask "请总结一下什么是向量数据库" --no-web-search
```

如果不传位置参数，CLI 会尝试从 `stdin` 读取问题文本。

当前支持的 `text file` 扩展名：

- `.txt`
- `.md`
- `.json`
- `.command`
- `.log`
- `.sh`
- `.csh`
- `.zsh`
- `.yaml`
- `.yml`
- `.toml`
- `.html`
- `.htm`

当前支持的 `image file` 扩展名：

- `.png`
- `.jpg`
- `.jpeg`
- `.webp`
- `.gif`
- `.bmp`
- `.tiff`
- `.tif`

当前不支持作为正式输入文件格式的 rich file 包括：

- `.docx`
- `.pdf`
- `.xlsx`

这类文件需要先转换成支持的文本或图片后再调用。

## Python 用法

```python
from llm_api import ask, ask_image, ask_text, ask_text_file

result = ask("请总结一下什么是向量数据库")
print(result.answer)
print(result.usage.total_tokens)

result = ask_text("请解释这段文本的作用")
print(result.answer)

result = ask_text_file(
    "examples/public_samples/demo_input.json",
    prompt="这是什么内容，解析一下它的结构并猜测用途",
)
print(result.answer)

result = ask_text_file(
    "examples/public_samples/demo_script.command",
    prompt="解释这个 shell 脚本的主要步骤",
)
print(result.answer)

result = ask_image(
    "/path/to/demo.png",
    prompt="请识别这张图里的文字，并说明它展示的内容",
)
print(result.answer)

result = ask_image(
    "/path/to/demo.png",
    prompt="请解释图片里的主要信息",
    context_text="这是一张命令行帮助截图",
)
print(result.answer)
```

## Public 仓库说明
- public 仓库不包含 `materials/`、handoff 文档和实验样本/结果
- 如果你需要测试文件输入能力，请使用 `examples/public_samples/` 中的安全示例，或替换为你自己的文件
- 本地 private 分支可以保留完整实验与素材，但不应直接推到 public 分支

## 参考代码
历史参考脚本保存在 `original_reference/mini_response_client.py`。该文件仅用于迁移参考，不作为正式入口维护。
