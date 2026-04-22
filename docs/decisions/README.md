# 设计决策

此目录用于存放重要项目决策的简要记录。

## 当前状态
- 目录已经预留，但尚未把各项决策拆成独立 ADR
- 在正式 ADR 出现之前，关键决策以 README、测试和 handoff 文档中的一致口径为准

## 当前已稳定的关键决策
- 正式能力不支持 `input_file`
- text file 统一读取内容后走 `input_text`
- 图片统一走 `input_image`
- 扩展名白名单必须来自显式配置文件

## 后续适合单独拆文档的主题
- 为什么默认示例 URL 使用占位地址，而真实 endpoint 只保留在本地忽略配置中
- 为什么 shared library 优先、CLI 次之
- 为什么 rich file 当前不直接进入 public API
