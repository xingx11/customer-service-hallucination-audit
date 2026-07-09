# 开发文档：第一阶段开发流程与进度

更新时间：2026-07-09

## 当前阶段判断

项目处于第一阶段：从“脚手架可运行”推进到“核心离线评测流水线可用”。当前已经具备项目规格、数据集、Python CLI 包骨架、测试骨架、CI、pre-commit、质量脚本和 ADR；尚未实现数据解析、规则检测、指标计算、报告生成和完整 CLI 参数。

第一阶段的完成标准是：

- 能读取 `data/replies.json` 和 `data/ground_truth.json`。
- 能为每条样本输出检测标签、幻觉类型和原因。
- 能计算 precision、recall、F1、false positive、false negative。
- 能生成可审阅的报告，解释漏检、误报和高风险案例。
- README 说明分类体系、检测方法、局限性和 AI 工具使用情况。
- `python -m ruff check .`、`python -m ruff format --check .`、`python -m mypy src`、`python -m pytest` 全部通过。

## 已确认上下文

- 产品形态：Python 3.11+ CLI，不使用 Web 框架、数据库或后台服务。
- 核心约束：默认离线可复现，不接入真实 LLM API，不新增运行时依赖。
- 数据闭环：`data/replies.json` 和 `data/ground_truth.json` 均为 20 条，ID 为 `h01` 到 `h20`。
- 标注分布：18 条幻觉、2 条非幻觉，覆盖政策编造、政策偏差、参数编造、优惠编造、信息编造、能力越界、安全误导、信息遗漏。
- 当前源码：`src/customer_service_hallucination_audit/__main__.py` 仅提供 `--version` 和基础 parser；`tests/test_scaffold.py` 仅验证版本和程序名。
- 当前工具：`scripts/quality.ps1` 依次运行 ruff、format check、mypy、pytest；CI 还会运行 pre-commit。
- 当前本地状态：CodeGraph 已初始化，`.codegraph/` 是本地索引目录，不应提交。

## 我的开发流程

后续每个开发任务按以下流程执行：

1. 读上下文：先读 `AGENTS.md`、`docs/SPEC.md`、本文件、`tasks/plan.md`、`tasks/todo.md`，结构问题优先用 CodeGraph。
2. 明确任务：只选择 `tasks/todo.md` 中一个小任务；若任务边界变化，先更新计划或规格。
3. 先写测试：行为逻辑变更先补 pytest，确认测试能暴露缺口，再实现最小代码。
4. 小步实现：每次只完成一个可验证切片，优先纯函数和小模块，不把文件读取、规则判定、指标计算混在一个大函数里。
5. 局部验证：任务内优先跑相关测试，跨模块任务完成后跑 `scripts/quality.ps1`。
6. 自审：按正确性、可读性、架构、安全、性能做自查，重点确认没有硬编码人工真值、没有引入不可复现行为。
7. 文档同步：行为、命令、报告格式或分类体系变化时，同步更新 README、SPEC 或 ADR。
8. 原子提交：每次提交只做一个逻辑变更，提交信息使用 `<type>: <中文摘要>`。

## 目标模块边界

第一阶段建议保持以下模块边界，实际命名可在实现时微调：

- `models.py`：定义输入样本、人工标注、检测结果、指标汇总等 dataclass。
- `io.py`：读取 JSON，校验字段、ID 对齐、重复 ID 和未知类型。
- `detector.py`：确定性规则检测，输出类型、原因和触发规则，不访问人工真值。
- `metrics.py`：计算混淆矩阵、precision、recall、F1、漏检和误报。
- `reporting.py`：生成 Markdown 和结构化 JSON 报告内容。
- `pipeline.py`：串联读取、检测、评估、报告生成。
- `__main__.py`：只负责 CLI 参数解析和调用 pipeline。

## 第一阶段依赖顺序

```text
数据 schema 理解
  -> dataclass 模型
  -> JSON 读取与校验
  -> 确定性规则检测
  -> 指标与错误分析
  -> 报告生成
  -> CLI 集成
  -> README/SPEC 更新
  -> 质量门禁与自审
```

这个顺序保证每一步都有可测试输出，也避免在 CLI 尚未稳定时把业务逻辑写进入口文件。

## 测试策略

- 模型与解析：覆盖空输入、缺字段、重复 ID、人工标注缺失、未知类型、非幻觉却带类型等情况。
- 规则检测：每类幻觉至少有一个正向样例，`h12`、`h16` 这类非幻觉样本至少有稳定的负向样例。
- 指标计算：覆盖完美命中、全错、空预测、无正例、无负例，避免除零。
- 报告生成：使用固定输入做 golden-style 结构测试，关注字段完整性和排序稳定。
- CLI 集成：验证默认路径、显式路径、输出目录、`--help` 和错误路径。

## 报告格式建议

阶段一建议同时保留两类输出：

- Markdown：面向人工审阅，包含指标汇总、分类结果、漏检/误报/高风险案例。
- JSON：面向自动化验证，包含逐条结果、metrics、false positives、false negatives。

如果后续要压缩范围，优先保留 Markdown；如果要接 CI 或其他工具消费结果，优先保留 JSON。

## 风险与约束

| 风险 | 影响 | 处理方式 |
| --- | --- | --- |
| 规则过拟合人工真值 | 工具不可泛化，也违反项目边界 | 规则只能读取回复和知识库，不读取 `ground_truth` 的 detail 作为预测依据 |
| 中文规则边界模糊 | 类型分类可能不稳定 | 每条检测结果输出触发原因，README 解释分类取舍 |
| 数据 ID 不一致 | 指标错误或报告漏样本 | loader 阶段强校验 replies 和 ground truth 的 ID 集合 |
| 指标除零 | 空样本或极端样本崩溃 | metrics 单元测试覆盖边界并返回 0.0 |
| 生成缓存误提交 | 仓库噪声、CI 风险 | `.gitignore` 忽略 `.codegraph/`、缓存和构建产物 |

## 当前进度

已完成：

- 项目规格：`docs/SPEC.md`
- CLI 技术决策：`docs/decisions/ADR-001-python-cli.md`
- README、CONTRIBUTING、CHANGELOG 初稿
- Python 包骨架和 console script 配置
- 基础测试、pre-commit、CI、质量脚本
- 任务数据和人工真值文件
- CodeGraph 本地索引初始化

待完成：

- 领域模型和 JSON 解析校验
- 确定性规则检测器
- 指标计算和错误分析
- Markdown/JSON 报告生成
- CLI 参数和端到端流水线
- README/SPEC 与实际行为同步
- 全量质量门禁和自审

## 开发时的默认命令

```bash
python -m pip install -e ".[dev]"
python -m customer_service_hallucination_audit --help
python -m ruff check .
python -m ruff format --check .
python -m mypy src
python -m pytest
powershell -ExecutionPolicy Bypass -File scripts/quality.ps1
```

PowerShell 读取中文文件时使用：

```powershell
Get-Content -Raw -Encoding utf8 docs/SPEC.md
```
