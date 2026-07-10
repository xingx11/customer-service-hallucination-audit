# Quality And CLI Smoke Results

本文件记录阶段四 Task 26 的最终质量门禁与安装/CLI smoke test 结果。目标是在 `v1.0.0` 发布收尾前确认默认离线路径、mock adapter 路径、LLM 缺配置错误路径和本地质量门禁均可复现。

## Review Date

2026-07-10

## Environment

- Platform: Windows / PowerShell
- Python: `py -3.13`
- Package version under test: `0.3.0`
- Branch scope: 阶段四发布前验证记录，不修改运行时代码、不新增依赖、不生成提交内报告产物。

## Install Smoke

```powershell
py -3.13 -m pip install -e ".[dev]"
```

Result: passed.

Notes:

- Editable install succeeded.
- Existing development dependencies were already satisfied.
- Installed package reported as `customer-service-hallucination-audit==0.3.0`.

## Quality Gate

```powershell
powershell -ExecutionPolicy Bypass -File scripts\quality.ps1
```

Result: passed.

Observed checks:

- `ruff check .`: passed.
- `ruff format --check .`: passed.
- `mypy src`: passed.
- `pytest`: 108 passed.

```powershell
pre-commit run --all-files
```

Result: passed.

Observed hooks:

- `ruff check`: passed.
- `ruff format`: passed.
- `check for added large files`: passed.
- `check json`: passed.
- `check toml`: passed.
- `check yaml`: passed.
- `fix end of files`: passed.
- `trim trailing whitespace`: passed.

## CLI Smoke

### Help

```powershell
py -3.13 -m customer_service_hallucination_audit --help
```

Result: passed.

Verified options:

- `--version`
- `--replies`
- `--ground-truth`
- `--detector`
- `--output-dir`

### Version

```powershell
py -3.13 -m customer_service_hallucination_audit --version
```

Result: passed.

Observed output:

```text
cs-hallucination-audit 0.3.0
```

The `1.0.0` version bump remains intentionally deferred to Task 27.

### Default Packaged Data And Deterministic Detector

```powershell
py -3.13 -m customer_service_hallucination_audit --output-dir <temp-output-dir>
```

Result: passed.

Observed behavior:

- Wrote `report.md`.
- Wrote `report.json`.
- Reported `total=20, precision=1.000, recall=1.000, f1=1.000`.
- Temporary output directory was removed after inspection.

### Mock Detector

```powershell
py -3.13 -m customer_service_hallucination_audit --detector mock --output-dir <temp-output-dir>
```

Result: passed.

Observed behavior:

- Wrote `report.md`.
- Wrote `report.json`.
- Reported `total=20, precision=1.000, recall=0.556, f1=0.714`.
- Temporary output directory was removed after inspection.

### LLM Detector Without Environment

```powershell
py -3.13 -m customer_service_hallucination_audit --detector llm --output-dir <temp-output-dir>
```

Result: passed as expected failure.

Observed behavior:

- Exit code was non-zero.
- Error listed the missing environment variables:
  - `CS_HALLUCINATION_AUDIT_LLM_API_KEY`
  - `CS_HALLUCINATION_AUDIT_LLM_ENDPOINT`
  - `CS_HALLUCINATION_AUDIT_LLM_MODEL`
- Error explicitly points users back to `--detector deterministic` for the reproducible offline path.
- No fake LLM result was produced.

## Outcome

Task 26 is complete. The next stage-four task is Task 27: update version metadata to `1.0.0`, generate the final stage-four delivery report, update release documentation, and prepare the merge/tag sequence.
