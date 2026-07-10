# 第三阶段任务清单：最小 LLM 接入闭环

## Task 17: 重新校准第三阶段规划

**Description:** 将第三阶段从长期“评测框架化”调整为交付优先的最小 LLM 接入闭环，明确项目后续只剩阶段三功能开发和阶段四最终交付收尾。

**Acceptance criteria:**

- [x] 阶段三目标改为 Adapter + 最小 LLM 接入。
- [x] 明确 `deterministic` 默认离线路径、`mock` 测试路径和 `llm` 显式 opt-in 路径。
- [x] 多套件 orchestration、复杂 suite 配置、报告回归比较等长期能力移出阶段三范围。

**Verification:**

- [x] 文档存在：`tasks/stage-3-plan.md`, `tasks/stage-3-todo.md`
- [x] `tasks/plan.md` 和 `tasks/todo.md` 指向当前阶段三活动计划。
- [x] README、SPEC、CHANGELOG、开发文档同步阶段三新目标。

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

**Description:** 修复 `v0.2.0` 标签后源码版本信息仍停留在旧版本的风险，明确阶段三开发版本策略，并让 CLI/package 元数据与当前发布状态一致。

**Acceptance criteria:**

- [ ] `pyproject.toml` 和 package `__version__` 与当前阶段版本策略一致。
- [ ] `python -m customer_service_hallucination_audit --version` 输出符合预期。
- [ ] CHANGELOG 中 `0.2.0` 发布段落和新的阶段三 `Unreleased` 段落清晰分离。

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

**Description:** 为检测器定义可替换接口，使 pipeline 可以接收不同 detector，同时默认 CLI 仍使用现有确定性规则检测器。

**Acceptance criteria:**

- [ ] adapter contract 明确输入为 `ReplyCase` 序列，输出为 `DetectionResult` 序列。
- [ ] contract 不依赖真实 LLM、网络、环境变量或 provider SDK。
- [ ] pipeline 可注入 detector，默认行为不变。

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

## Task 20: 接入 deterministic adapter 和 mock adapter

**Description:** 将现有规则检测器包装为 `deterministic` adapter，并增加一个离线 mock adapter，用于验证 CLI detector 选择、pipeline 注入和报告生成链路。

**Acceptance criteria:**

- [ ] `deterministic` adapter 复用当前规则检测器，默认输出不变。
- [ ] `mock` adapter 可生成稳定、可测试的 `DetectionResult`。
- [ ] adapter 选择错误时返回清晰错误。

**Verification:**

- [ ] Tests pass: `python -m pytest tests/test_detector.py tests/test_pipeline.py tests/test_cli.py`
- [ ] Delivery reports for deterministic path remain stable.

**Dependencies:** Task 19

**Files likely touched:**

- `src/customer_service_hallucination_audit/detector.py`
- `src/customer_service_hallucination_audit/pipeline.py`
- `src/customer_service_hallucination_audit/__main__.py`
- `tests/test_detector.py`
- `tests/test_cli.py`

**Estimated scope:** Medium

## Task 21: 增加 LLM 输出 schema、prompt 模板和解析校验

**Description:** 定义 LLM detector 的最小 prompt 和结构化输出 schema，提供离线解析与校验逻辑，确保 LLM 返回可以稳定转换为 `DetectionResult`。

**Acceptance criteria:**

- [ ] prompt 明确只依据用户问题、系统回复和知识库判断，不读取人工真值。
- [ ] parser 校验 `case_id`、`is_hallucination`、`hallucination_type`、`reasons`、`rule_ids`。
- [ ] 未知幻觉类型、case_id 不匹配、缺字段、非 JSON 输出均抛出可理解错误。

**Verification:**

- [ ] Tests pass: `python -m pytest tests/test_detector.py`
- [ ] Type check passes: `python -m mypy src`

**Dependencies:** Task 20

**Files likely touched:**

- `src/customer_service_hallucination_audit/detector.py`
- `src/customer_service_hallucination_audit/models.py`
- `tests/test_detector.py`

**Estimated scope:** Medium

## Task 22: 增加可选 LLM adapter 与 CLI detector 选择

**Description:** 增加显式 opt-in 的 LLM detector 路径和 CLI 参数，使用户可以选择 `deterministic`、`mock` 或 `llm`，其中 LLM 配置只从环境变量读取。

**Acceptance criteria:**

- [ ] CLI 支持 `--detector deterministic|mock|llm`，默认值为 `deterministic`。
- [ ] `llm` 路径缺少 API key 或配置时给出清晰错误，不影响默认路径。
- [ ] LLM adapter 可通过 fake client 离线测试，不进行真实网络调用。

**Verification:**

- [ ] Tests pass: `python -m pytest tests/test_cli.py tests/test_pipeline.py tests/test_detector.py`
- [ ] Manual check: `python -m customer_service_hallucination_audit --detector deterministic --output-dir reports`
- [ ] Manual check: `python -m customer_service_hallucination_audit --detector mock --output-dir reports`

**Dependencies:** Task 21

**Files likely touched:**

- `src/customer_service_hallucination_audit/__main__.py`
- `src/customer_service_hallucination_audit/pipeline.py`
- `src/customer_service_hallucination_audit/detector.py`
- `tests/test_cli.py`
- `tests/test_pipeline.py`

**Estimated scope:** Medium

## Task 23: 第三阶段交付收尾

**Description:** 更新文档、生成阶段三交付报告，运行完整质量门禁并记录阶段三完成状态，为最终 `v1.0.0` 交付阶段做准备。

**Acceptance criteria:**

- [ ] README/SPEC/CHANGELOG/开发文档说明阶段三 detector 选择、LLM opt-in 边界和局限性。
- [ ] 阶段三 deterministic 交付报告已提交并有一致性测试。
- [ ] 完整质量门禁通过，默认路径不依赖真实 LLM。

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
