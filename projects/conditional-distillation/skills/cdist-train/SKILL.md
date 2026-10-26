---
name: cdist-train
description: 按冻结矩阵执行条件蒸馏的分阶段训练、资源租约、诊断、检查点和续训，保持归因对照与计算公平；不自行扩展GPU预算。
---

# CDist 训练执行

方法范围：先读 [方法搜索与选择](../../specs/method_search_and_selection.md) 和当前候选/选定协议。本文涉及的OPD、H/O/C、投影/局部轨迹是初始家族要求，不是所有候选必用算法；其它路线按其冻结定义与控制执行，共同证据边界不变。

先读活跃项目 `project.yaml`、state和assignment、[共享契约](../../prompts/01_SHARED_WORKER_CONTRACT.md)、[实验矩阵](../../specs/experiment_matrix.csv)、[预测契约](../../specs/prediction_and_target_contract.md)、[阶段gate](../../specs/gates_and_evidence.md)。只执行分配run，不擅改总控state。安装的快照是参考，当前项目规范优先。

## 启动条件

W0同状态预测/转换/可微梯度/独立推理和成本通过；数据version/split冻结；protocol/code/config hash真实；唯一run_id和写目录；明确方法/训练seed/停止与checkpoint选择规则；资源计划完整且有租约。缺一先回报具体缺项并完成独立准备，不能默认八方法同时运行。

读真实仓库找到入口，不编造CLI或调度命令。记录host/job_id、环境、命令、working directory、代码脏状态；不能只记录“已启动”。提交前查重，续跑先核验调度器/进程/现有输出。主实验学生必须保留外部参考从新噪声独立生成能力。

## 方法与公平性

S0只作冻结起点。P、H0/H1/H2、O0/O1、C-H/C-O按矩阵逐项核对。C-H/C-O保留与H2/O1对应在线状态和共同损失，只移除KD；它们不是普通P。g、投影、半径、回溯、条件容差和fallback从预测契约实现。

同一数据/可训练模块/初始化/调参预算/开发选择/推理设定。LoRA rank16、alpha32、lr1e-5只是计划起点，不做未经说明的方法特权。先锁最终查询时间再构造k=0/1/3或轨迹来源；rollout停止梯度、条件全程固定。配对重加噪独立于teacher原seed；新状态KD标签不沿用最初epsilon。

按128小闭环→2048有限筛选→预算允许的正式8192/三训练seed推进。原计划约200/1000/3000更新是初值，以实际冻结协议为准。同步数和等实际计算预算两种视角分开建run/分析，报告teacher/student前向、GPU小时和有效更新。三训练seed不能用三个推理seed冒充。

## 诊断与恢复

日志保存pair/cond/KD各项、梯度范数、teacher方向/条件冲突、有效检测、接受率/步长、裁剪幅度、NaN/Inf、条件响应、动作/静止复制、时间/显存。近全拒绝或条件消失先诊断；不改阈值隐瞒。被拒绝局部KD仍有pair更新。训练loss下降不等于质量提升。

checkpoint保存模型/LoRA、optimizer、scheduler、RNG、数据游标、global_step和版本；用原子保存/完整性标记或上游可靠机制防半文件。恢复验证内容hash与状态；只有权重的恢复标非精确重启。原失败/中断run不覆盖，新run引用父run与恢复点。若修复改变算法或数据，交总控判定可比性与复验范围。

每run至少输出元数据必填字段、实际配置/命令、训练日志、checkpoint索引、开发评测和独立生成清单。主测试规则不由训练worker修改。总控根据开发集选择检查点后交独立评测。

done：完成assignment停止规则、退出/检查点完整、版本可追踪、可重载、诊断无未解释关键异常，报告全部失败和资源用量。证明方法有效由下游评价与QA判定，不能以“训练跑完”替代。


三任务范围：读取 [任务契约](../../specs/three_task_protocol.md)，按assignment.task_id选择T1身份视频、T2 Canny图像、T3人体姿态图像的独立数据、代理、指标、gate与预算；新run使用runs/<task_id>/<run_id>/。本技能原有视频/身份细节仅用于T1，不能强加给T2/T3。三者都是正式研究范围；负结果需保留，未执行不能声称三任务实验完成，可选第二视频架构不是第4个主任务。
