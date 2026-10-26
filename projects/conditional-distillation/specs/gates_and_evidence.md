# 阶段门槛、证据与结果契约

本文件规定证据怎样使工作可复算。当前状态为 PREPARED / NOT_STARTED，所有主张 UNTESTED。门槛不是“必须取得正结果”；负结果、停止扩展及收缩论文范围也是有效研究产出。没有预注册数值时先在开发集定值，不能在测试后补写门槛。

## 阶段门槛

| Gate | 需审查的可观测证据 | 通过后可做 | 未通过时 |
|---|---|---|---|
| G0 适配和成本 | 确切 checkpoint/许可/代码版本；状态与参数化 roundtrip；mask；可微身份梯度；一次真实完整更新与独立生成；5预热+20完整更新建议计时 | 申请/使用已授权的下一阶段预算 | 修适配或换经授权平台；不虚报单DiT耗时为全研究成本 |
| G1 冲突与老师价值 | 二维解析复核；冻结视频局部干预；共享续采；身份/质量/动作联合曲线、失败和CI | 128条试训 | 老师无局部收益则检查平台/时间段或收缩问题 |
| G2 试训闭环 | 约200更新；KD接受/拒绝；学生纯噪声完整推理；条件替换响应；静止/复制/失效审查 | 2,048条有限筛选 | 修目标/代理/数据，不能用老师前缀结果替代 |
| G3 归因与预注册 | P/H0/H1/H2/O0/O1/C-H/C-O 开发比较；公平配置；弱KD/随机门控/仅条件必要诊断；冻结正式协议、test case、阈值及资源预算 | 8,192条正式三seed | 缩小主张或先补关键对照；不无限跑网格 |
| G4 主实验 | 八方法三seed与S0；相同更新和相同compute分开报告；独立外测；训练seed与identity CI分开；全部失败入分母 | 确认主张与人评 | 公开缺失，区分确认/探索，不能填补造数 |
| G5 泛化与论文 | 必需关键消融、第二平台/任务或明确限定；图表脚本；claim→evidence；许可/复现材料；当前投稿要求 | 更新实证论文草稿与投稿材料 | 保留预实验草稿或有证据的窄结论，不把待验证写成完成 |

G1/G2 的目标是尽早判断研究可行性，不要求老师在所有时间段获益。若只某区间有效，预注册该范围并在论文写清。执行中保留用户暂停状态；阶段失败与用户暂停分开，不能自动恢复被暂停训练。费用、外部发信、公开上传、投稿依实际授权，不因本包文档而扩张。

## Run 最小字段

同一结果以不可复用的 `run_id` 追踪，字段与 `templates/run_manifest.example.json` 对齐：

`task_id,run_id,status,protocol_sha,code_sha,config_sha,data_version,split,method,train_seed,inference_seed,artifact_paths`。

实际 run 另记 `execution_kind,code_dirty,evaluation_version,checkpoint_sha,host,gpu_model,scheduler_job_id,started_at,finished_at,actual_gpu_hours,failure_reason,is_confirmatory`。时间带时区或 UTC，所有路径相对项目根或为有权限的 artifact URI；不放绝对私人路径、token 或凭据。run_id 建议包含任务/方法/seed/短SHA/attempt，不把“best”当唯一标识。

建议实际状态枚举 `PLANNED,RUNNING,COMPLETED,FAILED,BLOCKED,CANCELLED,MISSING`；模板用 `TEMPLATE_NOT_A_RUN`，矩阵用 `PLANNED_NOT_EXECUTED`，均不能当已执行记录。S0 `train_seed=null`；推理 seed 不适用时也为 null。`status=COMPLETED` 只表示这个 run 按协议执行完成，不意味着论文主张成立。

`protocol_sha` 对应冻结 protocol 文本及关键 manifests 的内容哈希；`code_sha` 对应实际执行 commit，dirty 时保存 patch/工作树内容hash并在 code_dirty 标记；`config_sha` 来自排序规范化配置文件；`data_version` 指向不可变样本/划分 manifest，不能只写“latest”。记录所有依赖版本及精度/设备相关设置。

## 证据分层

- **planned**：计划、模板、图表规格，无实验产出。
- **simulated**：toy 或 mock；不能作为真实平台训练结果。
- **smoke**：真实小规模功能/梯度验证；不能声称正式指标。
- **exploratory**：开发/敏感性或测试暴露后的探索。
- **confirmatory**：冻结协议下在未参与选择的确认数据上执行。

每张表/图和每条 claim 标明层级、生成脚本、输入 run IDs、数据/代码/协议 SHA、指标定义和失败处理。训练损失降低、目标检查成功、完整视频主指标改善是三种不同证据。

## 必需 artifact

每次训练：manifest、resolved config、日志、loss/接受率/梯度与拒绝原因、完整成本、checkpoint SHA、checkpoint选择记录、异常/重试日志。每次推理：预定 case manifest、视频/图像 hash、实际 seed/config、逐case状态。每次评价：逐视频/帧原始数值、评价器与预处理版本、缺失与失败、聚类ID、汇总与bootstrap脚本、bootstrap seed和统计配置。

主张表每行 `claim_id,claim_text,status,scope,evidence_run_ids,figure_table_ids,limitations,decision_date`。A/B/C 状态从 UNTESTED 变成 SUPPORTED/PARTIALLY_SUPPORTED/NOT_SUPPORTED 时必须附对应对照与不确定性，不能凭作者判断空更新。

## 公平预算与恢复

硬件无厂商要求；按实际可用资源测量。资源文件记录允许的并行度、有效GPU小时/墙钟上限、存储、作业ID和租约。一个任务写自己的 run/artifact 目录；协议、测试case与共享状态只由负责人合并。恢复先核对 run_id、job状态、最后checkpoint、SHA和已消费预算，禁止重复启动同一正式seed。

正式实验的 40,000 主测视频是预算估算，不是执行授权或已完成数量。所有耗时/费用估算标 estimated 并注明测量来源；actual 仅从真实日志汇总。预算不足优先缩探索网格，不无声删除归因对照。

## 提交论文前的证据审计

从原始记录复算主表与CI，核对每一数字是否有真实run支持；检查测试泄漏、分母、域权重、每seed结果、失败重试、资源口径和相同推理；检查所有“首次”“保证”“通用”措辞是否超证据。无完整实验时仍可交付含方法与实验设计的预实验初稿，摘要和结论必须写“待验证”，不写虚构实验结果。此包本身不授权提交到任何会议。

预算口径补充：40,000 仅覆盖每个方法/训练seed的一个开发集选定 checkpoint、一个冻结推理操作点及 S0 的一套评测。如果 update-matched 与 compute-matched 对应不同 checkpoint，并都进行全量外测，应分别增加生成与评价预算；额外操作点、性能曲线、消融和重试也不在这 40,000 内。不能同时宣称 40,000 已覆盖两套全量对照。


三任务完成门：每个T1/T2/T3独立记录G0–G4和A/B/C结论、数据/代理/独立评价/预算。三个任务均列入正式研究范围；某项未执行不得宣称三任务实验完成。任务内负结果允许，不能删任务。可选第二视频架构不计为额外主任务。跨任务规则与图像数量见 [three_task_protocol.md](three_task_protocol.md)。
