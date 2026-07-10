# 第四阶段任务清单：最终交付收尾

## Task 24: 建立阶段四发布准备计划和发布检查清单

**Description:** 将阶段四范围固定为最终交付收尾，补齐发布准备计划、任务清单和发布检查清单，并同步活动任务指针，避免后续继续扩大功能面。

**Acceptance criteria:**

- [x] 阶段四目标明确为 `v1.0.0` 发布准备，而不是新增 detector 能力。
- [x] `tasks/plan.md` 和 `tasks/todo.md` 指向阶段四活动计划。
- [x] 发布检查清单覆盖质量门禁、安装 smoke、默认 CLI、LLM opt-in 边界和标签步骤。
- [x] `.env.example` 暂不新增的原因已记录：当前应用不读取 `.env`，LLM 配置通过进程环境变量提供。

**Verification:**

- [x] 文档存在：`tasks/stage-4-plan.md`, `tasks/stage-4-todo.md`, `docs/RELEASE_CHECKLIST.md`
- [x] README、SPEC、CHANGELOG、开发文档同步阶段四启动状态。
- [x] Quality gate passes: `powershell -ExecutionPolicy Bypass -File scripts/quality.ps1`
- [x] Pre-commit passes: `pre-commit run --all-files`

**Dependencies:** 第三阶段合并并打 `v0.3.0` 标签

**Files likely touched:**

- `tasks/stage-4-plan.md`
- `tasks/stage-4-todo.md`
- `tasks/plan.md`
- `tasks/todo.md`
- `docs/RELEASE_CHECKLIST.md`
- `docs/SPEC.md`
- `docs/DEVELOPMENT.md`
- `README.md`
- `CHANGELOG.md`

**Estimated scope:** Small

## Task 25: 最终文档与交付复核

**Description:** 对 README、SPEC、开发文档、CHANGELOG 和已提交交付报告做最终一致性复核，确保项目目标、默认命令、LLM opt-in 配置、局限性和 AI 工具使用说明可以直接交付审阅。

**Acceptance criteria:**

- [x] README 的快速开始、质量命令、开发路线、交付报告链接和局限性保持一致。
- [x] SPEC 的阶段状态、成功标准、边界和已解决决策与当前源码行为一致。
- [x] DEVELOPMENT 文档能指导后续 agent 从阶段四继续开发。
- [x] CHANGELOG 的 `Unreleased` 内容准确描述阶段四收尾变更。
- [x] 文档明确项目不自动读取 `.env`，`llm` detector 只读取进程环境变量。
- [x] 交付复核结果记录在 `docs/DELIVERY_REVIEW.md`。

**Verification:**

- [x] Manual review: 打开 README、SPEC、DEVELOPMENT、CHANGELOG，逐项核对阶段状态。
- [x] Link review: 阶段一到阶段三报告链接和阶段四计划链接可访问。
- [x] `python -m pytest tests/test_delivery_reports.py`

**Dependencies:** Task 24

**Files likely touched:**

- `README.md`
- `docs/SPEC.md`
- `docs/DEVELOPMENT.md`
- `CHANGELOG.md`
- `tasks/stage-4-plan.md`
- `tasks/stage-4-todo.md`

**Estimated scope:** Small

## Task 26: 最终质量门禁与安装/CLI smoke test

**Description:** 在最终发布前运行完整质量门禁、pre-commit 和安装/CLI smoke test，证明默认数据随包可用，deterministic/mock 路径可离线生成报告，LLM 缺配置路径能清晰失败。

**Acceptance criteria:**

- [ ] ruff、format check、mypy、pytest 和 pre-commit 全部通过。
- [ ] 默认 packaged data 可在 CLI smoke test 中读取并生成 Markdown/JSON 报告。
- [ ] `--detector mock` 可离线生成报告。
- [ ] `--detector llm` 缺少环境变量时返回清晰错误，不产生伪结果。
- [ ] 验证结果记录到开发文档或阶段四最终收尾记录中。

**Verification:**

- [ ] `powershell -ExecutionPolicy Bypass -File scripts/quality.ps1`
- [ ] `pre-commit run --all-files`
- [ ] `python -m customer_service_hallucination_audit --help`
- [ ] `python -m customer_service_hallucination_audit --version`
- [ ] `python -m customer_service_hallucination_audit --output-dir <temp>`
- [ ] `python -m customer_service_hallucination_audit --detector mock --output-dir <temp>`
- [ ] `python -m customer_service_hallucination_audit --detector llm --output-dir <temp>` fails clearly without LLM env vars.

**Dependencies:** Task 25

**Files likely touched:**

- `docs/DEVELOPMENT.md`
- `CHANGELOG.md`

**Estimated scope:** Small

## Task 27: `v1.0.0` 发布收尾

**Description:** 完成正式版收尾：更新版本元数据和 CHANGELOG，生成阶段四最终交付报告，标记阶段四完成，并在合并 main 后按发布检查清单打 `v1.0.0` 标签。

**Acceptance criteria:**

- [ ] package/CLI 版本为 `1.0.0`，`--version` 输出一致。
- [ ] CHANGELOG 增加 `1.0.0` 发布段落，并清空或保留合理的 `Unreleased` 占位。
- [ ] 阶段四 Markdown/JSON 交付报告已提交并与当前 pipeline 输出一致。
- [ ] README、SPEC、DEVELOPMENT 和任务清单标记阶段四完成。
- [ ] 合并到 main 后按 `docs/RELEASE_CHECKLIST.md` 打 `v1.0.0` annotated tag。

**Verification:**

- [ ] `python -m pytest tests/test_cli.py tests/test_scaffold.py tests/test_delivery_reports.py`
- [ ] `powershell -ExecutionPolicy Bypass -File scripts/quality.ps1`
- [ ] `pre-commit run --all-files`
- [ ] Manual check: `git tag -n v1.0.0` after merge and tag.

**Dependencies:** Task 25-26

**Files likely touched:**

- `src/customer_service_hallucination_audit/__init__.py`
- `tests/test_cli.py`
- `tests/test_scaffold.py`
- `docs/reports/stage-4-report.md`
- `docs/reports/stage-4-report.json`
- `tests/test_delivery_reports.py`
- `README.md`
- `docs/SPEC.md`
- `docs/DEVELOPMENT.md`
- `CHANGELOG.md`
- `tasks/plan.md`
- `tasks/todo.md`
- `tasks/stage-4-plan.md`
- `tasks/stage-4-todo.md`

**Estimated scope:** Medium
