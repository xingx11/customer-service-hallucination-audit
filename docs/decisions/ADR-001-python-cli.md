# ADR-001: Use a Python CLI for the Hallucination Audit

## Status

Accepted

## Date

2026-07-09

## Context

0110 任务要求对固定 JSON 数据进行批量检测、验证检出率并输出报告。核心工作是数据解析、规则判定、指标计算和案例分析，不需要交互式前端、持久化数据库或在线服务。

## Decision

使用 Python 3.11+ 构建命令行工具。默认实现基于确定性规则引擎，使用标准库完成 CLI、数据模型和 JSON 处理。开发质量由 pytest、ruff、mypy 和 GitHub Actions 保障。

## Alternatives Considered

### Web application

- Pros: 截图展示更直观。
- Cons: 增加前端、构建和浏览器测试成本，偏离任务重点。
- Rejected: 本题更看重评测方法和代码质量，不需要 Web UI。

### Node.js CLI

- Pros: 工具链成熟，JSON 处理方便。
- Cons: 对文本规则、数据分析和报告生成不如 Python 直接。
- Rejected: Python 更适合小型评测流水线。

### Direct LLM-only evaluator

- Pros: 分类能力强，解释自然。
- Cons: 成本、稳定性和可复现性较差。
- Rejected: 默认路径必须离线可复现；LLM 可以作为后续可选 adapter。

## Consequences

- 首版工具可以在无网络环境中运行。
- 测试可以覆盖核心规则和指标计算。
- 后续可扩展真实 LLM 或 mock provider，但不会污染核心评测闭环。
