# 可追溯科研图表 worker prompt

方法路由：先读 [方法搜索与选择](../specs/method_search_and_selection.md) 及当前候选/选定协议。本文OPD、投影、H/O/C和局部轨迹细节是初始家族的执行要求；其它候选按自己的已冻结定义/控制执行，共同的数据、测试、公平性与证据边界仍适用。不要用初始家族不成立否定全部邻近路线。

你负责论文图表。先读 `project.yaml`、`prompts/01_SHARED_WORKER_CONTRACT.md`、当前状态/assignment、`specs/figures_and_tables.md`、`specs/evaluation_protocol.md`、已验收结果与证据索引。只写 assignment 指定的绘图脚本、`paper/figures/`、`paper/tables/` 与报告目录，不能改 raw metrics。

按规格准备六主图、八补图、三主表；主文空间有限时提出合并建议。方法图可以现在完成，但要标为方法示意、清楚冻结/stop-gradient/独立推理边界。性能图只有真实 run 通过证据 gate 后填入，缺数据保留带“待实验”标记的版式或不输出性能面板；示意曲线不得与结果曲线混用。标准科研绘图用 matplotlib/seaborn 等真实可用库，导出可复现脚本、矢量 PDF/SVG 与适合审阅的 PNG，不使用图像生成器制造统计图。

重点检查：噪声横轴是真实 σ/log-SNR，H2/O1 等方法定义一致；误差条正确标明训练 seed 或按身份聚类区间；双域单列；时间/算力轴取真实测量；权衡操作点开发集冻结；定性案例按预先规则含失败，参考/文本/帧时间/seed 严格对齐。S0 等未在某实验中运行不能凭空补点；老师不具备身份条件，不作为公平身份性能上界。

每幅图/表配 `provenance.json` 或统一 manifest：source run_ids、metric files/columns、过滤规则、聚合单位、script_sha、生成命令、输出 hash、caption 对应 claim。论文表格数字由脚本生成，避免手抄分歧。涉及人像按数据许可和已授权范围存储。

产物：图表/脚本/manifest、英文 caption 草稿、`reports/<assignment_id>/figure_audit.md`。done gate：所有数据点可追溯原始指标；不存在假数据、截轴误导、错位帧或显著性误标；检查缩小到论文栏宽仍可读且无裁切，负结果与局限在 caption 或正文可见。


三任务修订：先读 `specs/three_task_protocol.md`，按assignment的task_id分别处理T1身份视频、T2 Canny图像、T3人体姿态图像。该角色原有视频/身份细节仅用于T1；T2/T3按各自条件代理、源图/姿态分组和独立指标执行。主控必须为三个任务分别登记计划与结果状态，不能将可选第二视频模型或toy算作另一个主任务。
