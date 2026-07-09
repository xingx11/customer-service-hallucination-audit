# 第二阶段任务清单

## Task 9: 建立第二阶段计划和任务清单

**Description:** 在第一阶段 `v0.1.0` 基础上明确第二阶段目标、边界、任务顺序和验收标准，避免后续直接进入大范围实现。

**Acceptance criteria:**

- [x] 阶段二目标聚焦鲁棒性与可解释性增强。
- [x] 明确默认离线可复现、不接真实 LLM、不新增运行时依赖的边界。
- [x] 每个后续任务都有验收标准和验证命令。

**Verification:**

- [x] 文档存在：`tasks/stage-2-plan.md`, `tasks/stage-2-todo.md`
- [x] Markdown hooks pass for changed docs.

**Dependencies:** 第一阶段完成并打 `v0.1.0` 标签

**Files likely touched:**

- `tasks/stage-2-plan.md`
- `tasks/stage-2-todo.md`
- `docs/SPEC.md`
- `docs/DEVELOPMENT.md`

**Estimated scope:** Small

## Task 10: 设计阶段二鲁棒性测试样本集

**Description:** 构建不影响默认发布数据的测试 fixture，用于覆盖同义改写、困难负例、边界遗漏和多规则相近触发场景。

**Acceptance criteria:**

- [ ] 新样本不修改 `data/replies.json` 或 `data/ground_truth.json` 的格式。
- [ ] 样本覆盖至少 6 类幻觉和至少 3 条困难负例。
- [ ] 样本说明能解释为什么它们补足阶段一默认数据的盲区。

**Verification:**

- [ ] Tests pass: `python -m pytest tests/test_detector.py`
- [ ] Fixture review confirms no 人工真值硬编码进 detector。

**Dependencies:** Task 9

**Files likely touched:**

- `tests/test_detector.py`
- `tests/fixtures/`
- `docs/DEVELOPMENT.md`

**Estimated scope:** Medium

## Task 11: 扩展检测器边界测试

**Description:** 基于阶段二 fixture 增加 detector 测试，验证规则对同义表达、近似但正确回复、关键限制遗漏和安全敏感场景的行为。

**Acceptance criteria:**

- [ ] 同义改写样本能触发预期规则。
- [ ] 困难负例不被基础规则误报。
- [ ] 信息遗漏和政策偏差的边界有测试描述。

**Verification:**

- [ ] Tests pass: `python -m pytest tests/test_detector.py`
- [ ] Existing default-data detector tests still pass.

**Dependencies:** Task 10

**Files likely touched:**

- `tests/test_detector.py`
- `src/customer_service_hallucination_audit/detector.py`

**Estimated scope:** Medium

## Task 12: 引入规则元数据模型

**Description:** 将规则 ID、幻觉类型、风险等级、中文说明和触发意图结构化，减少 detector 中散落的解释文本。

**Acceptance criteria:**

- [ ] 每条规则有稳定 ID、类别、风险等级和中文说明。
- [ ] 检测逻辑引用规则元数据，不维护重复的规则说明文本。
- [ ] 默认 20 条样本的预测结果保持稳定，除非有明确测试说明。

**Verification:**

- [ ] Tests pass: `python -m pytest tests/test_detector.py`
- [ ] Type check passes: `python -m mypy src`

**Dependencies:** Task 11

**Files likely touched:**

- `src/customer_service_hallucination_audit/detector.py`
- `src/customer_service_hallucination_audit/models.py`
- `tests/test_detector.py`

**Estimated scope:** Medium

## Task 13: 暴露规则命中摘要

**Description:** 在报告 payload 或检测结果派生结构中提供规则命中摘要，使用户能看到哪些规则最常触发、哪些规则对应高风险案例。

**Acceptance criteria:**

- [ ] JSON 报告包含稳定排序的规则命中摘要。
- [ ] Markdown 报告能解释高风险规则命中的原因。
- [ ] 不在 CLI 层计算规则统计。

**Verification:**

- [ ] Tests pass: `python -m pytest tests/test_reporting.py tests/test_pipeline.py`
- [ ] Golden-style assertions cover 新增 JSON 字段顺序。

**Dependencies:** Task 12

**Files likely touched:**

- `src/customer_service_hallucination_audit/reporting.py`
- `src/customer_service_hallucination_audit/pipeline.py`
- `tests/test_reporting.py`
- `tests/test_pipeline.py`

**Estimated scope:** Medium

## Task 14: 增加按幻觉类型聚合的指标

**Description:** 在二分类指标之外，增加按人工标注类型和预测类型聚合的统计，帮助识别规则对不同幻觉类型的强弱项。

**Acceptance criteria:**

- [ ] per-type 统计包含 label count、predicted count、true positive count 和 mismatch count。
- [ ] 空输入、未知类型和无预测正例场景仍有清晰行为。
- [ ] 统计结果按幻觉类型稳定排序。

**Verification:**

- [ ] Tests pass: `python -m pytest tests/test_metrics.py`
- [ ] Type check passes: `python -m mypy src`

**Dependencies:** Task 12

**Files likely touched:**

- `src/customer_service_hallucination_audit/metrics.py`
- `src/customer_service_hallucination_audit/models.py`
- `tests/test_metrics.py`

**Estimated scope:** Medium

## Task 15: 增强报告解释

**Description:** 将 per-type 指标、规则命中摘要和高风险排序依据加入 Markdown/JSON 报告，提升报告可审阅性。

**Acceptance criteria:**

- [ ] Markdown 报告包含类型表现和规则命中统计。
- [ ] JSON 报告包含机器可读的类型统计和规则统计。
- [ ] 报告局限性说明更新样本规模和规则泛化边界。

**Verification:**

- [ ] Tests pass: `python -m pytest tests/test_reporting.py tests/test_delivery_reports.py`
- [ ] Golden-style assertions confirm 新增 sections and keys exist.

**Dependencies:** Task 13, Task 14

**Files likely touched:**

- `src/customer_service_hallucination_audit/reporting.py`
- `tests/test_reporting.py`
- `docs/reports/`

**Estimated scope:** Medium

## Task 16: 第二阶段交付与质量门禁

**Description:** 更新文档、交付报告和变更记录，运行完整质量命令，确认阶段二没有破坏离线可复现边界。

**Acceptance criteria:**

- [ ] README/SPEC 说明阶段二新增能力和局限性。
- [ ] CHANGELOG 记录阶段二增强。
- [ ] 完整质量门禁通过。

**Verification:**

- [ ] `powershell -ExecutionPolicy Bypass -File scripts/quality.ps1`
- [ ] `pre-commit run --all-files`
- [ ] `git status --short`

**Dependencies:** Task 10-15

**Files likely touched:**

- `README.md`
- `docs/SPEC.md`
- `docs/DEVELOPMENT.md`
- `CHANGELOG.md`
- `docs/reports/`

**Estimated scope:** Small
