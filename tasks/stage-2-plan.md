# Implementation Plan: 第二阶段鲁棒性与可解释性增强

## Overview

第二阶段在 `v0.1.0` 第一阶段离线流水线基础上推进，目标是提升规则检测器在默认 20 条样本之外的鲁棒性，并让报告更清楚地解释规则命中、类型表现和高风险案例。阶段二仍保持默认离线可复现，不接入真实 LLM API，不新增运行时依赖。

## Architecture Decisions

- 默认流水线继续使用确定性规则检测器，人工真值只用于评估。
- 新增鲁棒性样本优先放在测试 fixture 中，不改变 `data/replies.json` 和 `data/ground_truth.json` 的格式。
- 先结构化规则元数据，再扩展报告和指标，避免规则逻辑继续散落在条件分支里。
- 报告增强复用 metrics/reporting 模块，不把统计逻辑写进 CLI。
- LLM/mock adapter 只作为后续边界讨论；阶段二实现不依赖外部 API。

## Task List

### Phase 0: Stage 2 Planning

- [x] Task 9: 建立第二阶段计划和任务清单。

### Phase 1: Robustness Fixtures

- [x] Task 10: 设计阶段二鲁棒性测试样本集。
- [x] Task 11: 扩展检测器边界测试，覆盖同义改写、困难负例和遗漏场景。

### Checkpoint: Robustness Baseline

- [ ] 新 fixture 不改变阶段一默认数据格式。
- [ ] `python -m pytest tests/test_detector.py` 通过。
- [ ] 默认 20 条样本的检测结果不发生非预期漂移。

### Phase 2: Rule Explainability

- [x] Task 12: 引入规则元数据模型，描述规则 ID、类别、风险等级和说明。
- [x] Task 13: 让检测结果或报告 payload 暴露规则命中摘要。

### Checkpoint: Explainability

- [ ] 每条命中规则都有稳定 ID、中文说明和风险等级。
- [ ] 现有报告 JSON 顺序仍稳定。
- [ ] 规则元数据不读取人工真值。

### Phase 3: Metrics And Reporting

- [ ] Task 14: 增加按幻觉类型聚合的评估指标。
- [ ] Task 15: 增强 Markdown/JSON 报告，展示类型表现、规则命中统计和高风险排序依据。

### Checkpoint: Reporting

- [ ] 报告解释 precision/recall/F1 之外的类型表现。
- [ ] JSON 报告字段稳定并有测试覆盖。
- [ ] Markdown 报告仍适合人工审阅。

### Phase 4: Stage 2 Delivery

- [ ] Task 16: 更新 README/SPEC/CHANGELOG，生成阶段二交付说明并完成质量门禁。

### Checkpoint: Complete

- [ ] `powershell -ExecutionPolicy Bypass -File scripts/quality.ps1` 通过。
- [ ] 无缓存、虚拟环境、CodeGraph 数据库或生成产物进入提交。
- [ ] 阶段二变更拆分为可审查的小 PR。

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| 过度适配新增 fixture | 规则泛化能力仍不足 | 同时加入正例、困难负例和同义改写，避免只补命中条件 |
| 规则元数据变成重复维护负担 | 后续规则扩展成本升高 | 让规则执行逻辑直接引用同一份 RuleDefinition |
| 报告字段膨胀 | JSON 消费者和测试维护成本升高 | 新字段按阶段拆分加入，并为稳定顺序写测试 |
| per-type 指标样本太少 | 类型指标容易被误读 | README/报告明确说明样本规模限制 |
| adapter 提前接入真实 API | 破坏离线可复现边界 | 阶段二不接真实 LLM；如需 adapter，仅做 mock 边界并另开 PR |

## Open Questions

- 阶段二鲁棒性 fixture 的目标规模是否先定为 12-20 条，还是按每类幻觉固定配额？
- 规则风险等级是否应写入 `DetectionResult`，还是只作为报告层派生信息？
- 阶段二是否需要提交新的 `docs/reports/stage-2-report.*`，还是仅保留测试和文档说明？
