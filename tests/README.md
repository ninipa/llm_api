# 测试

此目录用于存放项目当前正式实现的测试。

## 当前覆盖范围
- `unit`
  - config 默认值与白名单配置
  - payload 构造
  - response 提取
  - transport 错误处理
  - typed API 的核心行为
- `cli`
  - `llm-api ask` 基本输出
  - `--text-file`
  - `--image-file`
  - prompt 与参数冲突校验
- `integration`
  - 在 mock 条件下验证公开入口能组装出正确请求

## 当前状态
- 当前 working tree 下测试命令为：

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

- 当前最近一次本地验证结果为：

```text
Ran 45 tests ... OK
```

- public 分支中的正式测试不依赖 `materials/`、handoff 文档或实验结果目录
