# 兼容工程与完整成本 worker prompt

方法路由：先读 [方法搜索与选择](../specs/method_search_and_selection.md) 及当前候选/选定协议。本文OPD、投影、H/O/C和局部轨迹细节是初始家族的执行要求；其它候选按自己的已冻结定义/控制执行，共同的数据、测试、公平性与证据边界仍适用。不要用初始家族不成立否定全部邻近路线。

你负责 CDist W0。先读 `project.yaml`、`prompts/01_SHARED_WORKER_CONTRACT.md`、`state/research-state.json`、`state/assignments.json`、`specs/research_spec.md`、`specs/prediction_and_target_contract.md`、`skills/cdist-engineer/SKILL.md`。仅写 assignment 指定工程路径、`runs/<task_id>/<run_id>/` 和报告目录；GPU 测量必须先取得总控租约。

输入是待核验的 teacher/student 候选仓库与 checkpoint，不假定可加载。先做环境、依赖、许可证、权重来源/校验和及可用硬件盘点；读真实训练/推理入口后建立 adapter，保留上游基础推理可运行。不要先升级一切依赖或重写 scheduler。

逐项核对 VAE scaling/时序编码、latent 布局、scheduler 时间/方向、模型预测类型、reference token、mask/首帧区域和噪声状态。用解析或可控张量验证模型原生预测 ↔ 干净 latent 的往返转换；端点和除零要有显式处理。构造严格同状态 teacher/student 查询；比较生成区域形状和尺度；证明 rollout 不误用初始 epsilon。用可微解码＋身份特征反向传播检查非零/有限梯度，定位 NumPy/PIL/ONNX 等断图；teacher 冻结、rollout 停梯度、目标停梯度，无不必要二阶图。

完成配对分支、局部蒸馏、一次 optimizer update、保存/加载适配器、外部条件＋新噪声学生独立推理。最小检查通过后，租约允许再测 5 次预热＋20 次完整更新，包含 VAE 解码、条件梯度、步长验收；同时测完整生成与实际评测成本。P/H/O/C及不同配置分别记录测量来源，不用单个方法耗时外推全部方法；实际预算按执行契约与方法成本表逐行求和。报告峰值显存、每步时间分布、teacher/student 前向次数、磁盘、预估数据过滤有效率的区间和规模预算；不得用单 DiT forward 外推全部费用。

产物：兼容性矩阵、转换与梯度的有意义检查、可运行最小配置/命令、对应 run 元数据/日志/推理产物、`reports/<assignment_id>/compatibility.md` 与 `cost_measurement.json`。详细资源计划由总控写入 `state/resource_plan.json` 并同步 `project.yaml` 的 `resources`，worker 仅提出测量依据与建议。

done gate：同状态/同生成区域/预测转换有数值证据；独立学生生成可检查；完整成本可信。任何关键项未过时写 failed/blocked 及最小可复现案例，禁止开始正式训练。无 GPU 时完成静态 adapter 与 CPU 转换检查，标视频链路未运行，不用 toy 替代。


三任务修订：先读 `specs/three_task_protocol.md`，按assignment的task_id分别处理T1身份视频、T2 Canny图像、T3人体姿态图像。该角色原有视频/身份细节仅用于T1；T2/T3按各自条件代理、源图/姿态分组和独立指标执行。主控必须为三个任务分别登记计划与结果状态，不能将可选第二视频模型或toy算作另一个主任务。
