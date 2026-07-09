# 第一阶段任务清单

## 已完成基线

- [x] Task 0: 梳理当前项目状态、开发流程和阶段一任务拆分。
  - Acceptance: 开发流程、当前进度、模块边界和风险记录在仓库文档中。
  - Verify: 文档文件存在，任务清单可直接指导后续开发。
  - Files: `docs/DEVELOPMENT.md`, `tasks/plan.md`, `tasks/todo.md`, `.gitignore`

## 待实施任务

## Task 1: 定义领域模型和类型边界

**Description:** 用 dataclass 定义回复样本、人工标注、检测结果、指标汇总和错误案例，明确公共函数返回类型。

**Acceptance criteria:**

- [x] 输入样本包含 `id`、`user_question`、`system_reply`、`knowledge_base`。
- [x] 人工标注能表达非幻觉时 `hallucination_type` 为 `None`。
- [x] 检测结果包含是否幻觉、类型、原因和触发规则。

**Verification:**

- [x] Tests pass: `python -m pytest tests/test_models.py`
- [x] Type check passes for new module: `python -m mypy src`

**Dependencies:** Task 0

**Files likely touched:**

- `src/customer_service_hallucination_audit/models.py`
- `tests/test_models.py`

**Estimated scope:** Small

## Task 2: 实现 JSON 读取与数据一致性校验

**Description:** 读取 `replies.json` 和 `ground_truth.json`，转换为领域模型，并在边界处校验缺字段、重复 ID、未知类型和 ID 不对齐。

**Acceptance criteria:**

- [ ] 默认数据文件可解析出 20 条回复和 20 条人工标注。
- [ ] replies 和 ground truth 的 ID 集合必须完全一致。
- [ ] 非法 JSON 结构抛出可理解的领域错误。

**Verification:**

- [ ] Tests pass: `python -m pytest tests/test_io.py`
- [ ] Integration check: 使用默认 `data/` 文件加载成功。

**Dependencies:** Task 1

**Files likely touched:**

- `src/customer_service_hallucination_audit/io.py`
- `src/customer_service_hallucination_audit/models.py`
- `tests/test_io.py`

**Estimated scope:** Medium

## Task 3: 实现确定性规则检测器

**Description:** 基于回复和知识库实现离线规则检测，覆盖政策、参数、优惠、信息、能力、安全和信息遗漏等类别。

**Acceptance criteria:**

- [ ] detector 不读取人工真值 detail，不硬编码 ground truth 作为预测结果。
- [ ] 每个检测结果都给出中文原因和触发规则。
- [ ] `h12`、`h16` 这类一致回复应保持非幻觉预测。

**Verification:**

- [ ] Tests pass: `python -m pytest tests/test_detector.py`
- [ ] Rule coverage includes at least one case per planned hallucination type.

**Dependencies:** Task 1, Task 2

**Files likely touched:**

- `src/customer_service_hallucination_audit/detector.py`
- `src/customer_service_hallucination_audit/models.py`
- `tests/test_detector.py`

**Estimated scope:** Medium

## Task 4: 实现指标计算和错误案例分析

**Description:** 对检测结果和人工标注计算 confusion matrix、precision、recall、F1、false positives 和 false negatives。

**Acceptance criteria:**

- [ ] 指标定义清晰，除零时返回 `0.0`。
- [ ] false positives 和 false negatives 按样本 ID 稳定排序。
- [ ] 类型错误和是否幻觉错误能在错误分析中区分。

**Verification:**

- [ ] Tests pass: `python -m pytest tests/test_metrics.py`
- [ ] Edge cases covered: empty input, all-positive, all-negative, no predicted positives.

**Dependencies:** Task 1

**Files likely touched:**

- `src/customer_service_hallucination_audit/metrics.py`
- `src/customer_service_hallucination_audit/models.py`
- `tests/test_metrics.py`

**Estimated scope:** Small

## Task 5: 实现报告生成

**Description:** 生成人工可读 Markdown 报告和机器可读 JSON 结构，包含逐条结果、指标汇总、漏检、误报和高风险案例。

**Acceptance criteria:**

- [ ] Markdown 包含总体指标、分类结果表、漏检/误报列表和局限性说明。
- [ ] JSON 包含 `results`、`metrics`、`false_positives`、`false_negatives`。
- [ ] 输出顺序稳定，便于 golden-style 测试。

**Verification:**

- [ ] Tests pass: `python -m pytest tests/test_reporting.py`
- [ ] Golden-style assertions confirm required sections and keys exist.

**Dependencies:** Task 3, Task 4

**Files likely touched:**

- `src/customer_service_hallucination_audit/reporting.py`
- `src/customer_service_hallucination_audit/models.py`
- `tests/test_reporting.py`

**Estimated scope:** Medium

## Task 6: 集成 CLI 参数和端到端 pipeline

**Description:** 将读取、检测、评估和报告生成串联为 CLI 流水线，支持默认路径和显式路径。

**Acceptance criteria:**

- [ ] `python -m customer_service_hallucination_audit --help` 展示输入和输出参数。
- [ ] 默认参数读取 `data/replies.json` 和 `data/ground_truth.json`。
- [ ] 指定输出目录后生成报告文件，并在终端输出摘要。

**Verification:**

- [ ] Tests pass: `python -m pytest tests/test_cli.py tests/test_pipeline.py`
- [ ] Manual check: `python -m customer_service_hallucination_audit --output-dir reports`

**Dependencies:** Task 2, Task 3, Task 4, Task 5

**Files likely touched:**

- `src/customer_service_hallucination_audit/__main__.py`
- `src/customer_service_hallucination_audit/pipeline.py`
- `tests/test_cli.py`
- `tests/test_pipeline.py`

**Estimated scope:** Medium

## Task 7: 更新 README/SPEC 和交付说明

**Description:** 根据实际实现更新分类体系、检测方法、运行命令、报告格式、局限性和 AI 工具使用说明。

**Acceptance criteria:**

- [ ] README 中的命令与 CLI 实际参数一致。
- [ ] README 解释分类体系和确定性规则的局限性。
- [ ] SPEC 中的开放问题被回答或保留为明确后续项。

**Verification:**

- [ ] Markdown review confirms no outdated command or behavior description.
- [ ] Pre-commit markdown hooks pass.

**Dependencies:** Task 6

**Files likely touched:**

- `README.md`
- `docs/SPEC.md`
- `CHANGELOG.md`

**Estimated scope:** Small

## Task 8: 质量门禁和自审

**Description:** 运行完整质量命令，按代码审查清单检查正确性、可读性、架构、安全和性能。

**Acceptance criteria:**

- [ ] ruff check、ruff format check、mypy、pytest 全部通过。
- [ ] 无缓存、虚拟环境、CodeGraph 数据库或构建产物进入待提交变更。
- [ ] 自审记录确认没有硬编码人工真值、没有新增不可复现依赖。

**Verification:**

- [ ] `powershell -ExecutionPolicy Bypass -File scripts/quality.ps1`
- [ ] `git status --short`

**Dependencies:** Task 1, Task 2, Task 3, Task 4, Task 5, Task 6, Task 7

**Files likely touched:**

- `README.md`
- `docs/DEVELOPMENT.md`
- task-specific files from earlier tasks

**Estimated scope:** Small
