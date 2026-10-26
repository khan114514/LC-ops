---
name: cdist-engineer
description: 为条件扩散蒸馏实现并验证同状态预测、参数化转换、条件梯度和最小训练推理闭环，测量完整成本；用于视频与第二任务平台适配。
---

# CDist 兼容与目标工程

先定位活跃项目，读 [共享契约](../../prompts/01_SHARED_WORKER_CONTRACT.md)、[预测与目标契约](../../specs/prediction_and_target_contract.md)、assignment与当前状态。只写分配目录；总控单写state，GPU先取租约。技能安装快照不能覆盖活跃项目协议。

## 先确定数学与上游约定

模型组合是候选，先核验官方repo/checkpoint/version/license与真实入口。教师可能有共有文本，只缺新增身份参考条件；学生已有条件能力。保存上游无修改推理的基准输出，避免把工程退化当研究效果。

列对齐表：VAE scaling/编码时序、latent布局/维度、时间t/σ/log-SNR与方向、scheduler/solver、原生预测类型（epsilon/v/flow/x0）、参考token/首帧/mask、共享文本/CFG、dtype。转换公式从实际scheduler定义推导，不能按模型名字猜。

在同一噪声状态和同一生成区域查询双方，再转干净latent。用受控张量检查 native→x0→native 往返、时间边界、mask/布局；有意义的数值检查应能抓住符号、尺度和时间错位。先查分母接近零的端点，禁止静默clip改变研究定义。参考token、固定首帧等非生成区域不参与KD。

## 实现两条分支

配对分支从完整teacher视频独立重加噪，使用该位置的正确原生标签。混合分支先确定最终监督时间，再反向安排teacher一步和student k步；参考固定，rollout stop-gradient。同状态对比和完整学生轨迹也匹配最终时间。经rollout改变后的状态不能再拿最初epsilon当标签。

目标构造：在detach的student干净latent上打开条件误差梯度，teacher冻结。g来自可微VAE解码与冻结身份特征，禁止NumPy/PIL/普通ONNX路径断图。用grad finite/nonzero、有限差分或局部扰动验证。g只构造目标，无需对学生参数反传二阶图。

按契约计算d0、投影、半径、1/1⁄2/1⁄4有限步条件检查，选择最大合法步；零/非有限梯度、无效人脸和全拒绝的策略显式实现并记录。最终target detach后正确转回原生预测空间。拒绝KD仍保留配对分支。一阶 gᵀd≤0不代替真实有限步验收，也不保证训练后身份。

## W0验收

完成最小数据加载→配对/局部分支→loss→一次optimizer更新→checkpoint→reload→外部参考和新噪声独立学生生成。检查teacher权重不变、rollout无梯度、目标无二阶图、学生参数/条件模块实际更新。首帧I2V单独标记，不当主身份结论。

GPU测量先租约：5次预热＋20次完整更新，含decode/身份梯度/回溯验收；统计每步时间分布、峰值显存、前向次数、完整生成/评测和存储。保留真实run元数据、依赖、命令和日志，向总控回交资源计划依据。

done：对齐/转换/梯度/独立推理/成本有真实证据；有任一关键项未验证时不能放行正式训练。无GPU时只声明完成静态与CPU检查。异常先用可用的systematic-debugging定位，保留失败run；修复产生新code/config版本并列受影响结果。


三任务范围：读取 [任务契约](../../specs/three_task_protocol.md)，按assignment.task_id选择T1身份视频、T2 Canny图像、T3人体姿态图像的独立数据、代理、指标、gate与预算；新run使用runs/<task_id>/<run_id>/。本技能原有视频/身份细节仅用于T1，不能强加给T2/T3。三者都是正式研究范围；负结果需保留，未执行不能声称三任务实验完成，可选第二视频架构不是第4个主任务。
