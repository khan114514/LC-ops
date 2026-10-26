#!/usr/bin/env python3
"""Calculate proposed workload from measured costs. Estimates are never execution evidence."""
import argparse
import json
import math


def positive(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError('must be a finite positive number')
    return number


def positive_int(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError('must be a positive integer')
    return number


def estimate(a):
    videos_per_checkpoint = a.domains * a.identities * a.prompts * a.inference_seeds
    trained_checkpoints = a.trained_methods * a.train_seeds
    main_videos = (trained_checkpoints + 1) * videos_per_checkpoint
    raw_teacher = math.ceil(a.accepted_teacher / a.acceptance) if a.acceptance else None
    train_h = trained_checkpoints * a.updates * a.update_seconds * a.train_gpus / 3600 if a.update_seconds else None
    gen_h = main_videos * a.generation_seconds * a.inference_gpus / 3600 if a.generation_seconds else None
    teacher_h = raw_teacher * a.teacher_generation_seconds * a.teacher_gpus / 3600 if raw_teacher and a.teacher_generation_seconds else None
    image_outputs = a.image_conditions * a.image_prompts * a.image_inference_seeds
    image_checkpoints = trained_checkpoints + 1
    image_tasks = {}
    for task_id, prefix in [('T2', 'canny'), ('T3', 'pose')]:
        update_seconds = getattr(a, prefix + '_update_seconds')
        generation_seconds = getattr(a, prefix + '_generation_seconds')
        image_tasks[task_id] = {
            'outputs_per_checkpoint': image_outputs,
            'checkpoint_count': image_checkpoints,
            'main_test_images': image_outputs * image_checkpoints,
            'formal_training_gpu_hours': trained_checkpoints * a.image_updates * update_seconds * a.image_train_gpus / 3600 if update_seconds else None,
            'main_test_generation_gpu_hours': image_outputs * image_checkpoints * generation_seconds * a.image_inference_gpus / 3600 if generation_seconds else None,
        }
    return {'kind': 'PROVISIONAL_ESTIMATE_NOT_MEASURED_RESULT', 'videos_per_checkpoint': videos_per_checkpoint,
            'trained_checkpoints': trained_checkpoints, 's0_checkpoints': 1, 'main_test_videos': main_videos,
            'accepted_teacher_videos': a.accepted_teacher, 'raw_teacher_candidates_estimate': raw_teacher,
            'formal_training_gpu_hours': train_h, 'main_test_generation_gpu_hours': gen_h,
            'teacher_data_generation_gpu_hours': teacher_h,
            'image_task_plans': image_tasks,
            'total_main_test_images': sum(task['main_test_images'] for task in image_tasks.values()),
            'excluded': ['pilot/dev generation', 'training data filtering', 'identity feature extraction',
                         'local intervention', 'ablations and tradeoff points', 'optional second video architecture',
                         'image teacher-data generation and task-specific condition extraction',
                         'metric evaluation', 'retries', 'storage', 'human ratings'],
            'notes': ['Use measured complete update costs including decoding, conditional gradients and backtracking.',
                      'Times must be measured per job at the stated GPU count; GPU-hours are device-hours, not wall-clock ETA.',
                      'Checkpoint count assumes one dev-selected checkpoint per trained method and seed plus S0.',
                      'T2 and T3 require separate measured update times: their condition-gradient costs may differ.',
                      'Null means unmeasured. This script does not authorize or submit any job.']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name, default in [('domains', 2), ('identities', 100), ('prompts', 4), ('inference-seeds', 2),
                          ('trained-methods', 8), ('train-seeds', 3), ('updates', 3000), ('accepted-teacher', 8192),
                          ('train-gpus', 1), ('inference-gpus', 1), ('teacher-gpus', 1),
                          ('image-conditions', 500), ('image-prompts', 2), ('image-inference-seeds', 2),
                          ('image-updates', 3000), ('image-train-gpus', 1), ('image-inference-gpus', 1)]:
        p.add_argument('--' + name, type=positive_int, default=default)
    for name in ['update-seconds', 'generation-seconds', 'teacher-generation-seconds', 'acceptance',
                 'canny-update-seconds', 'canny-generation-seconds', 'pose-update-seconds', 'pose-generation-seconds']:
        p.add_argument('--' + name, type=positive)
    a = p.parse_args()
    if a.acceptance and a.acceptance > 1:
        p.error('--acceptance must be in (0, 1]')
    print(json.dumps(estimate(a), indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
