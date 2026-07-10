# Spec: Customer Service Hallucination Audit

## Objective

实现一个客服回复幻觉检测工具，对 0110 任务的 20 条回复逐条标注是否存在幻觉、幻觉类型和原因，并用人工标注计算检出率。最终交付代码仓库、README、运行报告和质量验证结果。

## Stage 1 Status

第一阶段已经完成：默认离线流水线可读取随包数据或显式 JSON 路径，执行确定性规则检测，计算指标，生成 Markdown/JSON 报告，并提交阶段一交付报告。质量门禁以 `scripts/quality.ps1`、pytest、ruff 和 mypy 为准。

## Stage 2 Status

第二阶段聚焦鲁棒性与可解释性增强：扩展默认数据之外的测试样本，结构化规则元数据，增加规则命中摘要和按类型聚合的指标，并增强 Markdown/JSON 报告解释能力。阶段二仍保持默认离线可复现，不接入真实 LLM API，不新增运行时依赖。

当前阶段二已完成鲁棒性样本、检测器边界测试、规则元数据模型、规则命中摘要、按幻觉类型聚合的指标、Markdown/JSON 报告解释增强和阶段二交付收尾。规则命中摘要由报告层基于检测结果和规则元数据聚合生成，CLI 不负责计算规则统计；类型指标由 metrics 层计算并由报告层展示。阶段二交付报告位于 `docs/reports/stage-2-report.md` 和 `docs/reports/stage-2-report.json`。

阶段二规划文档：

- `tasks/stage-2-plan.md`
- `tasks/stage-2-todo.md`

## Stage 3 Status

第三阶段聚焦 Adapter + 最小 LLM 接入：已对齐 `v0.2.0` 标签后的版本元数据与发布记录，定义 detector adapter contract，把现有规则检测器包装为默认 `deterministic` adapter，增加离线 `mock` adapter，并提供显式 opt-in 的 `llm` adapter。当前已完成 `deterministic`、`mock` 与 `llm` 三条 detector 路径，也已定义 LLM prompt、输出 schema、离线解析校验和缺配置错误路径。阶段三保持默认离线可复现，不新增运行时依赖，不改变默认 `data/replies.json` 和 `data/ground_truth.json` 字段格式。阶段三交付报告位于 `docs/reports/stage-3-report.md` 和 `docs/reports/stage-3-report.json`。

项目后续阶段收敛为：

```text
v0.1.0  阶段一：离线评测 MVP，已完成
v0.2.0  阶段二：鲁棒性与可解释性，已完成
v0.3.0  阶段三：Adapter + 最小 LLM 接入，已完成
v1.0.0  阶段四：最终交付收尾，下一步
```

阶段三规划文档：

- `tasks/stage-3-plan.md`
- `tasks/stage-3-todo.md`

`llm` detector 只在显式选择 `--detector llm` 时启用，并从以下环境变量读取配置：

- `CS_HALLUCINATION_AUDIT_LLM_API_KEY`
- `CS_HALLUCINATION_AUDIT_LLM_ENDPOINT`
- `CS_HALLUCINATION_AUDIT_LLM_MODEL`

## Tech Stack

- Python 3.11+
- CLI: `argparse`
- Data model: `dataclasses`
- Test: pytest
- Lint/format: ruff
- Type check: mypy
- CI: GitHub Actions

不使用 Web 框架，不接入数据库。默认实现必须离线可复现。

## Commands

```bash
python -m pip install -e ".[dev]"
python -m customer_service_hallucination_audit --help
python -m customer_service_hallucination_audit --output-dir reports
python -m ruff check .
python -m ruff format --check .
python -m mypy src
python -m pytest
```

## Project Structure

```text
data/        原始任务数据
docs/        规格、决策记录和补充说明
src/         应用源码
tests/       单元测试和集成测试
.github/     CI 配置
```

## Code Style

```python
def calculate_f1(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)
```

- 函数名使用动词短语，表达业务含义。
- 类型边界要明确，避免无意义的 `dict[str, object]` 在业务层扩散。
- 规则、指标、报告生成拆分为独立模块。
- 注释解释非显而易见的取舍，不复述代码。

## Detection Scope

需要支持以下幻觉类别：

- 政策编造
- 政策偏差
- 参数编造
- 优惠编造
- 信息编造
- 能力越界
- 安全误导
- 信息遗漏

类别体系可在实现中合并或扩展，但 README 必须解释选择理由。

## Testing Strategy

- Unit tests: 数据模型、规则匹配、指标计算。
- Integration tests: 从 JSON 输入到报告输出的完整流程。
- Golden tests: 固定输入样本的输出结构稳定。
- Quality gate: ruff、mypy、pytest 全部通过。

## Boundaries

- Always: 离线可运行；可复现；有测试；报告解释误判。
- Ask first: 新增外部依赖；引入真实 LLM；改变提交数据。
- Never: 提交密钥；把人工真值硬编码为预测结果；删除失败测试来掩盖问题。

## Success Criteria

- 可以读取随包发布的默认数据，也可以显式读取 `data/replies.json` 和 `data/ground_truth.json`。
- 可以输出逐条检测结果。
- 可以计算 precision、recall、F1、漏检和误报。
- CLI 可以通过默认数据或显式路径运行端到端流水线，并生成 Markdown/JSON 报告。
- 仓库提交阶段一 Markdown/JSON 交付报告，并可用测试验证其与当前流水线输出一致。
- README 说明分类体系、检测方法、局限性和 AI 工具使用情况。
- CI 中 lint、format check、type check、tests 全部通过。

## Stage 2 Success Criteria

- 新增鲁棒性测试样本覆盖同义改写、困难负例、信息遗漏和安全敏感场景。
- 规则元数据包含稳定 ID、幻觉类型、风险等级和中文说明。
- 报告能展示规则命中摘要、按类型聚合的评估结果和高风险排序依据。
- 默认 CLI 仍可离线运行，阶段一默认数据、报告生成和质量门禁不回退。
- README、CHANGELOG、开发文档和任务清单已同步阶段二完成状态。

## Stage 3 Success Criteria

- CLI/package 版本信息与发布策略一致，`CHANGELOG` 中 `0.2.0` 发布段落和新的阶段三 `Unreleased` 段落清晰分离。
- pipeline 可以通过 detector contract 注入不同 detector，默认 CLI 仍使用确定性规则检测器。
- CLI 支持 `--detector deterministic|mock|llm`，默认值为 `deterministic`。
- mock detector 可离线端到端生成报告，并用于测试 adapter 注入链路。
- LLM detector 显式 opt-in，配置只从环境变量读取，缺少配置或输出非法时给出清晰错误。
- LLM 输出经过 schema 解析和幻觉类型校验后转换为现有 `DetectionResult`。
- README、SPEC、CHANGELOG、开发文档和阶段三交付报告已同步，完整质量门禁通过且不依赖真实 LLM。

## Resolved Decisions And Follow-ups

- 报告格式：阶段一同时生成 Markdown 和 JSON。Markdown 面向人工审阅，JSON 面向自动化消费和 golden-style 验证。
- LLM/mock 模式：第一阶段不接入真实 LLM，也不要求 mock adapter；核心评测保持离线可复现，adapter 边界留到后续阶段。
- 最差案例解释：阶段一报告已包含漏检、误报、高风险案例和局限性说明；更详细的中文解释模板作为后续增强项。
- 阶段二边界：优先增强鲁棒性样本、规则解释和报告指标；真实 LLM 接入仍不进入默认执行路径。
- 规则命中摘要：报告层按规则 ID 聚合命中次数、样本 ID、风险等级、触发意图和中文说明；JSON 保持稳定字段顺序，Markdown 面向人工审阅展示规则解释。
- 阶段三边界：优先完成 adapter contract、mock adapter 和显式 opt-in 的最小 LLM adapter；多套件 orchestration、复杂 suite 配置和报告回归比较移出阶段三。
- detector 选择：CLI 当前支持 `--detector deterministic|mock|llm`；`deterministic` 是默认离线路径，`mock` 只生成稳定合成结果用于验证 adapter 注入和报告链路，`llm` 只在显式选择且环境变量齐全时调用 OpenAI-compatible chat completions endpoint。
- LLM 输出边界：当前已定义只依据用户问题、系统回复和知识库的 prompt，以及 `case_id`、`is_hallucination`、`hallucination_type`、`reasons`、`rule_ids` 的最小 JSON schema、离线 parser 和 fake client 测试边界。
- 版本元数据跟进：`v0.2.0` 已打标签，阶段三第一批任务需要确认 package/CLI 版本来源，避免发布标签和运行时版本长期不一致。
- LLM 接入边界：真实 LLM 只作为显式选择路径，不进入默认 CI；密钥只从环境变量读取，不写入报告或日志。
