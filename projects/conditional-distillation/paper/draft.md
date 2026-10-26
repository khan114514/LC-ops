# Condition-Preserving Distillation from a Teacher without the Student's Reference Condition

**DRAFT v0 — October 26, 2026. Research plan; no empirical results.**

Reading copy generated from `main.tex`; TeX is authoritative for equations and formatting. Target ICML year is unconfirmed.

## Abstract
We propose to study diffusion distillation when a frozen teacher lacks an additional condition required by its student. The mandatory research scope comprises three tasks: reference-identity video generation (T1), Canny-edge-conditioned image generation (T2), and human-pose-conditioned image generation (T3). In every task, a condition extracted from a teacher sample creates paired data, but a later teacher prediction at a student-visited state need not preserve that condition. We formulate a local target construction that projects conflicting teacher directions against a differentiable condition-error gradient, limits their magnitude, and checks candidate targets with the actual proxy. We combine it with a teacher step followed by a short student rollout and require matched controls, independent condition evaluation, and separate gates for every task. This draft is a falsifiable protocol with no empirical results; task-specific negative outcomes must remain visible, and no cross-task success or efficiency claim is established.

## Introduction

A conditional student may have a capability that its proposed teacher does not expose. An identity video student receives a reference face, an edge-conditioned image student receives a Canny map, and a pose-conditioned image student receives a rendered skeleton; their teachers receive the shared text alone. Transferring a teacher's generation prior is attractive, but direct prediction matching can conflict with the student's additional condition. The teacher is not unconditional in the absolute sense: throughout this paper, it lacks only that *additional condition*, and still receives the text.

We construct paired data uniformly as $c=h(x_0^T)$ from a text-conditioned teacher sample. T1 extracts an identity reference outside the target video window; T2 extracts Canny edges from a teacher image; T3 estimates human keypoints offline and renders them with a locked pose renderer. This avoids asking a teacher to obey an externally imposed condition during pair generation. It does not make that teacher condition-aware at later noisy queries. A second design choice starts from a teacher-informed state, lets the student evolve locally, and queries supervision there. This changes where distillation occurs while leaving the compatibility of supervision unresolved.

These ingredients have substantial precedents. CoDi studies additional conditioning and conditional distillation ([codi](https://arxiv.org/abs/2310.01407)); Diffusion Self-Distillation constructs synthetic pairs for reference-conditioned generation ([dsd](https://arxiv.org/abs/2411.18616)). HPSD explicitly combines teacher trajectory anchors with student local rollouts ([hpsd](https://arxiv.org/abs/2608.13205)). We therefore do not claim novelty for synthetic pairs or hybrid trajectories alone. Our candidate research contribution is the diagnosis and controlled mitigation of a condition mismatch in the opposite direction from HPSD: the teacher lacks a condition the student must retain.

We test three hypotheses separately in each of the three mandatory tasks. **A:** at some relevant states, a teacher intervention improves final quality while degrading added-condition fidelity. **B:** correcting conflicting teacher targets improves the quality--control tradeoff beyond paired-data training, online condition losses, gating, or weaker distillation. **C:** hybrid states add value beyond corrected targets on full student trajectories, in quality or measured compute. Each hypothesis may be rejected per task. A negative or blocked task stays in the scope and result ledger with its evidence; it cannot be silently removed. The planned contributions are a same-query diagnostic, a bounded and checked target construction, and a three-task attribution protocol. None is an established empirical finding.

## Related Work and Novelty Boundaries

**Conditional adaptation and synthetic supervision.** 
ControlNet adds spatial controls to pretrained image diffusion models ([controlnet](https://arxiv.org/abs/2302.05543)). CoDi adapts pretrained diffusion models to new image conditions while distilling them ([codi](https://arxiv.org/abs/2310.01407)). Diffusion Self-Distillation generates and curates paired images before learning reference-conditioned generation ([dsd](https://arxiv.org/abs/2411.18616)). Our T1 single-video construction supplies a consistent reference and target window, but does not automatically supply verified cross-video pairs of the same person performing different actions. T2 and T3 instead extract spatial conditions from each generated image; sharing an extraction rule does not establish that a student preserves the condition on external deployment inputs.

**Distillation on hybrid states.** 
HPSD uses a teacher with privileged first-frame and text conditions and a student in base text-to-video mode. Teacher trajectory anchors are evolved by the student before velocity supervision, and the teacher is updated with an exponential moving average ([hpsd](https://arxiv.org/abs/2608.13205)). We instead freeze a teacher without the student's additional condition and explicitly test condition conflict in all three tasks. Our H0 and O0 controls are adapted state/target controls, not reproductions of official HPSD results. Any eventual comparison to HPSD must enumerate conditioning, teacher-update, and architectural changes.

**Projected updates and detached targets.** 
PDMD projects distribution-matching updates along a student--critic endpoint residual to filter critic error ([pdmd](https://arxiv.org/abs/2609.35768)). Our direction is a condition-error gradient and our constraint concerns the student's additional control. DiffusionOPSD constructs bounded, detached clean-output targets from reward gradients and separates target construction from finite fitting ([diffusionopsd](https://arxiv.org/abs/2608.24646)). We adopt this distinction in the evaluation protocol; neither projection nor stop-gradient supervision is itself a novelty claim. **[CITATION NEEDED: complete closest-work search on condition-aware distillation, gradient surgery, and recent on-policy personalization before asserting novelty]**.

**Task models and measurement.** 
Concat-ID ([concatid](https://arxiv.org/abs/2503.14151)) and Wan ([wan](https://arxiv.org/abs/2503.20314)) are the T1 candidates; ConsisID ([consisid](https://github.com/PKU-YuanGroup/ConsisID)) is an optional video architecture extension. VBench offers video-quality dimensions ([vbench](https://openaccess.thecvf.com/content/CVPR2024/html/Huang_VBench_Comprehensive_Benchmark_Suite_for_Video_Generative_Models_CVPR_2024_paper.html)); these do not replace reference-identity comparison. AdaFace ([adaface](https://openaccess.thecvf.com/content/CVPR2022/html/Kim_AdaFace_Quality_Adaptive_Margin_for_Face_Recognition_CVPR_2022_paper.html)) is a candidate independent T1 evaluator. T2 and T3 use the same Stable Diffusion 1.5 (SD1.5) text-only teacher and the corresponding ControlNet 1.1 Canny and OpenPose students. (Footnote: Official Canny model card: [source](https://huggingface.co/lllyasviel/control_v11p_sd15_canny). Official OpenPose model card: [source](https://huggingface.co/lllyasviel/control_v11p_sd15_openpose). Checkpoint revisions and exact inference pipelines must be locked before execution.} These two spatial controls are distinct tasks on a shared base architecture, not evidence from two independent architectures. Availability, compatible latent semantics, and successful execution remain separate questions for every compatibility gate.

## Problem and Proposed Method

### Models, data, and prediction space

Let $b$ be a shared text prompt, $c$ an additional condition, and $z_t$ a noisy image or video latent. For each task, a frozen teacher is $T(z_t,t,b)$ and a trainable student is $S_\theta(z_t,t,b,c)$, initialized from an existing condition-capable model $S_0$. Models and training runs are task-specific; the shared notation does not imply joint training or shared checkpoints. We do not assume the teacher is a quality upper bound on conditional generation.

In all tasks, sample $x_0^T\sim p_T(x\mid b)$ and set $c=h(x_0^T)$. For T1, $h$ extracts an identity reference from outside the target window and $y_0=\operatorname{Enc}(x_0^{T,\mathrm{target}})$ encodes the disjoint video window. The reference is separately encoded. If an overlap is unavoidable, exclude the corresponding generated frame from condition losses and evaluation, and report that case in a separate ablation. For T2, $h$ is a locked Canny extraction pipeline and $y_0=\operatorname{Enc}(x_0^T)$. For T3, $h$ consists of offline keypoint estimation plus a locked skeleton renderer, again with $y_0=\operatorname{Enc}(x_0^T)$. The extracted condition stays fixed throughout a local trajectory; offline extraction is separate from the differentiable training proxy.

Teacher and student predictions are mapped to a common clean-latent space, denoted $y_T$ and $y_S$. Let $M$ select generated coordinates; reference tokens and fixed input regions are excluded. All following vectors, dot products, and norms are defined on these generated coordinates with other coordinates held fixed. Implementations must record normalization so that a trust radius is comparable across resolutions.

### Paired supervision and hybrid query construction

The paired branch independently samples noise,

$$
z_t^{\mathrm{pair}}=\alpha_t y_0+\sigma_t\epsilon,
 \qquad \epsilon\sim\mathcal N(0,I),
$$

and uses the model's standard diffusion or flow training label. The noise is independent of the original teacher generation seed.

For the local branch, first sample a final query time $t_q$ from a development-fixed distribution. Choose a predecessor schedule with enough steps for one teacher transition and $k$ student transitions to end at $t_q$. Independently re-noise $y_0$ at the start time, take one teacher step, then $k$ student steps using $b,c$. The default planned value is $k=1$. Stop gradients through all state construction. Query both models at the terminal state $z_{t_q}^{H}$. Selecting $t_q$ first keeps the supervision noise distribution matched across $k=0,1,3$ and across state-source controls. It does not make the state distributions identical; changing those distributions is the intended intervention.

Full-student controls start from fresh noise and follow the student to the same final query-time distribution. A separate $T\!\to\!S$ versus $S\!\to\!S$ control keeps transition count and query time matched. A re-noised endpoint followed by one teacher step is not identical to a cached full teacher trajectory anchor; we will record this distinction when comparing to HPSD.

### Condition error and target construction

The general task-specific condition error is

$$
E_c(y)=D\!\left(F_{\mathrm{train}}(\operatorname{Dec}(y)),\rho(c)\right),
$$

where $F_{\mathrm{train}}$ is frozen but differentiable with respect to its input, $\rho$ expresses the fixed condition in the proxy's coordinate system, and $D$ is a preregistered discrepancy. The VAE inverse scaling, resize and normalization belong to the gradient path. The training proxy and deployment evaluator are separate objects, with versions and weights fixed before testing.

For **T1 identity control**, the specialization is

$$
E_c^{\mathrm{T1}}(y)=\frac{1}{|\mathcal F|}\sum_{f\in\mathcal F}
 \left[1-\left\langle \overline{F_{\mathrm{train}}(A_f(\operatorname{Dec}(y)))},
 \overline{F_{\mathrm{train}}(c)}\right\rangle\right].
$$

Bars denote normalized face features and $A_f$ is a differentiable crop/resize on a chosen generated frame. Valid regions and crop coordinates follow a fixed rule and remain fixed within target construction and its checks. Invalid faces or unreliable crops cause a logged local-KD rejection while valid paired supervision remains active.

For **T2 edge control**, a fixed differentiable soft-edge operator is compared with the Canny condition in a locked resolution and coordinate system. Hard Canny, thresholding and discrete matching do not lie on the training-gradient path. Deployment fidelity is measured independently with fixed hard-edge F1 and symmetric Chamfer distance, including the declared empty-edge and failed-output policies. These hard-edge metrics are not replaced by the optimized soft-edge error.

For **T3 pose control**, use a frozen differentiable PyTorch pose network, comparing its heatmaps or soft-argmax joint coordinates with targets derived from the stored keypoints. Preserve gradients through decoding, resize, network activations and the soft coordinate readout; NumPy, ONNX and hard argmax must not sever this path. Before generating data, lock the COCO-17/OpenPose-18 joint schemas, left/right ordering, missing/visibility masks, coordinate scaling, neck construction from the two shoulders, and conversion rules. The independent evaluation pose estimator must use a different model and weights from the training proxy. Evaluate PCK and OKS with preregistered scales, visibility rules and the same locked joint mapping; detections and joint failures remain in the full planned sample/joint denominators. Do not translate a generated torso, warp outputs or otherwise force body position in postprocessing to make the condition pass.

Frozen weights do not mean disabling activation gradients. Nonfinite gradients, invalid proxies or empty valid masks reject local KD and are counted. A task proceeds past its proxy gate only after a real-model batch demonstrates finite, meaningful input gradients and checked-target behavior; this does not certify the independent evaluator or final generation.

The conceptual constrained target is

$$
\begin{aligned}
\min_y\quad &\|y-y_T\|_2^2,\\
 \text{subject to}\quad&E_c(y)\le E_c(\operatorname{sg}(y_S))+\delta,\\
 &\|y-\operatorname{sg}(y_S)\|_2\le r,
\end{aligned}
$$

with $\delta\ge0$ and $r\ge0$. This is generally nonconvex; our practical construction does not claim to solve it globally.

Let $\bar y_S=\operatorname{sg}(y_S)$, $d_0=y_T-\bar y_S$, and $g=\nabla_y E_c(\bar y_S)$. For a reliable finite gradient with $\|g\|_2^2>\varepsilon_g$, compute

$$
d_{\perp}=d_0-
 \frac{\max(0,g^\top d_0)}{\|g\|_2^2}\,g,
 \qquad
 d_r=d_{\perp}\min\left(1,\frac{r}{\|d_{\perp}\|_2}\right).
$$

The zero-direction case is handled explicitly without division. If the finite gradient instead satisfies $\|g\|_2^2\le\varepsilon_g$, use the radius-clipped raw direction $d_0$ and still perform the same actual-proxy backtracking checks; accept only a checked target and log \texttt{zero\_grad\_checked}. Invalid proxy evaluations, nonfinite gradients or empty generated masks are rejected, rather than treated as zero gradients. The halfspace $g^\top d\le0$ is stricter than using all of the positive tolerance $\delta$ in a linearized constraint. It is a simple conservative starting design, not an optimal tolerance-aware solver.

Test step sizes $a\in\{1,1/2,1/4\}$ in decreasing order using the actual fixed proxy. Choose the largest satisfying

$$
E_c(\bar y_S+a d_r)\le E_c(\bar y_S)+\delta,
 \qquad \|a d_r\|_2\le r.
$$

Set $y^*=\operatorname{sg}(\bar y_S+a d_r)$ for accepted samples. Otherwise skip local KD and log the rejection. We do not turn a rejected nonzero target into a fabricated successful example. The paired and common condition branches remain active.

### Losses and scope of the guarantee

Let $\Psi_t(y;z_t)$ convert a clean target back into the model's native prediction space. The local loss is

$$
\mathcal L_{\mathrm{KD}}=
 \frac{\sum_i A_i w(t_i)\|M[S_\theta(z_i,t_i,b_i,c_i)-\Psi_{t_i}(y_i^*;z_i)]\|_2^2}
 {B},
$$

where $A_i$ indicates acceptance and $B$ is the full batch size, fixed across methods. Rejected samples have zero KD weight; the denominator does not shrink with acceptance. Conditional-on-acceptance loss is diagnostic only. Report acceptance rates and realized KD gradient norms so that exposure and dose remain visible. The total objective is

$$
\mathcal L=\mathcal L_{\mathrm{pair}}+
 \lambda_c\mathcal L_{\mathrm{cond}}+
 \lambda_{\mathrm{KD}}\mathcal L_{\mathrm{KD}}.
$$

The common condition loss uses paired predictions and, for online-state methods, their query predictions under a fixed relative weight. H0/H1/H2 and C-H share the hybrid-state construction protocol and common-loss definition; O0/O1 and C-O share the full-student-state construction protocol and common-loss definition. Each trained method rolls out its own current student, so their numerical states need not coincide; exactly shared cached states are used only in fixed-state diagnostics. Removing KD must not remove or add query-condition supervision. All trainable modules and tuning budgets are matched.

**Local mathematical statement.** 
For nonzero $g$, Equation (eq:projection) before radius clipping is the Euclidean projection of $d_0$ onto $\{d:g^\top d\le0\}$. Thus $g^\top d_{\perp}\le0$ and clipping preserves this inequality. If $E_c$ has $L$-Lipschitz gradient along the candidate segment, the descent lemma gives

$$
E_c(\bar y_S+a d_r)\le E_c(\bar y_S)+
 a g^\top d_r+\tfrac{L}{2}a^2\|d_r\|_2^2.
$$

The second-order term can be positive, especially for tangent directions. This is why a finite proxy check is necessary. For an accepted target, Equation (eq:check) holds by construction under the fixed proxy and its numerical tolerance. This statement concerns *the constructed target only*. It does not guarantee true identity, edge or pose fidelity, post-update predictions, deployed outputs, global quality, or a globally optimal solution to Equation (eq:ideal).

### Training algorithm

1. Within one task, sample a teacher unit, its fixed extracted condition, independent paired noise, and a terminal query time. Compute the paired branch.

1. Construct the detached teacher-step/student-rollout state ending at that query time. Obtain frozen teacher output and live student output; convert both to clean generated latents.

1. Create a detached student anchor that requires gradients only for target construction. Evaluate the frozen differentiable condition chain, validate the gradient, project and clip the teacher direction (or use the checked finite near-zero-gradient fallback), then check candidate step sizes. Reject invalid proxy or nonfinite-gradient samples and log the reason.

1. Detach an accepted target and map it into native prediction coordinates at the *current query*. Apply local KD plus the matched common condition losses; update only the authorized student parameters.

1. Log query noise, validity, conflict, target movement, acceptance, step size, loss components, gradient norms, latency and memory. Save the immutable run record.

The original noise used before rollout is not a correct native training label at the evolved state. No second-order gradient through target construction or backpropagation through the rollout is required.

## Planned Experiments

### Three mandatory tasks and separate gates

T1 uses the candidate Wan2.1-T2V-1.3B teacher and Concat-ID-Wan-AdaLN student. T2 uses a text-only SD1.5 teacher and its ControlNet 1.1 Canny student; T3 uses the same text-only base teacher and its ControlNet 1.1 OpenPose student. Exact base-model compatibility, ControlNet revisions and conditioning pipelines must be locked from actual checkpoints. T2 and T3 provide two controls on one image architecture. A compatible CogVideoX/ConsisID pair is an optional architecture extension within T1, not a fourth main task or a replacement for T2/T3. A fixed-first-frame I2V experiment cannot substitute for reference identity, edge or pose control.

Every task is mandatory in the research scope, launch specification and final report. Each has its own W0 compatibility/proxy gate, teacher-value/conflict gate, compute budget, development selection and result block. A failed or inconclusive gate is a reportable negative or blocked outcome with attempted runs and reasons; it never licenses quietly deleting the task. A positive T1 result does not clear a T2/T3 gate, and a shared SD1.5 base does not establish independent architecture replication.

W0 must demonstrate matching VAE coordinates, time conventions, scheduler semantics, prediction conversions and generated-region masks, plus finite input gradients through the task proxy on a real-model batch. Profile five warm-up and twenty full updates per task including decoding, condition gradients and all target checks, then profile complete student-only deployment generations. T3 additionally locks joint-schema conversion, renderer and independent pose-evaluation failure rules before data production. These are proposed checks, not completed measurements.

W1 begins with a two-dimensional Gaussian mixture with known conditional and marginal scores, using proposed 20,000 training samples, 10,000 test samples and five seeds. This common diagnostic does not count as one of the three tasks. Each real task then receives same-query interventions and a task-specific pilot (a starting design is 128 accepted units and approximately 200 valid updates). If teacher interventions have no stable quality value or there is no meaningful conflict, report that task's negative finding before any scale-up decision. W2 screens nested data subsets, W3 runs attribution controls, and W4 targets the full task-specific data scale with three independent training seeds. W5 audits all three task reports and any optional video-architecture extension. All stages are pending and constrained by measured per-task costs; reduced or unexecuted stages stay explicitly visible.

### Paired data, split units and external deployment

For T1, the proposed synthetic development and mechanism-test sets each contain 256 accepted complete-video units. Training subsets are nested as $512\subset2{,}048\subset8{,}192$. Filtering records attempted and accepted counts, decoding failures, identity instability, multiple people, cuts, action failure, static copies and severe artifacts. Video units, near duplicates and verified identity clusters are split together. Repeated crops or re-noising do not create independent videos or identities. Reference frames are selected outside target windows under the locked rule.

T1 external-reference domains are provisionally CelebV-HQ ([celebvhq](https://github.com/CelebV-HQ/CelebV-HQ)) and FFHQ. (Footnote: Official FFHQ source and per-image license information: [source](https://github.com/NVlabs/ffhq-dataset). Actual use requires a locked source and license manifest.) The starting design is 32 development identities per domain and 100 test identities or verified clusters per domain. Neither public metadata nor one image per file establishes unique identity labels; verify clustering, licensing and near-duplicate exclusion. Four prompts and two inference seeds per test identity give $2\times100\times4\times2=1{,}600$ videos per checkpoint.

For each of T2 and T3, the proposed budget is 8,192 accepted teacher images, 512 development units and 500 external condition maps, after task-specific filtering. Use nested $512\subset2{,}048\subset8{,}192$ training subsets for screening. These are requested sample budgets, not evidence of data availability or completion. T2 splits original source images and near-duplicate clusters before extracting maps. T3 splits source-image, verified-person and preregistered near-pose groups, and removes near-duplicate pose templates across training, development and test. Lock grouping thresholds and document collisions rather than inferring independent people from file names. Store original keypoints, visibility/confidence, estimator version, joint mapping and rendered maps so that renderer templates cannot create concealed leakage. Record failed/off-body/multiple-person extraction and all exclusions; duplicated renders or crops do not count as independent samples.

The 500 external maps per image task come from a locked source-image manifest disjoint from teacher-pair training and development groups. Two compatible text prompts and two inference seeds per map yield $500\times2\times2=2{,}000$ images per checkpoint. T3 prompts must describe a person in a way compatible with the fixed pose; this compatibility policy is locked before testing. Full deployment starts from fresh noise with only the student, text and supplied condition. No teacher prefix, target-source image, output warping or torso repositioning is allowed. ``External'' and ``unseen'' refer to this distillation/tuning process, not unknown foundation-model pretraining. Fixed-noise condition swaps and fixed-condition noise swaps test whether each student uses its condition without copying the source.

### Baselines and attribution in every task

| ID | Query states | Local target / purpose |
| --- | --- | --- |
| S0 | Deployment only | Original student; no training |
| P | Paired re-noising | Paired + condition losses; no local KD |
| H0 | Hybrid | Raw teacher target |
| H1 | Hybrid | Condition-gated raw target |
| H2 | Hybrid | Projected, clipped and checked target |
| O0 | Full student | Raw teacher target |
| O1 | Full student | Same correction as H2 |
| C-H | Same as H2 | Same common losses; remove KD |
| C-O | Same as O1 | Same common losses; remove KD |

The same S0 plus eight training controls are required separately for T1, T2 and T3. H0--H2/C-H share a state-construction protocol and common-loss definition; O0/O1/C-O do likewise. Each method uses its own current student. All outcomes are pending.

Each task requires eight trained methods with three independent training seeds, plus S0: 25 evaluated checkpoints per task at the proposed full scale. H1 accepts the unmodified $y_T$ only when its actual valid proxy satisfies $E_c(y_T)\le E_c(\operatorname{sg}(y_S))+\delta$. A radius-matched gating variant is a separate ablation. Report equal-update and equal-measured-compute comparisons, matching trainable modules, inference settings and tuning budgets within each task. Candidate LoRA rank/alpha and learning-rate ranges must be selected under each compatibility gate and development budget; T1 settings are not automatically suitable for SD1.5 or either ControlNet.

Required attribution checks are state source $\times$ correction; teacher versus student initial transition; $k=0,1,3$ at matched terminal noise; raw/gated/projected/projected-and-checked targets; radius-only and radius-matched gating controls; weaker raw KD matched by realized gradient strength; random gating matched within noise bins; and condition-only directions. Test independent re-noising versus trajectory-bound noise and data scale per task. Outside-window versus within-window references are a T1-specific check; edge-threshold/soft-edge and joint-schema/proxy sensitivity are T2/T3 checks. Each task has a predeclared development selection rule. Additional operating points and compute-matched runs are budgeted separately from the 25-checkpoint main test.

### Same-query intervention and target realization

Within each task, compare student, raw-teacher, gated-teacher and constrained transitions at identical query states. Continue every branch with the same frozen student and coupled subsequent randomness. Measure final quality, condition fidelity and text/action compliance by actual noise level. A local clean-prediction quality gain is insufficient because continuation can reverse it.

Separately measure proxy error in constructed targets, realized predictions after 1/5/20 fitting updates, and independently generated outputs. Fixed query sets support this diagnostic; checkpoint-conditional paired changes remain distinct from final training effects. Report rejection, invalid-gradient, detector and joint failures, accepted step sizes and realized KD norms. Count all attempted cases so that excluding difficult inputs cannot create a condition-preservation claim.

### Independent metrics and uncertainty

For T1, evaluate identity using an independent recognizer, provisionally AdaFace with its own official alignment, BGR ordering and normalization. Calibrate thresholds and the video-pass rule on development data; a proposed rule requires at least 90% of sixteen uniformly sampled generated frames to pass identity and valid-detection checks. Failures stay in the complete video/frame denominators. Back-facing and occluded cases receive a separate identity-recovery stress protocol. Report visual/aesthetic quality, temporal flicker, motion smoothness, action/text compliance, identity jumps, severe failures, static copying and condition-compatible diversity separately. Lock the VBench version and valid custom-video dimensions. Subject consistency is not proof of reference matching.

For T2, report independent hard-edge F1 and symmetric Chamfer distance, with fixed edge extraction, image scaling, matching tolerance, blank-map policy and full output denominator, alongside image quality, text compliance and condition-compatible diversity. Soft-edge training error is diagnostic only. For T3, use an independent pose estimator with different model/weights from the differentiable training proxy. Report PCK and OKS, pose/person detection rates, visible-joint coverage, image quality and text compliance under the locked COCO-17/OpenPose-18 mapping. Fix scale/visibility and missing-neck policies before test access. Undetected people, missing required joints and failed generations count as failures in the full planned sample/joint denominators; additionally report conditional-on-detection diagnostics without substituting them for full-denominator scores. No forced torso alignment or pose-fixing postprocess is permitted.

Quality claims require task-specific condition and text/action non-inferiority margins, calibrated before test access. Report every training seed separately and the mean and standard deviation across the three training seeds, for each task. Keep training seeds distinct from teacher-sampling and inference seeds. Paired cluster bootstrap intervals quantify generation-case uncertainty conditional on checkpoints: identity clusters for T1, source/near-duplicate groups for T2, and the locked source/person/near-pose groups for T3. Retain all texts and inference seeds inside the resampled group. Report cluster counts and each external domain; do not treat frames, joints or repeated prompts as independent experimental units. Do not average T1 identity, T2 edges and T3 pose scores into a universal score or treat the three tasks as independent architecture trials.

The proposed T1 human study uses 200 paired cases balanced across domains and training seeds for H2 versus P, O1 and H0. Three raters see randomized sides, can choose ties, and answer quality, identity and action questions separately: 1,800 displays and 5,400 component judgments if completed. These are protocol counts, not collected data. Consent, instructions, exclusions and agreement analysis are fixed before recruitment. Any T2/T3 human study requires its own condition-specific questions and budget; the T1 study cannot establish image-task success.

### Task budgets and result blocks

At the proposed full test scale, T1 requires $25\times1{,}600=40{,}000$ main-test videos. T2 and T3 each require $25\times2{,}000=50{,}000$ main-test images, totaling 100,000 images across the two tasks. These are arithmetic suggestions, not generated samples, approved GPU-hour commitments or completion-time estimates. Development, interventions, extra operating points, compute-matched checks and an optional second video architecture are additional costs. Each task records accepted-data yield, with $N_{\mathrm{raw}}\approx N_{\mathrm{accepted}}/r_{\mathrm{accept}}$, actual training/evaluation compute, peak memory and failed runs. Scaling requires its own full-step profile and task budget; compute saved on a failed task does not turn another task's score into a substitute result.

| Task | Mandatory comparisons | Condition evaluation | Current evidence |
| --- | --- | --- | --- |
| T1 | S0 and all eight controls | Independent identity, failures; quality/action | PENDING: A/B/C and deployment |
| T2 | Same controls, separate runs | Hard-edge F1/Chamfer; quality/text | PENDING: A/B/C and deployment |
| T3 | Same controls, separate runs | Independent PCK/OKS, full failures; quality/text | PENDING: A/B/C and deployment |

Mandatory three-task result ledger. Each task retains its own gate, budget, seeds, condition metrics and supported claims. Every cell is pending; negative or blocked results remain visible. No cross-task aggregate score is defined.

## Limitations

The proposed method relies on differentiable condition proxies, which can be biased, insensitive to identity or pose, unreliable under occlusion, mismatched to hard-edge structure, or exploitable by the student. The finite check validates that proxy only at a constructed latent target. Even a correct target can be poorly realized by limited-capacity or low-rank training. Decoding intermediate clean predictions may be expensive and may produce invalid crops, and rejecting difficult cases can bias supervision.

Each student must already have useful task control. Synthetic video pairs can entangle identity, action, viewpoint and background; synthetic image pairs inherit teacher biases, and edge/pose extraction can discard or mislabel structure. T3 has schema, occlusion and detection uncertainty, and common skeleton templates can leak across splits. Independent external-condition tests address only their chosen distributions. T2 and T3 share an SD1.5 architecture and therefore do not establish two independent architectural replications. Three training seeds can leave substantial uncertainty. Closest-work coverage and target-year ICML rules remain unverified, and all training, profiling and evaluation are unperformed. No result in this draft establishes quality improvement, identity/edge/pose preservation, efficiency or broad applicability. A failed task gate narrows claims and remains part of the report.

## Conclusion

We specify a three-task research program for distillation when the teacher lacks an additional condition the student must preserve: identity video, Canny-conditioned images and pose-conditioned images. The method proposes a condition-aware local target with teacher-start/student-rollout states. The decisive evidence is task-specific: whether useful conflicting teacher directions exist, and whether correction exceeds matched attribution controls under independent student generation and evaluation. All three tasks must be investigated and reported, including negative or blocked outcomes. Claims narrow when tests fail; this draft is a protocol, not a positive empirical conclusion.

## Impact Statement

Reference-identity video generation can support consent-based creative production, but can also enable impersonation, harassment and misleading media. Face-recognition proxies and source datasets may have demographic and acquisition biases. The study should use appropriately licensed material, document permitted uses and consent where required, minimize retention of identifiable reference data, and publish split identifiers and processing scripts when raw redistribution is restricted. Evaluation should include failure rates and subgroup checks where valid metadata and sample sizes permit them, without inferring sensitive identities from appearance. Any future release should assess impersonation risks, provenance and access choices based on actual capabilities. Pose-conditioned imagery also requires licensed source images and care around recognizable people, and pose-estimator failures or subgroup biases should be recorded where metadata support analysis. This draft reports no deployed system and no completed human-subject study.

## Appendices

## Prediction Conversions and Numerical Checks

For a variance-preserving parameterization $z_t=\alpha_t y+\sigma_t\epsilon$ with $\alpha_t^2+\sigma_t^2=1$, an epsilon prediction gives

$$
y=(z_t-\sigma_t\hat\epsilon)/\alpha_t.
$$

If $v=\alpha_t\epsilon-\sigma_t y$, then $y=\alpha_t z_t-\sigma_t\hat v$. For the linear flow path $z_t=(1-t)y+t\epsilon$ with $v=\epsilon-y$, $y=z_t-t\hat v$. These velocity definitions are different and must not be interchanged.

At fixed $z_t$, the corresponding inverse conversions are $\epsilon^*=(z_t-\alpha_t y^*)/\sigma_t$, VP $v^*=(\alpha_t z_t-y^*)/\sigma_t$, and linear-flow $v^*=(z_t-y^*)/t$, where denominators are nonsingular. More generally, with $v=\dot\alpha_t y+\dot\sigma_t\epsilon$,

$$
y=\frac{\dot\sigma_t z_t-\sigma_t v}
 {\alpha_t\dot\sigma_t-\sigma_t\dot\alpha_t}.
$$

Use the actual checkpoint/scheduler contract, including time shifts and scaling. Avoid singular endpoints or use explicitly derived limits. Required checks include native-to-clean-to-native round trips, equal-state teacher/student conversion, generation-mask invariance, finite condition gradients, and exclusion of all reference/fixed coordinates. These are proposed implementation checks; none has yet been executed on the candidate models.

## Projection Derivation

For $g\ne0$, minimize $\frac12\|d-d_0\|^2$ subject to $g^\top d\le0$. The Lagrangian is $\frac12\|d-d_0\|^2+\lambda g^\top d$. Stationarity gives $d=d_0-\lambda g$. Feasibility and complementary slackness yield $\lambda=\max(0,g^\top d_0)/\|g\|^2$, proving Equation (eq:projection) for the halfspace projection. Subsequent radius clipping and backtracking produce a feasible checked target when accepted, but are not claimed to be the nearest point to the teacher in the nonlinear feasible set.

When the finite gradient has squared norm at most $\varepsilon_g$, use the radius-clipped raw teacher direction and the same actual-proxy backtracking; only passing candidates are accepted and logged as \texttt{zero\_grad\_checked}. Invalid proxy values, nonfinite gradients and empty masks reject local KD. Paired and valid common supervision remain active; an all-loss-invalid batch skips optimizer and scheduler updates and is not counted as a valid training update. Numerical tolerances, the squared-gradient threshold $\varepsilon_g$, target radius and proxy tolerance are fixed on development data. Test-time adjustment of these choices is exploratory and requires a new confirmation set for confirmatory claims.

## Exact-Score Toy Diagnostic

A Gaussian-mixture diagnostic assigns mixture components to conditions. For means $\mu_j$, weights $\pi_j$ and isotropic covariance $s_0^2 I$, the noisy marginal has component means $\alpha_t\mu_j$ and variance $s_t^2=\alpha_t^2s_0^2+\sigma_t^2$. Its exact score is

$$
\nabla_z\log p_t(z)=\sum_j w_j(z,t)
 \frac{\alpha_t\mu_j-z}{s_t^2},\quad
 w_j\propto\pi_j\exp\left(-\frac{\|z-\alpha_t\mu_j\|^2}{2s_t^2}\right).
$$

For a condition selecting one component, the conditional score is $(\alpha_t\mu_c-z)/s_t^2$. These fields allow measurement of conflict and conditional-mode errors without a learned identity proxy. Report mode coverage and a fixed distribution discrepancy together with condition error. This controlled analysis cannot establish video quality or real-identity generalization.

## Planned Figures and Reporting Rules

The proposed six main figures are a three-task data/method/deployment schematic; same-query conflict by noise with T1/T2/T3 blocks; task-specific quality--condition tradeoffs; state-source attribution with measured compute per task; external-condition generalization and swaps per task; and matched video/image qualitative cases including failures in each task. Main tables contain separate T1/T2/T3 blocks for S0 and all eight training controls, three training seeds, independent condition metrics, failures and measured compute. Optional second-video-architecture evidence receives a separate extension table, not a replacement block. The eight supplemental figures cover filtering, leakage, toy fields, target-to-fitting realization, acceptance diagnostics, data/compute efficiency, sensitivity/shortcuts and unselected failures/evaluator disagreement, with task labels and units. Schematic panels can precede experiments; empirical curves and generated examples remain pending until actual artifacts exist.

Every number must map to code/data/checkpoint/evaluator versions, complete seeds and failures, raw output IDs and aggregation scripts. Development checkpoint selection is fixed before test access. All baselines use matching trainable modules, condition losses, sampling settings and tuning budgets. The project result manifest, rather than this prose, is the authority for completed evidence.

## Decision Rules and Submission Readiness

If H2 matches P, synthetic paired data may explain the result. If H2 matches C-H, online condition supervision may explain it. If it matches weak KD or a condition-only direction, projection may provide no teacher-specific advantage. If H2 matches O1, a hybrid-state claim can survive only as a measured efficiency result, if supported. Improvements limited to teacher-prefixed inference do not establish an independently deployable student. Identity gains with static copying/action failure, edge gains with degraded image/text quality, pose gains from torso repositioning or omitted detection failures, and training-proxy-only gains are failures of the intended objective. Apply these rules separately to T1/T2/T3, retain every task's gate and outcome, and never infer general success from a cross-task averaged score.

Before submission, complete the closest-work search; confirm the target ICML year; download the complete official template; verify current page, anonymity, impact and AI-disclosure rules; integrate only audited results; compile and inspect all pages. ICML 2026's published eight-page main-text rule is historical planning information, not a verified rule for the next conference. This draft has not been page-budgeted or declared submission-ready.



## Verified References

- **codi**: Kangfu Mei, Mauricio Delbracio, Hossein Talebi, et al.. [CoDi: Conditional Diffusion Distillation for Higher-Fidelity and Faster Image Generation](https://arxiv.org/abs/2310.01407). arXiv:2310.01407, 2024.

- **hpsd**: Jiazi Bu, Pengyang Ling, Yujie Zhou, et al.. [HPSD: Hybrid-Policy Self-Distillation for Text-Image-to-Video Diffusion Models](https://arxiv.org/abs/2608.13205). arXiv:2608.13205, 2026.

- **pdmd**: Zimo Wang, Junkun Yuan, Angtian Wang, et al.. [PDMD: Projected Distribution Matching Distillation for Video Diffusion Models](https://arxiv.org/abs/2609.35768). arXiv:2609.35768, 2026.

- **diffusionopsd**: Wei Zhou, Xiongwei Zhu, Lingdong Kong, et al.. [On-Policy Self-Distillation in Diffusion Models](https://arxiv.org/abs/2608.24646). arXiv:2608.24646, 2026.

- **dsd**: Shengqu Cai, Eric Chan, Yunzhi Zhang, et al.. [Diffusion Self-Distillation for Zero-Shot Customized Image Generation](https://arxiv.org/abs/2411.18616). arXiv:2411.18616, 2024.

- **concatid**: Yong Zhong, Zhuoyi Yang, Jiayan Teng, et al.. [Concat-ID: Towards Universal Identity-Preserving Video Synthesis](https://arxiv.org/abs/2503.14151). arXiv:2503.14151, 2025.

- **wan**: Team Wan, Ang Wang, Baole Ai, et al.. [Wan: Open and Advanced Large-Scale Video Generative Models](https://arxiv.org/abs/2503.20314). arXiv:2503.20314, 2025.

- **controlnet**: Lvmin Zhang, Anyi Rao, Maneesh Agrawala. [Adding Conditional Control to Text-to-Image Diffusion Models](https://arxiv.org/abs/2302.05543). arXiv:2302.05543, 2023.

- **adaface**: Kim, Minchul, Jain, Anil K., Liu, Xiaoming. [AdaFace: Quality Adaptive Margin for Face Recognition](https://openaccess.thecvf.com/content/CVPR2022/html/Kim_AdaFace_Quality_Adaptive_Margin_for_Face_Recognition_CVPR_2022_paper.html). Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR), 2022.

- **consisid**: Yuan, Shenghai, Huang, Jinfa, He, Xianyi, et al.. [Identity-preserving text-to-video generation by frequency decomposition](https://github.com/PKU-YuanGroup/ConsisID). Proceedings of the Computer Vision and Pattern Recognition Conference, 2025.

- **celebvhq**: Zhu, Hao, Wu, Wayne, Zhu, Wentao, et al.. [CelebV-HQ: A Large-Scale Video Facial Attributes Dataset](https://github.com/CelebV-HQ/CelebV-HQ). ECCV, 2022.

- **vbench**: Huang, Ziqi, He, Yinan, Yu, Jiashuo, et al.. [VBench: Comprehensive Benchmark Suite for Video Generative Models](https://openaccess.thecvf.com/content/CVPR2024/html/Huang_VBench_Comprehensive_Benchmark_Suite_for_Video_Generative_Models_CVPR_2024_paper.html). Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition, 2024.
