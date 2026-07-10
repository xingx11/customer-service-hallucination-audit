# 第三阶段任务清单

## Task 17: 建立第三阶段计划和任务清单

**Description:** 在 `v0.2.0` 第二阶段完成后，明确第三阶段目标、边界、任务顺序和验收标准，避免直接进入大范围实现。

**Acceptance criteria:**

- [x] 阶段三目标聚焦评测扩展、detector 适配边界、跨套件报告和回归比较。
- [x] 明确默认离线可复现、不接真实 LLM、不新增运行时依赖的边界。
- [x] 后续任务均包含验收标准、验证命令、依赖和预计触达文件。

**Verification:**

- [x] 文档存在：`tasks/stage-3-plan.md`, `tasks/stage-3-todo.md`
- [x] `tasks/plan.md` 和 `tasks/todo.md` 指向当前阶段三活动计划。
- [x] README、SPEC、CHANGELOG、开发文档同步阶段三规划状态。

**Dependencies:** 第二阶段合并并打 `v0.2.0` 标签

**Files likely touched:**

- `tasks/stage-3-plan.md`
- `tasks/stage-3-todo.md`
- `tasks/plan.md`
- `tasks/todo.md`
- `docs/SPEC.md`
- `docs/DEVELOPMENT.md`
- `README.md`
- `CHANGELOG.md`

**Estimated scope:** Small

## Task 18: 对齐版本元数据与发布记录

**Description:** 修复 `v0.2.0` 标签后源码版本信息仍停留在旧版本的风险，明确后续版本策略，并让 CLI/package 元数据与当前发布状态一致。

**Acceptance criteria:**

- [ ] `pyproject.toml` 和 package `__version__` 与当前阶段版本策略一致。
- [ ] `python -m customer_service_hallucination_audit --version` 输出符合预期。
- [ ] CHANGELOG 中 `0.2.0` 发布段落和新的 `Unreleased` 段落清晰分离。

**Verification:**

- [ ] Tests pass: `python -m pytest tests/test_cli.py`
- [ ] Quality gate passes: `powershell -ExecutionPolicy Bypass -File scripts/quality.ps1`

**Dependencies:** Task 17

**Files likely touched:**

- `pyproject.toml`
- `src/customer_service_hallucination_audit/__init__.py`
- `tests/test_cli.py`
- `CHANGELOG.md`

**Estimated scope:** Small

## Task 19: 定义 detector adapter contract

**Description:** 为检测器定义可替换接口，使 pipeline 可以在测试中注入 mock detector，同时默认 CLI 仍使用现有确定性规则检测器。

**Acceptance criteria:**

- [ ] adapter contract 明确输入为 `ReplyCase` 序列，输出为 `DetectionResult` 序列。
- [ ] 默认确定性 detector 被包装或适配到同一 contract 下。
- [ ] pipeline 可注入 mock detector，且默认行为不变。

**Verification:**

- [ ] Tests pass: `python -m pytest tests/test_pipeline.py tests/test_detector.py`
- [ ] Type check passes: `python -m mypy src`

**Dependencies:** Task 18

**Files likely touched:**

- `src/customer_service_hallucination_audit/models.py`
- `src/customer_service_hallucination_audit/detector.py`
- `src/customer_service_hallucination_audit/pipeline.py`
- `tests/test_pipeline.py`
- `tests/test_detector.py`

**Estimated scope:** Medium

## Task 20: 增加评测套件模型和 loader

**Description:** 增加描述评测套件的轻量模型和读取逻辑，用显式元数据组合 replies/ground truth 路径，为后续多数据集评测打基础。

**Acceptance criteria:**

- [ ] suite 模型包含稳定 ID、说明、回复路径和人工真值路径。
- [ ] loader 校验 suite ID、文件路径和数据 ID 一致性。
- [ ] 默认数据和阶段二 fixture 能通过 suite 形式被引用，不改变原 JSON 数据格式。

**Verification:**

- [ ] Tests pass: `python -m pytest tests/test_io.py`
- [ ] Edge cases covered: duplicate suite ID, missing file, mismatched IDs.

**Dependencies:** Task 19

**Files likely touched:**

- `src/customer_service_hallucination_audit/models.py`
- `src/customer_service_hallucination_audit/io.py`
- `tests/test_io.py`
- `tests/fixtures/`

**Estimated scope:** Medium

## Task 21: 支持跨套件运行与报告元数据

**Description:** 在单次 `run_audit` 之外增加 suite orchestration，使多个评测套件可顺序运行，并在报告中输出 dataset/suite、detector 和运行元数据。

**Acceptance criteria:**

- [ ] 单套件 `run_audit` 默认行为保持兼容。
- [ ] 新的 suite runner 可输出每个 suite 的指标和聚合摘要。
- [ ] Markdown/JSON 报告包含稳定的 suite/detector 元数据。

**Verification:**

- [ ] Tests pass: `python -m pytest tests/test_pipeline.py tests/test_reporting.py`
- [ ] Delivery report consistency tests updated if report schema changes.

**Dependencies:** Task 20

**Files likely touched:**

- `src/customer_service_hallucination_audit/pipeline.py`
- `src/customer_service_hallucination_audit/reporting.py`
- `src/customer_service_hallucination_audit/models.py`
- `tests/test_pipeline.py`
- `tests/test_reporting.py`

**Estimated scope:** Medium

## Task 22: 增加报告回归比较能力

**Description:** 提供离线比较两个 JSON 报告或当前输出与基线报告的能力，帮助后续修改规则时识别指标、类型表现和规则命中的漂移。

**Acceptance criteria:**

- [ ] 能比较总体指标、类型指标、规则命中摘要和错误案例数量变化。
- [ ] 比较输出稳定、可读，适合作为 PR 审查辅助。
- [ ] 默认比较逻辑不依赖真实 LLM 或外部服务。

**Verification:**

- [ ] Tests pass: `python -m pytest tests/test_reporting.py tests/test_cli.py`
- [ ] Manual check: 使用 stage-2 报告与临时生成报告比较。

**Dependencies:** Task 21

**Files likely touched:**

- `src/customer_service_hallucination_audit/reporting.py`
- `src/customer_service_hallucination_audit/__main__.py`
- `tests/test_reporting.py`
- `tests/test_cli.py`

**Estimated scope:** Medium

## Task 23: 第三阶段交付收尾

**Description:** 更新文档、生成阶段三交付报告，运行完整质量门禁并记录阶段三完成状态。

**Acceptance criteria:**

- [ ] README/SPEC/CHANGELOG/开发文档说明阶段三能力、边界和局限性。
- [ ] 阶段三交付报告或 suite summary 已提交并有一致性测试。
- [ ] 完整质量门禁通过。

**Verification:**

- [ ] `powershell -ExecutionPolicy Bypass -File scripts/quality.ps1`
- [ ] `pre-commit run --all-files`
- [ ] `git status --short`

**Dependencies:** Task 18-22

**Files likely touched:**

- `README.md`
- `docs/SPEC.md`
- `docs/DEVELOPMENT.md`
- `CHANGELOG.md`
- `docs/reports/`
- `tests/test_delivery_reports.py`

**Estimated scope:** Small
