# 贡献指南

本项目是一个小型评测工程，开发流程优先保证清晰、快速反馈和可复现。

## 本地初始化

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"
pre-commit install
```

如需恢复项目级 AI 辅助技能：

```bash
npx skills experimental_install
```

## 开发循环

1. 先阅读 `AGENTS.md` 和 `docs/SPEC.md`。
2. 选择一个小任务，明确验收标准。
3. 修改行为前先写或更新测试。
4. 运行本地质量门禁：

```bash
powershell -ExecutionPolicy Bypass -File scripts/quality.ps1
```

5. 使用中文提交信息提交一个原子变更。

## 提交规范

提交信息使用：

```text
<type>: <中文摘要>
```

`type` 保留英文，便于工具识别；摘要和正文使用中文。

常用类型：

- `feat`: 新增功能
- `fix`: 修复问题
- `test`: 增加或调整测试
- `docs`: 文档变更
- `refactor`: 不改变行为的重构
- `chore`: 工具、配置、仓库维护

示例：

```text
chore: 初始化幻觉检测项目脚手架
feat: 实现客服回复幻觉规则检测
test: 覆盖指标计算边界场景
```

## 精简原则

- 不为固定 JSON 评测引入 Web 框架或数据库。
- 不提交 `.agents/`、`.venv/`、缓存或构建产物。
- 新依赖必须有明确收益，并更新 `README.md` 或 ADR 说明原因。
- 优先小模块、小函数和可测试的纯逻辑。

## 审查清单

- 是否符合 `docs/SPEC.md`？
- 测试是否验证行为，而不是锁死实现细节？
- 工具是否仍可离线运行？
- 新增依赖是否必要？
- `scripts/quality.ps1` 是否本地通过？
