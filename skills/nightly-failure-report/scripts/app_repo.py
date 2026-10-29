#!/usr/bin/env python3
"""Clone (or update) a FOLIO module, backend or UI, so you can grep its code and read its history.

Usage: python app_repo.py <repo name, e.g. mod-orders or ui-users>

The clone has full commit history but no file contents up front (blobless), so it is fast.
Clones live in one shared cache outside any workspace, so IDEs do not pick them up as repositories:
paths.repos_dir in the config, FOLIO_REPOS_DIR, or ~/.cache/folio-repos. An existing clone is updated
to the latest default branch. Prints the local path and the HEAD commit to cite as "ref".
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402


def git(*args):
    r = subprocess.run(['git', *args], capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        sys.exit(f"git {' '.join(args)} failed:\n{r.stderr.strip()}")
    return r.stdout.strip()


def main():
    if len(sys.argv) != 2 or sys.argv[1].startswith('-'):
        sys.exit(__doc__)
    repo = sys.argv[1]
    root = common.repos_dir(common.load_config())
    path = os.path.join(root, repo)
    if not os.path.isdir(os.path.join(path, '.git')):
        os.makedirs(root, exist_ok=True)
        git('clone', '-q', '--filter=blob:none', f'https://github.com/folio-org/{repo}.git', path)
    else:
        git('-C', path, 'fetch', '-q', 'origin')
        git('-C', path, 'checkout', '-q', '--detach', 'origin/HEAD')
    ref, day = git('-C', path, 'log', '-1', '--format=%h %cd', '--date=short').split()
    print(f"{path.replace(os.sep, '/')} ref={ref} ({day})")


if __name__ == '__main__':
    main()
