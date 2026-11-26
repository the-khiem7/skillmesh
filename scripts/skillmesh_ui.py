# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Local control page for Skillmesh: a stdlib HTTP server on 127.0.0.1 and one static page.

Every operation calls the core in skillmesh.py. Apply is allowed only for rows of a scan
the server still holds, and only when a fresh scan with the same parameters gives the same
scan id, so what is applied is what the page showed.
"""
import contextlib
import hashlib
import hmac
import io
import json
import os
import secrets
import sys
import threading
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import skillmesh as core  # noqa: E402

INDEX = os.path.join(core.REPO, 'ui', 'index.html')
AGENTS = ('claude', 'kiro')
MAX_BODY = 64 * 1024
MAX_ITEMS = 500
MAX_SCANS = 20
MAX_RUNS = 50
MAX_OUT = 300

LOCK = threading.Lock()  # one operation at a time: scans, applies and stdout capture
SCANS = {}  # scan id -> {'target', 'no_hash', 'rows'}, newest last
TOKEN = secrets.token_urlsafe(32)
STARTED = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
RUNS = []  # runs of this server start, oldest first; memory only, nothing is written to disk
RUN_SEQ = [0]


class ApiError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


def scan_id(target, no_hash, rows):
    blob = json.dumps({'target': target, 'no_hash': no_hash, 'rows': rows}, sort_keys=True)
    return hashlib.sha256(blob.encode('utf-8')).hexdigest()[:16]


def summarize(rows):
    counts = {}
    for r in rows:
        counts[r['State']] = counts.get(r['State'], 0) + 1
    return counts


def load_cfg():
    if not os.path.exists(core.CFG_PATH):
        raise ApiError(400, 'skillmesh.config.json is missing; use Init, then edit it')
    return core.load_config()


def run_scan(cfg, target, no_hash):
    winners, conflicts = core.resolve_skills(cfg, core.find_skills(cfg))
    rows = []
    for tname, tpath in core.select_targets(cfg, target):
        rows.extend(core.scan_target(cfg, tname, tpath, winners, conflicts, None, no_hash))
    return winners, rows


def remember(cfg, winners, target, no_hash, rows):
    sid = scan_id(target, no_hash, rows)
    SCANS.pop(sid, None)
    SCANS[sid] = {'target': target, 'no_hash': no_hash, 'rows': rows}
    while len(SCANS) > MAX_SCANS:
        SCANS.pop(next(iter(SCANS)))
    return {'scanId': sid, 'scannedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'target': target,
            'noHash': no_hash, 'rows': rows, 'summary': summarize(rows),
            'sources': {name: w['source'] for name, w in winners.values()},
            'targetPaths': {n: cfg['targets'][n] for n in cfg['targets']}}


def need_choice(body, key, allowed):
    v = body.get(key)
    if not isinstance(v, str) or v not in allowed:
        raise ApiError(400, f'{key} must be one of {", ".join(allowed)}')
    return v


def api_scan(body):
    cfg = load_cfg()
    target = need_choice(body, 'target', core.valid_targets(cfg))
    no_hash = body.get('noHash')
    if not isinstance(no_hash, bool):
        raise ApiError(400, 'noHash must be true or false')
    try:
        winners, rows = run_scan(cfg, target, no_hash)
    except RuntimeError as e:
        raise ApiError(500, str(e))
    return remember(cfg, winners, target, no_hash, rows)


def api_apply(body):
    sid = body.get('scanId')
    items = body.get('items')
    if not isinstance(sid, str) or sid not in SCANS:
        raise ApiError(409, 'that scan is no longer held by the server; scan again')
    if not isinstance(items, list) or not items or len(items) > MAX_ITEMS:
        raise ApiError(400, f'items must be a list of 1 to {MAX_ITEMS} rows')
    rec = SCANS[sid]
    cfg = load_cfg()
    try:
        winners, fresh = run_scan(cfg, rec['target'], rec['no_hash'])
    except RuntimeError as e:
        raise ApiError(500, str(e))
    if scan_id(rec['target'], rec['no_hash'], fresh) != sid:
        raise ApiError(409, 'the filesystem changed since that scan; scan again and review it')
    index = {(r['Target'], r['Skill']): r for r in fresh}
    chosen = []
    for it in items:
        if not isinstance(it, dict) or not isinstance(it.get('target'), str) or not isinstance(it.get('skill'), str):
            raise ApiError(400, 'each item needs target and skill')
        r = index.get((it['target'], it['skill']))
        if r is None:
            raise ApiError(400, f"{it['target']}/{it['skill']} is not a row of that scan")
        if r['State'] not in core.FIX_STATES:
            raise ApiError(400, f"{r['Target']}/{r['Skill']} is {r['State']}, which Apply never changes")
        if (r['Target'], r['Skill']) in {(c['Target'], c['Skill']) for c in chosen}:
            raise ApiError(400, f"{r['Target']}/{r['Skill']} is listed twice")
        chosen.append(r)
    tpaths = dict(cfg['targets'])
    results = []
    for r in chosen:
        try:
            core.invoke_fix(cfg, r, tpaths[r['Target']], winners)
            results.append({'target': r['Target'], 'skill': r['Skill'], 'state': r['State'], 'ok': True})
        except (RuntimeError, OSError) as e:
            results.append({'target': r['Target'], 'skill': r['Skill'], 'state': r['State'], 'ok': False, 'error': str(e)})
    try:
        winners, rows = run_scan(cfg, rec['target'], rec['no_hash'])
    except RuntimeError as e:
        raise ApiError(500, str(e))
    SCANS.pop(sid, None)
    return {'results': results, 'scan': remember(cfg, winners, rec['target'], rec['no_hash'], rows)}


def api_doctor(body):
    cfg = load_cfg()
    checks = core.doctor_checks(cfg)
    issues = core.test_doctor(cfg)
    return {'ok': not issues, 'lines': ['Doctor: ok'] if not issues else [f'Doctor: {i}' for i in issues],
            'checks': [{k: c[k] for k in ('group', 'name', 'ok', 'detail')} for c in checks]}


def capture(fn):
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            fn()
    except (RuntimeError, OSError) as e:
        raise ApiError(500, str(e))
    return buf.getvalue().splitlines()


def link_agents(body):
    agents = body.get('agents')
    if not isinstance(agents, list) or not agents or any(a not in AGENTS for a in agents):
        raise ApiError(400, f'agents must be a non-empty list of {", ".join(AGENTS)}')
    return sorted(set(agents))


def api_link(body):
    agents = link_agents(body)
    preview = body.get('preview', False)
    if not isinstance(preview, bool):
        raise ApiError(400, 'preview must be true or false')
    if preview:
        return {'preview': True, 'plan': core.plan_link(agents)}
    lines = capture(lambda: core.invoke_link(agents))
    return {'preview': False, 'lines': lines, 'plan': core.plan_link(agents)}


def api_init(body):
    return {'lines': capture(lambda: core.main(['--mode', 'init']))}


def count_dirs(path):
    try:
        return sum(1 for _ in core.list_dirs(path))
    except OSError:
        return 0


def api_status(body):
    if not os.path.exists(core.CFG_PATH):
        return {'config': False, 'startedAt': STARTED, 'agents': list(AGENTS), 'configPath': core.CFG_PATH}
    cfg = load_cfg()
    targets = []
    for n, v in cfg['targets'].items():
        targets.append({'name': n, 'path': v, 'exists': os.path.exists(v),
                        'trash': count_dirs(os.path.join(v, cfg['trash_dir']))})
    return {'config': True, 'startedAt': STARTED, 'agents': list(AGENTS), 'trashDir': cfg['trash_dir'], 'configPath': core.CFG_PATH,
            'roots': cfg['roots'], 'targets': targets, 'validTargets': core.valid_targets(cfg),
            'ignore': len(cfg['ignore']), 'knownForeign': len(cfg['known_foreign']),
            'overrides': len(cfg['overrides'])}


def api_log(body):
    return {'startedAt': STARTED, 'runs': list(reversed(RUNS))}


def run_output(op, result):
    """(verdict, output lines) of a finished operation, for the Output log."""
    if op == 'scan':
        rows = result['rows']
        lines = [f"scan {result['target']} ({'no hash' if result['noHash'] else 'hash'}): {len(rows)} rows",
                 'Summary: ' + ' '.join(f'{k}={v}' for k, v in sorted(result['summary'].items()))]
        lines += [f"{r['State']:<12} {r['Target']} {r['Skill']}" for r in rows
                  if r['State'] != 'OK' and not (r['State'] == 'FOREIGN' and r['Detail'] == 'known')]
        return 'ok', lines
    if op == 'apply':
        lines = [('applied  ' if r['ok'] else 'FAILED   ') + f"{r['state']:<12} {r['target']} {r['skill']}"
                 + ('' if r['ok'] else f" - {r['error']}") for r in result['results']]
        return ('ok' if all(r['ok'] for r in result['results']) else 'issues'), lines
    if op == 'doctor':
        return ('ok' if result['ok'] else 'issues'), result['lines']
    if op == 'link':
        if result.get('preview'):
            return 'ok', [f"{i['state']:<9} {i['agent']} {i['skill']}" for i in result['plan']['items']]
        return ('issues' if any(x.startswith('SKIPPED') for x in result['lines']) else 'ok'), result['lines']
    return 'ok', result.get('lines', [])


def record_run(op, result=None, error=None):
    RUN_SEQ[0] += 1
    if error is not None:
        verdict, lines = 'error', [error]
    else:
        verdict, lines = run_output(op, result)
    RUNS.append({'id': RUN_SEQ[0], 'time': datetime.now().strftime('%H:%M:%S'), 'op': op,
                 'result': verdict, 'lines': lines[:MAX_OUT], 'truncated': max(0, len(lines) - MAX_OUT)})
    del RUNS[:-MAX_RUNS]


ROUTES = {'/api/scan': api_scan, '/api/apply': api_apply, '/api/doctor': api_doctor,
          '/api/link': api_link, '/api/init': api_init, '/api/status': api_status, '/api/log': api_log}
LOGGED = {'/api/scan': 'scan', '/api/apply': 'apply', '/api/doctor': 'doctor', '/api/link': 'link',
          '/api/init': 'init'}


class Handler(BaseHTTPRequestHandler):
    server_version = 'SkillmeshUI'
    sys_version = ''

    def log_message(self, fmt, *args):
        sys.stderr.write('%s %s\n' % (self.command, self.path))

    def hosts(self):
        port = self.server.server_address[1]
        return {f'127.0.0.1:{port}', f'localhost:{port}'}

    def send(self, status, body, ctype, extra=None):
        data = body if isinstance(body, bytes) else body.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Referrer-Policy', 'no-referrer')
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def fail(self, status, message):
        self.send(status, json.dumps({'error': message}), 'application/json; charset=utf-8')

    def host_ok(self):
        # A rebinding page reaches this server under its own hostname; refuse that Host.
        return self.headers.get('Host', '').lower() in self.hosts()

    def do_GET(self):
        if not self.host_ok():
            return self.fail(403, 'bad Host header')
        if self.path.split('?', 1)[0] not in ('/', '/index.html'):
            return self.fail(404, 'not found')
        try:
            with open(INDEX, encoding='utf-8') as f:
                page = f.read()
        except OSError:
            return self.fail(500, 'ui/index.html is missing')
        nonce = secrets.token_urlsafe(16)
        page = page.replace('__TOKEN__', TOKEN).replace('__NONCE__', nonce)
        # Fonts come from the Google Fonts CDN (stylesheet host and font-file host); nothing else is external.
        csp = (f"default-src 'none'; script-src 'nonce-{nonce}'; "
               f"style-src 'nonce-{nonce}' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; "
               "connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")
        self.send(200, page, 'text/html; charset=utf-8', {'Content-Security-Policy': csp})

    def do_POST(self):
        # Read the declared body before any refusal: replying with unread request data
        # makes Windows reset the connection and the client never sees the status.
        try:
            length = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            self.close_connection = True
            return self.fail(400, 'bad Content-Length')
        if length < 0 or length > MAX_BODY:
            self.close_connection = True
            return self.fail(413, 'body too large')
        raw = self.rfile.read(length)
        if not self.host_ok():
            return self.fail(403, 'bad Host header')
        port = self.server.server_address[1]
        if self.headers.get('Origin') not in {f'http://127.0.0.1:{port}', f'http://localhost:{port}'}:
            return self.fail(403, 'bad or missing Origin')
        if not hmac.compare_digest(self.headers.get('X-Skillmesh-Token', ''), TOKEN):
            return self.fail(403, 'bad or missing token')
        handler = ROUTES.get(self.path)
        if handler is None:
            return self.fail(404, 'not found')
        if self.headers.get('Content-Type', '').split(';')[0].strip().lower() != 'application/json':
            return self.fail(415, 'Content-Type must be application/json')
        try:
            body = json.loads(raw or b'{}')
        except ValueError:
            return self.fail(400, 'body is not JSON')
        if not isinstance(body, dict):
            return self.fail(400, 'body must be a JSON object')
        op = LOGGED.get(self.path)
        try:
            with LOCK:
                result = handler(body)
                if op and not (op == 'link' and result.get('preview')):
                    record_run(op, result)
        except ApiError as e:
            if op:
                with LOCK:
                    record_run(op, error=f'{e.status}: {e.message}')
            return self.fail(e.status, e.message)
        except Exception as e:  # keep the server alive; the message stays local
            if op:
                with LOCK:
                    record_run(op, error=f'{type(e).__name__}: {e}')
            return self.fail(500, f'{type(e).__name__}: {e}')
        self.send(200, json.dumps(result), 'application/json; charset=utf-8')


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(prog='skillmesh_ui.py')
    ap.add_argument('--port', type=int, default=8765, help='port on 127.0.0.1 (0 picks a free one)')
    ap.add_argument('--no-open', action='store_true', help='do not open the browser')
    a = ap.parse_args(argv)
    srv = ThreadingHTTPServer(('127.0.0.1', a.port), Handler)
    url = f'http://127.0.0.1:{srv.server_address[1]}/'
    print(f'Skillmesh control page: {url}  (Ctrl+C to stop)')
    if not a.no_open:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
