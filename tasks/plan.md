# Implementation Plan: 当前活动计划（第三阶段）

当前活动计划是第三阶段“Adapter + 最小 LLM 接入”。完整计划见：

- `tasks/stage-3-plan.md`
- `tasks/stage-3-todo.md`

## Overview

第三阶段从 `v0.2.0` 标签继续推进，目标是在保持默认离线可复现的前提下，让同一套 pipeline 可以运行 `deterministic`、`mock`、`llm` 三种 detector。第三阶段完成后打 `v0.3.0`，随后只保留最终交付收尾阶段，对应 `v1.0.0`。

## Task List

### Phase 0: Stage 3 Replanning

- [x] Task 17: 重新校准第三阶段为最小 LLM 接入闭环。

### Phase 1: Version And Adapter Contract

- [x] Task 18: 对齐版本元数据与发布记录。
- [x] Task 19: 定义 detector adapter contract。

### Phase 2: Offline Adapter Paths

- [ ] Task 20: 接入 deterministic adapter 和 mock adapter。
- [ ] Task 21: 增加 LLM 输出 schema、prompt 模板和解析校验。

### Phase 3: Optional LLM Path And Delivery

- [ ] Task 22: 增加可选 LLM adapter 与 CLI detector 选择。
- [ ] Task 23: 完成第三阶段交付报告、文档和质量门禁。

## Checkpoints

- [x] Adapter Foundation: CLI/package 版本策略清晰，pipeline 可接收不同 detector。
- [ ] Offline Confidence: deterministic 和 mock 路径均可离线端到端运行。
- [ ] Stage 3 Complete: LLM 路径显式 opt-in，默认质量门禁不依赖真实 LLM。

## Boundaries

- Always: 默认 detector 为 deterministic；LLM 必须显式选择；测试不依赖真实网络。
- Ask first: 新增运行时依赖；改变默认数据文件格式；把真实 LLM 调用纳入 CI。
- Never: 提交密钥；用人工真值硬编码预测；LLM 失败时静默伪装成确定性结果。
