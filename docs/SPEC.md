# Spec: Customer Service Hallucination Audit

## Objective

实现一个客服回复幻觉检测工具，对 0110 任务的 20 条回复逐条标注是否存在幻觉、幻觉类型和原因，并用人工标注计算检出率。最终交付代码仓库、README、运行报告和质量验证结果。

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

- 可以读取 `data/replies.json` 和 `data/ground_truth.json`。
- 可以输出逐条检测结果。
- 可以计算 precision、recall、F1、漏检和误报。
- CLI 可以通过默认路径或显式路径运行端到端流水线，并生成 Markdown/JSON 报告。
- README 说明分类体系、检测方法、局限性和 AI 工具使用情况。
- CI 中 lint、format check、type check、tests 全部通过。

## Open Questions

- 最终报告输出格式采用 Markdown、JSON，还是两者都生成？
- 是否需要加入可选 LLM/mock 模式来展示扩展能力？
- 是否需要为最差案例生成更详细的中文解释模板？
