#!/usr/bin/env python3
"""Show recent commits that touched a file (or a line range) in a cloned module, with their Jira keys.

Use it to prove a UI/API change was intended (outdated test) or to find the change that broke it (app bug).

Usage: python ticket.py <repo> <path> [<from line>,<to line>] [--since 6.months]

Clone the module first with app_repo.py.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402


def main():
    args = sys.argv[1:]
    since = '6.months'
    if '--since' in args:
        i = args.index('--since')
        if i + 1 >= len(args):
            sys.exit(__doc__)
        since = args[i + 1]
        del args[i:i + 2]
    if len(args) not in (2, 3):
        sys.exit(__doc__)
    repo, path, line_range = args[0], args[1], (args[2] if len(args) == 3 else None)
    clone = os.path.join(common.repos_dir(common.load_config()), repo)
    if not os.path.isdir(os.path.join(clone, '.git')):
        sys.exit(f'clone first: python app_repo.py {repo}')

    cmd = ['git', '-C', clone, 'log', f'--since={since}', '-n', '8', '--format=%h %cd %s', '--date=short']
    cmd += ['-L', f'{line_range}:{path}', '--no-patch'] if line_range else ['--', path]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        sys.exit(r.stderr.strip())
    lines = [l for l in r.stdout.splitlines() if l.strip()]
    for l in lines:
        print('  ' + l)
    if not lines:
        print(f'  no commits since {since}')
    for key in sorted(set(re.findall(r'\b[A-Z][A-Z0-9]+-\d+\b', '\n'.join(lines)))):
        print(f'jira: {key}')


if __name__ == '__main__':
    main()
