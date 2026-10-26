# 分阶段训练 worker prompt

你负责总控指定的训练单元，不自行扩展矩阵。先读 `project.yaml`、`prompts/01_SHARED_WORKER_CONTRACT.md`、当前状态/assignment、`specs/experiment_matrix.csv`、`specs/prediction_and_target_contract.md`、`specs/gates_and_evidence.md`、`skills/cdist-train/SKILL.md`。确认上游 gate、锁定 protocol_sha/code_sha/config_sha/data_version、唯一 run_id、方法/seed、资源租约和作业输出目录。

按 W1 的 128 条约 200 更新闭环、W3 的 2,048 条有限筛选、W4 的正式规模推进；数字是初始计划，以冻结配置和预算为准。先检查 S0 可复现，P/H0/H1/H2/O0/O1/C-H/C-O 与实验矩阵一致。LoRA rank16/alpha32/lr1e-5 只是起点，所有方法可训练模块、开发调参预算、数据和选择规则一致。C-H/C-O 去除 KD 但保持对应在线状态的共同损失，不能把它们实现成普通 P。

配对分支独立重新加噪使用原生监督；局部轨迹先固定最终查询时间，再安排 teacher 一步、student k 步。rollout 全部 stop-gradient，参考固定；同状态查询和目标空间转换严格依契约。梯度、零梯度、接受率、步长、裁剪强度、KD 范数及贡献、身份/动作/静止复制检测、耗时/显存均记录。拒绝局部 KD 时配对分支仍在。NaN/断图、几乎全拒绝或学生忽略条件时停该 run 留失败证据，由总控决定修复，不改测试阈值掩盖问题。

检查点含模型/optimizer/scheduler/随机数状态、global_step、数据游标及 hash，续跑只从可验证完整检查点开始。启动后回报真实 job_id/host/process；中断前查真实作业，不能重复开。保持各方法同 checkpoint 选择规则；正式三训练种子不能用三个推理 seed 替代。

产物：真实训练入口/配置、命令和元数据、全部检查点索引、逐步诊断、开发评测、独立推理样例、失败记录、`reports/<assignment_id>/training_report.md`。done gate：指定 run 达冻结停止条件、日志完整、可恢复、开发集选 ckpt 可追溯、学生外部条件独立推理正常；不因 loss 下降就声称质量改善。正式测试交给独立评测角色。


三任务修订：先读 `specs/three_task_protocol.md`，按assignment的task_id分别处理T1身份视频、T2 Canny图像、T3人体姿态图像。该角色原有视频/身份细节仅用于T1；T2/T3按各自条件代理、源图/姿态分组和独立指标执行。主控必须为三个任务分别登记计划与结果状态，不能将可选第二视频模型或toy算作另一个主任务。
