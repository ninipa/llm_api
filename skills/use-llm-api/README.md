# 使用 LLM API 的 Skill

此目录用于放置 repo-local Codex skill，目标是让 Codex 在别的仓库里优先复用本项目提供的 LLM 调用能力，而不是临时手写 HTTP 请求。

## 当前推荐用法
- 如果调用方已经在 Python 代码里：
  - 优先使用 `ask()`、`ask_text()`、`ask_text_file()`、`ask_image()`
- 如果调用方只需要命令行快速调用：
  - 优先使用 `llm-api ask ...`

## 当前输入策略
- 纯文本：
  - 使用 `ask()` 或 `ask_text()`
- text file：
  - 使用 `ask_text_file()`
  - 或 CLI 的 `--text-file`
- 图片：
  - 使用 `ask_image()`
  - 或 CLI 的 `--image-file --prompt`
- rich file：
  - 当前不要直传
  - 应先转换为支持的文本或图片

## 当前能力边界
- 当前 endpoint 已验证：
  - `input_text` 可用
  - `input_image` 可用
- 当前 endpoint 未打通：
  - `input_file`

因此 skill 在生成调用方案时，不应建议：
- `docx/pdf/xlsx` 直传
- “万能文件参数”方案
