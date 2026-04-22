# llm_api Package

此 package 是项目的正式实现层，当前已经包含：

- 共享库主入口
- CLI 支撑代码
- config 与输入白名单配置
- response 解析
- transport 请求层

## 当前公开入口
- `ask()`
  - 纯文本兼容入口
- `ask_text()`
  - 纯文本显式入口
- `ask_text_file()`
  - 读取支持的 text file 后走 `input_text`
- `ask_image()`
  - 读取支持的 image file 后走 `input_image`

## 当前输入边界
- 正式支持：
  - 文本字符串
  - text file 白名单中的文件
  - image file 白名单中的图片
- 当前不支持：
  - `docx`
  - `pdf`
  - `xlsx`
  - 其他 rich file 直传

## 目录说明
- `config/`
  - 默认配置、环境变量解析、输入扩展名白名单
- `cli/`
  - `llm-api ask` 的命令行入口
- `transport/`
  - HTTP 请求发送
- `parsing/`
  - 响应文本、usage、reasoning 提取
