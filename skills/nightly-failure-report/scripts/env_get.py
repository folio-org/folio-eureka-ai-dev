#!/usr/bin/env python3
"""Send one read-only GET request to a FOLIO environment and print the response.

Usage:
  python env_get.py <env name> <path?query> [--tenant <tenant>] [--max <chars>]
  python env_get.py --api <url> --login-tenant <tenant> --username <u> --password <p> <path?query> [--tenant <t>]

<env name> is an environment from the config (config.py show), e.g. snapshot or snapshot-ecs.
The second form is for a one-off environment; to reuse it, save it with config.py add-env instead.

Logs in as the environment's admin (POST /authn/login - the only non-GET request this script sends),
then GETs <path> with the token. --tenant sends the request to another tenant than the login one
(an ECS member tenant: log in to the central tenant, request with --tenant college).
The token is never printed. JSON responses are pretty-printed; --max cuts long output (default 20000 chars).
Exit code 3: the environment has no username/password yet - ask the user and save them with config.py set.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common  # noqa: E402


def login(api, tenant, username, password):
    req = urllib.request.Request(
        f'{api}/authn/login', method='POST',
        data=json.dumps({'username': username, 'password': password}).encode(),
        headers={'x-okapi-tenant': tenant, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read()
            cookies = r.headers.get_all('Set-Cookie') or []
    except urllib.error.HTTPError as e:
        sys.exit(f'login to {api} (tenant {tenant}) as {username} failed: HTTP {e.code} - '
                 'check the username/password saved in the config')
    try:
        token = json.loads(body).get('okapiToken')
    except ValueError:
        token = None
    if not token:
        for c in cookies:
            if c.startswith('folioAccessToken='):
                token = c.split('=', 1)[1].split(';', 1)[0]
    if not token:
        sys.exit('login response has no token (neither okapiToken nor folioAccessToken cookie)')
    return token


def main():
    args, opts, pos, i = sys.argv[1:], {}, [], 0
    while i < len(args):
        if args[i].startswith('--'):
            if i + 1 >= len(args):
                sys.exit(__doc__)
            opts[args[i][2:]] = args[i + 1]
            i += 2
        else:
            pos.append(args[i])
            i += 1

    if 'api' in opts:
        if len(pos) != 1 or not all(opts.get(k) for k in ('login-tenant', 'username', 'password')):
            sys.exit(__doc__)
        api, login_tenant, user, password, path = (opts['api'], opts['login-tenant'], opts['username'],
                                                   opts['password'], pos[0])
    else:
        if len(pos) != 2:
            sys.exit(__doc__)
        name, path = pos
        cfg = common.load_config()
        if name not in cfg.get('environments', {}):
            sys.exit(f"unknown environment {name!r}; known: {', '.join(cfg.get('environments', {}))}. "
                     'Add one with config.py add-env')
        p = f'environments.{name}'
        api, login_tenant, user, password = common.require(
            cfg, f'{p}.api', f'{p}.tenant', f'{p}.username', f'{p}.password')

    api = api.rstrip('/')
    token = login(api, login_tenant, user, password)
    url = f"{api}/{path.lstrip('/')}"
    # keep the query readable in commands, encode spaces/quotes here
    parts = urllib.parse.urlsplit(url)
    url = urllib.parse.urlunsplit(parts._replace(query=urllib.parse.quote(parts.query, safe='=&%+()*,:/<>!')))
    req = urllib.request.Request(url, headers={'x-okapi-tenant': opts.get('tenant', login_tenant),
                                               'x-okapi-token': token, 'Accept': 'application/json, text/plain'})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            status, body = r.status, r.read()
    except urllib.error.HTTPError as e:
        status, body = e.code, e.read()
    text = body.decode('utf-8', 'replace')
    try:
        text = json.dumps(json.loads(text), indent=1, ensure_ascii=False)
    except ValueError:
        pass
    limit = int(opts.get('max', 20000))
    print(f'HTTP {status} GET {path} (tenant {opts.get("tenant", login_tenant)})')
    print(text[:limit] + (f'\n... cut at {limit} of {len(text)} chars (use --max or a smaller limit=)' if len(text) > limit else ''))
    if status >= 400:
        sys.exit(1)


if __name__ == '__main__':
    main()
