# AGENTS.md

本文件是项目内 AI Agent 和开发者协作规则。所有代码修改前先读取本文件、`docs/SPEC.md` 和相关源码。

## 项目目标

构建一个可复现的客服回复幻觉检测工具，用 `data/replies.json` 作为输入，用 `data/ground_truth.json` 作为验证基准，输出检测标签、指标汇总和错误分析。

## 技术选择

- 使用 Python 3.11+。
- 不使用 Web 框架；本项目是 CLI + 离线评测流水线。
- 优先使用标准库；新增依赖必须有明确收益。
- 默认检测器应离线可运行，不依赖真实 LLM API。
- 可预留 LLM/mock adapter 边界，但不能让核心评测不可复现。
- 保持仓库精简，不提交生成缓存、虚拟环境或本地 Agent 技能副本。

## 开发流程

1. 使用 `spec-driven-development` 明确需求和成功标准。
2. 使用 `planning-and-task-breakdown` 将工作拆成小任务。
3. 使用 `incremental-implementation` 分片实现，每片保持可运行。
4. 使用 `test-driven-development` 先写测试再实现核心行为。
5. 使用 `code-review-and-quality` 在提交前做自审。
6. 使用 `git-workflow-and-versioning` 保持原子提交。
7. 使用 `documentation-and-adrs` 记录重要取舍。

## 命令

```bash
python -m pip install -e ".[dev]"
pre-commit install
python -m customer_service_hallucination_audit --help
python -m ruff check .
python -m ruff format --check .
python -m mypy src
python -m pytest
powershell -ExecutionPolicy Bypass -File scripts/quality.ps1
```

## 代码风格

- 使用 `src/` layout。
- 业务逻辑放在 `src/customer_service_hallucination_audit/`。
- 测试放在 `tests/`，测试名描述行为而不是实现细节。
- 使用类型标注，公共函数返回值必须显式标注。
- 优先小函数、清晰命名和纯函数。
- 不把文件读取、指标计算、规则判定混在一个大函数里。

示例风格：

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class DetectionResult:
    case_id: str
    is_hallucination: bool
    hallucination_type: str | None
    reasons: tuple[str, ...]
```

## 测试策略

- 规则判定和指标计算使用单元测试。
- JSON 解析、报告生成使用集成测试。
- 测试应覆盖空输入、未知类型、人工标注不一致、边界样本等情况。
- 不为了通过测试而修改测试期望；先确认规格。

## Git 规则

- 默认分支为 `main`。
- 提交信息使用中文描述，格式为 `<type>: <中文摘要>`，例如 `chore: 初始化幻觉检测项目脚手架`。
- `type` 保留英文，方便工具和历史检索；摘要和正文必须使用中文。
- 每次提交只做一件逻辑事情。
- 提交前运行 lint、type check 和 test。
- 优先运行 `scripts/quality.ps1` 作为本地质量门禁。
- 不提交 `.agents/`、`.venv/`、缓存、构建产物、密钥或本地环境文件。

## 边界

- Always: 保持离线可复现；提交前跑质量命令；更新 README/SPEC 中变化的行为。
- Ask first: 新增运行时依赖、接入真实 LLM API、改变数据文件格式。
- Never: 提交密钥；删除人工真值；用不可复现的模型输出替代确定性验证。
