# 开发文档：阶段进度与开发流程

更新时间：2026-07-10

## 当前阶段判断

项目第一阶段已经完成，并已打 `v0.1.0` 标签：核心离线评测流水线可通过 CLI 运行，默认数据随包发布，阶段一 Markdown/JSON 交付报告已提交，并有测试验证交付报告与当前 pipeline 输出一致。第二阶段鲁棒性与可解释性增强也已完成，并已打 `v0.2.0` 标签：已交付鲁棒性样本、检测器边界测试、规则元数据模型、规则命中摘要、按类型聚合指标、报告解释增强和阶段二 Markdown/JSON 交付报告。

当前第三阶段功能开发已经收尾，并已打 `v0.3.0` 标签：阶段三完成 Adapter + 最小 LLM 接入闭环，已交付版本/发布元数据一致性、detector adapter contract、deterministic adapter、mock adapter、LLM prompt、输出 schema、离线解析校验、显式 opt-in 的 `llm` adapter 与 CLI detector 选择，以及阶段三 Markdown/JSON 交付报告。默认路径继续保持离线、确定性、无真实 LLM API 依赖。

当前第四阶段已经启动：阶段四只做最终交付收尾，目标是完成 `v1.0.0` 发布准备，包括最终文档复核、发布检查清单、质量门禁、安装/CLI smoke test、阶段四交付报告和最终标签步骤。阶段四不新增 detector 能力，不新增运行时依赖，也不加入 `.env` 自动加载。当前已完成阶段四发布准备计划、发布检查清单和最终文档与交付复核，复核记录见 `docs/DELIVERY_REVIEW.md`。

第一阶段完成标准已经满足：

- 能读取随包发布的默认数据，也能显式读取 `data/replies.json` 和 `data/ground_truth.json`。
- 能为每条样本输出检测标签、幻觉类型和原因。
- 能计算 precision、recall、F1、false positive、false negative。
- 能生成可审阅的报告，解释漏检、误报和高风险案例。
- README 说明分类体系、检测方法、局限性和 AI 工具使用情况。
- `python -m ruff check .`、`python -m ruff format --check .`、`python -m mypy src`、`python -m pytest` 全部通过。

## 已确认上下文

- 产品形态：Python 3.11+ CLI，不使用 Web 框架、数据库或后台服务。
- 核心约束：默认离线可复现；真实 LLM 只能显式选择，不进入默认质量门禁；不新增运行时依赖。
- 数据闭环：`data/replies.json` 和 `data/ground_truth.json` 均为 20 条，ID 为 `h01` 到 `h20`。
- 标注分布：18 条幻觉、2 条非幻觉，覆盖政策编造、政策偏差、参数编造、优惠编造、信息编造、能力越界、安全误导、信息遗漏。
- 当前源码：核心模型、JSON 读取、确定性规则检测、指标计算、报告生成和 CLI 端到端流水线已经拆分到独立模块；默认数据也随包发布，安装后无需源码根目录即可运行。
- 当前 adapter 边界：`Detector` contract 定义输入为 `ReplyCase` 序列、输出为 `DetectionResult` 序列；`run_audit` 可注入 detector，默认仍使用确定性规则检测器。
- 当前 CLI detector：`--detector deterministic` 是默认规则检测器路径；`--detector mock` 使用稳定合成结果验证 adapter 注入和报告链路；`--detector llm` 是显式 opt-in 路径。
- 当前 LLM parser/adapter：prompt 明确只依据用户问题、系统回复和知识库；parser 校验 `case_id`、`is_hallucination`、`hallucination_type`、`reasons`、`rule_ids` 后转换为 `DetectionResult`；`llm` adapter 只从 `CS_HALLUCINATION_AUDIT_LLM_API_KEY`、`CS_HALLUCINATION_AUDIT_LLM_ENDPOINT` 和 `CS_HALLUCINATION_AUDIT_LLM_MODEL` 读取配置。
- 当前环境配置边界：项目不自动读取 `.env` 文件，暂不提供 `.env.example`；LLM 配置通过 shell、CI secret 或调用方进程环境显式注入。
- 当前工具：`scripts/quality.ps1` 依次运行 ruff、format check、mypy、pytest；CI 还会运行 pre-commit。
- 当前本地状态：CodeGraph 已初始化，`.codegraph/` 是本地索引目录，不应提交。
- 当前计划入口：`tasks/plan.md` 和 `tasks/todo.md` 已指向第四阶段；阶段四专属文档为 `tasks/stage-4-plan.md` 和 `tasks/stage-4-todo.md`，发布检查清单为 `docs/RELEASE_CHECKLIST.md`，交付复核记录为 `docs/DELIVERY_REVIEW.md`。

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
- `metrics.py`：计算混淆矩阵、precision、recall、F1、漏检、误报和按幻觉类型聚合的统计。
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
- CLI 集成：验证随包默认数据、显式路径、输出目录、`--help` 和错误路径。

## 报告格式建议

当前流水线同时保留两类输出：

- Markdown：面向人工审阅，包含总体指标、类型表现、分类结果、规则命中摘要、漏检/误报/类型错误/高风险案例。
- JSON：面向自动化验证，包含逐条结果、规则命中摘要、总体指标、类型指标、高风险筛选依据和误判分组。

如果后续要压缩范围，优先保留 Markdown；如果要接 CI 或其他工具消费结果，优先保留 JSON。

## 风险与约束

| 风险 | 影响 | 处理方式 |
| --- | --- | --- |
| 规则过拟合人工真值 | 工具不可泛化，也违反项目边界 | 规则只能读取回复和知识库，不读取 `ground_truth` 的 detail 作为预测依据 |
| 中文规则边界模糊 | 类型分类可能不稳定 | 每条检测结果输出触发原因，README 解释分类取舍 |
| 数据 ID 不一致 | 指标错误或报告漏样本 | loader 阶段强校验 replies 和 ground truth 的 ID 集合 |
| 指标除零 | 空样本或极端样本崩溃 | metrics 单元测试覆盖边界并返回 0.0 |
| 生成缓存误提交 | 仓库噪声、CI 风险 | `.gitignore` 忽略 `.codegraph/`、`reports/`、缓存和构建产物 |

## 当前进度

已完成：

- 项目规格：`docs/SPEC.md`
- CLI 技术决策：`docs/decisions/ADR-001-python-cli.md`
- README、CONTRIBUTING、CHANGELOG 初稿
- Python 包骨架和 console script 配置
- 基础测试、pre-commit、CI、质量脚本
- 任务数据和人工真值文件
- CodeGraph 本地索引初始化
- 领域模型和 JSON 解析校验
- 确定性规则检测器
- 指标计算和错误分析
- Markdown/JSON 报告生成
- CLI 参数和端到端流水线
- 阶段一 Markdown/JSON 交付报告
- 交付报告与当前流水线输出的一致性测试
- CLI 入口测试覆盖默认数据、显式路径、`--help` 和错误路径
- 第一阶段质量门禁与文档状态同步
- 第二阶段鲁棒性 fixture 与 detector 边界测试
- 规则元数据模型与报告规则命中摘要
- 按幻觉类型聚合的指标
- Markdown/JSON 报告解释增强
- 第二阶段交付报告、CHANGELOG 与质量门禁收尾
- 第三阶段版本元数据与发布记录对齐
- detector adapter contract 与 pipeline 注入边界
- deterministic/mock detector adapter 与 CLI 选择
- LLM prompt、输出 schema 和离线解析校验
- 可选 LLM adapter 与 CLI detector 选择
- 阶段三 Markdown/JSON 交付报告
- 阶段三文档、CHANGELOG 与质量门禁收尾
- 阶段四发布准备计划、任务清单和发布检查清单
- 阶段四最终文档与交付复核

待完成：

- Task 26：最终质量门禁与安装/CLI smoke test。
- Task 27：`v1.0.0` 发布收尾。

## 后续建议

- 阶段四计划：`tasks/stage-4-plan.md`
- 阶段四任务清单：`tasks/stage-4-todo.md`
- 发布检查清单：`docs/RELEASE_CHECKLIST.md`
- 交付复核记录：`docs/DELIVERY_REVIEW.md`
- 下一步建议执行 Task 26，完成最终质量门禁与安装/CLI smoke test。

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
