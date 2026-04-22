# AGENTS

## 项目定位
- 本仓库是一个 Python-only 的 LLM client 项目。
- 产品方向为：shared library 优先，CLI 次之，repo-local Codex skill 用于提供使用指引。
- 后端目标是 OpenAI-compatible API，包括支持自定义 `base_url` 的 gateway。
- 本仓库不是 MCP server，也不是 hook 集合。

## 当前阶段
- 当前阶段以项目结构和文档初始化为主。
- 除非任务明确要求实现功能，否则不要在 package 中提前加入 feature code。
- `original_reference/` 只作为只读参考材料，不视为 production code。

## 目录职责
- `src/llm_api/`：正式的 Python package
- `src/llm_api/cli/`：CLI entrypoint 与输出格式化
- `src/llm_api/config/`：config 读取、默认值和 environment parsing
- `src/llm_api/transport/`：HTTP transport 与请求发送
- `src/llm_api/parsing/`：response 提取、usage 解析和 error shaping
- `tests/unit/`：纯逻辑和模块行为的 unit tests
- `tests/cli/`：CLI 行为测试
- `tests/integration/`：基于 mock 的 integration tests
- `docs/`：面向开发者的文档
- `skills/use-llm-api/`：repo-local Codex skill
- `original_reference/`：历史脚本和迁移参考材料

## 工程规则
- 所有 secret 必须留在 source file 之外，通过 environment variables 或显式参数读取。
- 不要继续把旧的单文件脚本扩展为正式 product entrypoint。
- library 层和 CLI 层的职责必须分离。
- 优先使用显式类型、小函数和清晰边界，避免隐藏的 global behavior。
- 默认使用基于 mock 的测试来覆盖网络行为；真实远端调用只能作为显式选择的补充验证。

## 迁移规则
- 当前参考行为位于 `original_reference/mini_response_client.py`。
- 正式实现应当在 `src/llm_api/` 下按清晰模块边界重新组织。
- 只有当参考脚本中的行为仍然符合 package 设计时，才迁移为正式能力。

## 文档规则
- `README.md` 应面向人类开发者解释项目。
- `skills/` 下的文件应说明 Codex 应如何使用本仓库。
- architecture 和 design decision 应放在 `docs/` 中，而不是散落在临时笔记里。
- 从现在开始，后续新增的所有文档默认使用中文书写。
- 常用术语可保留英文，例如 shared library、CLI、skill、config、usage、response、mock、integration test。
- 如果某个文档需要中英文混排，默认以中文为主，英文术语只用于避免歧义或保持行业惯例。
- 没有用户的明确指示，禁止新增、修改或重写任何 handoff 文档，包括 `phase*_handoff.md`。

## 仓库卫生
- 在补充 `.gitignore` 后，应忽略 editor swap file、cache、virtual environment 等临时文件。
- 仓库根目录只保留高信号的项目文件，不堆放临时脚本或杂项产物。
