# Release Checklist

本清单用于阶段四 `v1.0.0` 发布收尾。它记录发布前必须确认的事项，避免质量门禁、默认数据、LLM 配置边界或标签步骤只停留在聊天记录里。

## Release Scope

- [ ] 阶段四只做最终交付收尾，不新增 detector 能力、Web UI、数据库或后台服务。
- [ ] 默认路径仍是 `deterministic` detector，离线、确定性、可复现。
- [ ] `mock` detector 只用于离线 adapter 链路验证。
- [ ] `llm` detector 只在显式选择 `--detector llm` 时启用，不进入默认 CI 或默认报告生成。
- [ ] 不新增运行时依赖；如新增，必须有单独决策记录和文档说明。
- [ ] 不新增 `.env` 自动加载。当前应用只读取进程环境变量，`.env` 和 `.env.*` 继续被忽略。

## Documentation Gate

- [ ] README 说明快速开始、默认数据、detector 选择、LLM 环境变量、质量命令、报告链接和局限性。
- [ ] `docs/SPEC.md` 的阶段状态、成功标准、边界和已解决决策与当前源码行为一致。
- [ ] `docs/DEVELOPMENT.md` 能让后续开发者或 agent 明确当前进度和下一步。
- [ ] `CHANGELOG.md` 包含待发布版本的用户可读变更摘要。
- [ ] `tasks/plan.md`、`tasks/todo.md` 和阶段专属任务清单状态一致。
- [ ] 阶段交付报告链接可访问，最终阶段报告与当前 pipeline 输出一致。

## Local Quality Gate

发布前运行以下命令：

```powershell
python -m ruff check .
python -m ruff format --check .
python -m mypy src
python -m pytest
powershell -ExecutionPolicy Bypass -File scripts/quality.ps1
pre-commit run --all-files
```

若本机默认 `python` 不是项目可用解释器，可使用当前开发环境验证过的 Python 版本，例如：

```powershell
py -3.13 -m ruff check .
py -3.13 -m ruff format --check .
py -3.13 -m mypy src
py -3.13 -m pytest
```

## CLI Smoke Gate

使用临时输出目录运行：

```powershell
python -m customer_service_hallucination_audit --help
python -m customer_service_hallucination_audit --version
python -m customer_service_hallucination_audit --output-dir <temp-output-dir>
python -m customer_service_hallucination_audit --detector mock --output-dir <temp-output-dir>
python -m customer_service_hallucination_audit --detector llm --output-dir <temp-output-dir>
```

期望结果：

- [ ] `--help` 展示 `--replies`、`--ground-truth`、`--detector`、`--output-dir` 和 `--version`。
- [ ] `--version` 与 package `__version__` 一致。
- [ ] 默认命令读取随包数据并生成 `report.md` 和 `report.json`。
- [ ] `--detector mock` 离线生成报告。
- [ ] 未配置 LLM 环境变量时，`--detector llm` 返回清晰错误并退出非零状态。

`llm` detector 如需真实调用，必须由用户显式配置以下进程环境变量：

- `CS_HALLUCINATION_AUDIT_LLM_API_KEY`
- `CS_HALLUCINATION_AUDIT_LLM_ENDPOINT`
- `CS_HALLUCINATION_AUDIT_LLM_MODEL`

项目当前不自动读取 `.env`，因此不要把密钥写入仓库文件。后续如需要 `.env.example` 或 `python-dotenv`，应作为单独变更讨论。

## Package And Data Gate

- [ ] `pyproject.toml` 仍使用 `customer_service_hallucination_audit.__version__` 作为版本来源。
- [ ] `src/customer_service_hallucination_audit/data/replies.json` 和 `ground_truth.json` 随包发布。
- [ ] 仓库根目录 `data/` 与随包数据内容保持一致，或已记录差异原因。
- [ ] `reports/`、`.env`、缓存、构建产物和本地索引目录未进入提交。

## PR And Merge Gate

- [ ] PR 描述使用 `.github/pull_request_template.md`。
- [ ] PR 中列出已运行和未运行的验证命令。
- [ ] 合并前确认 `git status --short` 干净。
- [ ] 合并后在 main 上执行 `git pull --ff-only`。

## Tagging Steps

阶段四最终 PR 合并到 main 后执行：

```powershell
git switch main
git pull --ff-only
git tag -a v1.0.0 -m "Release 1.0.0"
git push origin v1.0.0
git tag -n v1.0.0
```

如果发现标签打错且尚未发布制品，先删除本地和远端错误标签，再重新打标签：

```powershell
git tag -d v1.0.0
git push origin :refs/tags/v1.0.0
```

删除远端标签会影响协作者，只有在确认标签错误且需要重打时执行。
