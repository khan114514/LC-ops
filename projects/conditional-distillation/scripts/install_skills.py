#!/usr/bin/env python3
"""Install CDist project skills without changing global configuration or running research."""
import argparse
import re
import shutil
from pathlib import Path


def install(bundle, destination):
    sources = sorted((bundle / 'skills').glob('cdist-*'))
    if not sources:
        raise ValueError('No CDist skills found')
    destination = destination.expanduser().resolve()
    # Refuse before writing anything if a destination conflicts.
    conflicts = [str(destination / src.name) for src in sources if (destination / src.name).exists()]
    if conflicts:
        raise ValueError('Existing skills; choose a fresh destination: ' + ', '.join(conflicts))
    if any(destination == src.resolve() or src.resolve() in destination.parents for src in sources):
        raise ValueError('Destination cannot be inside a source skill')
    # Copy shared project resources into each installed skill, then rebase only actual
    # Markdown links. Runtime research paths still resolve against the active project.
    roots = ['specs', 'prompts', 'templates', 'literature', 'scripts']
    for src in sources:
        target = destination / src.name
        target.mkdir(parents=True)
        try:
            shutil.copytree(src, target, dirs_exist_ok=True)
            for name in roots:
                origin = bundle / name
                if origin.is_dir():
                    shutil.copytree(origin, target / 'references' / name, dirs_exist_ok=True,
                                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            text = (target / 'SKILL.md').read_text(encoding='utf-8')
            text = re.sub(r'\]\(\.\./\.\./(specs|prompts|templates|literature)/', r'](references/\1/', text)
            text += '\n\n安装说明：本技能的 references 是安装时的交接快照。执行时先定位实际研究根目录，优先读取当前项目的同名规范、状态与分配；不要把快照当成最新实验结果。\n'
            (target / 'SKILL.md').write_text(text, encoding='utf-8')
        except Exception:
            # Only this invocation's new target can be removed.
            shutil.rmtree(target)
            raise
    return [str(destination / src.name) for src in sources]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', required=True, type=Path, help='Actual skill discovery directory supported by your Codex host')
    args = parser.parse_args()
    bundle = Path(__file__).resolve().parents[1]
    try:
        paths = install(bundle, args.destination)
    except (OSError, ValueError) as exc:
        parser.exit(1, str(exc) + '\n')
    print('\n'.join(paths))
    print('Installed instruction files only. No experiment or API call was started.')


if __name__ == '__main__':
    main()
