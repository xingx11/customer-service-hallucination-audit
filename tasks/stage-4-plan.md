# Implementation Plan: 第四阶段最终交付收尾

## Overview

第四阶段从 `v0.3.0` 阶段三交付点继续推进，是项目正式发布前的最后收尾阶段。阶段四不再新增检测器能力、不接入新的 provider SDK、不改变默认数据格式，也不把真实 LLM 调用纳入默认质量门禁；核心目标是把当前离线评测流水线、可选 LLM adapter、交付报告、文档和发布流程整理到 `v1.0.0` 可发布状态。

阶段四目标版本为 `v1.0.0`。版本提升、最终报告和标签动作放在阶段四最后一个任务完成，避免在交付物尚未复核前提前声明正式版。

## Project Phase Map

```text
v0.1.0  阶段一：离线评测 MVP，已完成
v0.2.0  阶段二：鲁棒性与可解释性，已完成
v0.3.0  阶段三：Adapter + 最小 LLM 接入，已完成
v1.0.0  阶段四：最终交付收尾，已完成
```

## Assumptions

- `v0.3.0` 已从 main 打标签，阶段四基于 main 的最新稳定状态继续。
- 默认命令继续使用 `deterministic` detector，离线、确定性、可复现。
- `mock` detector 继续只用于离线 adapter 链路验证。
- `llm` detector 继续显式 opt-in，并只从进程环境变量读取配置。
- 当前不新增 `.env.example`，因为应用不自动读取 `.env`；`.env` 仍保持忽略，配置方式由 README 说明。
- 阶段四不新增运行时依赖；如必须新增，需要先单独确认收益。
- 默认数据、人工真值和报告 schema 不在阶段四前半段调整。

## Architecture Decisions

- 阶段四是发布准备阶段，不是功能扩展阶段；任何新能力必须拆出单独后续规划。
- 发布检查集中在 `docs/RELEASE_CHECKLIST.md`，避免打标签步骤散落在聊天记录或 PR 描述中。
- 任务顺序遵循“先锁范围，再复核文档，再跑质量和安装 smoke，最后版本/报告/标签”的发布节奏。
- `__version__` 和 CHANGELOG 的 `1.0.0` 段落只在最终收尾任务更新，确保版本号对应真实可发布状态。
- LLM 配置继续使用环境变量文档化，不引入 `python-dotenv` 或隐式配置文件读取。

## Task List

### Phase 0: Release Readiness Planning

- [x] Task 24: 建立阶段四发布准备计划和发布检查清单。

### Checkpoint: Release Scope Locked

- [x] `tasks/plan.md` 和 `tasks/todo.md` 指向阶段四。
- [x] 阶段四计划明确不新增 detector 能力、不新增运行时依赖、不新增 `.env` 自动加载。
- [x] 发布检查清单覆盖质量门禁、安装 smoke、默认 CLI、可选 LLM 边界和标签步骤。

### Phase 1: Documentation And Delivery Review

- [x] Task 25: 最终文档与交付复核。

### Checkpoint: Documentation Ready

- [x] README、SPEC、DEVELOPMENT、CHANGELOG 中的阶段状态一致。
- [x] 阶段一到阶段三交付报告链接可用，阶段四最终报告待生成项清晰。
- [x] README 明确默认离线路径、显式 `llm` 配置和不读取 `.env` 的边界。
- [x] 项目局限性、AI 工具使用说明和质量命令可直接用于交付审阅。
- [x] `docs/DELIVERY_REVIEW.md` 记录最终文档与交付复核结果。

### Phase 2: Quality And Install Smoke

- [x] Task 26: 最终质量门禁与安装/CLI smoke test。

### Checkpoint: Release Gate Passed

- [x] `powershell -ExecutionPolicy Bypass -File scripts/quality.ps1` 通过。
- [x] `pre-commit run --all-files` 通过。
- [x] `python -m customer_service_hallucination_audit --help` 和 `--version` 可运行。
- [x] 默认 deterministic 和 mock CLI smoke test 可生成报告。
- [x] `llm` 缺配置路径返回清晰错误，且不影响默认质量门禁。
- [x] `docs/QUALITY_SMOKE.md` 记录安装、质量门禁和 CLI smoke test 结果。

### Phase 3: v1.0.0 Release Closeout

- [x] Task 27: 完成 `v1.0.0` 发布收尾。

### Checkpoint: v1.0.0 Ready

- [x] package/CLI 版本更新为 `1.0.0`。
- [x] CHANGELOG 增加 `1.0.0` 发布段落。
- [x] 阶段四最终 Markdown/JSON 交付报告生成并提交。
- [x] README、SPEC、DEVELOPMENT 标记阶段四完成。
- [x] 合并到 main 后打 `v1.0.0` annotated tag 的步骤已写入发布检查清单。

## Out Of Scope For Stage 4

- 新增真实 LLM provider SDK 或多 provider 抽象。
- 新增 `.env` 自动加载、`.env.example` 或 secret 管理流程。
- 新增 Web UI、数据库、后台服务或在线评测平台。
- 多套件 orchestration、批量实验管理、成本统计和缓存。
- 改变默认数据字段、人工真值格式或报告 schema。
- 把真实 LLM 调用放入 CI 或默认质量门禁。

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| 收尾阶段继续扩功能 | 交付变慢，质量门禁风险增加 | 阶段四只接受发布准备、文档、质量和最终报告相关变更 |
| 提前改到 `1.0.0` | 版本号和真实交付状态不一致 | 最后一个任务再更新版本和 CHANGELOG |
| `.env.example` 暗示应用会读取 `.env` | 用户配置预期错误 | 不新增 `.env.example`；README 说明使用进程环境变量 |
| 发布步骤靠记忆执行 | 标签或检查遗漏 | 使用 `docs/RELEASE_CHECKLIST.md` 作为发布前门禁 |
| 真实 LLM 影响可复现性 | CI 不稳定或需要密钥 | LLM 继续显式 opt-in，不进入默认测试和报告生成 |

## Resolved Task 24 Decisions

- 当前不新增 `.env.example`，因为项目未实现 `.env` 自动读取；增加该文件反而容易让用户误以为配置会自动生效。
- 阶段四先做发布准备计划和检查清单，不在本任务修改源码行为。
- `v1.0.0` 版本提升留到 Task 27，完成最终文档复核、质量门禁和交付报告后再执行。

## Resolved Task 25 Decisions

- 最终文档复核结果记录在 `docs/DELIVERY_REVIEW.md`，作为 Task 26 和 Task 27 的交付前上下文。
- 阶段四最终 Markdown/JSON 报告留到 Task 27 生成；Task 25 只验证阶段一到阶段三已提交报告和阶段四文档链接。
- 当前仍不新增 `.env.example`，因为 README、SPEC 和发布检查清单已经明确项目不自动读取 `.env`。

## Resolved Task 26 Decisions

- 最终质量门禁和 CLI smoke test 结果记录在 `docs/QUALITY_SMOKE.md`，作为 Task 27 发布收尾的验证依据。
- CLI smoke test 使用临时输出目录运行并清理生成物，避免提交 `reports/` 或临时报告。
- `llm` detector 只验证缺少环境变量时的明确失败路径；真实 LLM 调用仍不进入默认质量门禁。

## Resolved Task 27 Decisions

- `1.0.0` 版本号写入 package 单一版本来源，并同步 CLI/scaffold 测试期望。
- 阶段四最终交付报告使用 deterministic 默认路径生成，和阶段一到阶段三报告一样纳入 `tests/test_delivery_reports.py` 一致性测试。
- 实际 annotated tag 需要在本 PR 合并到 main 后执行，避免标签指向未合并分支提交。
