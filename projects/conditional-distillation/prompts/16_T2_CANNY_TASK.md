# T2：Canny 边缘控制图像正式任务 worker prompt

你负责正式任务 `task_id=T2`。它与 T1 身份视频、T3 人体姿态图像并列，不是等待 T1 成功后才启用的可选泛化。先读 `project.yaml`、当前 state/assignment、`prompts/01_SHARED_WORKER_CONTRACT.md`、`specs/three_task_protocol.md`、`specs/research_spec.md`、`specs/prediction_and_target_contract.md`、数据/评价/实验矩阵和 gate 规范。以 assignment 的写目录、冻结协议和资源授权为边界；无 GPU 或无预算时完成准备材料，不启动实验。

## 对象与兼容性门槛

冻结匹配的 SD1.5 文本图像 teacher `T(z,t,b)`；学生从已有 ControlNet 1.1 Canny 条件模型 S0 起步，接收相同文本和新增 Canny 条件 `c`。候选条件权重为 `lllyasviel/control_v11p_sd15_canny`；候选不等于兼容已确认。锁定底座/ControlNet/VAE/scheduler 的实际 revision、许可、native 输出参数化、latent scaling、CFG、negative prompt 和可训练模块，不能把任意 SD1.5 衍生权重当作匹配底座。

T2 独立 W0 必须核验同一真实 `z,t` 的 teacher/student 状态、正反参数化 roundtrip、边界/生成 mask、可微 soft-edge 梯度、单真实 batch 完整更新和学生从纯噪声独立生成。按建议 5 预热 + 20 次完整更新实测 rollout/teacher query/VAE/条件梯度/回溯总成本，另测完整推理与评价；静态适配不冒充 W0 已通过。具体执行须已有预算和租约。

## 数据与条件

teacher 先按冻结文本、seed 与生成设置产出完整图像，再离线提取 Canny 图 `c=h(xT)`，保存原图、条件图和生成/提取元数据。记录颜色空间、输入归一化、resize/crop、Canny 双阈值、边缘宽度/细化与 canvas；同一条件贯穿整条 rollout。候选数、有效数、失败数和排除原因分开计数。

建议 smoke 128 张、有限筛选 2,048 张，正式 8,192 张有效 teacher 训练图、512 张开发图；嵌套训练子集和独立机制确认集由冻结协议明确。外部测试建议 500 个来源/许可可追溯自然图像的条件，文本在开发阶段预先选择为兼容且有差异的两条，禁止只用 teacher 训练图的边缘外测。原图、近重复、同源变体整体分组隔离 train/dev/test。与 T3 复用源图时共用全局 source/duplicate group，保留 T2 自己的有效条件清单和有效量，不把重用图重复计作独立样本。

T2 数据写入 assignment 授权的任务目录（例如 `data/T2/<data_version>/`），manifest 至少增加 `task_id,source_group_id,source_image_sha,condition_sha,canny_config_sha,canvas_transform,split,status,filter_reason`；沿用共有来源、许可、teacher/config/data hash 和 seed 字段。冻结候选与过滤日志后再正式训练，不按方法额外清洗数据。

## 训练误差与方法

条件梯度路径为 `y → 可微 VAE Decode → 固定可微归一化/resize → soft-edge → E_c`。soft-edge 可用经开发校准的平滑 Sobel 梯度幅值，但它不是 hard Canny 的精确等价物；硬阈值、非极大抑制、PIL/NumPy/ONNX Canny 只用于离线条件提取或评价，不放进梯度链路。保存训练代理、目标边缘归一化和有效像素规则，局部干预需检验代理改善是否同时改善独立硬边缘指标，尤其纹理、粗细边缘和背景偏差。

逐项遵守预测/目标契约：先固定最终 query time，`T 一步→S^k` 全程 stop-gradient，在新状态重新查询并转换到相同干净 latent；O 分支从部署纯噪声完整 student rollout；配对分支独立重新加噪并使用正确 native label。生成区域外不参与 KD/投影；teacher、条件代理参数和最终 target 冻结，但对学生解码输入保留一阶梯度。投影、每样本半径、实际误差回溯、近零梯度 fallback、拒绝原因和固定总 batch 分母均按契约，不为图像任务另造简化目标。

本任务完整保留 S0 + P/H0/H1/H2/O0/O1/C-H/C-O。正式八训练方法各三个独立 train seed（11/22/33 为起点），S0 `train_seed=null`。C-H/C-O 只移除 KD，保留对应在线状态和公共 `Lc,q`；所有方法同训练模块、数据、公共损失权重、开发搜索预算和选择规则。radius-only、半径匹配门控、弱 KD/随机门控/仅条件方向及路径归因按冻结矩阵执行，不能只做 H2 vs P；预算缺口如实保留，不静默删方法或 seed。

## 任务 gate 与资源

T2 自己通过 W0 兼容和成本 → W1 局部 teacher 质量/边缘冲突与 smoke → W2–W3 开发归因和正式预注册 → W4 正式训练/评价。W1 不能只展示 `g·d` 或 soft-edge target 通过；须有相同续采随机数下的图像质量与独立硬边缘变化。若 teacher 方向没有可用收益或代理投机，保留负结果并先诊断该任务；不阻断其他任务。

每 run 使用唯一 `run_id`，必含 `task_id=T2`，写 `runs/T2/<run_id>/`，保存真实协议/代码/配置/数据/检查点 hash、方法、train/inference seed、命令、host/job_id、完整成本与退出状态。已有历史路径只登记，不搬移或重启旧作业。任务资源申请单列显存/GPU数/时间/磁盘、完整更新与推理测量来源；总控登记租约后才执行。共享 adapter/训练文件由总控分配 single owner；worker 只写授权代码区域和 `reports/<assignment_id>/`，不改共享 state。

## 独立评价与统计

测试为冻结外部 Canny 条件 + 两条冻结兼容文本 + 两个新噪声 seed，由学生完整独立生成。每检查点 500 × 2 × 2 = 2,000 图；八方法 × 三 train seed + S0 = 25 检查点，单个开发选定检查点/推理操作点共 50,000 主测图。T2/T3 合计建议 100,000 图；这不是算力授权，额外 update/compute 检查点、开发/消融、teacher 数据与重试另计。

独立固定 hard-Canny 评价器与预处理不随方法/输出调整，报告开发集锁定像素容差下的 edge precision/recall/F1、双向边缘距离或 Chamfer（注明单位、空集合规则）、主要图像质量终点、文本符合、失败和同条件多样性。图像按输入规定 canvas 直接比较，不做输出后配准。空图/空边缘、纯线稿、过度锐化、直接描画条件线条与解码失败单列；不能仅凭边缘 F1 判成功。质量改善结论同时满足开发冻结的边缘控制非劣界和其他预设约束。

固定噪声换条件、固定条件换噪声的响应检查均保留。所有方法共享 condition/text/inference-seed 的预定槽位，不换 seed 挽救生成失败；失败和未检出边缘保留全分母，指标不可定义时报告覆盖率与预注册失败处理，不临时删除样本。按源图/近重复组聚类配对统计，保留同条件文本、推理 seed 和方法配对关系；每 train seed 原值、均值/SD 与抽样 CI 分开，不能把 2,000 图当 2,000 独立源图。

## 回交与 done

在 `reports/<assignment_id>/` 交付 `report.md`、`status.json`、`T2_task_report.md`，包含实际输入/协议版本、兼容性、来源/许可与数据冻结、独立资源测量、方法/run 清单、逐图原始指标与失败槽位、统计脚本、A/B/C 的 T2 证据建议和未完成项。done 以 assignment 的任务 gate 为准；只准备协议时明确 `NOT_EXECUTED`，不得写训练/三任务验证完成。负结果和代理失配同样回交，三个条件的范围不支持普适保证。


预算调整口径：完整正式协议为八方法各三训练seed；预算不足可在测试暴露前由总控显式冻结缩小协议并保留限制说明，不能静默省略方法/seed或声称完成原全量配置。B/C必须有本task_id的对应归因消融，不可借用其他任务结果升格。
