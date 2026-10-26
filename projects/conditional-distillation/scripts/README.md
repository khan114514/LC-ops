# 辅助脚本

这些 Python 3 脚本只使用标准库，不是视频训练代码。接收者工程任务仍需实现并验证实际 trainer、sampler、dataset、metrics 和复现命令。

- `python3 scripts/preflight.py`：只读 CPU/GPU/工具/磁盘信息，不读凭据，不探测远端。可用 `--output reports/preflight.json` 保存新文件。
- `python3 scripts/cost_plan.py`：默认分别计算T1视频、T2 Canny图像与T3姿态图像的建议样本/检查点数量；不填测量值就输出 null 成本。`--help` 列出参数。用真实完整更新、老师/学生分别生成的时间和实际 GPU 数量估算，不能把估算当实测消耗。
- `python3 scripts/install_skills.py --destination /你的项目/.agents/skills`：复制十二个专用技能并补齐引用快照；目标有同名文件时停止，不覆盖，不修改全局配置。默认直接读取包内技能同样可用。
- `python3 scripts/validate_bundle.py`：结构、JSON、专用技能名称和可点击相对链接检查。PASS 仅代表这些检查通过，不代表研究已验证或论文可投稿。

主测试默认 2 域 × 100 身份 × 4 文本 × 2 推理种子 ×（8 方法 × 3 训练种子 + 1 原学生）= 40,000 视频。`cost_plan.py` 明确列出不包含的开发集、消融和第二平台成本。没有按批吞吐测量时不要宣称线性并行加速或完成天数。


三任务修订：默认主测为T1 40,000视频，T2/T3各50,000图像、共100,000图像。新增canny/pose各自update-seconds和generation-seconds参数，缺失时成本为null；两任务条件梯度成本不同，不共享未测时间。原有--update-seconds等参数只对应T1视频。
