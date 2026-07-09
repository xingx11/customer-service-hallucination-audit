# Customer Service Hallucination Audit

面向客服自动回复场景的幻觉检测评测项目。项目会读取 20 条客服回复、对应知识库和人工标注，自动判断回复是否存在幻觉，输出检测结果、检出率指标和误判分析。

## 为什么选择这个题

0110 任务的数据闭环更完整：每条样本都包含用户问题、系统回复、知识库依据和人工真值。它适合展示可复现的数据处理、规则设计、指标计算、测试覆盖和 CI 质量门禁。

## 技术栈

- 语言：Python 3.11+
- 应用形态：命令行工具，不使用 Web 框架
- 核心实现：标准库 `argparse`、`dataclasses`、`json`
- 测试：pytest
- 代码质量：ruff、mypy
- 自动化：GitHub Actions

这个项目优先采用确定性规则引擎，后续可扩展 LLM 适配器。默认实现不依赖外部 API，保证评测可离线复现。

## 精简原则

- 不引入 Web 框架、数据库或后台服务，除非任务证明确实需要。
- 不提交本地 Agent 技能副本、虚拟环境、缓存或构建产物。
- `skills-lock.json` 记录 AI 辅助开发技能来源；本地 `.agents/` 目录只作为开发环境使用。
- 新增依赖必须能减少真实复杂度，不能只为了“看起来高级”。

## 项目结构

```text
.
├── data/
│   ├── replies.json
│   └── ground_truth.json
├── docs/
│   ├── SPEC.md
│   └── decisions/
├── src/
│   └── customer_service_hallucination_audit/
├── tests/
├── AGENTS.md
├── README.md
└── pyproject.toml
```

## 快速开始

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"
pre-commit install
python -m customer_service_hallucination_audit --help
python -m customer_service_hallucination_audit --output-dir reports
```

默认命令会读取随包发布的任务数据（内容与仓库 `data/replies.json` 和
`data/ground_truth.json` 保持一致），并在输出目录写入：

- `report.md`：面向人工审阅的指标汇总、逐条分类结果和错误分析。
- `report.json`：面向自动化消费的结构化检测结果、指标和误判分组。

也可以显式指定输入文件：

```bash
python -m customer_service_hallucination_audit ^
  --replies data/replies.json ^
  --ground-truth data/ground_truth.json ^
  --output-dir reports
```

如需恢复项目级 AI 辅助技能，可运行：

```bash
npx skills experimental_install
```

## 质量命令

```bash
pre-commit run --all-files
powershell -ExecutionPolicy Bypass -File scripts/quality.ps1
python -m ruff check .
python -m ruff format --check .
python -m mypy src
python -m pytest
```

## Git 提交规范

提交信息使用中文描述，保留英文类型前缀：

```text
chore: 初始化幻觉检测项目脚手架
feat: 实现客服回复幻觉规则检测
test: 覆盖指标计算边界场景
```

本地已提供 `.gitmessage` 作为提交模板。

## 当前评测输出

- 幻觉检出：是否识别出回复与知识库矛盾、无依据承诺或能力越界。
- 类型分类：政策编造、参数编造、能力越界、优惠编造、信息编造、安全误导、信息遗漏等。
- 检测质量：precision、recall、F1、false positive、false negative。
- 案例分析：列出漏检、误报和高风险案例，解释规则边界。

在当前默认 20 条样本上，确定性规则检测器的二分类指标为：

```text
total=20, precision=1.000, recall=1.000, f1=1.000
```

## 交付物

- README：分类体系、检测方法、检出率、AI 工具使用情况。
- 运行结果：检测报告、指标汇总、错误案例分析。
- 代码仓库：包含数据、源码、测试、CI 和项目说明。

## AI 工具使用说明

项目使用 Codex 辅助进行需求澄清、架构设计、测试设计、代码实现和审查。所有核心逻辑会通过测试和 CI 质量门禁验证，避免只依赖模型主观判断。
