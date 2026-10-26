# 本项目的 Codex 工作约定

这是普通开放研究项目，不是 AutoResearch Harbor 出题任务。不要沿用其他项目的 H20/L20 限制、12 小时轨迹、NOP、专家题 QA 或个别用户豁免。

先定位含 `project.yaml`、`specs/`、`state/` 的项目根；读取 `state/research-state.json`、自己的任务分配和相关规范。技能内相对链接默认以原包内 SKILL.md 为基准；安装器会为独立安装补齐 references。

总控是 `state/research-state.json`、`state/assignments.json`、`state/gpu_leases.json`、`state/resource_plan.json`、`state/claim_evidence.json` 的唯一写者。Worker 只写授权目录、独立 run 与完成消息；短任务用可用 subagent，长期角色按主 prompt 的用户授权创建项目聊天。没有消息工具时通过 worker 的磁盘报告交接。创建聊天不等于已完成其任务，必须读取实际完成状态。

所有性能结果起点为 UNTESTED。不能把原文配置值、toy、mock、局部干预或预填表当作学生独立视频生成的证据。对方法不利的结果和失败输出同样入库。实验前锁协议；测试数据不参与调参；预算不足时修改未执行范围并留下理由，不能删掉已经看到的负结果。

训练正式队列由当前资源计划和 GPU 租约约束，不能因为创建了多个聊天就同时启动多个占满设备的训练。保留现有在途 job 与用户暂停状态。例行代码修复、分析和文档无需反复确认；仅缺少资源/预算授权时继续独立工作并汇报具体缺项。不要自动创建周期自动化、采购算力或向外部用户发消息。

若本研究确需调用 Doubao / Ark / Seed，可信主控先读取用户当地最新授权配置。本机既有路径为 `/Users/khan/.config/ark/current.json`，它只是本机路径线索，交接到别人的机器必须换成对方授权的配置路径。使用 Coding Plan `https://ark.cn-beijing.volces.com/api/coding/v3`，Chat Completions `/chat/completions`；不得自动回退按量 `/api/v3`，不得改变任务指定模型。凭据只由可信主控持有，不输出、不打包、不进 worker 环境。安全轮次边界刷新配置并保留在途记录与暂停状态。本项目核心训练并不要求调用这些 API。

引文和会议规则以可访问的原始来源核实；`vendor/` 是可选知识材料，旧模板规则不覆盖目标年份官方规则。本轮交接包制作不授权执行其中的未来训练任务。


研究范围已明确为T1身份视频、T2 Canny图像、T3人体姿态图像，完整规范在specs/three_task_protocol.md。task_id必须在派工/运行/证据中保留；三个任务独立gate与预算，均不得静默省略。
