# 文献与资源核验（2026-10-26）

本次从原始研究计划出发核验主源，未运行训练、模型、数据下载或复现。`verified_references.bib` 的元数据来自本次程序下载的 arXiv BibTeX 或官方仓库 README BibTeX，原始条目保存在 `raw_bibtex/`；只统一 citation key，不从记忆生成作者表。**核验存在和方法描述不等于复现其结果，也不等于本项目新颖性已成立。**

## 必须正面处理的近邻

| 条目 | 本次核验主源 | 已确认内容及边界 | 对本研究的含义 |
|---|---|---|---|
| CoDi, 2310.01407，v2 2024-02-17 | [arXiv](https://arxiv.org/abs/2310.01407)、[全文](https://arxiv.org/html/2310.01407v2) | 条件适配与条件一致性蒸馏。正文的 unconditional 也包含只有文本条件的基础模型。不能将它简写为“新增条件蒸馏没人做过”。 | 新增条件与已有先验结合本身已有先例；需比较机制与训练目标。 |
| HPSD, 2608.13205，2026-08-13 | [arXiv](https://arxiv.org/abs/2608.13205)、[全文 §3.3](https://arxiv.org/html/2608.13205v1)、[作者仓库](https://github.com/Bujiazi/HPSD) | 老师轨迹锚点后由学生局部 rollout，并在新状态查询老师；其老师有首帧/增强文本特权，学生是基础 T2V，且老师 EMA 更新。 | 与混合轨迹高度接近，不能声称首次 teacher anchor + student rollout。本研究拟研究反向条件差：冻结老师缺少学生身份参考。H0/O0 等是受控适配，不得冒称官方 HPSD 复现。 |
| PDMD, 2609.35768，2026-09-28 | [arXiv](https://arxiv.org/abs/2609.35768)、[全文](https://arxiv.org/html/2609.35768v1)、[作者项目页](https://pdmd2026.github.io/) | 投影移除 DMD 方向沿学生—critic 端点残差的分量，目标是过滤 critic 误差；不是条件误差半空间投影。 | 投影运算本身不能当新颖性。需说明方向、目标、监督来源与约束对象不同。 |
| DiffusionOPSD, 2608.24646，2026-08-25 | [arXiv](https://arxiv.org/abs/2608.24646)、[作者仓库](https://github.com/worldbench/DiffusionOPSD) | 奖励梯度构造有界正负 clean-output targets，目标停止梯度，有限拟合后更新行为策略；区分目标改善与实现改善。 | 本研究同样必须分别测目标构造、有限拟合和部署输出；不能声称 first detached target 或直接移植其理论保证。 |
| Diffusion Self-Distillation, 2411.18616 | [arXiv](https://arxiv.org/abs/2411.18616)、[CVPR 2025 PDF](https://openaccess.thecvf.com/content/CVPR2025/papers/Cai_Diffusion_Self-Distillation_for_Zero-Shot_Customized_Image_Generation_CVPR_2025_paper.pdf) | 文本模型生成与筛选成对数据，再训练图像+文本条件模型。 | 合成训练对不是单独创新；其跨图配对能力也不能自动假定为本研究单视频数据所具有。 |

上述 2026 年 8–9 月编号在当前日期之前，且本次均成功打开主源。初稿不把第三方性能数字抄作本研究证据。

## 模型、工具与数据候选

| 资源 | 主源 | 当前可确认 | 启动实验前仍必须核验 |
|---|---|---|---|
| Concat-ID | [官方仓库](https://github.com/ML-GSAI/Concat-ID)、[论文](https://arxiv.org/abs/2503.14151) | README 有 Wan2.1-T2V-1.3B、AdaLN 及训练/推理脚本。 | 当前 commit、依赖版本、checkpoint 许可、VAE/时间步/参考 token/生成 mask；README 可运行示例不保证本实验兼容。 |
| Wan2.1 | [官方仓库](https://github.com/Wan-Video/Wan2.1)、[报告](https://arxiv.org/abs/2503.20314) | 提供开放视频生成模型及 1.3B 方案。 | 参数化/shift/CFG、相同 scheduler 原生接口、权重 checksum、实测完整训练成本。不得以推理显存估算训练需求。 |
| ConsisID | [官方仓库](https://github.com/PKU-YuanGroup/ConsisID) | README 提供 training 与 evaluation 指南、脚本和权重。 | CogVideoX 版本、具体 checkpoint、输入对齐、第二平台自己生成的配对数据。 |
| VBench | [官方仓库](https://github.com/Vchitect/VBench)、[CVPR 2024](https://openaccess.thecvf.com/content/CVPR2024/html/Huang_VBench_Comprehensive_Benchmark_Suite_for_Video_Generative_Models_CVPR_2024_paper.html) | 分维度视频评价；仓库当前包含多个后续版本。 | 锁定具体版本、自定义视频支持维度、clip 长度/采样/聚合配置；不得把主体一致性当参考人物身份正确率。 |
| AdaFace | [官方仓库](https://github.com/mk-minchul/AdaFace)、[CVPR 2022](https://openaccess.thecvf.com/content/CVPR2022/html/Kim_AdaFace_Quality_Adaptive_Margin_for_Face_Recognition_CVPR_2022_paper.html) | 官方实现说明 BGR、112×112 对齐输入及相应归一化。 | 具体权重许可/版本、独立于训练识别器、阈值开发集校准；不要通用地假定所有人脸模型相同 RGB 预处理。 |
| CelebV-HQ | [官方仓库](https://github.com/CelebV-HQ/CelebV-HQ) | 视频人脸数据候选与使用条款。 | 原始视频可用性、用途许可、人物/近重复分簇；不能把公开 clip 元数据视为完整身份标签。 |
| FFHQ | [官方仓库](https://github.com/NVlabs/ffhq-dataset) | 数据说明及逐图来源/许可元数据。 | 外部测试身份聚类、逐项许可、去重、是否许可使用/发布派生结果；不能假定每张图都是不同人物。 |
| ControlNet | [论文](https://arxiv.org/abs/2302.05543)、[作者仓库](https://github.com/lllyasviel/ControlNet) | 空间条件控制方法，可作为边缘条件第二任务候选。 | 与老师同一基础权重、具体 checkpoint/scheduler、软边缘可微链与独立硬边缘评价。 |

## ICML 年份与规则

目标年份未由用户确定。2026-10-26 本次访问 [ICML 2027](https://icml.cc/Conferences/2027) 未能获取可核验内容；定向查找也未得到可确认的 2027 CFP。此结果只表示本次未核实，不证明官方尚未发布。

已核实的 [ICML 2026 CFP](https://icml.cc/Conferences/2026/CallForPapers) 要求主文 8 页，参考文献、impact statement、附录不计入主文页数，并要求 impact statement。**仅供历史规划参考，不能当成 2027 规定或截止日期。** `paper/icml2026_reference/` 完整保留本地技能所带的 2026 模板，不修改样式文件；正式投稿前必须从目标年份官网重新下载并检查。

## 引用范围和未完成工作

本次核验聚焦用户给出的关键来源及实验依赖，不是系统性文献综述。四个最近工作都可确认，不代表没有更近/更同构方法。初稿明确保留 `[CITATION NEEDED]` 的 novelty 扩展检索项，详见 `PENDING_VERIFICATION.md`。每项拟使用的论文结论、基线实现以及 license 必须进入结构化审计，不能由“页面存在”升级为“已复现”。


## 三任务修订

正式范围新增T2 Canny与T3人体姿态条件图像。已打开核对ControlNet1.1作者仓库和Canny/OpenPose作者模型卡：两者均给出SD1.5使用方案。HRNet官方仓库提供PyTorch姿态热图网络；其完整推理后处理不能直接假定可微。精确revision/权重兼容、梯度、许可和运行效果仍待W0实测。本次不新增未经抓取的BibTeX，论文以已核验ControlNet引用和官方模型卡脚注支持候选选择。
