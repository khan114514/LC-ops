#!/usr/bin/env python3
"""Read-only local capability inventory. Does not inspect environment variables or credentials."""
import argparse
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Optional new JSON report; existing files are not overwritten')
    args = parser.parse_args()
    bundle = Path(__file__).resolve().parents[1]
    free = shutil.disk_usage(bundle).free
    result = {'report_kind': 'ENVIRONMENT_INVENTORY_NOT_EXPERIMENT', 'python': sys.version.split()[0],
              'system': platform.system(), 'machine': platform.machine(), 'free_disk_gib': round(free / 2**30, 2),
              'tools': {name: shutil.which(name) is not None for name in ['git', 'nvidia-smi', 'sbatch', 'squeue', 'latexmk', 'pdflatex']},
              'gpus': [], 'video_compatibility': 'UNVERIFIED', 'training_started': False}
    if result['tools']['nvidia-smi']:
        try:
            cmd = ['nvidia-smi', '--query-gpu=name,memory.total,driver_version', '--format=csv,noheader,nounits']
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if proc.returncode == 0:
                result['gpus'] = proc.stdout.strip().splitlines()
            else:
                result['gpu_query_status'] = 'FAILED'
        except (OSError, subprocess.TimeoutExpired):
            result['gpu_query_status'] = 'UNAVAILABLE'
    text = json.dumps(result, indent=2, ensure_ascii=False) + '\n'
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x', encoding='utf-8') as handle:
            handle.write(text)
    print(text, end='')


if __name__ == '__main__':
    main()
