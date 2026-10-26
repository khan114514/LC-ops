# LC-ops

## 条件扩散蒸馏：三任务 Codex 研究交接包

完整项目位于 [`projects/conditional-distillation/`](projects/conditional-distillation/)。

| 任务 | 条件与输出 |
|---|---|
| T1 身份保持视频生成 | 人物参考图＋动作文本 → 视频 |
| T2 Canny 边缘控制图像生成 | 边缘图＋文本 → 图像 |
| T3 人体姿态控制图像生成 | 人体骨架图＋文本 → 人物图像 |

包含 18 份 prompts、12 个专用 skills、3 个通用技能快照、实验协议、证据与预算模板，以及 ICML 目标的英文论文 v0。

### 从这里开始

1. 克隆整个仓库，或下载下方的完整 ZIP；不要只复制一个 SKILL.md。
2. 阅读 [使用指南](projects/conditional-distillation/README_先读这里.md)。
3. 将 [总启动 prompt](projects/conditional-distillation/prompts/00_START_HERE_CN.md) 的复制区内容发给 Codex，指明当前机器上 `projects/conditional-distillation` 的实际绝对路径。
4. Codex 按三任务独立 gate、资源租约和已授权预算推进，持续保存实验证据与论文。

### 主要文件

- [三任务契约](projects/conditional-distillation/specs/three_task_protocol.md)
- [任务路线](projects/conditional-distillation/WORKFLOW.md)
- [技能清单](projects/conditional-distillation/SKILL_CATALOG.md)
- [英文论文阅读版](projects/conditional-distillation/paper/draft.md)
- [LaTeX 源码](projects/conditional-distillation/paper/main.tex)
- [三任务版 ZIP](downloads/conditional_distillation_icml_handoff_20261026_three_tasks.zip)
- [ZIP SHA-256](downloads/conditional_distillation_icml_handoff_20261026_three_tasks.zip.sha256)

**状态：研究交接材料，无实验结果。** 未启动训练或图像/视频生成；英文论文是明确标注 PENDING 的预实验草稿，LaTeX 已通过编译。ICML 投稿年份尚未指定，2026 样式仅作参考。
