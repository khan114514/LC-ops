# Paper status: DRAFT v0 — three-task research plan, no empirical results

本目录是可继续研究与写作的英文完整初稿，当前没有本项目的训练曲线、样本、统计检验、人工评价或性能数字。

- `main.tex`：当前编辑和预览的单文件英文主稿，article 排版，参考文献内嵌。必须在这个文件原地更新；不要新建替代 main 或切换到另一个编辑标签。
- `main_icml2026.tex`、`draft.md`：由主稿统一生成的两栏参考版与可读稿。主稿修改后需统一刷新，不能让派生版本成为另一个事实来源。2026 模板不代表符合未核验的下一届要求。
- `references.bib`：已取得的参考文献元数据；来源审计见 `../literature/`。新增引用必须核验，不能凭记忆补 BibTeX。
- `results_requirements.md`：任何结果占位转为完成时必须提供的证据。
- `icml2026_reference/`：完整复制且未经修改的 2026 模板及例稿。来源为已安装 ml-paper-writing 技能；正式投稿必须重新核验目标年份官网。

## 必须保留的三个研究任务

候选题目：**Condition-Preserving Distillation from a Teacher without the Student's Additional Condition**。

统一问题是冻结老师不接收学生新增条件时，老师监督是否存在可利用但破坏条件的方向，以及局部条件约束能否在公平对照下改善独立部署学生。候选贡献不是“第一次合成配对数据/混合轨迹/投影”；HPSD 的 teacher-anchor + student-rollout 等已有方法必须直接讨论。

| 任务 | 老师 → 学生 | 从老师样本提取条件 | 独立条件评价 |
|---|---|---|---|
| T1 身份保持视频 | Wan2.1-T2V-1.3B → Concat-ID-Wan-AdaLN | 目标时间窗之外的人脸参考 | 独立身份识别、完整失败分母，配质量/动作指标 |
| T2 Canny 边缘条件图像 | SD1.5 文本老师 → 对应 ControlNet 1.1 Canny | 锁定 Canny 管线 | 独立 hard-edge F1、对称 Chamfer，配质量/文本指标 |
| T3 人体姿态条件图像 | 同一 SD1.5 文本老师 → 对应 ControlNet 1.1 OpenPose | 离线关键点估计 + 锁定 renderer | 与训练代理不同模型/权重的姿态评估，PCK/OKS 与完整失败分母 |

三个任务必须同时出现在启动 prompt、研究范围与最终结果块；每项都有独立兼容性/梯度/teacher-value gate、预算、开发选择与实验状态。可以得到负结果或因实证 gate 阻塞，但必须记录已尝试证据及原因，不能无声删去任务。三个任务均未执行，A/B/C 假设均 PENDING。T2/T3 共用 SD1.5 底座，不是两个独立架构；第二视频架构是 T1 的可选扩展，不是第四个主任务，也不能替代 T2/T3。

统一 `c=h(x_teacher)`。T1 按身份 cluster 和近重复拆分；T2 按原图/近重复 cluster 拆分；T3 按源图、人物、近姿态组拆分并隔离近重复骨架模板。T2 训练用可微软边代理，评价用独立硬边规则。T3 训练必须冻结可微 PyTorch 网络并保留输入梯度，可用热图/soft-argmax；不能由 NumPy、ONNX 或硬 argmax 截断梯度。数据生成前锁定 COCO17/OpenPose18、左右、neck、可见性与坐标转换；不得平移躯干或强制后处理使条件通过。

建议预算：每任务 S0 加 8 个训练对照、每对照 3 个独立训练 seed，主测共 25 checkpoints。T1 主测 40,000 视频。T2/T3 各建议 8,192 有效老师图、512 开发单位、500 外部条件图；`500×2文本×2推理seed=2,000图/checkpoint`，每任务主测 50,000 图，图像合计 100,000。以上仅为协议算术，开发、干预、额外 operating points、compute-matched checks 与第二视频架构另计，不能写成已完成数量或 GPU 时间承诺。

每个任务分别报告所有训练 seed、均值与标准差，推理 seed 与老师采样 seed 单独记录。不把身份、边缘和姿态分数跨任务平均成通用总分。主图表必须保留 T1/T2/T3 分块、负结果与失败率。详细协议另见 `../specs/three_task_protocol.md`、`../specs/prediction_and_target_contract.md` 和 `results_requirements.md`。

## 编译与结果写入

单文件主稿可以用 Codex 内建 LaTeX 编译器编译，并在当前已打开的 `main.tex` 原地预览。本次三任务扩展修改后，必须重新取得 built-in compile 的成功诊断；历史编译记录不能充当本版验证。不要为预览另建 PDF、替代 main 或切换编辑标签。

两栏参考版使用完整 `icml2026_reference/` 样式目录，正式使用前先验证原版例稿；不要修改 sty/bst 压缩页数。当前主稿重在完整协议，未按 8 页主文预算裁剪，也未完成目标年份版式/匿名/AI 披露检查。

写入任何实测时必须先满足 `results_requirements.md`，再将对应 planned 改为完成时态，并按每个任务的证据缩小结论。初稿中的 `[CITATION NEEDED]` 是最近邻综述未完成标记，不是杜撰论文。编译成功仅说明 TeX 可编译，不证明研究完成、创新性或投稿准备就绪。


The current three-task main.tex passed the built-in compiler again. Its current SHA and result are in ../reports/latex_compile_check.md. The existing source was edited in place; no replacement document or separate PDF was created.

当前论文只描述初始候选家族，尚未选定最终方法。方法开放要求与改写范围见 [DRAFT_STATUS.md](DRAFT_STATUS.md)；最终按开发选择结果重写，不能因为已有这份初稿而锁死OPD。
