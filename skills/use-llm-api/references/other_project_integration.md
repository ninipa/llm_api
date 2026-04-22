# 另一个 Python 项目接入 llm_api

## 目标

在另一个 Python 项目里复用本仓库提供的 `llm_api` shared library 或 CLI，避免临时手写 OpenAI-compatible HTTP 请求。

## 前提

- 本机上已经有 `llm_api` 仓库。
- 目标项目是 Python 项目。
- 建议在目标项目自己的虚拟环境中安装 `llm_api`。

## 接入步骤

1. 进入目标项目目录。

```bash
cd /path/to/your_other_project
```

2. 创建并激活目标项目自己的虚拟环境；如果已有虚拟环境，则激活现有环境。

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. 通过本地路径安装 `llm_api`。

```bash
python -m pip install -e /path/to/llm_api
```

4. 在目标项目根目录创建 `.llm_api.json`，或通过环境变量提供同等配置。

最小示例：

```json
{
  "api_key": "替换为你的 API key",
  "base_url": "https://api.example.com/v1/responses",
  "model": "gpt-5.4",
  "reasoning_effort": "medium",
  "web_search": true
}
```

5. 先验证配置是否生效。

```bash
llm-api ask --show-config
```

期望结果：

- `project_config_path` 指向目标项目根目录的 `.llm_api.json`
- `project_config` 中能看到当前配置字段

6. 再补最小调用代码或 CLI 调用。

## Python 调用模板

### 纯文本调用

```python
from llm_api import ask

result = ask("请总结一下这个任务要做什么")
print(result.answer)
```

### 文本文件调用

```python
from llm_api import ask_text_file

result = ask_text_file(
    "data/input.json",
    prompt="解释这个 JSON 的结构和用途",
)
print(result.answer)
```

### 图片调用

```python
from llm_api import ask_image

result = ask_image(
    "screenshots/demo.png",
    prompt="请识别图片中的文字，并说明它展示的内容",
)
print(result.answer)
```

### 图片加文本上下文

```python
from llm_api import ask_image

result = ask_image(
    "screenshots/demo.png",
    prompt="请解释图片里的主要信息",
    context_text="这是项目里的接口错误截图，请按开发调试场景理解",
)
print(result.answer)
```

## 最小验证顺序

1. 确认能导入：

```bash
python -c "from llm_api import ask, ask_text_file, ask_image; print('ok')"
```

2. 确认配置文件被识别：

```bash
llm-api ask --show-config
```

3. 跑一条最简单的文本调用：

```python
from llm_api import ask
print(ask("你好，请简要自我介绍").answer)
```

4. 如果目标项目里有 `.json/.md/.txt/.sh` 等文本文件，再跑一条 `ask_text_file()`。

5. 如果目标项目里有可用图片，再跑一条 `ask_image()`。

## 当前能力边界

### 正式支持

- 纯文本字符串
- text file 白名单中的文件
- image file 白名单中的图片

### 当前不要建议

- `input_file`
- `.docx` 直传
- `.pdf` 直传
- `.xlsx` 直传
- rich file 直传

如果目标项目里出现 `docx/pdf/xlsx`，先转换为支持的文本或图片，再调用 `llm_api`。
