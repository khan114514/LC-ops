#!/usr/bin/env python3
"""Check deliverable structure and local references; never certifies experimental validity."""
import argparse
import csv
import json
import re
from pathlib import Path
from urllib.parse import unquote


def validate(root):
    errors = []
    required = ['README_先读这里.md', 'AGENTS.md', 'project.yaml', 'source/original_research_plan_zh.txt',
                'state/research-state.json', 'prompts/00_START_HERE_CN.md', 'specs/research_spec.md',
                'specs/experiment_matrix.csv', 'specs/three_task_protocol.md',
                'prompts/16_T2_CANNY_TASK.md', 'prompts/17_T3_POSE_TASK.md',
                'prompts/18_METHOD_SEARCH_AND_SELECTION.md', 'specs/execution_contract.md',
                'specs/method_search_and_selection.md', 'state/method_search.json',
                'templates/assignment.example.json', 'templates/completion_report.example.json',
                'templates/method_candidate.example.json', 'templates/method_costs.example.json', 'paper/main.tex']
    for name in required:
        if not (root / name).is_file():
            errors.append('Missing ' + name)
    for path in root.rglob('*.json'):
        try:
            json.loads(path.read_text(encoding='utf-8'))
        except (ValueError, UnicodeError) as exc:
            errors.append(str(path.relative_to(root)) + ': invalid JSON: ' + str(exc))
    skills = sorted((root / 'skills').glob('*/SKILL.md'))
    names = set()
    for path in skills:
        body = path.read_text(encoding='utf-8')
        header = re.match(r'^---\n(.*?)\n---\n', body, re.S)
        if not header:
            errors.append(str(path.relative_to(root)) + ': missing front matter')
            continue
        name = re.search(r'^name:\s*([a-z0-9-]+)\s*$', header[1], re.M)
        desc = re.search(r'^description:\s*\S.+$', header[1], re.M)
        if not name or not desc:
            errors.append(str(path.relative_to(root)) + ': missing name/description')
        elif name[1] != path.parent.name or name[1] in names:
            errors.append(str(path.relative_to(root)) + ': inconsistent/duplicate skill name')
        else:
            names.add(name[1])
    # Only authored Markdown links. Vendor/template snapshots may link to upstream resources
    # not distributed here. Code fences are examples, not navigational references.
    for path in root.rglob('*.md'):
        rel = path.relative_to(root)
        if 'vendor' in rel.parts or 'icml2026_reference' in rel.parts:
            continue
        body = re.sub(r'```.*?```', '', path.read_text(encoding='utf-8'), flags=re.S)
        for target in re.findall(r'\]\(([^)]+)\)', body):
            target = target.strip().strip('<>')
            if re.match(r'^[a-zA-Z]+:', target) or target.startswith('#') or '{' in target:
                continue
            target = unquote(target.split('#')[0])
            if target and not (path.parent / target).exists():
                errors.append(str(rel) + ': broken link ' + target)
    matrix = root / 'specs/experiment_matrix.csv'
    if matrix.exists():
        with matrix.open(encoding='utf-8', newline='') as h:
            rows = list(csv.DictReader(h))
        all_values = {str(value) for row in rows for value in row.values()}
        for method in ['S0', 'P', 'H0', 'H1', 'H2', 'O0', 'O1', 'C-H', 'C-O']:
            if method not in all_values:
                errors.append('Experiment matrix missing ' + method)
        for task_id in ['T1', 'T2', 'T3']:
            methods = {row.get('method') for row in rows if row.get('task_id') == task_id}
            for method in ['S0', 'P', 'H0', 'H1', 'H2', 'O0', 'O1', 'C-H', 'C-O']:
                if method not in methods:
                    errors.append(task_id + ' matrix missing ' + method)
    example = root / 'templates/run_manifest.example.json'
    if example.exists() and 'task_id' not in json.loads(example.read_text(encoding='utf-8')):
        errors.append('Run manifest template missing task_id')
    return {'check_kind': 'STRUCTURE_AND_LINKS_ONLY', 'skill_count': len(skills),
            'markdown_count': len(list(root.rglob('*.md'))), 'errors': errors,
            'status': 'PASS' if not errors else 'FAIL',
            'experimental_evidence_certified': False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    a = p.parse_args()
    result = validate(a.root.resolve())
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if not result['errors'] else 1)


if __name__ == '__main__':
    main()
