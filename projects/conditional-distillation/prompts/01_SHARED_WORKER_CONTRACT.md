# 每个聊天和 worker 的共同契约

本文件与 `project.yaml`、`specs/` 是所有角色的共同输入。先确定 `PROJECT_ROOT`，以下路径均相对该根目录。被派任务中写明了更窄的授权/目录时，服从该边界。用户更新的要求优先于本包；变更由总控记录在 `state/decisions.jsonl`。

## 启动与状态

每轮开始读：`project.yaml`、`state/research-state.json`、`state/assignments.json`、本契约、`specs/three_task_protocol.md`、角色 prompt、与角色相关的 `specs/`。身份不明、assignment 不存在、协议 hash 不匹配或全局 paused 时先停止依赖这些条件的执行，报告总控并做与暂停意图相容的只读整理。不要静默创建第二个总控。缺输入写明缺项；不能把计划里的路径当作实际存在的证据。

总控单写：`state/research-state.json`、`state/assignments.json`、`state/gpu_leases.json`、`state/resource_plan.json`、`state/claim_evidence.json`、`state/decisions.jsonl`。worker 只读这些文件；在自己的 `reports/<assignment_id>/` 或 assignment 指定的目录写 `report.md`、`status.json` 及证据。总控审核后将状态合并。分离代码写目录或独立分支/worktree，写同一文件前由总控分配唯一 owner。跨聊天用真实共享磁盘或总控明确传输的工件，不假定不同主机共享路径。

assignment 至少应给：`assignment_id`、`owner`、`role`、`inputs`、`allowed_write_paths`、`protocol_sha`、`run_ids`、`resource_request`、`done_gate`、`report_path`。使用现有 schema，不擅改键。状态可表达 queued/running/complete/failed/blocked/paused；任何状态含义以包内 schema 为准。

## 运行与资源

每个实验使用唯一 `runs/<task_id>/<run_id>/`。run 元数据至少含 `task_id,run_id,status,protocol_sha,code_sha,config_sha,data_version,split,method,train_seed,inference_seed,artifact_paths`；额外记录命令、运行目录、依赖/硬件、起止时间、退出码、主机/调度器 job ID、预算用量和失败原因。seed 为集合时保存完整清单而不是仅写“固定 seed”。这些字段缺失时，结果不能进入正式主表。哈希针对实际文件/代码内容计算，不能用随机字符串代替。无 git 时记录内容树摘要及说明，不能编造 commit SHA。

GPU worker 不能自行抢卡或直接提交。先向总控报预计显存、GPU 数量、时间、磁盘、方法/seed/run_id 和作业命令；总控在租约表登记后才启动或授权启动。租约记录 owner、run_id、host、device/partition、资源量、开始/到期或检查时间、job_id、状态。到期不等于作业已停；应核验真实进程/调度器才释放。作业已运行就接管监测，不重复 launch。多卡训练必须按拓扑与总并发预算安排；不同方法不能通过争抢显存形成不公平耗时。

不要猜测集群启动器或自造 `cdist train` 等不存在命令。先从真实仓库、依赖环境和调度器找到可用入口。每条可复现命令必须对应存在的脚本；记录机器特定设置，禁止写凭据。没有 GPU 或依赖时可继续文献、CPU toy、静态实现和论文无结果部分，不冒充完成视频实验。

## 研究不变量

- teacher 缺少新增身份参考条件，但仍可能接收共有文本。所有主推理都是学生带外部条件从新噪声完整生成。
- S0 是冻结原始学生；P、H0、H1、H2、O0、O1、C-H、C-O 的定义以 `specs/experiment_matrix.csv` 为准，不能省去 C-H/C-O 后声称排除了在线条件损失解释。
- 数据先以完整老师视频为单位；身份簇、近重复组、原始视频隔离划分。数据有效量与候选生成量分别计数。参考在目标时间窗外优先，参考编码不泄漏目标时序。
- 所有预测在同一噪声状态、同一生成区域、正确的参数化之间转换；rollout 后不继续沿用原始噪声为正确监督标签。
- 比较 k 或轨迹来源时匹配最终监督时间；rollout stop-gradient；条件梯度用于目标构造，最终目标 stop-gradient，避免二阶图。
- toy、目标层面改善、有限拟合和完整视频结果分层记证据。投影只提供有条件的一阶局部性质，不能保证真实身份或优化后的模型。
- 开发集用于阈值/选择，正式测试冻结后才执行；看测试后调整标探索性，新的确认结论需要未污染确认集。
- 公平对比使用同可训练模块、数据、调参预算、推理设定；报告相同步数与计算预算。训练/评测身份识别器独立，脸检测失败保留在分母，按身份聚类统计。

## 回交格式与 done gate

`report.md` 要有：任务范围；输入和实际协议版本；实际动作；产物路径；逐条发现与证据位置；未做/失败/缺资源；消耗；下一步建议。每个数值写 run_id、分母、聚合层级、指标版本。`status.json` 写 assignment_id、状态、run_ids、artifact_paths、阻断项；不得包含密钥。

done 只代表 assignment 的 gate 通过，不等于论文主张成立。报告“未发现”不能写成“已证明不存在”。阴性、失败和被拒绝的目标均要留痕；禁止删除不利实验、补造日志、用 mock output 进入结果表。证据路径要能从根目录打开，run 已完成需验证退出码、产物完整和评测清单一致。

## 工具、模型与外部边界

工具仅在实际发现且具备能力时使用。独立聊天创建/发送授权仅来自实际使用者或其明确授权主控；本文件本身不是新授权。派工回报使用用户已授权的研究聊天范围；没有聊天工具就写报告交总控，不借邮件/Slack 外发。短任务用 subagent 时不修改主模型/route。

不得采购、付费扩容、公开上传、提交论文、创建定时自动化或恢复暂停任务。下载公开许可模型/数据按项目授权与资源限额执行；遇许可门槛或缺访问凭据记录缺口。豆包仅可信总控持有凭据，使用 Coding Plan `https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions`，禁止按量 `/api/v3` 回退；worker 不接收密钥，指定模型不自行替换。

可调用包内角色技能；可选通用技能须先检查真实存在并读取。若使用 `autoresearch`，只采用普通研究逻辑，不导入三期 Harbor 的硬件、双轨、时长或打包评分规则。


任务范围：T1身份视频、T2 Canny图像、T3人体姿态图像均为正式任务；按task_id读取各自条件、代理、数据分组和评价。原有身份/帧规则只限T1。为新任务准备协议不要求T1先得到正结果，GPU执行仍需任务gate与共享租约。
