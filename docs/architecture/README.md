# 架构说明

此目录用于存放 `llm_api` 项目的架构相关文档。

## 当前状态
- 目录已经预留，但尚未拆出独立架构文档
- 当前架构事实以 `src/llm_api/` 中的模块边界和 handoff 文档为准

## 后续优先沉淀内容
- `config -> core -> transport -> parsing` 的分层结构
- typed API 的输入模型与校验边界
- CLI 与 shared library 的关系
- 支持输入类型与后端能力边界的映射关系

## 相关入口
- `src/llm_api/core.py`
- `src/llm_api/config/`
- `src/llm_api/transport/`
- `src/llm_api/parsing/`
