# 待核验队列

优先级排序，不因计划需要而预判结论。

1. **最近邻完整检索（阻塞 novelty claim）**：截至实际开跑/投稿日期检索 conditional distillation、constraint-aware distillation、teacher–student condition mismatch、hybrid/on-policy diffusion distillation、gradient surgery for generative control、personalization distillation。保存主源、检索词、日期、纳入/排除理由；特别补查 D-OPSD/最新同类方法。对每个最近邻读方法与附录，不只读摘要。当前初稿的 `[CITATION NEEDED]` 对应此项。
2. **四个关键近邻的代码级对照**：固定 CoDi/HPSD/PDMD/DiffusionOPSD 的 version/commit，列出状态来源、老师条件、冻结/EMA、目标空间、约束方向、stop-gradient、是否加速。H0 只称本项目原始目标对照。若改造官方方法，列出所有改动。
3. **基础模型兼容证明**：Concat-ID-Wan-AdaLN 与 Wan2.1 老师是否共享可比较生成 latent；调度器时间约定、flow/VP 参数化、参考 token 的 mask。提供一次同状态预测转换的数值检查。
4. **许可与 checkpoint 清单**：代码、基础模型、身份权重、数据、派生内容逐项核验。仓库 README 与代码 license 不替代 checkpoint license。不能把外部许可限制自动升级为需用户审批的泛化流程。
5. **身份测量有效性**：训练识别器可微实现及其权重来源；AdaFace 官方 BGR 对齐验证；跨身份错误、检测失败、背脸恢复、人口组分布与阈值校准。以盲审人工评价验证代理。
6. **数据身份与近重复**：不能默认 FFHQ 逐图唯一或 CelebV-HQ 元数据包含可靠完整身份 ID；冻结实际簇与审计样本。
7. **ICML 目标年份**：先记录用户选择/合理工作假设，再从该年份官网核验 CFP、样式、匿名规则、impact/LLM 披露、正文长度、补充材料及截止日期。不得将 2026 CFP 当 2027 要求。
8. **BibTeX 更新与 venue**：已下载 arXiv 条目可用；投稿前有正式 proceedings 的换成主源程序获取条目，保留版本映射。本次引文不从记忆补全作者或 DOI。

每项完成后写 source ledger：`id, title, primary_url, secondary_authoritative_url, accessed_at, version, metadata_path, supported_claim, unsupported_extrapolation, status, reviewer`。不可访问写 `unverified`，不得写“论文不存在”。
