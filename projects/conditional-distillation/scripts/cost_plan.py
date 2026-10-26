#!/usr/bin/env python3
"""Calculate proposed workload from measured costs. Estimates are never execution evidence."""
import argparse
import json
import math
from pathlib import Path
import re


TASKS = ('T1', 'T2', 'T3')
METHODS = ('P', 'H0', 'H1', 'H2', 'O0', 'O1', 'C-H', 'C-O')
ROW_FIELDS = {'task_id', 'method', 'config_id', 'hardware_id', 'updates',
              'train_seeds', 'repeats', 'gpu_count', 'update_seconds', 'measurement_run_id'}
MEASUREMENT_FIELDS = ('config_id', 'hardware_id', 'gpu_count', 'update_seconds', 'measurement_run_id')


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


def require_fields(value, fields, location, optional=()):
    if not isinstance(value, dict):
        raise ValueError(location + ' must be a JSON object')
    if not fields.issubset(value) or set(value) - fields - set(optional):
        missing = sorted(fields - set(value))
        unknown = sorted(set(value) - fields - set(optional))
        raise ValueError(f'{location} fields: missing={missing}, unknown={unknown}')


def seed_list(value, location):
    if not isinstance(value, list) or not value:
        raise ValueError(location + ' must be a nonempty train_seeds list')
    if any(type(seed) is not int or seed < 0 for seed in value):
        raise ValueError(location + ' train_seeds must be nonnegative integers')
    if len(set(value)) != len(value):
        raise ValueError(location + ' contains a duplicate train seed')
    return value


def positive_json_number(value, location, integer=False):
    valid_type = type(value) is int if integer else type(value) in (int, float)
    try:
        valid = valid_type and math.isfinite(value) and value > 0
    except OverflowError:
        valid = False
    if not valid:
        kind = 'integer' if integer else 'number'
        raise ValueError(location + ' must be a finite positive ' + kind)


def finite_hours(value):
    if not math.isfinite(value):
        raise ValueError('calculated GPU-hours must be finite; input workload is too large')
    return value


def unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def reject_json_constant(value):
    raise ValueError('JSON numbers must be finite; found ' + value)


def declared_methods(document):
    if 'required_methods' not in document:
        return {task: list(METHODS) for task in TASKS}
    matrix = document['required_methods']
    require_fields(matrix, set(TASKS), 'required_methods')
    for task, methods in matrix.items():
        if not isinstance(methods, list) or not methods:
            raise ValueError('required_methods.' + task + ' must be a nonempty method ID list')
        for method in methods:
            if not isinstance(method, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]{0,63}', method) or method == 'S0':
                raise ValueError('required_methods.' + task + ' contains an invalid training method ID; S0 is inference-only')
        if len(set(methods)) != len(methods):
            raise ValueError('required_methods.' + task + ' contains a duplicate method ID')
    return matrix


def method_cost_plan(path, expected_seed_count, expected_method_count):
    """Validate declared training coverage and sum estimates; do not verify evidence or authority."""
    document = json.loads(path.read_text(encoding='utf-8'),
                          object_pairs_hook=unique_json_object, parse_constant=reject_json_constant)
    require_fields(document, {'schema_version', 'train_seeds', 'rows'}, 'method-cost document',
                   optional=('required_methods',))
    if type(document['schema_version']) is not int or document['schema_version'] != 1:
        raise ValueError('method-cost schema_version must be 1')
    seeds = seed_list(document['train_seeds'], 'document')
    if len(seeds) != expected_seed_count:
        raise ValueError('--train-seeds must match the declared train_seeds count')
    explicit_matrix = 'required_methods' in document
    required_methods = declared_methods(document)
    if not explicit_matrix and expected_method_count != len(METHODS):
        raise ValueError('--trained-methods must match the eight required training methods')
    if not isinstance(document['rows'], list):
        raise ValueError('method-cost rows must be a list')

    rows, seen_rows, seen_runs, covered = [], set(), set(), set()
    for index, row in enumerate(document['rows']):
        location = f'rows[{index}]'
        require_fields(row, ROW_FIELDS, location)
        task, method = row['task_id'], row['method']
        if task not in TASKS:
            raise ValueError(location + ': unknown task_id')
        if method not in required_methods[task]:
            reason = 'undeclared training method' if explicit_matrix else 'unknown training method'
            raise ValueError(location + ': ' + reason + ' (S0 has no training cost)')
        row_seeds = seed_list(row['train_seeds'], location)
        if not set(row_seeds).issubset(seeds):
            raise ValueError(location + ': undeclared train seed')
        for field in ('updates', 'repeats'):
            positive_json_number(row[field], location + '.' + field, integer=True)
        for field in ('config_id', 'hardware_id', 'measurement_run_id'):
            value = row[field]
            if value is not None and (not isinstance(value, str) or not value or value != value.strip()):
                raise ValueError(location + '.' + field + ' must be a nonempty trimmed string or null')
        if row['gpu_count'] is not None:
            positive_json_number(row['gpu_count'], location + '.gpu_count', integer=True)
        if row['update_seconds'] is not None:
            positive_json_number(row['update_seconds'], location + '.update_seconds')

        row_key = (task, method, row['config_id'], row['hardware_id'])
        if row_key in seen_rows:
            raise ValueError(location + ': duplicate row; merge seeds/repeats for the same task/method/config/hardware')
        seen_rows.add(row_key)
        for seed in row_seeds:
            run_key = (task, method, row['config_id'], seed)
            if run_key in seen_runs:
                raise ValueError(location + ': duplicate planned seed for the same task/method/config on different hardware')
            seen_runs.add(run_key)
            covered.add((task, method, seed))

        missing_fields = [field for field in MEASUREMENT_FIELDS if row[field] is None]
        hours = None
        if not missing_fields:
            try:
                hours = finite_hours(row['updates'] * len(row_seeds) * row['repeats'] *
                                     row['gpu_count'] * row['update_seconds'] / 3600)
                if hours <= 0:
                    raise ValueError(location + ': calculated GPU-hours must be positive; input underflow')
            except OverflowError as exc:
                raise ValueError(location + ': calculated GPU-hours must be finite') from exc
        rows.append({**row, 'training_gpu_hours': hours, 'missing_measurement_fields': missing_fields})

    missing_coverage = [{'task_id': task, 'method': method, 'train_seed': seed}
                        for task in TASKS for method in required_methods[task] for seed in seeds
                        if (task, method, seed) not in covered]
    unmeasured = [index for index, row in enumerate(rows) if row['training_gpu_hours'] is None]
    per_task = {}
    try:
        for task in TASKS:
            task_rows = [row for row in rows if row['task_id'] == task]
            missing = [item for item in missing_coverage if item['task_id'] == task]
            unknown = [index for index in unmeasured if rows[index]['task_id'] == task]
            known = finite_hours(math.fsum(row['training_gpu_hours'] for row in task_rows
                                          if row['training_gpu_hours'] is not None))
            per_task[task] = {
                'status': 'COMPLETE' if not missing and not unknown else 'INCOMPLETE',
                'formal_training_gpu_hours': known if not missing and not unknown else None,
                'known_training_gpu_hours': known,
                'missing_coverage': missing,
                'unmeasured_rows': unknown,
            }
        known_total = finite_hours(math.fsum(task['known_training_gpu_hours'] for task in per_task.values()))
    except OverflowError as exc:
        raise ValueError('calculated total GPU-hours must be finite') from exc
    return {
        'planning_scope': 'EXPLICIT_METHOD_MATRIX' if explicit_matrix else 'DEFAULT_INITIAL_MATRIX',
        'scope': {'tasks': list(TASKS), 'required_methods': required_methods, 'train_seeds': seeds,
                  'default_train_seed_count': 3, 'matches_default_seed_count': len(seeds) == 3,
                  'matches_initial_method_matrix': all(set(methods) == set(METHODS) for methods in required_methods.values()),
                  'configuration_coverage': 'DECLARED_ROWS_ONLY'},
        'coverage_status': 'COMPLETE' if not missing_coverage else 'INCOMPLETE',
        'measurement_status': 'COMPLETE' if rows and not unmeasured else 'INCOMPLETE',
        'status': 'COMPLETE' if not missing_coverage and not unmeasured else 'INCOMPLETE',
        'missing_coverage': missing_coverage,
        'unmeasured_rows': unmeasured,
        'per_task': per_task,
        'known_training_gpu_hours': known_total,
        'total_formal_training_gpu_hours': known_total if not missing_coverage and not unmeasured else None,
        'rows': rows,
        'source_runs_verified': False,
        'notes': ['COMPLETE refers only to declared training-cost coverage, not a completed experiment or approved budget.',
                  'All additional planned configurations must be declared as rows; absent configurations cannot be inferred.',
                  'Null costs or references remain unknown; known_training_gpu_hours is only the measured-reference subtotal.',
                  'Measurement references and hardware/configuration identities require independent verification.',
                  'Repeats add compute, not independent training seeds. Reduced seed scopes do not complete the default three-seed protocol.',
                  'An explicit candidate matrix must be frozen before its experiments; COMPLETE does not imply completion of the initial eight-method matrix.'],
    }


def estimate(a, required_methods=None):
    method_mode = bool(getattr(a, 'method_costs', None))
    videos_per_checkpoint = a.domains * a.identities * a.prompts * a.inference_seeds
    video_method_count = len(required_methods['T1']) if required_methods is not None else a.trained_methods
    trained_checkpoints = video_method_count * a.train_seeds
    main_videos = (trained_checkpoints + 1) * videos_per_checkpoint
    raw_teacher = math.ceil(a.accepted_teacher / a.acceptance) if a.acceptance else None
    train_h = trained_checkpoints * a.updates * a.update_seconds * a.train_gpus / 3600 if a.update_seconds and not method_mode else None
    gen_h = main_videos * a.generation_seconds * a.inference_gpus / 3600 if a.generation_seconds else None
    teacher_h = raw_teacher * a.teacher_generation_seconds * a.teacher_gpus / 3600 if raw_teacher and a.teacher_generation_seconds else None
    image_outputs = a.image_conditions * a.image_prompts * a.image_inference_seeds
    image_tasks = {}
    for task_id, prefix in [('T2', 'canny'), ('T3', 'pose')]:
        method_count = len(required_methods[task_id]) if required_methods is not None else a.trained_methods
        image_trained_checkpoints = method_count * a.train_seeds
        image_checkpoints = image_trained_checkpoints + 1
        update_seconds = getattr(a, prefix + '_update_seconds')
        generation_seconds = getattr(a, prefix + '_generation_seconds')
        image_tasks[task_id] = {
            'outputs_per_checkpoint': image_outputs,
            'checkpoint_count': image_checkpoints,
            'main_test_images': image_outputs * image_checkpoints,
            'formal_training_gpu_hours': image_trained_checkpoints * a.image_updates * update_seconds * a.image_train_gpus / 3600 if update_seconds and not method_mode else None,
            'main_test_generation_gpu_hours': image_outputs * image_checkpoints * generation_seconds * a.image_inference_gpus / 3600 if generation_seconds else None,
        }
    return {'kind': 'PROVISIONAL_ESTIMATE_NOT_MEASURED_RESULT',
            'cost_mode': 'SIMPLIFIED_ESTIMATE', 'is_final_resource_budget': False,
            'videos_per_checkpoint': videos_per_checkpoint,
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
            'notes': ['Simplified mode uses one update time per task for all methods; it is not a final resource budget.',
                      'Use measured complete update costs including decoding, conditional gradients and backtracking.',
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
    p.add_argument('--method-costs', type=Path,
                   help='JSON training cost rows by task/method/config/hardware; no fallback to simplified training costs')
    a = p.parse_args()
    if a.acceptance and a.acceptance > 1:
        p.error('--acceptance must be in (0, 1]')
    try:
        costs = method_cost_plan(a.method_costs, a.train_seeds, a.trained_methods) if a.method_costs else None
        result = estimate(a, costs['scope']['required_methods'] if costs is not None else None)
        if costs is not None:
            result['cost_mode'] = 'METHOD_LEVEL_ESTIMATE'
            result['planning_scope'] = costs['planning_scope']
            result['method_cost_plan'] = costs
            result['formal_training_gpu_hours'] = costs['per_task']['T1']['formal_training_gpu_hours']
            for task in ('T2', 'T3'):
                result['image_task_plans'][task]['formal_training_gpu_hours'] = costs['per_task'][task]['formal_training_gpu_hours']
            result['notes'][0] = 'Method mode replaces training estimates only; generation estimates still use the existing CLI inputs.'
            result['notes'].extend([
                'Simplified training times, updates and GPU counts are ignored in method mode; JSON rows are authoritative.',
                'Main-test counts use each declared task method count and the single-checkpoint formula; additional configurations/repeats may require additional evaluation outputs.',
                'With required_methods, JSON method counts replace --trained-methods; without it, the initial eight-method matrix is required.',
                'Training costs exclude all other research costs listed below; this output is never a final budget or authorization.',
            ])
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
    except (OSError, UnicodeError, ValueError, OverflowError) as exc:
        p.error(str(exc))


if __name__ == '__main__':
    main()
