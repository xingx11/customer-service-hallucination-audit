# Implementation Plan: 当前活动计划（第三阶段）

当前活动计划是第三阶段“评测扩展与适配边界”。完整计划见：

- `tasks/stage-3-plan.md`
- `tasks/stage-3-todo.md`

## Overview

第三阶段从 `v0.2.0` 标签继续推进，优先补齐版本与发布元数据一致性，然后建立 detector adapter contract、评测套件输入模型、跨套件报告和报告回归比较能力。默认 CLI 仍保持离线、确定性、无真实 LLM API 依赖。

## Task List

### Phase 0: Stage 3 Planning

- [x] Task 17: 建立第三阶段计划、任务清单和文档状态。

### Phase 1: Release And Adapter Foundation

- [ ] Task 18: 对齐版本元数据与发布记录。
- [ ] Task 19: 定义 detector adapter contract，并保留确定性默认实现。

### Phase 2: Evaluation Suite Inputs

- [ ] Task 20: 增加评测套件模型和 loader。
- [ ] Task 21: 支持跨套件运行与报告元数据。

### Phase 3: Regression And Delivery

- [ ] Task 22: 增加报告回归比较能力。
- [ ] Task 23: 完成第三阶段交付收尾。

## Checkpoints

- [ ] Foundation: CLI/package 版本策略清晰，默认 detector 行为不回退。
- [ ] Multi-suite Evaluation: 默认数据和显式 suite 均可离线运行。
- [ ] Complete: 完整质量门禁通过，README/SPEC/CHANGELOG/开发文档同步。

## Boundaries

- Always: 默认离线可复现；每个任务有测试或文档验证；报告 JSON 保持稳定排序。
- Ask first: 接入真实 LLM API；新增运行时依赖；改变默认数据文件格式。
- Never: 用人工真值硬编码预测；提交密钥、缓存、虚拟环境或 CodeGraph 数据库。
