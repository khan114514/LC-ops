---
name: cdist-paper
description: Draft and revise an ICML-oriented paper from audited conditional diffusion distillation evidence, with strict separation between plans and measured claims.
---

# Evidence-grounded ICML drafting

方法范围：先读 [方法搜索与选择](../../specs/method_search_and_selection.md) 和当前候选/选定协议。本文涉及的OPD、H/O/C、投影/局部轨迹是初始家族要求，不是所有候选必用算法；其它路线按其冻结定义与控制执行，共同证据边界不变。

Use for the manuscript, figure narrative, results integration, appendix or submission readiness. Resolve `PROJECT_ROOT` from the supplied bundle path or an ancestor with `paper/README.md`; do not assume an installed skill resides in the project. Read `paper/README.md`, the research specification, literature audit and evidence manifest.

If available, read the bundled `vendor/skills/ml-paper-writing/SKILL.md`. This project authorizes drafting a concrete reviewable manuscript without a separate pre-draft permission round. Draft now with explicit framing assumptions; ask only for a necessary unresolved scientific decision after making independent progress.

1. Begin in `DRAFT v0 — no empirical results` unless verified experiment records justify another state. All unrun experiments, datasets and scales are planned/pending. Do not write “we demonstrate”, performance deltas, p-values, acceptance claims or completed human-study statements without traceable evidence.
2. Frame the candidate contribution as diagnosing and mitigating teacher/student added-condition conflict and separately testing hybrid states. Do not claim first synthetic pairs, first hybrid rollout, first projection or a global condition-preservation guarantee.
3. Read `paper/results_requirements.md` before integrating any metric. Every numerical manuscript value must map to immutable run config/code/data/checkpoint/evaluator hashes, all seeds, full-denominator failures, paired output IDs and aggregation code. Never copy third-party scores into this project's result tables.
4. Keep a mathematical scope check: projection is onto a linearized proxy non-increase halfspace; finite checks constrain the constructed target only. Detached targets do not guarantee the trained model or deployed video. Distinguish oracle labels for re-noised endpoints from fresh rollout states. Check epsilon/VP-v/flow-v conversions and singular endpoints.
5. Use all necessary sections: abstract, introduction, related work, method and algorithm, experiments, limitations, impact statement, conclusion and appendices. Before results, use a planned-experiments section and `PENDING` tables. Include C-H/C-O, weak-KD, random gating and condition-only controls; report equal updates and equal measured compute.
6. Use only verified citations; retain `[CITATION NEEDED]` gaps visibly. Read `literature/PENDING_VERIFICATION.md`; do not delete novelty gaps to improve appearance.
7. Copy complete official target-year template before final formatting and never edit style files. Bundled ICML 2026 styles are a reference, not a 2027 compliance claim. Confirm target-year author rules, anonymization, impact and AI disclosure, page count, attachments and deadlines from official primary sources.
8. Render/compile, inspect equations, line breaks, table widths, bibliography and all figure panels. Use vector plots generated from actual data; no synthetic illustrative plot may look like an experimental result. Preserve an editable source and document any unavailable compiler.

Deliver the revised TeX/PDF (if compilation available), a readable draft, claim-to-evidence matrix, citation gaps and readiness status. In negative or null findings, narrow conclusions according to the preregistered decision rules rather than hiding the result.


三任务范围：读取 [任务契约](../../specs/three_task_protocol.md)，按assignment.task_id选择T1身份视频、T2 Canny图像、T3人体姿态图像的独立数据、代理、指标、gate与预算；新run使用runs/<task_id>/<run_id>/。本技能原有视频/身份细节仅用于T1，不能强加给T2/T3。三者都是正式研究范围；负结果需保留，未执行不能声称三任务实验完成，可选第二视频架构不是第4个主任务。
