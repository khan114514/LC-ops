# 辅助脚本

这些 Python 3 脚本只使用标准库，不是视频训练代码。接收者工程任务仍需实现并验证实际 trainer、sampler、dataset、metrics 和复现命令。

- `python3 scripts/preflight.py`：只读 CPU/GPU/工具/磁盘信息，不读凭据，不探测远端。可用 `--output reports/preflight.json` 保存新文件。
- `python3 scripts/cost_plan.py`：默认分别计算T1视频、T2 Canny图像与T3姿态图像的建议样本/检查点数量；不填测量值就输出 null 成本。旧 CLI 保留为 `SIMPLIFIED_ESTIMATE`，每任务一个更新时间不能代表不同方法的最终预算。`--method-costs <JSON路径>` 按任务、方法、配置和硬件分别汇总训练成本；详见下方。两种模式均不授权作业、不证明实测消耗，`is_final_resource_budget` 始终为 false。
- `python3 scripts/install_skills.py --destination /你的项目/.agents/skills`：复制十二个专用技能并补齐引用快照；目标有同名文件时停止，不覆盖，不修改全局配置。默认直接读取包内技能同样可用。
- `python3 scripts/validate_bundle.py`：结构、JSON、专用技能名称和可点击相对链接检查。PASS 仅代表这些检查通过，不代表研究已验证或论文可投稿。

主测试默认 2 域 × 100 身份 × 4 文本 × 2 推理种子 ×（8 方法 × 3 训练种子 + 1 原学生）= 40,000 视频。`cost_plan.py` 明确列出不包含的开发集、消融和第二平台成本。没有按批吞吐测量时不要宣称线性并行加速或完成天数。


三任务修订：默认主测为T1 40,000视频，T2/T3各50,000图像、共100,000图像。新增canny/pose各自update-seconds和generation-seconds参数，缺失时成本为null；两任务条件梯度成本不同，不共享未测时间。原有--update-seconds等参数只对应T1视频。

## 方法级训练成本表

先复制 [未测量模板](../templates/method_costs.example.json)，用真实完整更新计时和冻结配置填写，再执行：

```bash
python3 scripts/cost_plan.py --method-costs templates/method_costs.example.json
python3 scripts/test_cost_plan.py
```

模板覆盖 T1/T2/T3 各八种训练方法，3000 更新与三个 seed 是待冻结的计划；测量、配置、硬件和来源均为 null，不含虚构实测。模板运行会得到覆盖完整、测量不完整及 null 总成本，不代表运行就绪。脚本只读 JSON 并打印结果。

JSON 顶层必须有 `schema_version: 1`、实际 `train_seeds` 列表和 `rows` 列表。可选 `required_methods` 按 T1/T2/T3 分别声明本轮候选或选定方法，三任务的列表均须存在且非空；方法 ID 使用以英文字母开头的 1–64 位字母、数字、下划线、点或连字符，不可重复，S0 仍仅作推理基线。新方法不必属于初始八方法，只需在本任务清单中显式声明并在实验前冻结其定义、对照和候选筛选协议。例如下面仅为字段格式示意，不是已实现方法或已冻结协议：

```json
"required_methods": {
  "T1": ["P", "Candidate-A"],
  "T2": ["P", "Candidate-B"],
  "T3": ["P", "Candidate-C"]
}
```

缺省时兼容原八方法并输出 `planning_scope=DEFAULT_INITIAL_MATRIX`；显式声明时输出 `EXPLICIT_METHOD_MATRIX`，完整性只针对该声明矩阵，不能冒充初始八方法全矩阵已完成。成本工具不批准方法选择，实际候选与对照由总控依据研究证据和资源协议决定。每行字段如下，字段本身不得省略：

| 字段 | 含义 |
|---|---|
| `task_id` / `method` | T1/T2/T3 与该任务 `required_methods` 中声明的方法；缺省为 P/H0/H1/H2/O0/O1/C-H/C-O；S0 无训练成本，不放入此表 |
| `config_id` / `hardware_id` | 可追溯的冻结完整更新配置标识和实际计时硬件/拓扑标识；尚未确定填 null |
| `updates` | 每次独立训练的更新数，正整数 |
| `train_seeds` | 本行实际计划 seed，是顶层 seed 的非空子集；重复 seed 无效 |
| `repeats` | 每 seed 独立重复作业数，正整数；增加计算量，不增加独立训练 seed 数 |
| `gpu_count` | 一次计时作业使用的 GPU 数，正整数；未知填 null |
| `update_seconds` | 该配置与硬件下完整一次 optimizer update 的实测墙钟秒数，包含 rollout/teacher/VAE/条件梯度/回溯；未测填 null |
| `measurement_run_id` | 上述测量的真实来源 run 标识；缺来源填 null |

每行成本为 `updates × len(train_seeds) × repeats × gpu_count × update_seconds / 3600`，单位是 GPU device-hours。H/O/C 及不同 k、代理、分辨率分别填行，不能把 H2 的时间套给其余方法。脚本仅支持实测来源引用；有依据的保守上界由总控另列资源计划，不冒充实测行。脚本不检查 run 是否存在或测量是否可信，`source_runs_verified=false`；这些引用仍须总控/QA 核验。

完整覆盖检查针对 **每个任务 × 该任务声明的方法 × 顶层声明 seeds**，缺省方法清单为初始八方法。任一方法/seed 缺行，或某行成本/来源/配置/硬件字段为 null，对应任务与总训练成本均保持 null，状态为 `INCOMPLETE`；已知部分只出现在明确命名的 `known_training_gpu_hours` 小计。不会以 0、其他方法时间或旧 CLI 估算补缺。合法但不完整的表退出码仍为 0，调用者必须检查 `method_cost_plan.status`，不能把进程成功当成本完整。

同 task/method/config/hardware 的行必须合并；同 task/method/config/seed 跨硬件重复登记也会拒绝，防止双计。同一方法的额外配置可以另列，但所有额外计划必须主动登记，脚本无法发现未声明的配置；`scope.configuration_coverage=DECLARED_ROWS_ONLY`。负数、零成本、非有限数、错误类型、重复行/seed/JSON键、未知任务、未声明方法和未知字段均以退出码 2 拒绝。

顶层 seed 数必须匹配 `--train-seeds`（默认 3）。缺省初始矩阵时，`--trained-methods` 必须为 8；声明 `required_methods` 时，各任务的方法数从 JSON 分别获取，替代该 CLI 计数。缩小协议例如一个 seed 时，同时传 `--train-seeds 1` 并在 JSON 只列该 seed；输出保留实际 seed 和 `matches_default_seed_count=false`，不能冒充原三 seed 协议完整。`matches_initial_method_matrix` 则明确方法清单是否仍与初始矩阵相同。此工具不据此授权缩小研究范围。

方法模式下，训练时间/更新数/GPU数取 JSON，旧 `--update-seconds`、`--canny-update-seconds`、`--pose-update-seconds`、`--updates`、`--image-updates`、`--train-gpus`、`--image-train-gpus` 不参与训练核算；生成时间等旧参数仍按原公式工作。主测数量保持原单检查点公式，但显式矩阵分别使用各任务实际方法数；缺省仍为 40,000 视频与两个各 50,000 图像。额外配置或 repeats 不自动扩大评测数量，必须另列。该表仍不覆盖完整研究预算：老师数据、过滤、开发、消融、额外评测检查点、评价、重试、存储和人评须按真实工作计划另计；`COMPLETE` 只指声明范围的训练成本覆盖，不代表研究完成、资源获授权或完整预算已通过。
