#!/usr/bin/env python3
"""CLI regression tests. All measurements below are synthetic test inputs, not research evidence."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name('cost_plan.py')
METHODS = ('P', 'H0', 'H1', 'H2', 'O0', 'O1', 'C-H', 'C-O')
SEEDS = [11, 22, 33]
RATES = (1, 2, 3, 4, 20, 25, 1.5, 15)


def fixture():
    return {
        'schema_version': 1,
        'train_seeds': SEEDS.copy(),
        'rows': [
            {'task_id': task, 'method': method, 'config_id': 'test-config',
             'hardware_id': 'test-hardware', 'updates': 10,
             'train_seeds': SEEDS.copy(), 'repeats': 2, 'gpu_count': 2,
             'update_seconds': rate * factor,
             'measurement_run_id': 'SYNTHETIC_TEST_ONLY-' + task + '-' + method}
            for factor, task in enumerate(('T1', 'T2', 'T3'), 1)
            for method, rate in zip(METHODS, RATES)
        ],
    }


def candidate_fixture():
    document = fixture()
    document['required_methods'] = {
        'T1': ['P', 'Candidate-A'],
        'T2': ['P'],
        'T3': ['P', 'Candidate-B', 'Candidate-C'],
    }
    template = document['rows'][0]
    document['rows'] = [{**copy.deepcopy(template), 'task_id': task, 'method': method}
                        for task, methods in document['required_methods'].items() for method in methods]
    return document


class CostPlanTests(unittest.TestCase):
    def cli(self, *args, document=None, raw=None):
        with tempfile.TemporaryDirectory() as temporary:
            if document is not None or raw is not None:
                path = Path(temporary) / 'costs.json'
                path.write_text(raw if raw is not None else json.dumps(document), encoding='utf-8')
                args = ('--method-costs', str(path), *args)
            return subprocess.run([sys.executable, str(SCRIPT), *args],
                                  capture_output=True, text=True, check=False)

    def output(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def rejected(self, document, message):
        result = self.cli(document=document)
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn(message, result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_legacy_default_quantities_and_unknown_costs(self):
        result = self.output(self.cli())
        self.assertEqual(result['main_test_videos'], 40000)
        self.assertEqual(result['total_main_test_images'], 100000)
        self.assertEqual(result['image_task_plans']['T2']['main_test_images'], 50000)
        self.assertIsNone(result['formal_training_gpu_hours'])
        self.assertEqual(result['cost_mode'], 'SIMPLIFIED_ESTIMATE')
        self.assertFalse(result['is_final_resource_budget'])

    def test_legacy_measured_estimate_remains_compatible(self):
        result = self.output(self.cli('--update-seconds', '2', '--train-gpus', '2',
                                      '--canny-update-seconds', '3', '--pose-update-seconds', '5',
                                      '--generation-seconds', '4', '--acceptance', '0.5',
                                      '--teacher-generation-seconds', '2'))
        self.assertEqual(result['formal_training_gpu_hours'], 80)
        self.assertEqual(result['image_task_plans']['T2']['formal_training_gpu_hours'], 60)
        self.assertEqual(result['image_task_plans']['T3']['formal_training_gpu_hours'], 100)
        self.assertEqual(result['raw_teacher_candidates_estimate'], 16384)
        self.assertAlmostEqual(result['main_test_generation_gpu_hours'], 40000 * 4 / 3600)

    def test_method_mode_does_not_evaluate_ignored_simple_training_costs(self):
        result = self.output(self.cli('--update-seconds', '1e308', '--updates', '1' + '0' * 400,
                                      document=fixture()))
        self.assertIsNotNone(result['formal_training_gpu_hours'])

    def test_method_specific_costs_sum_seeds_repeats_gpus_and_configurations(self):
        document = fixture()
        extra = copy.deepcopy(document['rows'][3])
        extra.update(config_id='test-extra-config', updates=5, repeats=1,
                     gpu_count=1, update_seconds=8)
        document['rows'].append(extra)
        result = self.output(self.cli(document=document))
        plan = result['method_cost_plan']
        per_task = sum(RATES) * 10 * 3 * 2 * 2 / 3600
        extra_hours = 5 * 3 * 8 / 3600
        self.assertEqual(result['cost_mode'], 'METHOD_LEVEL_ESTIMATE')
        self.assertEqual(plan['coverage_status'], 'COMPLETE')
        self.assertEqual(plan['measurement_status'], 'COMPLETE')
        self.assertAlmostEqual(result['formal_training_gpu_hours'], per_task + extra_hours)
        self.assertAlmostEqual(result['image_task_plans']['T2']['formal_training_gpu_hours'], per_task * 2)
        self.assertAlmostEqual(plan['total_formal_training_gpu_hours'], per_task * 6 + extra_hours)
        self.assertEqual(plan['rows'][3]['measurement_run_id'], 'SYNTHETIC_TEST_ONLY-T1-H2')
        self.assertEqual(result['main_test_videos'], 40000)
        self.assertEqual(result['total_main_test_images'], 100000)
        self.assertFalse(result['is_final_resource_budget'])
        self.assertEqual(plan['planning_scope'], 'DEFAULT_INITIAL_MATRIX')

    def test_explicit_candidate_methods_define_coverage_and_test_counts(self):
        document = candidate_fixture()
        result = self.output(self.cli(document=document))
        plan = result['method_cost_plan']
        self.assertEqual(plan['planning_scope'], 'EXPLICIT_METHOD_MATRIX')
        self.assertEqual(plan['scope']['required_methods'], document['required_methods'])
        self.assertEqual(plan['status'], 'COMPLETE')
        self.assertEqual(result['trained_checkpoints'], 6)
        self.assertEqual(result['main_test_videos'], 11200)
        self.assertEqual(result['image_task_plans']['T2']['main_test_images'], 8000)
        self.assertEqual(result['image_task_plans']['T3']['main_test_images'], 20000)
        self.assertEqual(result['total_main_test_images'], 28000)
        self.assertFalse(plan['scope']['matches_initial_method_matrix'])

    def test_missing_declared_candidate_keeps_coverage_incomplete(self):
        document = candidate_fixture()
        document['rows'] = [row for row in document['rows'] if row['method'] != 'Candidate-A']
        result = self.output(self.cli(document=document))
        plan = result['method_cost_plan']
        self.assertEqual(plan['coverage_status'], 'INCOMPLETE')
        self.assertEqual(len(plan['missing_coverage']), 3)
        self.assertEqual(plan['missing_coverage'][0]['method'], 'Candidate-A')
        self.assertIsNone(plan['total_formal_training_gpu_hours'])

    def test_undeclared_method_rejected_in_explicit_matrix(self):
        document = candidate_fixture()
        document['rows'][0]['method'] = 'Unregistered-Candidate'
        self.rejected(document, 'undeclared training method')

    def test_invalid_required_method_declarations_rejected(self):
        for methods in ([], ['P', 'P'], [''], ['../candidate'], ['S0'], [True]):
            with self.subTest(methods=methods):
                document = candidate_fixture()
                document['required_methods']['T1'] = methods
                self.rejected(document, 'required_methods')
        document = candidate_fixture()
        del document['required_methods']['T3']
        self.rejected(document, 'required_methods')

    def test_declared_matrix_replaces_simplified_method_count(self):
        result = self.output(self.cli('--trained-methods', '99', document=candidate_fixture()))
        self.assertEqual(result['trained_checkpoints'], 6)
        self.assertEqual(result['main_test_videos'], 11200)

    def test_missing_method_does_not_fall_back_to_cli_or_zero(self):
        document = fixture()
        document['rows'].pop()
        result = self.output(self.cli('--pose-update-seconds', '999', document=document))
        plan = result['method_cost_plan']
        self.assertEqual(plan['coverage_status'], 'INCOMPLETE')
        self.assertEqual(len(plan['missing_coverage']), 3)
        self.assertIsNone(plan['total_formal_training_gpu_hours'])
        self.assertIsNone(result['image_task_plans']['T3']['formal_training_gpu_hours'])
        self.assertGreater(plan['known_training_gpu_hours'], 0)
        self.assertIsNotNone(result['formal_training_gpu_hours'])

    def test_unmeasured_row_keeps_task_and_total_unknown(self):
        document = fixture()
        document['rows'][0].update(update_seconds=None, measurement_run_id=None)
        result = self.output(self.cli('--update-seconds', '999', document=document))
        plan = result['method_cost_plan']
        self.assertEqual(plan['coverage_status'], 'COMPLETE')
        self.assertEqual(plan['measurement_status'], 'INCOMPLETE')
        self.assertIsNone(plan['rows'][0]['training_gpu_hours'])
        self.assertIsNone(result['formal_training_gpu_hours'])
        self.assertIsNone(plan['total_formal_training_gpu_hours'])
        self.assertEqual(plan['unmeasured_rows'], [0])

    def test_missing_measurement_reference_or_identity_is_incomplete(self):
        for field in ('measurement_run_id', 'config_id', 'hardware_id', 'gpu_count'):
            with self.subTest(field=field):
                document = fixture()
                document['rows'][0][field] = None
                result = self.output(self.cli(document=document))
                plan = result['method_cost_plan']
                self.assertEqual(plan['measurement_status'], 'INCOMPLETE')
                self.assertIsNone(plan['rows'][0]['training_gpu_hours'])
                self.assertIsNone(plan['total_formal_training_gpu_hours'])
                self.assertIn(field, plan['rows'][0]['missing_measurement_fields'])

    def test_missing_seed_is_incomplete_even_when_other_seeds_repeat(self):
        document = fixture()
        document['rows'][0]['train_seeds'] = [11, 22]
        document['rows'][0]['repeats'] = 5
        result = self.output(self.cli(document=document))
        self.assertEqual(result['method_cost_plan']['missing_coverage'],
                         [{'task_id': 'T1', 'method': 'P', 'train_seed': 33}])
        self.assertIsNone(result['formal_training_gpu_hours'])

    def test_duplicate_row_rejected(self):
        document = fixture()
        document['rows'].append(copy.deepcopy(document['rows'][0]))
        self.rejected(document, 'duplicate row')

    def test_same_config_seed_on_two_hardware_rows_rejected(self):
        document = fixture()
        duplicate = copy.deepcopy(document['rows'][0])
        duplicate['hardware_id'] = 'other-hardware'
        document['rows'].append(duplicate)
        self.rejected(document, 'duplicate planned seed')

    def test_invalid_row_values_rejected(self):
        cases = [
            ('task_id', 'T4', 'unknown task_id'),
            ('method', 'S0', 'unknown training method'),
            ('update_seconds', -1, 'update_seconds'),
            ('update_seconds', 0, 'update_seconds'),
            ('update_seconds', '2', 'update_seconds'),
            ('update_seconds', True, 'update_seconds'),
            ('gpu_count', -2, 'gpu_count'),
            ('gpu_count', 1.5, 'gpu_count'),
            ('updates', 0, 'updates'),
            ('updates', True, 'updates'),
            ('repeats', -1, 'repeats'),
            ('train_seeds', [11, 11, 33], 'duplicate train seed'),
            ('train_seeds', [11, 22, 44], 'undeclared train seed'),
            ('train_seeds', [True], 'train_seeds'),
            ('train_seeds', [], 'train_seeds'),
            ('measurement_run_id', '', 'measurement_run_id'),
            ('config_id', '', 'config_id'),
            ('hardware_id', '', 'hardware_id'),
        ]
        for field, value, message in cases:
            with self.subTest(field=field, value=value):
                document = fixture()
                document['rows'][0][field] = value
                self.rejected(document, message)

    def test_non_finite_and_overflow_inputs_rejected(self):
        for value in (float('nan'), float('inf'), -float('inf'), 1e308):
            with self.subTest(value=value):
                document = fixture()
                document['rows'][0]['update_seconds'] = value
                self.rejected(document, 'finite')
        raw = json.dumps(fixture()).replace('"update_seconds": 1,', '"update_seconds": 1e400,', 1)
        result = self.cli(raw=raw)
        self.assertEqual(result.returncode, 2)
        self.assertIn('finite', result.stderr)

    def test_numeric_underflow_cannot_produce_a_zero_cost_measurement(self):
        document = fixture()
        document['rows'][0]['update_seconds'] = 5e-324
        self.rejected(document, 'positive')

    def test_malformed_structure_and_unknown_keys_rejected(self):
        cases = [([], 'object'), ({}, 'fields'),
                 ({**fixture(), 'rows': {}}, 'rows'),
                 ({**fixture(), 'schema_version': 2}, 'schema_version'),
                 ({**fixture(), 'extra': 1}, 'fields')]
        for document, message in cases:
            with self.subTest(message=message):
                self.rejected(document, message)
        document = fixture()
        document['rows'][0]['update_second'] = 2
        self.rejected(document, 'fields')

    def test_duplicate_json_keys_rejected(self):
        raw = json.dumps(fixture()).replace('"schema_version": 1',
                                            '"schema_version": 1, "schema_version": 1', 1)
        result = self.cli(raw=raw)
        self.assertEqual(result.returncode, 2)
        self.assertIn('duplicate JSON key', result.stderr)

    def test_cli_method_and_seed_counts_must_match_declared_plan(self):
        for args in (('--trained-methods', '2'), ('--train-seeds', '2')):
            result = self.cli(*args, document=fixture())
            self.assertEqual(result.returncode, 2)
            self.assertIn('must match', result.stderr)

    def test_empty_table_reports_missing_all_required_coverage(self):
        document = fixture()
        document['rows'] = []
        result = self.output(self.cli(document=document))
        plan = result['method_cost_plan']
        self.assertEqual(len(plan['missing_coverage']), 72)
        self.assertIsNone(plan['total_formal_training_gpu_hours'])
        self.assertEqual(plan['known_training_gpu_hours'], 0)
        self.assertIsNone(result['formal_training_gpu_hours'])

    def test_reduced_seed_scope_is_explicit_and_counts_follow_legacy_formula(self):
        document = fixture()
        document['train_seeds'] = [11]
        for row in document['rows']:
            row['train_seeds'] = [11]
        result = self.output(self.cli('--train-seeds', '1', document=document))
        plan = result['method_cost_plan']
        self.assertEqual(plan['scope']['train_seeds'], [11])
        self.assertFalse(plan['scope']['matches_default_seed_count'])
        self.assertEqual(plan['coverage_status'], 'COMPLETE')
        self.assertEqual(result['main_test_videos'], 14400)

    def test_distributed_template_is_unmeasured_and_not_evidence(self):
        path = SCRIPT.parent.parent / 'templates/method_costs.example.json'
        result = self.output(self.cli('--method-costs', str(path)))
        plan = result['method_cost_plan']
        self.assertEqual(plan['coverage_status'], 'COMPLETE')
        self.assertEqual(plan['measurement_status'], 'INCOMPLETE')
        self.assertEqual(len(plan['unmeasured_rows']), 24)
        self.assertIsNone(plan['total_formal_training_gpu_hours'])
        self.assertFalse(plan['source_runs_verified'])


if __name__ == '__main__':
    unittest.main()
