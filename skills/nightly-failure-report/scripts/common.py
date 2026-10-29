"""Shared helpers: UTF-8 console output and the user's config file.

Importing this module switches stdout/stderr to UTF-8, so the scripts print the same on every OS
(the Windows console default, cp1252, cannot print the arrows and dashes they use).

The config lives outside the skill and outside any repository, so skill updates do not overwrite it
and it cannot be committed by accident:
    ~/.folio-nightly-report/config.json      (FOLIO_NIGHTLY_HOME overrides the folder)
It is created from assets/config.template.json on first use. Manage it with config.py.
"""
import copy
import json
import os
import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(SKILL_DIR, 'assets', 'config.template.json')
HOME = os.path.abspath(os.path.expanduser(os.environ.get('FOLIO_NIGHTLY_HOME') or '~/.folio-nightly-report'))
CONFIG = os.path.join(HOME, 'config.json')
SECRET_KEYS = ('password',)
MISSING_EXIT = 3  # exit code when a config value must be asked from the user


def disp(path):
    """A path as printed for the user and agent: forward slashes on every OS."""
    return str(path).replace(os.sep, '/')


def _merge_defaults(cfg, defaults):
    """Add keys that exist in the template but not in the user's file (new skill versions)."""
    for k, v in defaults.items():
        if k not in cfg:
            cfg[k] = copy.deepcopy(v)
        elif isinstance(v, dict) and isinstance(cfg[k], dict) and k != 'environments':
            _merge_defaults(cfg[k], v)
    return cfg


def load_config():
    with open(TEMPLATE, encoding='utf-8') as f:
        defaults = json.load(f)
    if not os.path.exists(CONFIG):
        save_config(defaults)
        return defaults
    with open(CONFIG, encoding='utf-8') as f:
        cfg = json.load(f)
    # environments shipped with the template are added if the user has none of that name
    for name, env in defaults.get('environments', {}).items():
        cfg.setdefault('environments', {}).setdefault(name, env)
    return _merge_defaults(cfg, defaults)


def save_config(cfg):
    os.makedirs(HOME, exist_ok=True)
    tmp = CONFIG + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
        f.write('\n')
    os.replace(tmp, CONFIG)
    if os.name != 'nt':
        os.chmod(CONFIG, 0o600)


def get_key(cfg, dotted):
    node = cfg
    for part in dotted.split('.'):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node


def set_key(cfg, dotted, value):
    parts = dotted.split('.')
    node = cfg
    for part in parts[:-1]:
        node = node.setdefault(part, {})
        if not isinstance(node, dict):
            sys.exit(f'{dotted}: {part} is not an object')
    node[parts[-1]] = value


def is_secret(dotted):
    return dotted.split('.')[-1].lower() in SECRET_KEYS


def mask(cfg):
    def walk(node):
        if isinstance(node, dict):
            return {k: ('****' if k.lower() in SECRET_KEYS and v else walk(v)) for k, v in node.items()}
        return node
    return walk(cfg)


def require(cfg, *dotted):
    """Return the values of the given keys, or stop with a message telling the agent what to ask."""
    missing = [k for k in dotted if get_key(cfg, k) in (None, '')]
    if missing:
        print(f'MISSING CONFIG: {", ".join(missing)}\n'
              f'Ask the user for the value(s), then save them (they are reused in later runs):\n'
              + '\n'.join(f'  python "{disp(os.path.join(SKILL_DIR, "scripts", "config.py"))}" set {k} "<value>"'
                          for k in missing)
              + f'\nor let the user edit {disp(CONFIG)} directly.', file=sys.stderr)
        sys.exit(MISSING_EXIT)
    return [get_key(cfg, k) for k in dotted]


def path_setting(cfg, key, env_var, default):
    return os.path.abspath(os.path.expanduser(os.environ.get(env_var) or get_key(cfg, key) or default))


def work_root(cfg):
    return path_setting(cfg, 'paths.work_dir', 'NIGHTLY_TRIAGE_DIR', os.path.join(HOME, 'runs'))


def repos_dir(cfg):
    return path_setting(cfg, 'paths.repos_dir', 'FOLIO_REPOS_DIR', '~/.cache/folio-repos')


def testrail(cfg):
    """TestRail base URL and auth headers. TESTRAIL_* environment variables override the config."""
    import base64
    vals = {key: os.environ.get(env) or get_key(cfg, f'testrail.{key}')
            for key, env in (('base_url', 'TESTRAIL_BASE_URL'), ('username', 'TESTRAIL_USERNAME'),
                             ('password', 'TESTRAIL_PASSWORD'))}
    require(cfg, *[f'testrail.{k}' for k, v in vals.items() if not v])
    auth = base64.b64encode(f"{vals['username']}:{vals['password']}".encode()).decode()
    return vals['base_url'].rstrip('/'), {'Authorization': 'Basic ' + auth, 'Content-Type': 'application/json'}
