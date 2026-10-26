# 三任务协调与可选架构复核 worker prompt

方法路由：先读 [方法搜索与选择](../specs/method_search_and_selection.md) 及当前候选/选定协议。本文OPD、投影、H/O/C和局部轨迹细节是初始家族的执行要求；其它候选按自己的已冻结定义/控制执行，共同的数据、测试、公平性与证据边界仍适用。不要用初始家族不成立否定全部邻近路线。

你负责 T1/T2/T3 适用范围和任务间证据协调。先读 `project.yaml`、`prompts/01_SHARED_WORKER_CONTRACT.md`、当前 state/assignment、`specs/three_task_protocol.md`、`specs/research_spec.md`、实验矩阵、预测/数据/评价契约及各任务 gate 报告。任务细节分别读 `prompts/16_T2_CANNY_TASK.md` 与 `prompts/17_T3_POSE_TASK.md`；T1 沿用身份视频协议。

三个正式任务为：T1 参考身份视频（Wan/Concat-ID 候选）；T2 Canny 边缘图像（匹配 SD1.5 + ControlNet 1.1 Canny）；T3 单人人体姿态图像（同一 SD1.5 + ControlNet 1.1 OpenPose）。T2/T3 不再是可选第二任务，也不以 T1 主实验成功为准备或推进的共同前提。各任务独立走 W0 兼容/成本、W1 局部机制与小训练、W2–W3 开发归因、W4 冻结正式评价。GPU 排队服从总控资源和租约；无 GPU 或预算时仅准备，不执行训练/正式生成。某任务负结果不取消其余任务。

每任务独立 data_version/manifest、资源实测与预算、gate、run 和 A/B/C claim。每 run 必含 `task_id=T1|T2|T3`，目录 `runs/<task_id>/<run_id>/`；报告目录 `reports/<assignment_id>/`。同源图跨 T2/T3 重用须保持全局 source/duplicate 分组，不能变成额外独立数据。共享代码写入只由总控指定 single owner，worker 不改共享 state；已有历史路径登记后保留，不搬移、覆盖或重复启动。

每个正式任务保留 S0 + P/H0/H1/H2/O0/O1/C-H/C-O，八训练方法各三个独立 train seed。C-H/C-O 保留对应在线状态和公共条件损失，仅置 KD 为零，不能为了跨任务节省预算而省略。弱 KD、随机门控、仅条件方向、radius-only、半径匹配门控与路径消融按冻结矩阵执行。比较最终 query time、同参数化/生成区域、训练模块、数据、调参与推理；分别报告相同 updates 与实际 compute。预算缺口保留为未执行范围，不静默删方法或 seed。

T2/T3 各建议 8,192 有效 teacher 训练图、512 开发图、500 外部测试条件。每个条件 × 2 兼容文本 × 2 推理 seed = 2,000 图/检查点；八方法三 train seed + S0 共 25 检查点，即各 50,000 主测图像、两任务 100,000。完整老师生成、开发、消融、额外 update/compute 检查点和重试另计。此处只给范围规划，不自行开启预算；实际减样由总控先冻结三任务协议并披露影响，不能把缺失任务写成验证完成。

T2 从 teacher 输出图离线提 Canny 条件，训练误差用可微 soft-edge，独立评价冻结 hard-Canny F1/双向距离或 Chamfer，并报告质量、文本、同条件多样性和失败。固定输入画布映射，不能按生成结果拟合对齐；检查空图、纯线稿、锐化和直接画条件线条的捷径。

T3 从 teacher 单人全身图离线提 keypoints 与 rendered skeleton，训练梯度来自冻结 PyTorch pose 网络的原始 heatmap/soft-argmax 路径。默认 OpenPose 检测与后处理并不自动可微。输入关节 mask、目标框与 canvas 事先固定；COCO17/OpenPose18 按关节名、左右和 neck 规则映射，不混用 BODY25。评价 detector 使用不同于训练代理的独立权重（ViTPose 等须核验），报告 PCK/OKS 与人体伪影/失败；预期人体缺失、关节缺失和多人输出留在全分母，禁止输出后 Procrustes 对齐、换姿态或只留成功检测。

第二视频架构 CogVideoX-5B / ConsisID 是可选 T1 架构扩展，不算第四主任务。重新核验 VAE、native 参数化、scheduler 与参考机制，独立 W0，从该 teacher 生成自己的配对数据（建议先 2,048 有效视频）。复用 T1 第一平台数据只能叫跨平台数据迁移；T2/T3 共用 SD1.5/ControlNet 不能算两种架构。

产物：任务登记与缺口表、各任务适配/独立成本和数据版本、对照/统计/失败审查、任务级 claim 建议，以及 `reports/<assignment_id>/scope_report.md`。done gate：三个任务均被明确登记，已分配 gate 的证据可复算，未执行与负结果透明，主张逐任务判断。三个条件范围不构成普适保证；两域不等于两任务，两个条件权重不等于两架构。论文角色根据真实结果收窄结论。


预算调整口径：完整正式协议为八方法各三训练seed；预算不足可在测试暴露前由总控显式冻结缩小协议并保留限制说明，不能静默省略方法/seed或声称完成原全量配置。B/C必须有本task_id的对应归因消融，不可借用其他任务结果升格。

全矩阵是完整正式目标；满足事前停止规则并经独立复核的阴性分支可按 [执行契约](../specs/execution_contract.md) 关闭。后继逐项记NOT_RUN_WITH_REASON，不能标成完整实证；三个任务均需有真实状态与依据。
