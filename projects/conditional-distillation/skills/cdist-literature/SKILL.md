---
name: cdist-literature
description: Verify primary literature, source claims, code releases and novelty boundaries for condition-preserving diffusion distillation; maintain a portable citation audit.
---

# Conditional distillation literature audit

方法范围：先读 [方法搜索与选择](../../specs/method_search_and_selection.md) 和当前候选/选定协议。本文涉及的OPD、H/O/C、投影/局部轨迹是初始家族要求，不是所有候选必用算法；其它路线按其冻结定义与控制执行，共同证据边界不变。

Use for this project's literature task, closest-work comparison or citation refresh. Find `PROJECT_ROOT` from the supplied bundle path or an ancestor containing `literature/SOURCE_AUDIT.md`; do not assume this skill's installation directory is the research repository. Read the root research specification and literature ledger before browsing.

1. Read `literature/SOURCE_AUDIT.md`, `literature/PENDING_VERIFICATION.md`, and any new evidence. Verify current date and the actual target ICML year. An inaccessible source is unverified, not nonexistent.
2. Search primary sources. Open arXiv/full paper, official proceedings, author project/repo. Fetch BibTeX programmatically from arXiv/DOI/proceedings/official README; save the raw entry and retrieval URL/date. Never fill authors, results or DOIs from memory. Use a second authoritative source when available; record the exact evidence level.
3. For every proposed contribution, compare teacher condition set, state source, query noise, target parameterization, gradient path, teacher update (frozen/EMA), constraints and deployment. HPSD already has teacher anchors plus student local rollout; PDMD already projects distillation updates; CoDi already handles additional conditions; DSD already synthesizes paired data; DiffusionOPSD already constructs detached bounded targets. None of these establishes or refutes this project's empirical hypotheses by itself.
4. Keep supported factual claims separate from interpretation, implementation compatibility and reproduced results. Paper reading does not authorize writing a completed-result claim. Modified baselines must be named adapted controls and enumerate deviations.
5. Update the ledger, `verified_references.bib`, pending queue and a short novelty risk memo. For missing material, report `[CITATION NEEDED: specific gap]` with its evidence to the orchestrator and paper owner, who owns manuscript edits; the literature worker must not modify `paper/` outside its assignment. Never fabricate a plausible citation.
6. Refresh during the project at safe boundaries and once before submission. Verify the target year's official ICML requirements; 2026 is historical reference only.

Deliver `literature/SOURCE_AUDIT.md`, a machine-readable source ledger, verified bibliography/raw provenance and a gap list. No training, model choice changes, paid API calls or external messages are required by this skill.
