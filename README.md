# LC-ops

## 条件扩散蒸馏：三任务 Codex 研究交接包

完整项目位于 [`projects/conditional-distillation/`](projects/conditional-distillation/)。

| 任务 | 条件与输出 |
|---|---|
| T1 身份保持视频生成 | 人物参考图＋动作文本 → 视频 |
| T2 Canny 边缘控制图像生成 | 边缘图＋文本 → 图像 |
| T3 人体姿态控制图像生成 | 人体骨架图＋文本 → 人物图像 |

包含 19 份 prompts、12 个专用 skills、3 个通用技能快照、实验协议、证据与预算模板，以及 ICML 目标的英文论文 v0。

### 从这里开始

1. 克隆整个仓库，或下载下方的完整 ZIP；不要只复制一个 SKILL.md。
2. 阅读 [使用指南](projects/conditional-distillation/README_先读这里.md)。
3. 将 [总启动 prompt](projects/conditional-distillation/prompts/00_START_HERE_CN.md) 的复制区内容发给 Codex，指明当前机器上 `projects/conditional-distillation` 的实际绝对路径。
4. 提供或复用已有主机/GPU、GPU 小时、墙钟、存储与费用限额。Codex 会实现缺少的训练/评价入口，按三任务独立 gate 和资源租约持续执行；缺资源时集中报告并继续独立工作。
5. 按 [执行与完成契约](projects/conditional-distillation/specs/execution_contract.md) 验收：待实验稿和任务派出不是项目完成，阴性提前关闭、缩水协议和外部阻断分别披露。

### 主要文件

- [三任务契约](projects/conditional-distillation/specs/three_task_protocol.md)
- [任务路线](projects/conditional-distillation/WORKFLOW.md)
- [开放方法搜索与选择](projects/conditional-distillation/specs/method_search_and_selection.md)
- [执行循环与完成标准](projects/conditional-distillation/specs/execution_contract.md)
- [本次修复与验证](projects/conditional-distillation/reports/autoresearch_execution_revision.md)
- [技能清单](projects/conditional-distillation/SKILL_CATALOG.md)
- [英文论文阅读版](projects/conditional-distillation/paper/draft.md)
- [LaTeX 源码](projects/conditional-distillation/paper/main.tex)
- [三任务版 ZIP](downloads/conditional_distillation_icml_handoff_20261026_three_tasks.zip)
- [ZIP SHA-256](downloads/conditional_distillation_icml_handoff_20261026_three_tasks.zip.sha256)

**状态：研究交接材料，无实验结果。** 未启动训练或图像/视频生成；英文论文是明确标注 PENDING 的预实验草稿，LaTeX 已通过编译。ICML 投稿年份尚未指定，2026 样式仅作参考。

2026-10-26 执行修订：同步修复主 prompt、角色契约、阴性分支、TOY/run 路径和方法级成本核算；下载 ZIP 与源码同步。辅助脚本测试和文档审查不代替真实 GPU 端到端验证。

研究问题固定，方法开放：原OPD/投影仅为初始候选。执行者将探索邻近路线，基于新颖性主源与开发集实测效果—成本自主选择，完成正式验证后汇总为ICML导向论文；候选取舍与负结果保留。
