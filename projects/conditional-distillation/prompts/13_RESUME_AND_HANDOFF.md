# 跨聊天续跑 / 上下文恢复 prompt

继续执行本 CDist 项目。请先定位 `PROJECT_ROOT`，读 `project.yaml`、`prompts/01_SHARED_WORKER_CONTRACT.md`、`state/research-state.json`、`state/assignments.json`、`state/gpu_leases.json`、`state/decisions.jsonl` 最近相关记录、最新交接报告和你被分配的角色技能。不要从研究计划第一步重跑。

先确认你是总控还是 worker、此前用户是否暂停、当前授权预算和写目录。暂停仍有效时保持暂停，不因本文件或已过时间自行恢复；“继续”由实际使用者明确发送时才恢复授权范围。若另一个总控活跃，只回报准备情况，不争写 state。旧聊天消息或 subagent 请求不是跨项目额外授权。

建立实际状态快照：逐个 active run 核验 host/scheduler/job_id/process、日志最后更新时间、检查点完整性和输出；租约过期不能推断作业停止。真实作业还在就重新附着监测，已完成未收录就验证产物后由总控合并，失联只标 unknown，不重复提交；确认已终止才按预算决定恢复。代码/config/protocol/data 变更不能覆盖旧 run；可比性受影响则生成新 run_id 并写变更决策。

worker 从总控 assignment 继续，不自行改阶段或抓取另一个 worker 的工作。续训须检查模型/optimizer/scheduler/RNG/data cursor/global_step、content hash 与训练入口；只有 weights 的恢复要标非精确重启，不声称连续训练。先保留所有历史正负证据与失败产物。

产物：`reports/<assignment_id>/resume_audit.md`，列已完成、正在运行、失败/失联、预算余量、当前版本与下一项最小动作。总控写状态和派工后再执行；worker 直接回交 audit。无需未来唤醒时不创建自动化。done gate：没有重复 run、状态与实际作业一致、暂停/版本/预算边界保留，并开始恰当的下一项已授权工作。
