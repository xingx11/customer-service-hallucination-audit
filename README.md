# Customer Service Hallucination Audit

面向客服自动回复场景的幻觉检测评测项目。项目会读取 20 条客服回复、对应知识库和人工标注，自动判断回复是否存在幻觉，输出检测结果、检出率指标和误判分析。

当前状态：第一阶段离线评测流水线已经完成并打 `v0.1.0` 标签；第二阶段鲁棒性与可解释性增强已完成并打 `v0.2.0` 标签；第三阶段 Adapter + 最小 LLM 接入闭环已完成并打 `v0.3.0` 标签，支持 `deterministic`、`mock` 与显式 opt-in 的 `llm` detector 路径。项目当前进入第四阶段最终交付收尾，目标是完成 `v1.0.0` 发布准备；默认命令可读取随包数据并生成 Markdown/JSON 报告，阶段一、阶段二和阶段三交付报告均已提交在 `docs/reports/` 下，并随当前流水线格式保持一致。

## 为什么选择这个题

0110 任务的数据闭环更完整：每条样本都包含用户问题、系统回复、知识库依据和人工真值。它适合展示可复现的数据处理、规则设计、指标计算、测试覆盖和 CI 质量门禁。

## 技术栈

- 语言：Python 3.11+
- 应用形态：命令行工具，不使用 Web 框架
- 核心实现：标准库 `argparse`、`dataclasses`、`json`
- 测试：pytest
- 代码质量：ruff、mypy
- 自动化：GitHub Actions

这个项目优先采用确定性规则引擎，同时提供可选 LLM 适配器边界。默认实现不依赖外部 API，保证评测可离线复现。

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
│   ├── reports/
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

- `report.md`：面向人工审阅的总体指标、类型表现、逐条分类结果、规则命中摘要和错误分析。
- `report.json`：面向自动化消费的结构化检测结果、总体指标、类型指标、规则命中摘要、高风险筛选依据和误判分组。

默认 detector 为 `deterministic`，即现有离线规则检测器。也可以显式运行离线 mock adapter 验证 adapter 注入和报告链路：

```bash
python -m customer_service_hallucination_audit --detector mock --output-dir reports
```

`llm` detector 是显式 opt-in 路径，仅在用户选择时读取环境变量并调用 OpenAI-compatible chat completions endpoint。默认路径、测试和质量门禁不会依赖真实 LLM：

```powershell
$env:CS_HALLUCINATION_AUDIT_LLM_API_KEY = "<api-key>"
$env:CS_HALLUCINATION_AUDIT_LLM_ENDPOINT = "https://example.com/v1/chat/completions"
$env:CS_HALLUCINATION_AUDIT_LLM_MODEL = "<model-name>"
python -m customer_service_hallucination_audit --detector llm --output-dir reports
```

缺少任一环境变量时，`llm` 路径会返回清晰错误并停止，不会静默降级为确定性结果。项目当前不自动读取 `.env` 文件，因此暂不提供 `.env.example`；如需使用 `llm` detector，请通过 shell、CI secret 或调用方进程环境显式设置上述变量。

也可以显式指定输入文件：

```bash
python -m customer_service_hallucination_audit ^
  --detector deterministic ^
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

## 分类体系与检测方法

当前规则检测器覆盖 8 类客服回复幻觉：

- `政策编造`：把不存在或更宽松的售后、发票等政策说成确定承诺。
- `政策偏差`：回复与知识库政策方向一致但关键条件、入口或时效不一致。
- `参数编造`：编造或抬高商品参数、材质、接口、保修等事实。
- `优惠编造`：承诺知识库明确不存在的优惠券、折扣或认证权益。
- `信息编造`：编造退货地址、门店、品牌关系等知识库未提供的信息。
- `能力越界`：声称已查询物流、退款、订单修改或工单升级等系统不具备的能力。
- `安全误导`：在孕妇、哺乳期等安全敏感场景给出与知识库相反的建议。
- `信息遗漏`：遗漏知识库中的关键限制或用户反馈，导致回复结论误导。

检测方法是离线确定性规则：每条规则只读取用户问题、系统回复和知识库文本，通过关键词组合判断是否触发，并输出规则 ID、幻觉类型和中文原因。规则元数据包含稳定 ID、风险等级、中文说明和触发意图，用于报告中的规则命中摘要。第二阶段补充了鲁棒性 fixture 和检测器边界测试，用于覆盖同义改写、困难负例、信息遗漏和安全敏感场景。人工真值只用于评估 precision、recall、F1、按类型聚合指标和错误分析，不参与预测。

## 当前评测输出

- 幻觉检出：是否识别出回复与知识库矛盾、无依据承诺或能力越界。
- 类型分类：政策编造、政策偏差、参数编造、能力越界、优惠编造、信息编造、安全误导、信息遗漏等。
- 类型表现：按幻觉类型统计标注数、预测数、命中数和错配数。
- 规则解释：按规则统计命中次数、样本 ID、风险等级、触发意图和中文说明。
- 检测质量：precision、recall、F1、false positive、false negative。
- 案例分析：列出漏检、误报、类型错误和高风险案例，并说明高风险筛选与排序依据。

在当前默认 20 条样本上，确定性规则检测器的二分类指标为：

```text
total=20, precision=1.000, recall=1.000, f1=1.000
```

阶段一交付报告：

- [Markdown 检测报告](docs/reports/stage-1-report.md)
- [JSON 结构化报告](docs/reports/stage-1-report.json)

阶段二交付报告：

- [Markdown 检测报告](docs/reports/stage-2-report.md)
- [JSON 结构化报告](docs/reports/stage-2-report.json)

阶段三交付报告：

- [Markdown 检测报告](docs/reports/stage-3-report.md)
- [JSON 结构化报告](docs/reports/stage-3-report.json)

阶段二规划：

- [阶段二实施计划](tasks/stage-2-plan.md)
- [阶段二任务清单](tasks/stage-2-todo.md)

阶段三规划：

- [阶段三实施计划](tasks/stage-3-plan.md)
- [阶段三任务清单](tasks/stage-3-todo.md)

阶段四发布准备：

- [阶段四实施计划](tasks/stage-4-plan.md)
- [阶段四任务清单](tasks/stage-4-todo.md)
- [发布检查清单](docs/RELEASE_CHECKLIST.md)

## 开发路线

```text
v0.1.0  阶段一：离线评测 MVP，已完成
v0.2.0  阶段二：鲁棒性与可解释性，已完成
v0.3.0  阶段三：Adapter + 最小 LLM 接入，已完成
v1.0.0  阶段四：最终交付收尾，进行中
```

## 第四阶段方向

第四阶段不再推进功能扩展，而是完成正式交付前的发布准备：

- 最终复核 README、SPEC、CHANGELOG、开发文档和交付报告链接。
- 使用 `docs/RELEASE_CHECKLIST.md` 固化质量门禁、CLI smoke test、安装验证和打标签步骤。
- 保持默认 deterministic 路径离线可复现，mock/LLM 路径只作为显式选择。
- 不新增 `.env` 自动加载、provider SDK 或运行时依赖。
- 在最后收尾任务中更新 `1.0.0` 版本、生成阶段四交付报告，并在合并 main 后打 `v1.0.0` 标签。

真实 LLM API 不进入默认路径，必须显式选择并通过环境变量配置；默认质量门禁仍然离线运行。

## 局限性

- 当前规则针对 0110 数据集设计，能够保证离线可复现，但无法覆盖所有客服表达变体。
- 第二阶段鲁棒性 fixture 提升了边界覆盖，但默认交付指标仍基于 20 条固定样本，不代表真实线上分布。
- 规则依赖文本关键词和知识库片段，对复杂多轮上下文、隐含事实和规则外风险的泛化能力有限。
- 高风险案例筛选偏保守，后续可结合业务风险等级继续细化。

## 交付物

- README：分类体系、检测方法、检出率、AI 工具使用情况。
- 运行结果：检测报告、指标汇总、错误案例分析。
- 代码仓库：包含数据、源码、测试、CI 和项目说明。

## AI 工具使用说明

项目使用 Codex 辅助进行需求澄清、架构设计、测试设计、代码实现、文档整理和审查。默认检测逻辑不调用真实 LLM API，所有核心逻辑通过单元测试、集成测试、pre-commit、ruff、mypy 和 pytest 质量门禁验证，避免只依赖模型主观判断。
