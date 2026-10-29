#!/usr/bin/env python3
"""Manage the user's config (~/.folio-nightly-report/config.json): environments, TestRail, paths.

Usage:
  python config.py show                         print the config (passwords masked) and its location
  python config.py get <key>                    print one value, e.g. paths.stripes_testing_repo (passwords masked)
  python config.py set <key> <value>            save one value, e.g. environments.snapshot.username diku_admin
  python config.py add-env <name> --api <url> --tenant <tenant> [--ui <url>] [--members a,b]
                           [--username <u>] [--password <p>] [--description <text>]
                                                save a new environment (or update one) to reuse by name
  python config.py import-testrail <.env file>  copy TESTRAIL_BASE_URL/USERNAME/PASSWORD from a .env file
                                                (e.g. the one of a TestRail MCP server)
  python config.py workdir <name>               create (if needed) and print the work folder <work_dir>/<name>
  python config.py repo                         print the stripes-testing clone path, or exit 3 if not set

Keys are dotted paths into the JSON. The file is created from assets/config.template.json on first use;
it is written atomically and, on macOS/Linux, readable only by its owner.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402


def parse_opts(args):
    opts, i = {}, 0
    while i < len(args):
        if not args[i].startswith('--') or i + 1 >= len(args):
            sys.exit(__doc__)
        opts[args[i][2:]] = args[i + 1]
        i += 2
    return opts


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    cmd, rest = args[0], args[1:]
    cfg = common.load_config()

    if cmd == 'show':
        import json
        print(f'# {common.disp(common.CONFIG)}')
        print(json.dumps(common.mask(cfg), indent=2, ensure_ascii=False))
    elif cmd == 'get' and len(rest) == 1:
        v = common.get_key(cfg, rest[0])
        print('****' if v and common.is_secret(rest[0]) else ('' if v is None else v))
    elif cmd == 'set' and len(rest) == 2:
        common.set_key(cfg, rest[0], rest[1])
        common.save_config(cfg)
        print(f"{rest[0]} = {'****' if common.is_secret(rest[0]) else rest[1]}  (saved to {common.disp(common.CONFIG)})")
    elif cmd == 'add-env' and rest and not rest[0].startswith('--'):
        name, opts = rest[0], parse_opts(rest[1:])
        env = cfg.setdefault('environments', {}).setdefault(name, {'username': '', 'password': ''})
        if 'api' not in env and 'api' not in opts or 'tenant' not in env and 'tenant' not in opts:
            sys.exit('add-env needs --api and --tenant for a new environment')
        for k, v in opts.items():
            env[k] = [m.strip() for m in v.split(',') if m.strip()] if k == 'members' else v
        common.save_config(cfg)
        print(f'environment {name} saved to {common.disp(common.CONFIG)}: '
              + ', '.join(f"{k}={'****' if k == 'password' and v else v}" for k, v in env.items()))
        common.require(cfg, f'environments.{name}.username', f'environments.{name}.password')
    elif cmd == 'import-testrail' and len(rest) == 1:
        found = {}
        with open(os.path.expanduser(rest[0]), encoding='utf-8') as f:
            for line in f:
                if '=' in line and not line.lstrip().startswith('#'):
                    k, v = line.split('=', 1)
                    found[k.strip()] = v.strip().strip('"\'')
        mapping = {'TESTRAIL_BASE_URL': 'base_url', 'TESTRAIL_USERNAME': 'username', 'TESTRAIL_PASSWORD': 'password'}
        saved = [key for env, key in mapping.items() if found.get(env)]
        for env, key in mapping.items():
            if found.get(env):
                common.set_key(cfg, f'testrail.{key}', found[env])
        common.save_config(cfg)
        print(f"imported testrail.{', testrail.'.join(saved) or '(nothing)'} into {common.disp(common.CONFIG)}")
    elif cmd == 'workdir' and len(rest) == 1:
        path = os.path.join(common.work_root(cfg), rest[0])
        os.makedirs(path, exist_ok=True)
        print(path.replace('\\', '/'))
    elif cmd == 'repo' and not rest:
        repo = os.environ.get('STRIPES_TESTING_REPO') or common.get_key(cfg, 'paths.stripes_testing_repo')
        if not repo:
            common.require(cfg, 'paths.stripes_testing_repo')
        repo = os.path.abspath(os.path.expanduser(repo))
        if not os.path.isdir(os.path.join(repo, '.git')):
            sys.exit(f'{repo} is not a git clone; fix paths.stripes_testing_repo with: config.py set ...')
        print(repo.replace('\\', '/'))
    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
