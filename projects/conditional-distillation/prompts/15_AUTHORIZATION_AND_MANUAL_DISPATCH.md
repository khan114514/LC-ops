# 可复制授权与无工具时的手工派工

`00_START_HERE_CN.md` 已包含完整启动授权。若用户先建立项目、稍后只想补授权，可复制下一段；它不替代明确的算力/费用限额。

> 我授权本项目的 Codex 总控在当前 CDist 项目中创建所需的独立 Codex 聊天，并为这些聊天发送任务与后续消息；我也授权受派研究聊天向总控回报、在这些研究聊天间传递本项目所需的信息。优先复用已有聊天；短子任务可用 subagent。不要覆盖默认模型，不要借此对外发消息、购买算力、创建定时自动化、公开上传或提交论文。所有执行遵循项目资源计划；已暂停任务保持暂停，除非我明确要求继续。独立 worker 不写总控 state，GPU 作业须总控发租约。现在按项目 `prompts/00_START_HERE_CN.md` 和共享契约推进。

## 手工模式

当 `create_thread`/聊天消息工具不可用，总控仍负责状态与依赖；输出真实派工卡，不宣称已创建聊天。用户新建普通项目聊天，把该角色 prompt 和派工卡复制过去。若 subagent 可用，优先用它处理短任务；没有并发工具则按依赖串行执行，不影响工件契约。

每张派工卡填写真实值，未确定填 `unassigned` 并先完成准备工作：

```yaml
project_root: <当前机器真实绝对路径>
assignment_id: <总控唯一分配>
task_id: <T1或T2或T3；二维机制用TOY；非实验工作为null>
task_ids: [<非实验工作涉及的正式任务；实验工作填唯一task_id>]
role_prompt: prompts/<对应文件>.md
owner: <真实聊天/worker标识>
inputs: [<实际存在的输入相对路径>]
allowed_write_paths: [<独占输出路径>]
protocol_sha: <实际协议摘要>
run_ids: [<预分配run_id；只读任务可空>]
resource_request: <CPU或已批准GPU租约引用>
done_gate: <该任务的具体验收条件>
report_path: reports/<assignment_id>/report.md
reply_to: <已获授权的总控聊天标识或手工回交>
```

启动独立角色：先粘贴派工卡，再粘贴 `02`–`14` 或 `16`/`17`/`18` 对应角色 prompt；共享目录必须真实可访问。涉及不同机器时由总控安排显式同步清单与 checksum，不假设路径自动共享。回交将 `report.md`、`status.json` 和工件清单给总控；不要在每个聊天里重启整套主流程。

建议先并行文献核验、静态兼容工程、CPU toy；数据生成、视频局部干预、训练、外部生成等依照 gate 和 GPU 租约排队。paper/图表在早期完成结构与方法示意，真实结果晚些填入；QA 用只读独立角色复核同一版本。
