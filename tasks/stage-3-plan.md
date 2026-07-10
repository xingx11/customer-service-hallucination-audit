# Implementation Plan: 第三阶段评测扩展与适配边界

## Overview

第三阶段从 `v0.2.0` 第二阶段交付点继续推进，目标是把当前单一默认数据集、单一确定性检测器、单次报告输出，扩展成更容易演进的离线评测框架。阶段三优先建立 detector 适配边界、评测套件输入模型、跨套件报告和回归比较能力，为后续 mock/LLM adapter 或更多业务数据接入预留结构，但默认路径仍保持离线、确定性、无外部 API 依赖。

## Assumptions

- `main` 已完成第二阶段合并，并已打 `v0.2.0` 标签。
- 第三阶段不接入真实 LLM API；如要引入真实模型调用，需要单独确认、单独设计、单独评审。
- 第三阶段不改变 `data/replies.json` 和 `data/ground_truth.json` 的既有字段格式；新增评测输入优先通过显式路径、fixture 或 suite 配置表达。
- 新增能力优先使用标准库和现有模块，不新增运行时依赖。
- 阶段三交付仍以小 PR 推进，每个任务控制在约 1-5 个主要文件内。

## Architecture Decisions

- 先补齐版本与发布元数据一致性，再继续功能开发，避免 `v0.2.0` 标签后 CLI/package 版本信息长期滞后。
- detector 适配边界只定义离线可复现接口和 mock/test double，不把真实 LLM adapter 放入默认执行路径。
- 评测套件以“回复文件 + 人工真值文件 + 元数据”的显式组合建模，避免污染默认 20 条交付数据。
- pipeline 继续负责 orchestration；数据读取、检测器调用、指标计算、报告渲染仍保持模块边界分离。
- 报告新增字段必须保持稳定排序，并通过 golden-style 测试验证序列化结果。

## Task List

### Phase 0: Stage 3 Planning

- [x] Task 17: 建立第三阶段计划、任务清单和文档状态。

### Phase 1: Release And Adapter Foundation

- [ ] Task 18: 对齐版本元数据与发布记录。
- [ ] Task 19: 定义 detector adapter contract，并保留确定性默认实现。

### Checkpoint: Foundation

- [ ] `python -m customer_service_hallucination_audit --version` 与阶段版本策略一致。
- [ ] 默认 CLI 输出和阶段二交付报告不发生非预期漂移。
- [ ] mock detector 可用于测试 pipeline 注入边界，但默认路径仍使用确定性规则。

### Phase 2: Evaluation Suite Inputs

- [ ] Task 20: 增加评测套件模型和 loader。
- [ ] Task 21: 支持跨套件运行与报告元数据。

### Checkpoint: Multi-suite Evaluation

- [ ] 默认 20 条数据仍可用原命令运行。
- [ ] 显式 suite 配置可运行多个数据集并输出稳定汇总。
- [ ] 报告中能区分 dataset/suite、detector 和运行元数据。

### Phase 3: Regression And Delivery

- [ ] Task 22: 增加报告回归比较能力。
- [ ] Task 23: 完成第三阶段交付收尾。

### Checkpoint: Complete

- [ ] `powershell -ExecutionPolicy Bypass -File scripts/quality.ps1` 通过。
- [ ] `pre-commit run --all-files` 通过。
- [ ] README、SPEC、CHANGELOG、开发文档和阶段三交付报告已同步。
- [ ] 没有提交缓存、虚拟环境、CodeGraph 数据库、真实密钥或生成污染物。

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| adapter 边界过早绑定真实 LLM | 破坏离线可复现与测试稳定性 | 阶段三只做 contract 和 mock/test double；真实 API 单独确认 |
| suite 输入模型变成新数据格式迁移 | 增加兼容成本 | 保留原 replies/ground truth schema，只在外层增加 suite 元数据 |
| 报告 JSON 字段漂移 | 下游测试和交付报告失去稳定性 | 新字段稳定排序，更新 golden-style 断言和交付报告一致性测试 |
| 多套件汇总让 pipeline 变复杂 | 模块边界变模糊 | 保持单次 run_audit 不变，新增 suite orchestration 包装层 |
| 版本信息继续滞后标签 | 用户无法确认运行版本 | 阶段三第一批任务先处理版本策略和 CLI --version 行为 |

## Open Questions

- 阶段三是否要提交 `docs/reports/stage-3-report.*`，还是改为提交跨套件 summary 报告？
- 版本号应继续手动维护在 `pyproject.toml` / `__init__.py`，还是改为从 git tag 派生？
- 第三阶段是否需要正式引入一个 `docs/decisions/ADR-002-detector-adapter.md` 来记录 adapter 边界？
