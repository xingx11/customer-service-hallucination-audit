# Implementation Plan: 当前活动计划（第四阶段）

当前活动计划是第四阶段“最终交付收尾”。完整计划见：

- `tasks/stage-4-plan.md`
- `tasks/stage-4-todo.md`

## Overview

第四阶段从 `v0.3.0` 标签后的稳定功能面继续推进，不再扩大检测能力或新增运行时依赖。目标是在 `v1.0.0` 前完成最终文档复核、发布检查清单、安装/CLI smoke test、完整质量门禁和最终交付报告，让项目具备可审阅、可复现、可发布的收尾状态。

## Task List

### Phase 0: Release Readiness Planning

- [x] Task 24: 建立阶段四发布准备计划和发布检查清单。

### Phase 1: Documentation And Delivery Review

- [x] Task 25: 最终文档与交付复核。

### Phase 2: Quality And Install Smoke

- [x] Task 26: 最终质量门禁与安装/CLI smoke test。

### Phase 3: v1.0.0 Release Closeout

- [ ] Task 27: 完成 `v1.0.0` 发布收尾。

## Checkpoints

- [x] Release Scope Locked: 阶段四范围固定为最终交付准备，不再新增 detector 能力。
- [x] Documentation Ready: README、SPEC、CHANGELOG、开发文档和交付报告链接一致。
- [x] Release Gate Passed: 质量门禁、pre-commit、安装和 CLI smoke test 均通过。
- [ ] v1.0.0 Ready: 版本、CHANGELOG、最终报告和打标签步骤准备完成。

## Boundaries

- Always: 默认 detector 为 deterministic；LLM 继续显式 opt-in；质量门禁不依赖真实 LLM 或网络。
- Ask first: 新增运行时依赖；加入 `.env` 自动加载；改变默认数据或报告 schema。
- Never: 提交密钥或 `.env`；把真实 LLM 调用纳入默认 CI；用不可复现输出替代确定性报告。
