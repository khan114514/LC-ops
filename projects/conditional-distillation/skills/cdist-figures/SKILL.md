---
name: cdist-figures
description: Build the CDist study's paper figures and tables from traceable experiment artifacts, including null results and uncertainty.
---

# CDist 证据图表

方法范围：先读 [方法搜索与选择](../../specs/method_search_and_selection.md) 和当前候选/选定协议。本文涉及的OPD、H/O/C、投影/局部轨迹是初始家族要求，不是所有候选必用算法；其它路线按其冻结定义与控制执行，共同证据边界不变。

用于本项目图表制作；不用于生成实验结果。先定位含 project.yaml 的研究根目录，读 [图表计划](../../specs/figures_and_tables.md)、[评价协议](../../specs/evaluation_protocol.md)、state/claim_evidence.json 与分配的 run 清单。

图表只能读取已有真实逐样本数据；没有数据时输出绘图代码、字段需求和明确 PENDING 的版式占位，不能画示意性能曲线当实测。机制示意图可以现在绘制，但须标 schematic，无性能数字。

先复算每张图的输入数量、方法、训练 seed、域、checkpoint 和失败分母。配对比较检查 identity/prompt/inference seed 是否正确 join；不要跨训练 seed 随意复用配对关系。区间的重采样层级遵循锁定评价协议。训练 seed 的差异与身份样本不确定性分开标注。不能把视频帧当独立样本。

为每张图保存 figure_manifest.json：figure_id、claim_id、run_ids、输入文件 SHA、生成脚本/code SHA、筛选规则、样本数量、统计定义、输出路径。六主图、八补图、三主表依实际证据合并，不能为凑图数编内容。定性案例按开发阶段固定规则选择，保留随机样本和失败/不占优案例索引。

科学绘图用 Matplotlib 等标准工具，输出可分享的 PDF/SVG 和必要 PNG。避免使用 ImageGen 绘制数据图或修改人物生成结果；方法示意图应清晰标冻结/stopgrad/条件与训练/部署。使用色盲友好配色、灰度与双栏字号检查，caption 说明估计量和误差条。

Done：绘图脚本能从锁定输入复算，主表数值与原始日志一致，清单覆盖引用、图注自包含、未完成图显式列出。只接收自己负责的 figures/tables 目录，不改原始 run 日志。


三任务范围：读取 [任务契约](../../specs/three_task_protocol.md)，按assignment.task_id选择T1身份视频、T2 Canny图像、T3人体姿态图像的独立数据、代理、指标、gate与预算；新run使用runs/<task_id>/<run_id>/。本技能原有视频/身份细节仅用于T1，不能强加给T2/T3。三者都是正式研究范围；负结果需保留，未执行不能声称三任务实验完成，可选第二视频架构不是第4个主任务。
