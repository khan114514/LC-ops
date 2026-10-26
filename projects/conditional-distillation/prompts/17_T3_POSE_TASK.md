# T3：单人人体姿态控制图像正式任务 worker prompt

方法路由：先读 [方法搜索与选择](../specs/method_search_and_selection.md) 及当前候选/选定协议。本文OPD、投影、H/O/C和局部轨迹细节是初始家族的执行要求；其它候选按自己的已冻结定义/控制执行，共同的数据、测试、公平性与证据边界仍适用。不要用初始家族不成立否定全部邻近路线。

你负责正式任务 `task_id=T3`。它与 T1 身份视频、T2 Canny 图像并列，不是可选附加实验，也不以 T1 成功为推进前提。先读 `project.yaml`、当前 state/assignment、`prompts/01_SHARED_WORKER_CONTRACT.md`、`specs/three_task_protocol.md`、研究/预测/数据/评价规范、实验矩阵和 gate。只在 assignment 写目录和已有资源授权内工作；无 GPU 或无预算时完成准备，不执行实验。

## 对象与兼容性门槛

冻结与 T2 相同、且经核验匹配的 SD1.5 文本图像 teacher `T(z,t,b)`，不向 teacher 提供目标姿态。学生从已有 ControlNet 1.1 OpenPose 模型 S0 起步，输入相同文本和新增 body pose 条件 `c`。候选权重为 `lllyasviel/control_v11p_sd15_openpose`；先核验底座/条件权重/VAE/scheduler/revision/许可、native 参数化、CFG、negative prompt、预处理和可训练模块。不得把任意 SD1.5 衍生权重视为兼容，不能将 T2/T3 两套 ControlNet 条件当作两种架构验证。

独立 W0 检查同真实 `z,t` 的双方状态、native 预测 roundtrip、边界/生成 mask、姿态代理对解码输入的有效梯度、一个真实 batch 的完整更新和纯噪声独立姿态生成。建议 5 预热 + 20 次完整更新实测所有 rollout/teacher/VAE/pose forward/条件梯度/回溯成本，另测完整推理和独立 detector 评价；静态代码可用不等于 W0 实验通过。启动仍需预算和 GPU 租约。

## teacher 数据与姿态条件

teacher 先生成单人、全身完整可见图像，再离线提取数值 keypoints、置信度、可见性与同源 rendered skeleton。先只做 OpenPose body，不混入手/脸关键点；保存原图、数值点、渲染图、提取器权重/版本与全部变换。过滤多人、截断/出界、严重肢体伪影、关节不可辨和错误姿态标注，记录候选/有效/排除数量及原因，不用渲染图存在冒充有效人体。

建议 smoke 128 张、有限筛选 2,048 张、正式 8,192 张有效 teacher 训练图与 512 张开发图。外部测试建议 500 个来源与许可可核验的姿态条件，可从 COCO person-keypoint 等候选来源准备，但使用方式、许可和具体版本须先核验。外部条件不由训练 teacher 图回收替代；文本预先锁定为与姿态兼容的两条。按源图/人物簇/近重复及预注册近姿态模板组隔离 train/dev/确认测试；人物 ID 不可得时如实写可核验分组与残余相关性，不能声称已做严格身份隔离。与 T2 复用源图时保留全局 source/duplicate 分组与 T3 自己的有效样本 manifest，不重复计算独立量。

任务数据放 assignment 授权目录（例如 `data/T3/<data_version>/`）。manifest 保存 `task_id,source_group_id,person_cluster_id,pose_group_id,source_image_sha,keypoint_schema,keypoints,confidence,visibility,input_joint_mask,target_bbox,canvas_transform,skeleton_sha,extractor_revision,split,status,filter_reason`，以及共有来源/许可、teacher/config/data hash 与生成 seed。失败提取与过滤前条目也保留，不能按某方法输出选择条件。

## schema、画布与可见关节

预先锁定 COCO17、OpenPose18 的关节名称、左右、连线与 canvas 映射，按关节名核对，不能按张量索引硬配，也不能混用 BODY25（相同索引未必是相同关节）。需要 neck 时仅在双肩输入均有效时取双肩中点，否则该派生点无效；COCO17 评价不额外重复计 neck。目标点、渲染骨架和训练/评价坐标必须由同一个冻结映射产生。

固定输入可见性 mask 和目标 bbox/canvas 决定关节分母与归一化；生成图的低置信度、缺关节或缺人体不缩小该分母。输入规定的 resize/crop/letterbox 映射允许且需记录；输出不得再做 Procrustes、旋转、平移或缩放配准以消除姿态位置误差，不用输出自己的 bbox 归一化，也不换目标姿态、重选文本或只保留检测成功结果。

## 可微姿态误差与目标

训练使用冻结且 eval 的 PyTorch pose 网络（如待核验的 HRNet）的原始 heatmap forward，在固定输入有效关节上比较目标 Gaussian heatmap，可加可微 soft-argmax 坐标项。VAE/pose 参数不更新，但从热图误差到 Decode 输入保留梯度；预处理/normalization/resize 用可微 PyTorch 操作。默认 OpenPose 推理 API、NumPy、ONNX 和硬 argmax 后处理不自动可微；例如 HRNet 的 `get_max_preds` 一类 NumPy/argmax 后处理不能接在训练梯度链路上。须用真实 batch 核验非零有限梯度，不能仅以网络名声称满足要求。

检测/裁剪可在 detached 输入估计，但一次目标构造的 before/raw/after 与回溯检查使用同一固定 crop、人员匹配、坐标与 mask；不能候选目标变化后重选更容易的人或可见关节。条件代理在某噪声区间失效时，记录无效/拒绝并按开发预注册限制 query 区间；不能把代理失效当零梯度接受任意 teacher 方向。

其余目标严格按预测契约：固定最终 query time，teacher 一步→student k 步整体 stop-gradient，新状态同坐标查询与参数化转换；O 分支从纯噪声完整学生 rollout，配对独立重加噪；生成 mask、每样本投影/半径/实际代理回溯、有限近零梯度 fallback、最终 target stop-gradient 和固定总 batch KD 分母均保留。target 通过只说明代理检查通过，不保证真实姿态或训练后生成保持。

## 方法、gate 与资源

本任务保留 S0 + P/H0/H1/H2/O0/O1/C-H/C-O，八训练方法正式各三个独立 train seed（11/22/33 是起点）；S0 `train_seed=null`。C-H/C-O 只置 KD 为零，保留对应在线状态和公共条件损失；所有方法同数据/可训练模块/公共权重/开发搜索和选择规则。弱 KD、随机门控、仅条件方向、radius-only、半径匹配门控与路径消融由冻结矩阵约束，不缩成 H2 vs P；预算缺口如实保留，不静默删方法或 seed。

T3 独立走 W0 兼容/完整成本 → W1 局部 teacher 价值与姿态冲突、smoke → W2–W3 开发归因/正式预注册 → W4 正式评价。局部机制比较相同 query/续采 RNG 下真实图像质量与独立姿态指标，不用 `g·d`、代理热图下降或几次固定状态拟合替代完整采样。teacher 无收益/代理失配时保存负结果并诊断 T3，不取消 T1/T2。

每实际 run 必含 `task_id=T3` 与唯一 run_id，写 `runs/T3/<run_id>/`，记录真实 protocol/code/config/data/checkpoint hash、method、train/inference seed、命令、host/job_id、完整成本、起止和退出状态。历史路径如有只登记保留，不搬移或重复 launch。任务资源单独测量和申请，GPU 作业由总控租约排队；共享代码由总控指定 single owner，worker 不改共享 state，只写授权代码区和 `reports/<assignment_id>/`。

## 独立评价与失败

正式测试由学生接外部固定 skeleton + 两条冻结兼容文本 + 两个新噪声 seed 独立完整生成。500 条件 × 2 文本 × 2 推理 seed = 2,000 图/检查点；八方法 × 三 train seed + S0 = 25 检查点，共建议 50,000 主测图。T2/T3 合计 100,000 图仅是范围规划；老师数据、开发、消融、重试、不同 update/compute 检查点另计，不能自行开启预算。

评价 pose detector 必须使用不同于训练代理的独立权重，可选择不同模型/实现，但仅改包装代码不构成权重独立。候选 ViTPose 等先核验来源、许可、schema、输出坐标、可见性和实际运行。固定推理/匹配规则，预先说明预期单人与额外人体处理，不按方法挑最有利 detector。报告 PCK、OKS（阈值、目标 bbox/尺度、OKS sigmas、有效关节、missing 规则均冻结）、主要真实感/质量终点、文本符合、人体/肢体伪影、检测失败、额外人物和多样性。姿态非劣界与质量改善联合判断，不能仅靠一个姿态分数判成功。

未检出预期人体、输入有效关节在输出缺失/低置信度和额外人物按冻结失败规则计入所有预定槽位及关节分母；不以“detector failed”为由删行，不换 seed/姿态补成功样本。其他指标不可定义时报告覆盖率和预注册失败处理，不伪填正常数值。训练过滤与输出失败是两种记录，不能用输出过滤复写已冻结测试集。

按源图/人物簇和预注册近姿态组处理依赖，配对保留相同条件、文本、推理 seed 和方法，不能把同姿态的多个文本/seed当独立样本。逐 train seed 结果、三 seed 均值/SD 与条件抽样 CI 分开报告；CI 的聚类单位和残余依赖明确。固定噪声换姿态、固定姿态换噪声检查均保留。

## 回交与 done

交 `reports/<assignment_id>/report.md`、`status.json`、`T3_task_report.md`，附实际兼容性/数据/许可/坐标映射、代理梯度与独立评价器版本、资源测量、run 清单、逐图/逐关节指标和完整失败分母、统计脚本、任务级 A/B/C 证据建议及缺项。done 只代表 assignment 的 gate 完成；只准备时写 `NOT_EXECUTED`，不得写三任务实验完成。负结果、姿态代理失效及未测范围保留，三种条件不能支撑普适保证。


预算调整口径：完整正式协议为八方法各三训练seed；预算不足可在测试暴露前由总控显式冻结缩小协议并保留限制说明，不能静默省略方法/seed或声称完成原全量配置。B/C必须有本task_id的对应归因消融，不可借用其他任务结果升格。

全矩阵是完整正式目标；满足事前停止规则并经独立复核的阴性分支可按 [执行契约](../specs/execution_contract.md) 关闭。后继逐项记NOT_RUN_WITH_REASON，不能标成完整实证；三个任务均需有真实状态与依据。
