# Result integration requirements

Status: all empirical claims in T1, T2 and T3 are PENDING. Do not replace PENDING with estimates, intended outcomes, third-party scores or illustrative numbers. All three tasks are mandatory research scope and must remain in the launch prompt and final report. Negative and blocked outcomes retain their attempted evidence and reason; a failed gate never licenses silently deleting a task.

## Evidence bundle for every reported number

Link each result to an immutable run ID; code commit and dirty diff; environment/dependencies; model/checkpoint revisions, hashes and licenses; data/split/filter manifests; teacher-sampling, training and inference seeds separately; losses, target/rejection settings and condition proxy; scheduler/CFG/inference steps; actual compute and peak memory; selected checkpoint and development selection; independent evaluator version/weights/preprocessing; individual outputs including failures; raw metrics, aggregation script, uncertainty method and plot/table source.

Store planned/started/completed/failed/skipped counts. Interrupted jobs remain incomplete. Keep checkpoint lineage, rejected samples and failed runs. Every task has its own compatibility/proxy gate, teacher-value/conflict gate, budget, development selection and status. One task's positive result cannot clear another task's gate. No project training, data production or measurement has yet been performed.

## Mandatory tasks and condition contracts

| Task | Candidate teacher/student and pair construction | Training proxy | Independent deployment evaluation |
|---|---|---|---|
| T1 identity video | Wan2.1-T2V-1.3B / Concat-ID-Wan-AdaLN; reference outside target window from `c=h(x_teacher)` | Frozen differentiable face encoder and fixed differentiable crops; exclude reference/fixed/overlap frames | Independent identity recognizer/weights, calibrated video/frame pass rules, full detector/output failures; quality, motion and text/action compliance |
| T2 Canny image | Same SD1.5 text-only teacher / corresponding ControlNet 1.1 Canny; locked Canny extraction | Differentiable soft-edge discrepancy in locked coordinates | Independent hard-edge F1 and symmetric Chamfer with locked thresholds/tolerances and empty-map rules; full output failures, quality/text compliance |
| T3 pose image | Same SD1.5 text-only teacher / corresponding ControlNet 1.1 OpenPose; offline keypoints plus locked renderer | Frozen differentiable PyTorch heatmap or soft-argmax proxy, preserving input gradient | Different pose model and weights from training proxy; PCK/OKS, person/joint failures and coverage with full planned sample/joint denominators; quality/text compliance |

Lock exact checkpoints and actual scheduler/latent compatibility before execution. T2/T3 are distinct condition tasks on the same architecture, not two independent architecture replications. A second compatible video architecture is an optional T1 extension; it is not a fourth main task and cannot replace either image task. Fixed-first-frame I2V cannot substitute for any main task.

For T3, freeze COCO17/OpenPose18 joint order, left/right mapping, neck from shoulders, coordinate scale, missing-joint/confidence/visibility masks and renderer before data generation. Preserve stored source keypoints and conversion audit. Validate a real PyTorch input-gradient path through VAE decode, resize, network and soft readout: no NumPy, ONNX or hard argmax in the training-gradient path. Evaluation may use detached discrete extraction, but must be independent and count failures. Do not translate the torso, align the generated body by force, warp outputs or perform other condition-fixing postprocessing. Conditional-on-detection scores may be diagnostics only; they cannot replace full-denominator PCK/OKS and detection/joint failure reporting.

## Data, leakage and proposed resource ledger

| Task | Split/grouping unit | Proposed accepted data and external test | Main-test arithmetic |
|---|---|---|---|
| T1 | Video, verified identity and near-duplicate clusters together; reference outside target window | Nested 512/2,048/8,192 train videos, 256 development and 256 mechanism units; two external domains × 100 test identities/clusters | 4 texts × 2 inference seeds per identity: 1,600 videos/checkpoint; 25 checkpoints = 40,000 videos |
| T2 | Original source images and near-duplicate clusters before map extraction | 8,192 train teacher images, 512 development units, 500 external maps | 500 × 2 texts × 2 inference seeds = 2,000 images/checkpoint; 25 checkpoints = 50,000 images |
| T3 | Source images, verified people and preregistered near-pose groups; no near-duplicate skeleton templates across splits | 8,192 train teacher images, 512 development units, 500 external maps | 500 × 2 texts × 2 inference seeds = 2,000 images/checkpoint; 25 checkpoints = 50,000 images |

All counts are suggested protocol budgets, not completed samples or compute commitments. T2/T3 main-test total is 100,000 images. Record raw attempts and acceptance yields, all data filters/exclusions and grouping thresholds. Repeated crops, re-noising and rendered template duplicates are not independent units. External condition maps must be disjoint from teacher-pair training/development groups; source manifests and prompt-compatibility rules are frozen before testing. Unseen means absent from this distillation/tuning, not unknown foundation-model pretraining. Development, interventions, extra operating points, compute-matched checks and the optional video architecture extension are additional costs.

Every task separately runs S0 plus P/H0/H1/H2/O0/O1/C-H/C-O. The eight trained methods each have three independent training seeds: 24 trained checkpoints plus S0 = 25 main-test checkpoints. Match trainable modules, common losses, data, HPO and inference budgets within a task. Separately report equal-update and measured-compute views; the latter may require extra runs outside the main budget. Retain gate failures/reduced stages and their reasons in the ledger.

## Claim-to-evidence map, applied separately to all three tasks

| Candidate claim | Required evidence | Comparisons and failure conditions |
|---|---|---|
| A: useful teacher supervision sometimes harms added-condition fidelity | Same-query interventions at matched actual noise levels, coupled common-student continuation, independent task condition metrics and quality/text/action metrics, cluster intervals and prevalence | Teacher vs student, gated/constrained controls. If there is no stable quality value or meaningful conflict, report a negative task result and do not claim a useful-conflict problem there. |
| B: correction improves the quality/control tradeoff | H2 vs H0/H1/P/C-H, weak KD, acceptance-rate-matched random gate, condition-only direction; target checks, 1/5/20-step fitting and full independent generation; development-locked operating points | Match modules/data/HPO/deployment; report equal-update and measured-compute views. If C-H, weak KD or condition-only directions explain gains, narrow/remove teacher-specific correction claims. |
| C: hybrid states add value | H0/O0 and H2/O1 factorial; T→S vs S→S; k=0/1/3 at matched terminal noise; C-H/C-O | Report task-specific quality/control/text-action metrics, acceptance, wall time and model-call counts. If H2≈O1, retain only measured efficiency claims supported by evidence. |
| Independent external-condition deployment | Frozen leakage-disjoint manifests, new-noise student-only deployment, condition/noise swaps and shortcut checks | No teacher prefix or source-target access. T1 copying/static outputs, T2 trivial edge artifacts and T3 forced torso alignment/failure omissions do not pass. |
| Three-task scope | Complete separate gate/status/result blocks for T1/T2/T3, with independent task evaluation and negative findings retained | No cross-task universal score or silent task deletion. Same-base Canny/OpenPose do not establish two independent architectures. Optional video extension has separate paired data/settings/evaluation. |
| Validity of target construction | Generated-coordinate-only norms/masks, finite gradient audits, actual proxy check and measured radius on accepted targets, native-space round trips, fallback/rejection logs | Claim only constructed-target proxy behavior under fixed preprocessing. No final-output, parameter-update or real-condition guarantee follows. |

## Locked main tables and figures

Table 1: three mandatory blocks, T1/T2/T3, each containing S0 plus all eight trained methods, independent task condition metrics, quality/text-action measures, failures and actual compute. Preserve external domains where applicable. Do not average identity, edges and pose into a universal score.

Table 2: three-task state-source × correction attribution, required controls, query times, teacher/student calls and measured cost. Optional second-video-architecture evidence gets a separate extension table.

Every numeric row states training-seed count, inference-seed count, cluster/source count, failure counts, CI type and checkpoint-selection status. For each task show every training seed, then mean and standard deviation across the three seeds. Paired cluster bootstrap intervals describe generation-case uncertainty conditional on checkpoints; they do not erase training-seed uncertainty. T1 uses identity clusters, T2 source/near-duplicate clusters, T3 locked source/person/near-pose groups, retaining all repeated texts and inference seeds within groups. Do not flatten frames, joints, repeated prompts or seeds into independent samples.

Six planned main figures: three-task pipeline (schematic permitted now); same-query conflict; quality/condition tradeoffs; hybrid contribution with compute; external generalization/condition use; matched qualitative videos/images including failures. All empirical figures use T1/T2/T3 blocks with their own units. Eight supplements cover filtering, leakage, toy mechanisms, target-to-fitting-to-deployment, acceptance, data/compute efficiency, sensitivity/shortcuts, and random outputs/failures/evaluator disagreement. Optional architecture results stay separate.

Empirical panels stay absent or visibly PENDING until raw data exist. Do not generate plausible curves. Qualitative cases use a frozen deterministic selection policy; retain random galleries and complete videos. Captions identify sample/cluster units, seeds and uncertainty. No task may disappear from figures merely because its result is negative.

## Human evaluation and submission transition

The proposed T1 study requires consent/instructions, recognizable-face handling, randomized sides, ties, three separate quality/identity/action questions, reference display, balanced seed allocation, exclusions and agreement rules. Planned 200 cases × 3 comparisons × 3 raters = 1,800 displays and 5,400 component judgments. This is arithmetic, not a completed study. Any T2/T3 human evaluation needs its own condition questions and budget; T1 raters cannot establish image-task success.

After evidence audit, rewrite claims around supported per-task results and retain all mandatory task outcomes, including negative/blocked results. Remove unsupported positive claims rather than removing their tasks. Refresh closest-work literature and actual-year ICML rules, compile/render and inspect all pages, and check placeholders, anonymity, paths and secrets. The current edit remains in the existing `main.tex`; use the built-in compiler and preview without creating an alternative main or independent PDF. Successful compilation does not establish research completion or acceptance readiness.
