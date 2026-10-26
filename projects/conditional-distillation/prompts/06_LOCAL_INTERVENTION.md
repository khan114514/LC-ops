# 视频局部干预与冲突诊断 worker prompt

方法路由：先读 [方法搜索与选择](../specs/method_search_and_selection.md) 及当前候选/选定协议。本文OPD、投影、H/O/C和局部轨迹细节是初始家族的执行要求；其它候选按自己的已冻结定义/控制执行，共同的数据、测试、公平性与证据边界仍适用。不要用初始家族不成立否定全部邻近路线。

你负责 W1 的真实视频局部干预。先读 `project.yaml`、`prompts/01_SHARED_WORKER_CONTRACT.md`、当前状态/assignment、`specs/prediction_and_target_contract.md`、`specs/mechanism_protocol.md`、`specs/evaluation_protocol.md`。W0 兼容性未通过不能执行本任务；GPU 使用总控派发租约。

从冻结数据和同一查询状态分叉：学生原始一步、老师原始一步、条件门控老师一步、修正老师一步；随后全部由同一个冻结学生、同一 solver/余下噪声、同一条件完成生成。任何结果中使用不同后缀采样噪声都要作为单独分析。先锁查询 log-SNR/σ 区间、每身份样本数、指标和失败处理，再执行。

记录每个分支的查询状态 checksum、时间、参考、d0/g/conflict、半径/步长、验收/拒绝、剩余 scheduler 状态、输出 artifact。分别观察目标构造的身份误差、有限步干预后的变化、最终生成的身份/动作/质量；对同一案例进行配对比较。质量不能用“更接近老师”代替。训练识别器以外的评测器按协议独立运行，检测失败计入分母。

产物：run manifest 与完整视频、配对指标表、按实际噪声作图的数据、按身份聚类的区间、随机/失败案例、`reports/<assignment_id>/teacher_value_diagnosis.md`。报告哪些区间存在质量收益且会破坏条件、哪些完全无收益；把探索性阈值选择与预先确定分析分开。

done gate：分支确实共享查询状态及学生后缀；最少样本量达 assignment 规定；三层证据完整；指标与人工抽查一致。若 teacher 在学生相关状态上没有稳定正向价值，提交 no-go/缩小范围建议，不在未通过时扩大训练。这个结果不能通过只展示 teacher 前缀的好视频代替学生独立生成。


三任务修订：先读 `specs/three_task_protocol.md`，按assignment的task_id分别处理T1身份视频、T2 Canny图像、T3人体姿态图像。该角色原有视频/身份细节仅用于T1；T2/T3按各自条件代理、源图/姿态分组和独立指标执行。主控必须为三个任务分别登记计划与结果状态，不能将可选第二视频模型或toy算作另一个主任务。

科学阴性与工程故障按 [执行契约](../specs/execution_contract.md) 分开。满足事前停止规则并经独立复核后，可建议总控关闭本分支；后继矩阵逐项记未运行，不能伪标后继gate通过，也不阻断其余任务。
