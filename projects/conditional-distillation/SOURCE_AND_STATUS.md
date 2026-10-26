# 来源、状态和授权

唯一用户研究材料是 `source/original_research_plan_zh.txt`。内容原样保留；原文中的旧 sandbox 文档链接不是本包实际拥有的附件。本次仅编写交接材料并进行文献/结构/脚本/论文排版检查，未执行实验。

专用研究技能和流程为本次编写；可选上游技能保留 `UPSTREAM.json` 和 `UPSTREAM-LICENSE`。没有复制任何 Ark 配置、API key、SSH key、模型权重或人脸数据。

Codex 使用依据：

- [Skills 概念](https://developers.openai.com/plugins/concepts/skills)：SKILL.md 与支持资源、按任务加载。
- [长任务与外部状态](https://developers.openai.com/blog/run-long-horizon-tasks-with-codex)：使用文件和可验证循环维持长期工作。
- [仓库技能实践](https://developers.openai.com/blog/skills-agents-sdk)：`.agents/skills` 项目技能目录实例。
- [工作流与 skill 创建](https://developers.openai.com/cookbook/examples/codex/iterating-development-workflows-with-codex)：不同宿主目录和工作流的参考。

以上于 2026-10-26 访问。桌面聊天创建/等待/发消息操作按运行时实际工具 schema 使用，不从网页文档假定每个接收者都拥有相同工具。没有这些能力时使用 subagent 或手工聊天入口。


三任务修订：本轮新增T2 Canny图像、T3人体姿态图像的正式研究定义与派工提示，同步原T1视频研究。没有实际生成图像/视频或启动训练。原始source文本保持不变；扩展内容由three_task_protocol.md显式维护，不伪称来自原文。
