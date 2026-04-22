# 另一个项目接入模板

## 目标
本文档用于指导 AI agent 在“另一个 Python 项目”中接入并使用 `llm_api`。

适用场景：

- 目标项目也是 Python 项目
- 目标项目希望直接从 Python 调用 `llm_api`
- 当前安装方式采用本机本地路径安装
- 当前配置方式采用目标项目根目录的 `.llm_api.json`

这份文档优先面向 agent 直接执行，不展开背景介绍。

## 前提条件
开始前默认满足这些条件：

- 本机上已经有 `llm_api` 仓库
- 路径示例为：

```text
/path/to/llm_api
```

- 目标项目有自己的工作目录
- 建议在目标项目自己的虚拟环境中安装 `llm_api`

## 接入步骤

### 1. 进入目标项目

```bash
cd /path/to/your_other_project
```

### 2. 创建并激活虚拟环境
如果目标项目还没有虚拟环境：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

如果目标项目已有虚拟环境，则激活现有环境即可。

### 3. 安装本地 `llm_api`
在目标项目的虚拟环境中执行：

```bash
python -m pip install -e /path/to/llm_api
```

说明：

- 这是本机本地路径安装
- 安装后，目标项目中的 Python 应该可以直接：

```python
from llm_api import ask
```

### 4. 在目标项目根目录创建 `.llm_api.json`
在目标项目根目录创建：

```text
.llm_api.json
```

最小可用内容：

```json
{
  "api_key": "替换为你的 API key",
  "base_url": "https://api.example.com/v1/responses",
  "model": "gpt-5.4",
  "reasoning_effort": "medium",
  "web_search": true
}
```

注意：

- `.llm_api.json` 不应提交到版本库
- 如果目标项目还没有忽略规则，应把它加入 `.gitignore`

### 5. 验证配置是否生效
在目标项目根目录执行：

```bash
llm-api ask --show-config
```

期望结果：

- `project_config_path` 指向目标项目根目录的 `.llm_api.json`
- `project_config` 中能看到当前配置字段

如果这里看不到配置文件，优先检查：

- 当前 shell 的工作目录是否在目标项目内
- `.llm_api.json` 是否放在目标项目根目录
- JSON 格式是否有效

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

### 图片 + 文本上下文

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
agent 在目标项目里完成接入后，建议按这个顺序做最小验证：

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

4. 如果目标项目里有 `.json/.md/.txt/.sh` 等文本文件，再跑一条 `ask_text_file()`

5. 如果目标项目里有可用图片，再跑一条 `ask_image()`

## 当前能力边界

### 正式支持
- 纯文本字符串
- text file 白名单中的文件
- image file 白名单中的图片

### 当前 text file 白名单
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

### 当前 image file 白名单
- `.png`
- `.jpg`
- `.jpeg`
- `.webp`
- `.gif`
- `.bmp`
- `.tiff`
- `.tif`

### 明确不支持
- `input_file`
- `.docx` 直传
- `.pdf` 直传
- `.xlsx` 直传
- rich file 直传

如果目标项目里出现 `docx/pdf/xlsx`，当前策略不是“继续尝试”，而是：

- 先转换为支持的文本
- 或先转换为支持的图片

## 典型失败排查

### 1. `ModuleNotFoundError: No module named 'llm_api'`
检查：

- 是否激活了目标项目的虚拟环境
- 是否在该虚拟环境里执行过：

```bash
python -m pip install -e /path/to/llm_api
```

### 2. `--show-config` 看不到项目配置
检查：

- 当前目录是否位于目标项目内
- `.llm_api.json` 是否放在目标项目根目录
- JSON 是否合法

### 3. API key 缺失
检查：

- `.llm_api.json` 是否含 `api_key`
- 或者环境变量是否覆盖了项目配置

### 4. 文件格式不支持
检查：

- 调用的是 `ask_text_file()` 还是 `ask_image()`
- 扩展名是否属于该类型白名单
- 不要把 rich file 当成正式支持输入

## Agent 执行清单
以后如果在另一个项目中让 AI agent 接入 `llm_api`，建议它按下面顺序执行：

1. 进入目标项目目录
2. 创建或激活目标项目虚拟环境
3. 执行本地路径安装：

```bash
python -m pip install -e /path/to/llm_api
```

4. 在目标项目根目录创建 `.llm_api.json`
5. 运行：

```bash
llm-api ask --show-config
```

6. 在目标项目代码中导入：

```python
from llm_api import ask, ask_text_file, ask_image
```

7. 先跑一条最小文本调用
8. 再按项目需要使用 `ask_text_file()` 或 `ask_image()`
9. 遇到 rich file 时，不要尝试直传
