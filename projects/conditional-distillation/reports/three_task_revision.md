# Three-task revision

The user requested three tasks, all visible in the same main prompt. The revised scope is T1 reference-identity video, T2 Canny-conditioned image generation, T3 single-person pose-conditioned image generation. T2/T3 share a matched SD1.5/ControlNet base and do not constitute two independent architecture replications.

Updated the main prompt, task prompts 16/17, task protocol, configuration, state, task_id metadata, budget helper, 76-row experiment matrix, relevant skills and paper. Every task has its own gates, complete controls and applicable attribution ablations. Negative findings remain visible; unrun tasks cannot count as completed evidence.

Validation: 12 skill schemas; 18 prompts and local links; isolated installation; independent per-task workload arithmetic and measured costs; original source preservation; paper citation completeness; current source compiled with the built-in compiler. New p-column tables exposed a nested-brace parsing defect in the reading-copy converter; a balanced parser fixed the actual table and regression checks passed.

Primary sources checked: ControlNet 1.1 author repository, Canny/OpenPose author model cards, official HRNet implementation. No checkpoint execution, gradient validation, training, generated images/videos, GPU jobs, new chats or paid services were started. Current editor and original main.tex were preserved. No standalone PDF was created.
