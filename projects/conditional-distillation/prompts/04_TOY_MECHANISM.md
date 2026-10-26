# 二维机制实验 worker prompt

你负责 CPU 可完成的二维机制实验。先读 `project.yaml`、`prompts/01_SHARED_WORKER_CONTRACT.md`、`state/research-state.json`、`state/assignments.json`、`specs/research_spec.md`、`specs/mechanism_protocol.md`、`specs/prediction_and_target_contract.md`。写入独立代码路径、`runs/<run_id>/`、assignment 报告；不修改主控状态。

构造二维高斯混合：分量是条件，明确 p(x|c)、p(x)、扩散/flow 过程、条件误差代理；推导并数值核对精确 unconditional/conditional score。默认计划 20,000 训练/10,000 测试、5 个训练种子，实际配置先按 CPU 资源设定并锁协议。比较原始学生、直接 KD、条件门控、投影、投影＋实际检查、混合轨迹与完整学生轨迹；完整定义每个参数，不能用视频 H2 名称掩盖不同算法。

匹配查询时间、总更新与计算统计，明确哪些是精确 oracle、哪些是学习模型。固定训练/测试随机数来源，条件比例与 mode 覆盖有检查。记录 d0、g、gᵀd0、投影方向、半径裁剪和验收；单独检查零梯度/非有限梯度/步长全拒绝。一阶 gᵀd≤0 只验证局部近似；要测有限步条件误差，不能把一阶性质等同全局保证。

产物：运行脚本、锁定配置、run metadata/原始指标/种子、向量场/轨迹图、条件错误/模式覆盖/分布误差及置信区间、`reports/<assignment_id>/mechanism_report.md`。图须追溯 run，oracle 用不同标记；报告机制成立的条件和反例。

done gate：解析 score 与数值检查一致、至少一套完整训练/评测闭环、对照公平且各 seed 可重跑、结论不超出二维设置。主张冲突未出现时诊断分布/目标或报告阴性，不人为挑例保证有效。此任务完成不代表视频 W1 通过。
