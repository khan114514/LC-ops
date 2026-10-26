# 数据、划分与参考条件协议

当前方法范围以 [方法搜索与选择](method_search_and_selection.md) 为准：问题固定，算法开放。本文OPD、H/O/C、投影和局部轨迹描述初始候选家族；原experiment_matrix.csv是该家族模板。其它候选的专用步骤/机制门/控制由selected_method和active_experiment_matrix定义，数据隔离、公平预算、独立部署及证据真实性等共同要求保留。

三任务范围修订：正式任务为T1身份视频、T2 Canny图像、T3人体姿态图像，见 [three_task_protocol.md](three_task_protocol.md)。本文件原有视频/身份/帧数和40,000视频细节描述T1；图像任务按三任务契约执行，不能套用人脸检测或按视频身份分组来评图像边缘/姿态。

状态：待执行；下列规模为过滤后的有效量建议。数据版本冻结后生成不可变 manifest 与 SHA，不以目录文件数代替样本、身份或视频数。

## 数据角色与规模建议

| 数据角色 | 建议量 | 用途 |
|---|---:|---|
| synthetic-smoke-train / dev | 128 / 32 个完整老师视频 | 闭环、过拟合与梯度检查 |
| synthetic-train | 8,192 个完整老师视频 | 正式训练，嵌套 512⊂2,048⊂8,192 |
| synthetic-dev | 256 个完整老师视频 | checkpoint 与超参数选择 |
| synthetic-mechanism-test | 256 个完整老师视频 | 冻结机制确认，不参与调参 |
| external-dev-A / B | 每域 32 身份簇 | 校准阈值、生成设置与非劣界 |
| external-test-A / B | 每域 100 身份簇 | 主外部测试，身份×4文本×2生成seed |
| cross-platform-train | 第二老师独立产生，先 2,048 个有效视频 | 跨平台流程验证 |
| canny-train / dev / external-test | 8,192 / 512 / 500 张 | 第二条件任务，按自身许可与去重冻结 |

一个完整老师视频为训练独立基本单元；同视频多个脸裁剪、窗口、多次加噪、多个 seed augmentation 不能计为更多独立身份或视频。实际帧数、分辨率、fps、时长、压缩方式待模型与预算核验后写入 `data_version`。

## 老师数据构建

1. 固定可获得且许可可用的老师 checkpoint、VAE、scheduler、CFG、negative prompt、文本模板与生成 seed。先做单人、近景/半身、基础动作，再增加姿态、背景与光照。
2. 保存完整视频及原始生成元数据，失败尝试也有 ID。每批统计候选数、有效数、重复数与原因分布。
3. 自动检查解码、帧数、尺寸/fps、单主要人物、切镜/人物替换、跨帧身份、动作完成、静止重复、脸/手/时序伪影。动作判定不能只用同一个训练身份特征器。
4. 按动作、姿态和质量分层人工核验至少 100 条的建议样本；记录抽样规则、评者与一致性。过滤阈值在开发阶段固定，不通过测试集反调。
5. 每个候选只给一个主排除原因，同时可有多项 secondary flags；按原始 ID 保留完整过滤日志。预算按实际接受率 `Nraw≈Neffective/r` 计算。

老师训练数据的质量、动作分布和身份分布需报告；未经身份核验的两条老师视频不能当成同一人的多动作训练对。所有方法共享同一冻结数据版本和嵌套采样顺序，不能为 H2 清洗更多数据。

## 条件提取与防复制

优先选择目标时间窗口之外的清晰参考帧；参考与目标视频分别编码，防止视频 VAE 将目标时间上下文泄漏进条件。每视频可存 2–3 张候选，一次更新只选一张，并在整条 local rollout 固定。保存 reference-frame index、target-window indices 和两个编码路径。

若无窗口外参考，显式标记 `reference_overlap=true`；重叠帧排除身份 loss 与相应生成区域评分，并单独做同帧/窗口外消融。不能只删除不利输出帧。评估复制捷径需同时观察静止/重复率、动作完成、参考条件替换、噪声替换与时间变化。

首帧 I2V 固定区域不计身份或生成视频评分；参考 token 不混入 latent KD；是否存在时序下采样跨固定区域污染，要按 VAE 的实际 receptive field 验证并记录 mask 映射。

## 划分与去重

以原始视频、来源 URL/ID、身份簇和近重复连通分量联合分组，先去重分组再划分。一个分组不可跨 train/dev/test；从同一视频抽的所有窗口与参考归属同组。外部 dev/test 按身份簇互斥，不把一图默认一身份。合成 train/dev/mechanism-test 同样按视频/身份簇/近重复分组。

近重复检测至少覆盖精确 hash、感知图像/视频相似度及身份近邻核验，阈值从开发数据校准；边界样本人工复核。身份相似不等于必然同人，需保留人工判定与未知状态。无法确认的跨划分冲突先隔离，不把不确定身份写成严格未见。

CelebV-HQ 与 FFHQ 是候选外部来源；实际下载前核验当前来源、研究/再分发条件、逐图许可与元数据。不得把公开可下载当成可无条件打包分发。发布清单、处理/下载脚本、过滤规则、种子和必要来源信息；原始文件只按许可发布。这里“未见身份”仅指未参与本次蒸馏训练和调参，不声称基础预训练从未见过。

## Manifest 最小字段

每条源资产：`sample_id,source_id,source_uri,source_dataset,license_ref,source_sha256,teacher_checkpoint_sha,teacher_generation_config_sha,prompt_id,prompt_text,teacher_seed,video_sha256,identity_cluster_id,duplicate_group_id,split,data_version,status,filter_reason,filter_flags,reference_candidates,target_window,reference_overlap`。

训练采样派生条目额外含 `parent_sample_id,reference_choice,noise_seed,timestep,alpha,sigma,scheduler_version,generation_mask_sha`，但不增加独立样本量。外部测试条目额外含 `domain,identity_id,reference_asset_sha,prompt_id,inference_seed,case_id`，一条 case 表示一个预定输出槽位。

冻结材料包括 manifest、来源/许可索引、划分脚本与参数、过滤阈值、人工抽查记录、去重审查、嵌套子集 ID、文本列表。仅报告计数与 ID 不等同于发布受限原始视频。

## 数据门槛

在正式训练前确认：数量可复算；无跨 split 的已知视频/身份/近重复分组；参考窗口可复核；失败与排除原因不丢失；许可状态足以支持实际使用；按方法共用版本。若合法访问方式或所需 checkpoint 尚未获得，将状态写 `blocked` 并继续可做的模拟与文献工作，不伪造数据路径。
