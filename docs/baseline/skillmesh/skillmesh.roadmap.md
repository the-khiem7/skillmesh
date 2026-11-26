---
baseline_schema: "3.0"
pack: "skillmesh"
document: "roadmap"
status: "active"
updated: "2026-11-26"
code_ref: "uncommitted"
---

# Skillmesh - roadmap

## Phases

| Phase | Work | Depends on | Status |
|---|---|---|---|
| SKM-P1 | Scan and compare script | - | complete |
| SKM-P2 | Link both targets to the repos | SKM-P1 | complete |
| SKM-P3 | Session-start watch and project skills | SKM-P1 | complete |
| SKM-P4 | Guidance file and decision record | SKM-P2 | complete |
| SKM-P5 | Convert the documents into this pack | SKM-P4 | complete |
| SKM-P6 | Triage NEW FOREIGN entries | SKM-P2 | complete |
| SKM-P7 | Move personal values into gitignored config | SKM-P5 | active |
| SKM-P8 | Python core trial and parity gate | SKM-P7 | complete |
| SKM-P9 | Local control page in Python | SKM-P8 | active |

### SKM-P1: Phase 1 - scan and compare script

- Delivered `scripts\Skillmesh.ps1` with `Scan`, `Apply` and `Doctor`, `skillmesh.config.json` and `.gitignore` (commit `de953be`).
- Acceptance: every skill under the roots is classified per target as OK, MISSING, COPY, WRONG-TARGET, BROKEN or CONFLICT, and every unmatched entry as FOREIGN.
- Evidence: the first scan on 2026-11-03 classified 128 rows: 76 COPY, 4 MISSING, 4 WRONG-TARGET, 43 FOREIGN, no CONFLICT.

### SKM-P2: Phase 2 - link both targets

- Applied to `claude`, then to `agents`, each after the user approved the exact scan output (`SKM-D4`, `SKM-D6`).
- Acceptance: a rescan shows no MISSING, COPY, WRONG-TARGET, BROKEN or CONFLICT row.
- Evidence: `OK=84` after both applies on 2026-11-04; `OK=100 FOREIGN=43` on 2026-11-09 after more skills were linked later.
- Evidence: a probe file written through a `claude` junction appeared in the source folder and was removed; Claude Code listed newly linked skills while the session ran.

### SKM-P3: Phase 3 - session-start watch and project skills

- Delivered the `SessionStart` hook and `skillmesh-watch`, `skillmesh-scan`, `skillmesh-sync`, `skillmesh-doctor` (commit `ddeacc0`, `SKM-D8`).
- Acceptance: a session opened here prints one summary line when something mismatches and nothing otherwise.
- Evidence: the hook output appeared on resumed sessions (`12 MISSING` on 2026-11-06, `2 FOREIGN` on 2026-11-09).
- Not verified: the hook on a fresh start (not a resume), and the four skills invoked by name.

### SKM-P4: Phase 4 - guidance file and decision record

- Delivered `AGENTS.md` and `DECISIONS.md` (commit `6c29d1f`, `SKM-D12`).
- Acceptance: guidance and reasons sit in separate files and `-Mode Doctor` prints `ok`.

### SKM-P5: Phase 5 - convert the documents into this pack

- Delivered this pack: introduction, roadmap, decisions, source topology.
- Acceptance: every decision from `DECISIONS.md` is present in `skillmesh.hallucination.md` (`D7a` migrated as `SKM-D15`); `SKM-Q1` is closed by `SKM-D16` and `DECISIONS.md` and `DECISIONS.local.md` are removed; `-Mode Doctor` prints `ok`.
- Not verified: `bldh.sh check` after the last edit.

### SKM-P6: Phase 6 - triage NEW FOREIGN entries

- A NEW FOREIGN entry was present in both targets and not in `known_foreign`; the user chose to add it on 2026-11-09 (`SKM-D5`).
- Acceptance: each NEW entry is either added to `known_foreign` or left reported, by the user's choice.
- Evidence: after the edit `-Watch` printed nothing.

### SKM-P7: Phase 7 - personal values into gitignored files

- Delivered: `skillmesh.config.example.json`, `-Mode Init`, environment-variable expansion in `roots` and `targets`, the setup section in `AGENTS.md` (`SKM-D14`).
- Acceptance: a search of every tracked file for the owner's user name, absolute personal paths, personal skill and repo names and email finds nothing; `-Mode Doctor` prints `ok` with the real config; `-Mode Init` on a clone without a config creates one from the example.
- Not verified until run: the clone test.

### SKM-P8: Phase 8 - Python core trial and parity gate

- Plan (`SKM-D17`): `scripts\skillmesh.py`, run with `uv`, stdlib only, Python 3.12+, same modes and switches as `Skillmesh.ps1`; ports `Find-Skills`, `Resolve-Skills`, `Scan-Target`, `Compare-Trees`, `Invoke-Fix`, `Test-Doctor`, `Invoke-Link` and config load with `%VAR%` expansion.
- Junctions: create with `mklink /J`, detect with `os.path.isjunction` and `os.readlink`, remove only with `os.rmdir`; `shutil.rmtree` is never called on a junction.
- The trial writes `state\last-scan.py.json` and leaves the PowerShell state and hook untouched; Apply runs only on a sandbox config in the scratchpad, never on the real targets.
- Gate, all must pass: scan rows identical to PowerShell on the real config (with and without hash); Apply, Link, Init and Doctor give the same filesystem result and exit codes on identical sandboxes; content behind a removed junction intact; `-Watch` line identical and `uv run` start time acceptable for the hook.
- Delivered `scripts\skillmesh.py` (uncommitted; written in `py\`, moved to `scripts\` by the user): all five modes, `--target`, `--name`, `--no-hash`, `--watch`, `--agent`; no `shutil` call, links removed only through `os.rmdir`, and `remove_link_only` refuses a path that is not a link.
- Evidence, real config, read-only scans on 2026-11-26: 180 of 180 rows identical to PowerShell for `-Target all`, with hash and with `-NoHash`, and for `both`, `agents`, `claude`, `kiro`; the `-Watch` line identical (`9 FOREIGN`), exit 0.
- Evidence, two identical sandboxes (3 targets; MISSING, COPY, WRONG-TARGET, BROKEN, CONFLICT, known and NEW FOREIGN, shallow-wins, ignored paths): scan rows, Apply output lines, resulting target trees (junction targets, trash entries) and a rescan identical; Apply by one `-Name` identical; the source directories behind the replaced junctions intact.
- Evidence, sandbox Link, Init, Doctor: output, hook JSON, idempotent rerun, real directory in the way (skipped), wrong junction (relinked), `-Agent kiro`, Doctor exit 1 with a missing `AGENTS.md`, Init file bytes, scan with no config (exit 1 both) identical.
- Evidence, start time of the `-Watch` scan on the real config: Python through `uv run` 0.35 s, PowerShell 1.9 s.
- Differences kept: the table layout of a plain scan differs (Python prints plain aligned columns); the Python scan writes `state\last-scan.py.json`; PowerShell takes `-Name` as an array only through `-Command`, not `-File`; the Python core refuses a path holding a `cmd` metacharacter before `mklink` (`SKM-D19`).
- The one defect found: `SKM-D18` (lesson, `hallucination`).
- Not verified: the Python core against the real targets in Apply (never run there by design); `uv run` through the real `SessionStart` hook; behaviour with a symlink at a target, a reparse point other than a junction or symlink, or a skill name differing only in case between two roots.
- Result: every gate check passed; the user chose to migrate the core to Python (`SKM-D19`, `hallucination`).
- Switch after `SKM-D19` (2026-11-26, uncommitted): the hook that Link creates in `skillmesh.py`, the local `.claude\settings.json`, the four project skills and `AGENTS.md` call `uv run scripts\skillmesh.py` (`--mode`, `--target`, `--watch`). The hook command taken from `.claude\settings.json` and run from the repo printed `Skillmesh: 9 FOREIGN`, exit 0, in 1.9 s.
- Not verified after the switch: the hook through a fresh Claude Code session start; the four skills invoked by name. `README.md` and `Skillmesh.ps1 -Mode Link` (which still writes the PowerShell hook) are not switched.

### SKM-P9: Phase 9 - local control page in Python

- Plan (`SKM-D17`): `scripts\skillmesh_ui.py` on stdlib `ThreadingHTTPServer` bound to `127.0.0.1`, one static `ui\index.html` without CDN.
- Acceptance: the page scan matches a manual scan; Apply with a stale scan id is refused; a POST without token or from a foreign origin is refused.
- Delivered (uncommitted, 2026-11-26): `scripts\skillmesh_ui.py` imports the Python core and serves `ui\index.html`; Scan, Doctor, Link, Init as buttons; Apply on ticked rows (`SKM-D20`); FOREIGN and CONFLICT rows are view only; `AGENTS.md` documents how to start it and `README.md` was switched to the Python commands.
- Apply rule: the server keeps the last 20 scans; Apply needs a held scan id and a fresh scan with the same target and hash setting giving the same id, so a filesystem change since the scan gives 409; only MISSING, COPY, WRONG-TARGET and BROKEN rows of that scan are accepted, and a used scan id cannot be replayed.
- Request guards: `Host` must be `127.0.0.1:<port>` or `localhost:<port>`; POST needs a matching `Origin`, the per-start token header, `Content-Type: application/json` and a body of at most 64 KB; the page carries a nonce CSP.
- Evidence, 46 of 46 HTTP checks in-process: no token, wrong token, foreign `Origin`, no `Origin`, foreign `Host`, `text/plain`, bad JSON, oversize body, unknown route, bad target and bad agent are refused; the page scan equals the core scan on the real config for `both` (121 rows) and `all` (180 rows) and its summary equals the CLI `Summary` line; Doctor ok.
- Evidence, sandbox Apply: a MISSING and a COPY row ticked became junctions with the copy in `.trash`; an unticked WRONG-TARGET and MISSING row and a FOREIGN entry were untouched; the source folders stayed intact; a scan outgrown by a new directory gave 409 and changed nothing; a replayed scan id gave 409; a second Apply of the two remaining rows worked; Init created the config at the sandbox path; a scan with no config gave 400.
- Evidence, browser: `http://127.0.0.1:8791/` in a real browser, Scan printed `Scan e1ff91fd1de59758: 121 rows` with the state chips and an empty console after the `SKM-D21` fix.
- Evidence, user report (2026-11-26): the user ran Apply from the page on the real targets and it worked; the output was not shown to the agent.
- Status stays active: the user wants the finished, polished UI to be the output of this phase, so the UI and UX improvement is part of `SKM-P9`, not a later phase.
- Delivered (uncommitted, 2026-11-26): `ui\index.html` redesigned (user: use the `design-taste-frontend` workflow, "smooth and spacing"; that installed skill, whose text names `Leonxlnx`, was used, nothing reinstalled). Only the page changed; routes, the Apply rule and the request guards did not. Applied from the skill: one spacing scale (4 to 48), one radius family, one hairline, one blue accent on a warm neutral ground (no violet), 16px reading text and nothing under 13px, 44px buttons with a 1px lift on hover and a press sink (150, 120 and 90 ms, one ease), a 2px focus ring, field focus ring, row and chip hover tints, a dialog that eases in, reduced-motion support, light and dark by `prefers-color-scheme`. Added: skip link, an empty state, a segmented target control, state badges with a dot as well as colour, a plain-words legend, a sticky table header inside a scroll area, a "Tick all fixable shown" box, a per-state count in the confirm dialog, and stacked cards for rows under 640px. The filled button is the next step: Scan until rows are ticked, then Apply.
- Not applied from the skill, on purpose: its page plans, hero, photographs, effects and the `gate.mjs` finish gate target marketing sites; the gate was not armed so this repository gets no `.taste-skill` folder or copied kit.
- Evidence, browser, real Chrome through the browser tool: wide (1440), 390 and 320 windows, light and dark; no horizontal overflow at 320; equal left and right edges at 390 (16px each); the console empty; on a sandbox, ticking, "Tick all", the confirm dialog and Apply by click turned MISSING, COPY and WRONG-TARGET rows into OK and printed the applied lines; the 46 HTTP checks still pass 46 of 46. The one defect found is `SKM-D22` (lesson, `hallucination`).
- Not verified by the agent: Link and Init from the page on the real repository; a second browser tab racing the first; keyboard-only use end to end and a screen reader; the page on a touch device (the layout was checked by window size only); `prefers-reduced-motion` was coded but not observed.
- Remove `Skillmesh.ps1` only after one full verified cycle and the user's approval.

## Risks

| Risk | Effect | Mitigation |
|---|---|---|
| `npx skills update` run on a linked skill | junction replaced by a copy | rescan shows COPY; `Apply` restores |
| A repo moves or is deleted | junctions become BROKEN | scan reports it; ask whether the skill is gone or relocated |
| Hook output ignored | drift persists | none beyond the one-line summary |

## Next action

- Finish `SKM-P7` verification (the clone test), then run `bldh.sh check` on this pack.
- `SKM-P9` (the control page) works and the user ran Apply from it on the real targets; it stays active until its UI and UX are polished and the user approves. Nothing is committed; the user chose to commit later.
- Confirm the `SessionStart` hook on the next fresh session start, then decide on removing `Skillmesh.ps1`.
- Remove `Skillmesh.ps1` only after one full verified cycle and the user's approval.
