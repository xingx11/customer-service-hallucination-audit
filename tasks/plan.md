# Implementation Plan: 第一阶段离线评测流水线

## Overview

第一阶段要把当前 Python CLI 脚手架扩展为可复现的离线评测流水线：读取固定 JSON 数据，执行确定性幻觉规则检测，对照人工真值计算指标，生成报告，并通过本地质量门禁与 CI。

## Architecture Decisions

- 核心逻辑保持离线确定性，不接入真实 LLM API。
- 使用标准库和 dataclass，不新增运行时依赖。
- CLI 入口只做参数解析和 orchestration 调用，业务逻辑拆分到可单测模块。
- 报告内容保持稳定排序，便于测试和审阅。
- 人工真值只用于评估，不参与检测器预测。

## Current State

- 已有：`docs/SPEC.md`、README、ADR、数据文件、CI、pre-commit、质量脚本、Python 包骨架、基础测试。
- 未有：数据模型、JSON loader、detector、metrics、reporting、pipeline、完整 CLI 参数、报告样例。
- 本地注意：`.codegraph/` 是 CodeGraph 索引目录，不能提交。

## Task List

### Phase 0: Planning Baseline

- [x] Task 0: 梳理当前项目状态、开发流程和阶段一任务拆分。

### Phase 1: Data Foundation

- [x] Task 1: 定义领域模型和类型边界。
- [x] Task 2: 实现 JSON 读取与数据一致性校验。

### Checkpoint: Data Foundation

- [x] 数据模型测试通过。
- [x] loader 能发现缺字段、重复 ID、ID 不对齐和未知类型。
- [x] 业务层没有无约束 `dict[str, object]` 扩散。

### Phase 2: Detection And Evaluation

- [ ] Task 3: 实现确定性规则检测器。
- [ ] Task 4: 实现指标计算和错误案例分析。

### Checkpoint: Detection And Evaluation

- [ ] 每类幻觉至少有一个测试样例。
- [ ] 非幻觉样本不会被基础规则误报。
- [ ] precision、recall、F1、漏检、误报均有边界测试。

### Phase 3: Reporting And CLI

- [ ] Task 5: 实现 Markdown 和 JSON 报告生成。
- [ ] Task 6: 集成 CLI 参数和端到端 pipeline。

### Checkpoint: Reporting And CLI

- [ ] 默认命令可读取 `data/` 下的样本并生成报告。
- [ ] 显式输入路径和输出目录可用。
- [ ] 报告内容排序稳定，便于 golden-style 测试。

### Phase 4: Documentation And Quality

- [ ] Task 7: 更新 README/SPEC，说明分类体系、方法、局限性和 AI 工具使用。
- [ ] Task 8: 运行质量门禁并完成自审。

### Checkpoint: Complete

- [ ] `powershell -ExecutionPolicy Bypass -File scripts/quality.ps1` 通过。
- [ ] CI 同等命令本地可复现。
- [ ] 没有提交缓存、虚拟环境、CodeGraph 数据库或构建产物。
- [ ] 变更可拆成清晰的原子提交。

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| 检测器无意硬编码人工真值 | 破坏评测可信度 | detector 只接收回复和知识库，评估阶段才读取 ground truth |
| 规则太分散难维护 | 后续扩展成本高 | 用小规则函数或规则表描述触发条件、类型和原因 |
| 报告和指标口径不一致 | README、测试和输出互相冲突 | 先在 metrics 测试中固定定义，再让报告复用同一数据结构 |
| CLI 变成大函数 | 难测试、难复用 | CLI 只解析参数，业务流程放进 pipeline |
| 缓存目录污染仓库 | 误提交生成文件 | `.gitignore` 覆盖 `.codegraph/`、`.mypy_cache/`、`.pytest_cache/`、`.ruff_cache/` |

## Open Questions

- 最终交付是否必须同时提交 Markdown 和 JSON 报告文件，还是运行时生成即可？
- 是否要在第一阶段加入 mock LLM adapter 边界，还是等核心规则流水线稳定后再做？
- 信息遗漏类边界是否要与“政策偏差/信息编造”严格区分，还是允许在 README 中说明优先级规则？
