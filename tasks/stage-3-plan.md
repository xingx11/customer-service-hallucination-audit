# Implementation Plan: 第三阶段最小 LLM 接入闭环

## Overview

第三阶段从 `v0.2.0` 第二阶段交付点继续推进，但不再走“多套件评测平台化”的长期路线。考虑剩余时间，第三阶段调整为最后一个功能开发阶段：在保持默认离线可复现的前提下，加入 detector adapter 边界、mock detector 和可选 LLM detector，让同一套 pipeline 可以运行 `deterministic`、`mock`、`llm` 三种检测器，并继续生成当前稳定的 Markdown/JSON 报告。

阶段三目标版本为 `v0.3.0`。阶段三完成后，项目只保留一个最终交付收尾阶段，对应 `v1.0.0`。

## Project Phase Map

```text
v0.1.0  阶段一：离线评测 MVP，已完成
v0.2.0  阶段二：鲁棒性与可解释性，已完成
v0.3.0  阶段三：Adapter + 最小 LLM 接入，当前重点
v1.0.0  阶段四：最终交付收尾
```

## Assumptions

- 默认执行路径继续是确定性规则检测器，不需要网络、API key 或真实 LLM。
- LLM detector 必须显式选择，例如 `--detector llm`，并通过环境变量读取密钥和配置。
- LLM adapter 的测试使用 mock/fake client，不依赖真实网络调用。
- 不新增运行时依赖；如必须新增依赖，需要先单独确认收益。
- 不改变 `data/replies.json` 和 `data/ground_truth.json` 的既有字段格式。
- 阶段三不做多 provider 平台化、不做复杂 suite 配置、不做报告回归比较工具。

## Architecture Decisions

- detector 以统一 contract 接入 pipeline：输入为 `ReplyCase` 序列，输出为 `DetectionResult` 序列。
- 现有规则检测器作为 `deterministic` adapter，是默认和 CI 必跑路径。
- `mock` adapter 用于验证 adapter 注入、CLI 选择和报告链路，不依赖网络。
- `llm` adapter 是显式 opt-in 路径，负责 prompt 构造、调用 provider、解析结构化输出并校验为 `DetectionResult`。
- LLM 输出必须符合最小 JSON schema：`case_id`、`is_hallucination`、`hallucination_type`、`reasons`、`rule_ids`。
- LLM 解析失败、缺少 API key、返回未知类型时必须给出清晰错误，不静默降级为确定性结果。
- 报告 schema 尽量保持现状；如需记录 detector 名称，优先使用小范围字段扩展并更新 golden-style 测试。

## Task List

### Phase 0: Stage 3 Replanning

- [x] Task 17: 重新校准第三阶段为最小 LLM 接入闭环。

### Phase 1: Version And Adapter Contract

- [x] Task 18: 对齐版本元数据与发布记录。
- [x] Task 19: 定义 detector adapter contract。

### Checkpoint: Adapter Foundation

- [x] `python -m customer_service_hallucination_audit --version` 与版本策略一致。
- [x] 默认 CLI 输出和阶段二交付报告不发生非预期漂移。
- [x] pipeline 可以通过 contract 接收不同 detector。

### Phase 2: Offline Adapter Paths

- [x] Task 20: 接入 deterministic adapter 和 mock adapter。
- [x] Task 21: 增加 LLM 输出 schema、prompt 模板和解析校验。

### Checkpoint: Offline Confidence

- [x] `deterministic` 是默认 detector，完整质量门禁可离线通过。
- [x] `mock` detector 可端到端生成报告，并被测试覆盖。
- [x] LLM 输出解析和错误路径均可离线测试。

### Phase 3: Optional LLM Path And Delivery

- [ ] Task 22: 增加可选 LLM adapter 与 CLI detector 选择。
- [ ] Task 23: 完成第三阶段交付报告、文档和质量门禁。

### Checkpoint: Stage 3 Complete

- [ ] 默认命令仍离线可复现。
- [ ] `--detector deterministic`、`--detector mock`、`--detector llm` 路径清晰。
- [ ] LLM 路径缺少配置时失败信息可理解，且不会影响默认 CI。
- [ ] README、SPEC、CHANGELOG、开发文档和阶段三交付报告已同步。
- [ ] `powershell -ExecutionPolicy Bypass -File scripts/quality.ps1` 通过。
- [ ] `pre-commit run --all-files` 通过。

## Out Of Scope For Stage 3

- 多套件 orchestration。
- 复杂 suite 配置和批量运行。
- 报告回归比较 CLI。
- 多 provider 抽象层。
- Prompt 调优平台、缓存、重试、并发和成本统计。
- 将真实 LLM 路径纳入默认 CI。

## Risks and Mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| LLM 接入破坏默认可复现性 | CI 不稳定，默认用户无法离线运行 | 默认 detector 保持 deterministic，LLM 必须显式选择 |
| LLM 返回非结构化文本 | 无法稳定计算指标和生成报告 | 增加 JSON schema 解析校验，失败时抛出明确错误 |
| API key 泄漏 | 安全风险 | 只读环境变量，不写入报告和日志，不提交 `.env` |
| 为了 LLM 过度抽象 | 开发变慢，交付价值滞后 | 只做 deterministic/mock/llm 三条最小路径 |
| provider API 细节变化 | 实现失败或难维护 | 实现前查官方文档；adapter 边界隔离 provider 细节 |

## Open Questions

- LLM adapter 首选 provider 是否固定为 OpenAI，还是先做 OpenAI-compatible HTTP 配置？
- 阶段三交付报告是否只提交 deterministic 报告，还是同时提交 mock/LLM 示例报告？
- LLM 返回 `rule_ids` 是使用 `llm.*` 虚拟规则 ID，还是允许为空并只在 `reasons` 中说明？
