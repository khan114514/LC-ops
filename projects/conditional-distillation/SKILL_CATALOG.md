# 技能用途与装载顺序

不必一次装载全部技能。总控先读取编排技能；每个 worker 仅加载对应技能、共享契约和所需规范。包内 `skills/` 是本研究专用；`vendor/skills/` 是可选通用技能快照。

## 包内十二个专用技能

| 技能 | 使用阶段 | 直接读取 |
|---|---|---|
| `cdist-orchestrate` | 总控、派工、资源队列、证据与续跑 | [SKILL.md](skills/cdist-orchestrate/SKILL.md) |
| `cdist-literature` | 最近邻、引文核验、目标ICML规则 | [SKILL.md](skills/cdist-literature/SKILL.md) |
| `cdist-engineer` | 模型与 scheduler 对齐、可微条件通路 | [SKILL.md](skills/cdist-engineer/SKILL.md) |
| `cdist-method` | 混合轨迹与受约束目标的实现 | [SKILL.md](skills/cdist-method/SKILL.md) |
| `cdist-mechanism` | CPU toy、视频局部干预、机制否证 | [SKILL.md](skills/cdist-mechanism/SKILL.md) |
| `cdist-data` | 老师数据、过滤、参考构建和划分 | [SKILL.md](skills/cdist-data/SKILL.md) |
| `cdist-train` | 阶段训练、匹配对照、成本与恢复 | [SKILL.md](skills/cdist-train/SKILL.md) |
| `cdist-evaluate` | 独立生成、指标、失败、统计与人工评价 | [SKILL.md](skills/cdist-evaluate/SKILL.md) |
| `cdist-generalize` | T2 Canny、T3人体姿态与可选T1第二架构 | [SKILL.md](skills/cdist-generalize/SKILL.md) |
| `cdist-figures` | 六主图、八补图、三主表和数据追溯 | [SKILL.md](skills/cdist-figures/SKILL.md) |
| `cdist-paper` | 真实证据驱动的英文论文和会议格式 | [SKILL.md](skills/cdist-paper/SKILL.md) |
| `cdist-review` | 独立复核、复算、主张收缩与返修 | [SKILL.md](skills/cdist-review/SKILL.md) |

## 随包附带的通用技能

| 技能 | 适用场景 | 注意 |
|---|---|---|
| [ml-paper-writing](vendor/skills/ml-paper-writing/SKILL.md) | 写作、引文验证、会议模板与图表 | 原版快照，部分历史规则需更新；优先本项目真实证据和目标年份官网 |
| [brainstorming-research-ideas](vendor/skills/brainstorming-research-ideas/SKILL.md) | 局部老师方向没有收益或假设被否定时重构可检验问题 | 不得为了正结果看测试调方向 |
| [creative-thinking-for-research](vendor/skills/creative-thinking-for-research/SKILL.md) | 两轮有信息实验仍不能区分机制时设计更有区分力的测试 | 不代替必要的归因对照 |

通用技能按需直接读取；安装器默认只装项目专用技能，避免改写接收者已有同名通用技能。原来源与许可证在 `vendor/manifest.json` 及各技能的 UPSTREAM 文件中。

## 接收环境按需使用的技能

下列能力有明确用途，但不是启动本项目的硬依赖。本包不假装这些插件或工具在接收者机器上存在，也不复制其整个依赖运行时。

| 技能/能力 | 何时使用 | 缺少时怎么做 |
|---|---|---|
| `autoresearch`（普通研究分支） | 内外实验循环、状态综合、否定结果与方向调整 | 使用本包 `cdist-orchestrate`；勿套用 Harbor 管理技能 |
| `systematic-debugging` | NaN、梯度断链、平台不兼容、恢复后指标变化 | 先复现最小失败、定位根因，再修复；保留原失败日志 |
| `jupyter-notebook` | 临时机制探索与可复查分析笔记 | 用脚本保留等价分析；正式数字由可复算脚本产生 |
| `pdf:pdf` | 论文/补充材料 PDF 渲染和视觉检查 | 用宿主 LaTeX 预览或已有编译器；如无法导出应明确说出 |
| `documents:documents` | 项目方需要 Word 研究计划或修订文档 | 英文论文仍以 TeX 为主，Markdown 可作阅读版 |
| `presentations:Presentations` | 阶段研究汇报、组会或最终报告 | 图表加简洁 Markdown 报告即可 |
| `spreadsheets:Spreadsheets` | 审阅原始 CSV、人工评价组织和预算表 | CSV/JSON 与脚本足够，不能手改正式统计结果 |
| `skill-creator` | 执行中发现流程缺口并维护专用 skill | 窄范围修订、独立行为验证，避免堆成泛化审批规则 |
| `openai-docs` | Codex 工具/技能/模型/运行行为需要核验时 | 读运行时 schema；仍需解释时查官方文档 |
| 已授权 SSH / Slurm / torchrun | 对方提供的真实远端算力与分布式训练 | 本地独立工作继续；不能自动采购算力或寻找私钥 |

不需要为本研究装前端、Figma、宠物、专家题 QA 等无关技能；科学数据图不使用图像生成模型伪造。


三任务入口：总启动prompt已内含T1/T2/T3的定义、数据与评价；[T2专用prompt](prompts/16_T2_CANNY_TASK.md)、[T3专用prompt](prompts/17_T3_POSE_TASK.md)用于分派对应执行者。共19份prompts，仍为12个专用skills。

新增角色入口：[18 方法探索与选择](prompts/18_METHOD_SEARCH_AND_SELECTION.md)。总控协调文献、工程、方法与评价技能，按 [方法搜索规范](specs/method_search_and_selection.md) 完成候选比较、选择与ICML汇总；不是新增第十三个技能。
