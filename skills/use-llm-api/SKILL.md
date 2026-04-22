---
name: use-llm-api
description: 在另一个 Python 项目中接入并使用本仓库提供的 llm_api shared library 与 CLI。适用于 Codex 需要复用已有 OpenAI-compatible API client、避免临时手写 HTTP 请求、为目标项目补齐本地安装/配置/调用代码、或判断应使用 ask()、ask_text()、ask_text_file()、ask_image()、llm-api ask ... 的场景。
---

# 快速执行

- 优先复用 `llm_api`，不要在目标项目里重新手写 OpenAI-compatible HTTP 请求。
- 优先使用正式 package API，不要扩展 `original_reference/` 下的历史脚本。
- 先确认目标项目是否已经安装并配置 `llm_api`；如果没有，按 [接入模板](./references/other_project_integration.md) 执行。

# 选择调用入口

- 纯文本输入：
  - 使用 `ask()` 或 `ask_text()`
- 文本文件输入：
  - 使用 `ask_text_file()`
  - 或使用 CLI `llm-api ask --text-file ... --prompt ...`
- 图片输入：
  - 使用 `ask_image()`
  - 或使用 CLI `llm-api ask --image-file ... --prompt ...`
- 图片需要额外上下文：
  - 为 `ask_image()` 或 CLI 追加 `context_text` / `--context-text`
- 只需要命令行快速验证配置或行为：
  - 使用 `llm-api ask ...`

# 接入步骤

1. 进入目标项目目录并激活该项目自己的虚拟环境。
2. 通过本地路径安装 `llm_api`，默认参考：

```bash
python -m pip install -e /path/to/llm_api
```

3. 在目标项目根目录放置 `.llm_api.json`，或通过环境变量提供 `api_key`、`base_url`、`model` 等配置。
4. 先运行 `llm-api ask --show-config`，确认目标项目根目录的配置已被识别。
5. 再补最小调用代码或 CLI 调用，避免一上来写复杂封装。

# 代码模式

```python
from llm_api import ask, ask_image, ask_text_file

text_result = ask("请总结一下这个任务要做什么")
print(text_result.answer)

file_result = ask_text_file(
    "data/input.json",
    prompt="解释这个文件的结构和用途",
)
print(file_result.answer)

image_result = ask_image(
    "screenshots/demo.png",
    prompt="请识别图片中的文字，并说明它展示的内容",
)
print(image_result.answer)
```

# 能力边界

- 当前正式支持：
  - `input_text`
  - `input_image`
  - text file 白名单中的文本文件
- 当前不要建议：
  - `input_file`
  - `.docx` 直传
  - `.pdf` 直传
  - `.xlsx` 直传
  - “万能文件参数”方案
- 遇到 rich file：
  - 先转换为支持的文本
  - 或先转换为支持的图片

# 参考资料

- 需要完整跨项目接入步骤时，读取 [接入模板](./references/other_project_integration.md)。
- 如果当前环境也能访问 `llm_api` 仓库，再补充查看仓库根目录的 `README.md` 和 `src/llm_api/` 下的正式模块。
- 需要确认包内边界时，优先查看 `src/llm_api/` 下的正式模块，不要把 `original_reference/` 当作 production code。
