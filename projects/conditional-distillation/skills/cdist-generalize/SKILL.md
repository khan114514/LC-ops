---
name: cdist-generalize
description: Coordinate the three formal CDist condition tasks and optional video architecture replication, preserving task-specific evidence, gates, and budgets.
---

# CDist 三任务与适用范围

先定位活跃项目根，读取当前 state/assignment、[共享 worker 契约](../../prompts/01_SHARED_WORKER_CONTRACT.md)、[三任务协议](../../specs/three_task_protocol.md)、[研究定义](../../specs/research_spec.md)、[预测及目标契约](../../specs/prediction_and_target_contract.md) 与 [评价协议](../../specs/evaluation_protocol.md)。当前项目冻结协议优先于安装快照；本技能不授权新增训练或算力。

## 正式任务与推进边界

研究有且仅有三个正式条件任务，必须各自登记数据、run、资源、gate、A/B/C 主张和正负结果：

| task_id | 正式任务 | 候选平台 | 执行 prompt |
|---|---|---|---|
| T1 | 外部参考身份控制视频 | Wan2.1-T2V-1.3B → Concat-ID-Wan-AdaLN | 主启动与既有视频角色 prompt |
| T2 | Canny 边缘控制图像 | 匹配的 SD1.5 → ControlNet 1.1 Canny | [T2 任务](../../prompts/16_T2_CANNY_TASK.md) |
| T3 | 单人人体姿态控制图像 | 同一 SD1.5 → ControlNet 1.1 OpenPose | [T3 任务](../../prompts/17_T3_POSE_TASK.md) |

T2/T3 是正式任务，不是等 T1 成功后才决定是否执行的可选泛化。每任务独立通过兼容/成本、局部干预与 smoke、开发归因、冻结正式评价门槛；准备可并行，GPU 作业按总控租约排队。某任务失败只阻断依赖它的工作，不自动取消其他任务。无 GPU 或预算时只完成协议、兼容性检查清单、代码准备与资源申请，实验保持未执行。

每个实际 run 必含 `task_id=T1|T2|T3`，写入 `runs/<task_id>/<run_id>/`；worker 报告写 `reports/<assignment_id>/`。数据版本与 manifest 按任务独立；复用源图仍保留全局 source/duplicate 分组，不算新增独立样本。任务资源和 claim 由 worker 报告、总控合并，worker 不写共享状态。共享 adapter/训练代码由总控指定 single owner，不能多人并发改同一文件。历史路径若已存在只登记，不搬移或重启已有作业。

## 三任务共同证据

每任务均是冻结文本老师 `T(z,t,b)` 缺少新增条件 `c`，现有条件学生 `S(z,t,b,c)` 从 S0 起点独立纯噪声生成。老师完整输出后离线提取条件；同状态参数化转换、固定最终 query time、rollout/target stop-gradient、生成 mask、固定 batch 分母、近零梯度实际回溯和无效样本拒绝均按预测契约执行。

正式对照每任务保留 S0 加 P/H0/H1/H2/O0/O1/C-H/C-O，八训练方法各 3 个独立 train seed；C-H/C-O 仅去掉 KD，保留对应在线公共条件损失，不能省去后宣称排除了该解释。弱 KD、随机门控、仅条件方向、radius-only 和半径匹配门控按冻结归因矩阵保留。可训练模块、数据、开发搜索与推理设置在任务内公平；update-matched 与实际 compute-matched 分开报告。预算未到位时保留计划与缺项，不静默删方法或 seed。

T2/T3 各建议 8,192 张有效 teacher 训练图、512 张开发图、500 个外部测试条件。每条件 2 个兼容文本 × 2 个推理 seed = 2,000 图/检查点；8 方法 × 3 train seed + S0 = 25 检查点，各 50,000 主测图像，两图像任务合计 100,000。数字是范围建议，不是预算授权；老师数据、开发、消融、重试与不同 update/compute 检查点另计。

T2 由 teacher 图离线提 Canny；训练用可微 soft-edge，独立评价用冻结 hard-Canny precision/recall/F1 与双向距离/Chamfer，另报质量、文本和失败。soft-edge 不等价于 Canny，需检验代理与硬指标的一致性，不能用硬 Canny 后处理回传。

T3 由 teacher 单人全身图离线提数值 keypoints 与 rendered skeleton。训练使用冻结可微 PyTorch 姿态网络的原始 heatmap forward，可配 soft-argmax；不能假装默认 OpenPose 整条检测/NumPy/硬 argmax 流水线可微。独立 detector 使用不同于训练代理的权重评价 PCK、OKS，ViTPose 等仅为待核验候选；输入可见关节和固定 canvas/bbox 决定分母。按关节名固定 COCO17/OpenPose18 映射、neck 与左右，不能与 BODY25 索引混用。检测/关节失败保留全分母；禁止输出后 Procrustes 对齐、换目标姿态或只保留检测成功样本。

## 可选视频架构复核

CogVideoX-5B / ConsisID 仅是 T1 的可选第二架构，不是第四主任务。须核验实际 checkpoint、许可、VAE、scheduler、参考路径与预测参数化，独立 W0 测成本，由该 teacher 生成自身训练对（起点建议 2,048 有效视频）。复用第一平台数据只支持跨平台数据迁移主张。T2/T3 共用 SD1.5/ControlNet，不能把两个条件权重称作两个架构。

## 完成与论文范围

输出任务适配/数据/成本版本、冻结配置、完整成功/失败证据、独立统计和 `reports/<assignment_id>/scope_report.md`。done 表示分配的任务 gate 通过，不表示三任务均已执行或主张成立。A/B/C 逐任务判定，异质条件指标不直接平均成总分。三种条件的结果只界定已测范围，不能保证所有条件适用；部分有效时收窄论文措辞，保留阴性与未执行状态。


预算调整口径：完整正式协议为八方法各三训练seed；预算不足可在测试暴露前由总控显式冻结缩小协议并保留限制说明，不能静默省略方法/seed或声称完成原全量配置。B/C必须有本task_id的对应归因消融，不可借用其他任务结果升格。
