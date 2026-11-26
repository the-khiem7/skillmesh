# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Skillmesh core in Python: same modes and switches as scripts/Skillmesh.ps1.

Junction handling: junctions are created with `mklink /J` (CPython has no public
API) and removed only with os.rmdir, which removes the link and never the
content behind it. shutil.rmtree is never used.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG_PATH = os.path.join(REPO, 'skillmesh.config.json')
EXAMPLE_PATH = os.path.join(REPO, 'skillmesh.config.example.json')
STATE_FILE = os.path.join(REPO, 'state', 'last-scan.py.json')
FIX_STATES = ('MISSING', 'COPY', 'WRONG-TARGET', 'BROKEN')
REPARSE = 0x400
DIRECTORY = 0x10


def full_path(p):
    return os.path.abspath(p).rstrip('\\')


def same_path(a, b):
    return full_path(a).lower() == full_path(b).lower()


def lower_set(values):
    return {str(v).lower() for v in values}


def link_info(p):
    """(kind, target) for a junction or symlink, else (None, None)."""
    if os.path.isjunction(p):
        kind = 'Junction'
    elif os.path.islink(p):
        kind = 'SymbolicLink'
    else:
        return None, None
    t = os.readlink(p)
    for prefix in ('\\\\?\\', '\\??\\'):
        if t.startswith(prefix):
            t = t[len(prefix):]
    return kind, t


CMD_UNSAFE = set('&|<>^%"!()') | {chr(c) for c in range(32)}


def make_junction(path, target):
    # cmd.exe re-parses the command line, and subprocess only quotes spaces, so a
    # directory name holding a cmd metacharacter would run as a second command.
    for p in (path, target):
        bad = sorted({c for c in p if c in CMD_UNSAFE})
        if bad:
            raise RuntimeError(f'refusing to pass a path with cmd metacharacters {bad!r} to mklink: {p!r}')
    if os.path.lexists(path):
        raise RuntimeError(f'cannot create junction, path exists: {path}')
    r = subprocess.run(['cmd', '/c', 'mklink', '/J', path, target], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f'mklink failed for {path}: {r.stdout.strip()} {r.stderr.strip()}')


def remove_link_only(path):
    """Remove a junction or symlink as a link; refuse anything else."""
    kind, _ = link_info(path)
    if kind is None:
        raise RuntimeError(f'refusing to remove a non-link: {path}')
    os.rmdir(path)


def load_config():
    with open(CFG_PATH, encoding='utf-8-sig') as f:
        cfg = json.load(f)
    cfg['roots'] = [os.path.expandvars(r) for r in cfg.get('roots', [])]
    cfg['targets'] = {k: os.path.expandvars(v) for k, v in cfg.get('targets', {}).items()}
    cfg.setdefault('ignore', [])
    cfg.setdefault('known_foreign', [])
    cfg.setdefault('overrides', {})
    cfg.setdefault('trash_dir', '.trash')
    return cfg


def list_dirs(path):
    out = []
    with os.scandir(path) as it:
        for e in it:
            attrs = e.stat(follow_symlinks=False).st_file_attributes
            if attrs & DIRECTORY:
                out.append((e.name, e.path, bool(attrs & REPARSE)))
    return out


def find_skills(cfg):
    found = []
    ignore = lower_set(cfg['ignore'])
    for root in cfg['roots']:
        root_n = full_path(root)
        stack = [root_n]
        while stack:
            d = stack.pop()
            for name, path, is_reparse in list_dirs(d):
                if name.startswith('.') or name == 'node_modules':
                    continue
                if is_reparse:
                    continue
                rel = path[len(root_n) + 1:]
                if rel.lower() in ignore:
                    continue
                if os.path.exists(os.path.join(path, 'SKILL.md')):
                    found.append({'name': name, 'source': path, 'rel': rel, 'depth': len(rel.split('\\'))})
                else:
                    stack.append(path)
    return found


def resolve_skills(cfg, skills):
    """One winner per name: override first, else shallowest; equal depth is a conflict."""
    groups = {}
    for s in skills:
        groups.setdefault(s['name'].lower(), []).append(s)
    overrides = {k.lower(): v for k, v in cfg['overrides'].items()}
    winners, conflicts = {}, {}
    for key, group in groups.items():
        name = group[0]['name']
        cands = sorted(group, key=lambda c: (c['depth'], c['rel'].lower()))
        pick = None
        if key in overrides:
            pick = next((c for c in cands if c['rel'].lower() == str(overrides[key]).lower()), None)
        elif len(cands) == 1:
            pick = cands[0]
        elif cands[0]['depth'] < cands[1]['depth']:
            pick = cands[0]
        if pick:
            winners[key] = (name, pick)
        else:
            conflicts[key] = (name, cands)
    return winners, conflicts


def tree_map(p):
    base = len(full_path(p)) + 1
    out = {}
    for dirpath, dirnames, filenames in os.walk(p):
        if '.git' in dirnames:
            dirnames.remove('.git')
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            h = hashlib.sha256()
            with open(fp, 'rb') as f:
                for chunk in iter(lambda: f.read(1 << 20), b''):
                    h.update(chunk)
            out[fp[base:].lower()] = h.hexdigest()
    return out


def compare_trees(src, copy):
    a, b = tree_map(src), tree_map(copy)
    only_src = sum(1 for k in a if k not in b)
    only_copy = sum(1 for k in b if k not in a)
    changed = sum(1 for k in a if k in b and a[k] != b[k])
    if only_src + only_copy + changed == 0:
        return 'identical'
    return f'src-only {only_src}, copy-only {only_copy}, changed {changed}'


def row(skill, target, state, detail, action):
    return {'Skill': skill, 'Target': target, 'State': state, 'Action': action, 'Detail': detail}


def scan_target(cfg, tname, tpath, winners, conflicts, names, no_hash):
    rows = []
    if not os.path.exists(tpath):
        raise RuntimeError(f'target missing: {tpath}')
    want = lower_set(names) if names else None
    for key in sorted(winners):
        name, w = winners[key]
        if want is not None and name.lower() not in want:
            continue
        src = w['source']
        p = os.path.join(tpath, name)
        if not os.path.lexists(p):
            rows.append(row(name, tname, 'MISSING', src, 'link'))
            continue
        kind, cur = link_info(p)
        if kind == 'Junction':
            if cur and same_path(cur, src):
                rows.append(row(name, tname, 'OK', src, '-'))
            elif not cur or not os.path.exists(cur):
                rows.append(row(name, tname, 'BROKEN', f'was {cur}', 'relink'))
            else:
                rows.append(row(name, tname, 'WRONG-TARGET', f'points to {cur}', 'relink'))
        elif kind:
            rows.append(row(name, tname, 'WRONG-TARGET', f'{kind} -> {cur}', 'relink'))
        else:
            d = 'not compared' if no_hash else compare_trees(src, p)
            rows.append(row(name, tname, 'COPY', d, 'trash+link'))
    for key in sorted(conflicts):
        name, cands = conflicts[key]
        if want is not None and name.lower() not in want:
            continue
        rows.append(row(name, tname, 'CONFLICT', ' | '.join(c['rel'] for c in cands), 'none'))
    known = lower_set(cfg['known_foreign'])
    with os.scandir(tpath) as it:
        entries = sorted(e.name for e in it)
    for en in entries:
        if en.lower() in winners or en.lower() in conflicts:
            continue
        if want is not None and en.lower() not in want:
            continue
        rows.append(row(en, tname, 'FOREIGN', 'known' if en.lower() in known else 'NEW', 'none'))
    return rows


def invoke_fix(cfg, r, tpath, winners):
    p = os.path.join(tpath, r['Skill'])
    src = winners[r['Skill'].lower()][1]['source']
    if r['State'] == 'COPY':
        trash = os.path.join(tpath, cfg['trash_dir'])
        os.makedirs(trash, exist_ok=True)
        os.rename(p, os.path.join(trash, '{}-{}'.format(r['Skill'], datetime.now().strftime('%Y%m%d-%H%M%S'))))
    elif r['State'] in ('WRONG-TARGET', 'BROKEN'):
        remove_link_only(p)
    make_junction(p, src)


def test_doctor(cfg):
    issues = []
    for n, v in cfg['targets'].items():
        if not os.path.exists(v):
            issues.append(f"target '{n}' missing: {v}")
    for r in cfg['roots']:
        if not os.path.exists(r):
            issues.append(f'root missing: {r}')
    for f in ('AGENTS.md', 'skills'):
        if not os.path.exists(os.path.join(REPO, f)):
            issues.append(f'repo file missing: {f}')
    return issues


def invoke_link(agents):
    src = os.path.join(REPO, 'skills')
    skills = sorted(
        (n for n, pth, _ in list_dirs(src) if os.path.exists(os.path.join(pth, 'SKILL.md'))), key=str.lower)
    for a in agents:
        d = os.path.join(REPO, f'.{a}', 'skills')
        os.makedirs(d, exist_ok=True)
        for s in skills:
            p = os.path.join(d, s)
            sp = os.path.join(src, s)
            if not os.path.lexists(p):
                make_junction(p, sp)
                print(f'linked   {a} {s}')
                continue
            kind, cur = link_info(p)
            if kind == 'Junction' and cur and same_path(cur, sp):
                print(f'ok       {a} {s}')
            elif kind == 'Junction':
                remove_link_only(p)
                make_junction(p, sp)
                print(f'relinked {a} {s}')
            else:
                print(f'SKIPPED  {a} {s} - a real directory is in the way, move it by hand')
    hook = os.path.join(REPO, '.claude', 'settings.json')
    if 'claude' in agents and not os.path.exists(hook):
        cmd = 'uv run "$CLAUDE_PROJECT_DIR/scripts/skillmesh.py" --mode scan --watch --target all'
        obj = {'hooks': {'SessionStart': [{'hooks': [{'type': 'command', 'command': cmd}]}]}}
        os.makedirs(os.path.dirname(hook), exist_ok=True)
        with open(hook, 'w', encoding='utf-8') as f:
            json.dump(obj, f, indent=2)
        print('created  claude SessionStart hook')


def select_targets(cfg, target):
    out = []
    for n, v in cfg['targets'].items():
        if target == 'all' or target == n or (target == 'both' and n in ('agents', 'claude')):
            out.append((n, v))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(prog='skillmesh.py')
    ap.add_argument('--mode', choices=['scan', 'apply', 'doctor', 'link', 'init'], default='scan')
    ap.add_argument('--agent', nargs='+', choices=['claude', 'kiro'], default=['claude', 'kiro'])
    ap.add_argument('--target', choices=['both', 'all', 'agents', 'claude', 'kiro'], default='both')
    ap.add_argument('--name', nargs='+')
    ap.add_argument('--no-hash', action='store_true')
    ap.add_argument('--watch', action='store_true')
    a = ap.parse_args(argv)
    mode = a.mode

    if mode == 'init':
        if os.path.exists(CFG_PATH):
            print('skillmesh.config.json already exists; left unchanged')
        else:
            with open(EXAMPLE_PATH, 'rb') as s, open(CFG_PATH, 'wb') as d:
                d.write(s.read())
            print('created skillmesh.config.json from the example; edit roots, targets, ignore and known_foreign, then run -Mode Doctor')
        return 0
    cfg = None
    if os.path.exists(CFG_PATH):
        cfg = load_config()
    elif mode != 'link':
        print('skillmesh.config.json is missing. Run -Mode Init to create it from skillmesh.config.example.json, then edit it.', file=sys.stderr)
        return 1

    if mode == 'link':
        invoke_link(a.agent)
        return 0
    if mode == 'doctor':
        issues = test_doctor(cfg)
        if not issues:
            print('Doctor: ok')
        for i in issues:
            print(f'Doctor: {i}')
        return 0 if not issues else 1

    no_hash = a.no_hash or a.watch
    winners, conflicts = resolve_skills(cfg, find_skills(cfg))
    all_rows = []
    for tname, tpath in select_targets(cfg, a.target):
        rows = scan_target(cfg, tname, tpath, winners, conflicts, a.name, no_hash)
        if mode == 'apply':
            for r in [x for x in rows if x['State'] in FIX_STATES]:
                invoke_fix(cfg, r, tpath, winners)
                print('applied {:<12} {} {}'.format(r['State'], tname, r['Skill']))
            rows = scan_target(cfg, tname, tpath, winners, conflicts, a.name, no_hash)
        all_rows.extend(rows)

    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump({'scanned_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%S'), 'mode': mode.capitalize(),
                   'target': a.target, 'rows': all_rows}, f, indent=2)

    bad = [r for r in all_rows if r['State'] != 'OK' and not (r['State'] == 'FOREIGN' and r['Detail'] == 'known')]
    if a.watch:
        if bad:
            counts = {}
            for r in bad:
                counts[r['State']] = counts.get(r['State'], 0) + 1
            print('Skillmesh: ' + ', '.join(f'{c} {s}' for s, c in counts.items()) + ' - see skillmesh-scan / skillmesh-sync')
        return 0

    ordered = sorted(all_rows, key=lambda r: (r['Target'], 0 if r['State'] != 'OK' else 1, r['State'], r['Skill'].lower()))
    cols = ('Target', 'Skill', 'State', 'Action', 'Detail')
    widths = {c: max([len(c)] + [len(str(r[c])) for r in ordered]) for c in cols}
    print('  '.join(c.ljust(widths[c]) for c in cols))
    for r in ordered:
        print('  '.join(str(r[c]).ljust(widths[c]) for c in cols))
    counts = {}
    for r in all_rows:
        counts[r['State']] = counts.get(r['State'], 0) + 1
    print('Summary: ' + ' '.join(f'{k}={counts[k]}' for k in sorted(counts)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
