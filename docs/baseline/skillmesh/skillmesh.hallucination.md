---
baseline_schema: "3.0"
pack: "skillmesh"
document: "hallucination"
status: "active"
updated: "2026-11-26"
code_ref: "uncommitted"
---

# Skillmesh - decisions and open questions

## Entry index

| Entry | About | Status | Related |
|---|---|---|---|
| SKM-D1 | junction naming and layout in the targets | closed | - |
| SKM-D2 | which source wins when a skill name repeats | closed | SKM-D1 |
| SKM-D3 | repos with no SKILL.md | closed | - |
| SKM-D4 | handling a real copy at a target | closed, part assumed | SKM-D6 |
| SKM-D5 | entries at a target with no source (FOREIGN) | closed, personal-reason file dropped by SKM-D16 | SKM-D4, SKM-D16 |
| SKM-D6 | wrong or broken junctions | closed | SKM-D4 |
| SKM-D7 | choosing the target of a run | closed | SKM-D15 |
| SKM-D8 | session-start watch | closed, part assumed | - |
| SKM-D9 | whether scan state is committed | closed, assumed | - |
| SKM-D10 | runtime and link type | closed, part assumed, runtime part reversed by SKM-D19 | SKM-D19 |
| SKM-D11 | config and decision record must agree | closed, reversed by SKM-D16 | SKM-D12, SKM-D16 |
| SKM-D12 | guidance and decisions in separate files | closed, record moved to the pack by SKM-D16 | SKM-D11, SKM-D16 |
| SKM-D13 | project skills in skills\ linked into gitignored agent folders | closed | SKM-D8, SKM-D12 |
| SKM-D14 | personal values in gitignored files, committed example config | closed, local decision file dropped by SKM-D16 | SKM-D5, SKM-D11, SKM-D16 |
| SKM-D15 | Kiro as a third target, `all` | closed | SKM-D7, SKM-D8 |
| SKM-D16 | the pack is the only decision record | closed | SKM-D11, SKM-D12, SKM-D14 |
| SKM-D17 | local control page in Python; Python core trialled against PowerShell before any migration | closed | SKM-D10, SKM-D19 |
| SKM-D18 | lesson: Python existence check on a dangling junction | closed | SKM-D17 |
| SKM-D19 | migrate the core from PowerShell to Python | closed | SKM-D10, SKM-D17, SKM-Q2 |
| SKM-D20 | Apply is enabled on the control page from the first version | closed | SKM-D17, SKM-D19 |
| SKM-D21 | lesson: inline style attributes under the page CSP; unread request body on a refused POST | closed | SKM-D17 |
| SKM-D22 | lesson: the select-all box hidden with the table header on a phone | closed | SKM-D21 |
| SKM-D23 | control page design direction from the board rounds | closed | SKM-D17, SKM-D24, SKM-D25, SKM-D26 |
| SKM-D24 | brand fonts loaded from the Google Fonts CDN | closed | SKM-D17, SKM-D21, SKM-D23 |
| SKM-D25 | `/api/scan` returns source paths and target folders | closed | SKM-D17, SKM-D23 |
| SKM-D26 | Round 4 is one screening round of every page, edited in place | closed | SKM-D23, SKM-D28 |
| SKM-D27 | core `--target` accepts any configured target name | closed | SKM-D7, SKM-D15, SKM-D23 |
| SKM-D28 | pages, states, agents, themes and widths of Round 4 | closed | SKM-D23, SKM-D26, SKM-Q3 |
| SKM-D29 | Round 4 screens approved as the build spec of the control page | closed | SKM-D23, SKM-D25, SKM-D26, SKM-D27, SKM-D28 |
| SKM-D30 | build plan of the control page: data for Link, Doctor and Output log, test method, single file, run 1 to 5 | closed | SKM-D17, SKM-D24, SKM-D25, SKM-D27, SKM-D29 |
| SKM-D31 | lesson: the nonce CSP blocks inline style attributes and a test page without the CSP hid it | closed | SKM-D24, SKM-D30 |

## Open questions

None.

## Closed decisions

### SKM-D1: flat junctions named after the skill directory

- Decision: every skill becomes `<target>\<skill-dir-name>` however deep it sits in its repo, for example `<bundle>\skills\<category>\<skill>` becomes `<target>\<skill>` - agents read skills one level deep under the skills directory.
- If ignored: skills nested under a category folder are never discovered.
- Rejected: mirroring the category structure in the target - agents would not find the skills.

### SKM-D2: shallowest source wins a name clash

- Decision: when one skill name has several sources, the source closest to a root wins; equal depth is a CONFLICT and nothing is linked until an entry in `overrides` picks one - a standalone skill repo is the maintained copy and a skill nested in a bundle repo is a bundle copy. Example: `<root>\<skill>` beats `<root>\<bundle>\skills\<category>\<skill>`.
- If ignored: the bundle copy can shadow the maintained one.
- Rejected: newest-modified wins - the winner changes silently with every edit.

### SKM-D3: repos with no SKILL.md are ignored

- Decision: repos listed in `ignore` are never scanned - a repo that holds no skill has nothing to link.
- If ignored: noise in every scan.

### SKM-D4: real copies are moved to trash, then replaced

- Decision: a real directory at a target (an `npx skills` install) is moved to `<target>\.trash\<name>-<timestamp>` and replaced by a junction; the scan reports how the copy differs from the source (files only in source, only in copy, changed) and a difference does not stop the move - the junction makes the repo the single source of truth and the trash keeps the old copy recoverable. The answer to the difference question was a recommended default, not an explicit answer.
- If ignored: the copy keeps shadowing the repo and edits in the repo never show up.
- Rejected: deleting the copy - not recoverable. Stopping on every difference - copies almost always differ, because the repo carries README and git files an install omits and installs carry extras such as `agents\openai.yaml`.

### SKM-D5: FOREIGN entries are reported only

- Decision: a FOREIGN entry is one at a target with no source in the roots and is never touched; names in `known_foreign` are shown as known and anything else as NEW - they may be hand-made skills, installs from elsewhere, retired skills or tool state, and removing them loses knowledge irreversibly.
- Decision: `known_foreign` holds names to show as known, such as `.trash` and the skills installed by `npx skills`, so the session-start watch stays quiet; `npx skills` manages those, junctions do not. Which names a user lists is personal and recorded in the gitignored `DECISIONS.local.md` (`SKM-D14`). The `.trash` directories are never cleaned by this repository.
- Decision: the state is named FOREIGN, not orphan - most such entries are installs from outside the repos, not leftovers of one.
- If ignored: skills with no repo copy get deleted.
- Rejected: moving `npx skills` installs into a repo - `npx skills` already updates them.

### SKM-D6: wrong or broken junctions point straight at the source

- Decision: a junction targeting anything other than the winning source (for example `.claude` pointing into `.agents`) is removed and recreated against the source in both targets, removing only the link and never the content behind it - chaining through `.agents` ends at a copy, not the repo.
- If ignored: edits in the repo do not propagate.

### SKM-D7: target selectable, default both

- Decision: `-Target agents|claude|both`, default `both` - lets one side be applied and verified before the other. `kiro` and `all` were added by `SKM-D15`.

### SKM-D8: session-start watch, project scoped, read-only

- Decision: a `SessionStart` hook in this repository's `.claude\settings.json` runs a read-only scan and injects a one-line summary only when something other than OK or a known FOREIGN entry exists; it never fixes anything and was built before the other skills - a mismatch is visible at the start of every session opened here. The scope and ordering answers were recommended defaults.
- If ignored: drift goes unnoticed until a skill misbehaves.
- Rejected: a user-level hook - outside the project-scoped requirement. Sessions opened in other repositories therefore get no warning.

### SKM-D9: scan state is not committed

- Decision: `state\last-scan.json` is generated by the script and listed in `.gitignore` - each scan would otherwise produce a diff. Recommended default, not an explicit answer.

### SKM-D10: PowerShell 5.1 and junctions

- Decision: one script, `scripts\Skillmesh.ps1`, for Windows PowerShell 5.1, linking with NTFS junctions - 5.1 is what the machine has and junctions need no administrator rights, which the standard-user account requires. The 5.1 part was a recommended default.
- If ignored: symlinks or newer syntax need elevation or a second runtime.

### SKM-D11: config and decision record must agree

- Decision: `-Mode Doctor` checks that every name in `ignore`, `known_foreign` and `overrides` appears in the gitignored `DECISIONS.local.md` when it exists, and that roots, targets, `AGENTS.md`, `DECISIONS.md` and `skills\` exist - the config carries no reasons, so the record is the only place they live.
- If ignored: config entries accumulate with no recorded reason.
- Reversed by `SKM-D16`: the check was removed.

### SKM-D12: guidance and decisions live in separate files

- Decision: `AGENTS.md` carries working guidance only and the decisions with their reasons sit in a separate record - user instruction of 2026-11-04; guidance is reread every session while decisions change rarely.
- If ignored: guidance and reasons drift together and every decision change edits the file agents rely on to operate.
- Rejected: decisions inside `AGENTS.md`.

### SKM-D13: project skills live in skills\ and are linked into agent folders on demand

- Decision: the project skills are the only real copy, in `skills\<name>`; `.claude\`, `.kiro\` and `.agents\` are gitignored; `-Mode Link [-Agent claude,kiro]` creates one junction `.<agent>\skills\<name>` per skill and the Claude `SessionStart` hook when `.claude\settings.json` is absent - a fresh clone gets the workflow by one command (user, 2026-11-18) [user].
- If ignored: copies in agent folders drift from `skills\`.
- Rejected: committing `.claude\skills` and `.kiro\skills` - git does not store a junction. Junctioning the whole `.<agent>\skills` folder - the user could not add their own skills beside the project ones. Overwriting an existing `.claude\settings.json` - it may hold the user's settings.
- Limit: a real directory in the way is skipped, never deleted; Kiro does not read the Claude hook.

### SKM-D14: personal values live in gitignored files, a committed example shows the shape

- Decision: `skillmesh.config.json` and `DECISIONS.local.md` are gitignored; `skillmesh.config.example.json` is committed with neutral values and environment variables (`%USERPROFILE%`), which the script expands in `roots` and `targets`; `-Mode Init` copies the example when the config is absent; a committed file never holds a user name, a personal absolute path, a personal skill or repo name, or an email (user, 2026-11-18) [user].
- If ignored: a published file leaks the owner's paths and skill inventory, and each clone edits a committed file.
- Rejected: keeping the config committed with personal values - leaks them. Committing the real config and asking each user to edit it - every user commits their own paths.
- Limit: `-Mode Link` works without a config; every other mode stops until `-Mode Init` has run. Publishing starts from a fresh `git init`, so the old history with personal values is not carried over.

### SKM-D15: Kiro is a third target; `all` covers it, `both` stays two

- Decision: `-Target agents|claude|kiro|both|all`; `kiro` is the Kiro user-level skills directory, `both` keeps meaning agents+claude and stays the default, `all` is all three, and the `SessionStart` hook of `SKM-D8` scans `-Target all` [agent].
- Why: Kiro reads user-level skills from `.kiro\skills`, so it needs the same links; leaving `both` and the default unchanged keeps old commands and approvals meaning what they did [agent].
- If ignored: Kiro misses every skill added to a root and its drift is never reported.
- Rejected: making `both` mean all three - silently widens what an old `-Target both` approval changes [agent]. Default `all` - same reason [agent].
- Source: migrated from the retired root `DECISIONS.md` (entry D7a), where it was recorded without a user tag.

### SKM-D16: the baseline pack is the only decision record

- Decision: the pack under `docs\baseline\skillmesh` is the source of truth for decisions and development state; the root `DECISIONS.md` and the gitignored `DECISIONS.local.md` are removed, `Test-Doctor` no longer checks config names against a decision file or the existence of `DECISIONS.md`, and `AGENTS.md` and the project skills point at the pack (user, 2026-11-22) [user]. Closes `SKM-Q1`.
- Why: two records had drifted (`DECISIONS.md` held `SKM-D15` before the pack did) and the pack contract forbids code naming a pack file, so the check could not move to the pack [user].
- If ignored: decisions are edited in two places and diverge again.
- Rejected: keep `DECISIONS.md` beside the pack (option B of `SKM-Q1`) - two copies to keep equal [user]. Doctor reads the pack (option C) - code would name a pack file [user].
- Secret separation is unchanged: `skillmesh.config.json` stays gitignored and `skillmesh.config.example.json` stays committed (`SKM-D14`); the pack and every committed file hold no personal value.
- Limit: the personal reasons for the config entries (why a repo is ignored, why a name is `known_foreign`) are no longer recorded anywhere in the repository; the pack states only generic rules. The removed `DECISIONS.md` stays in git history.

### SKM-D17: a local control page in Python; the Python core is trialled before any migration

- Decision: build a local page to run Skillmesh operations by clicking instead of prompting an agent; first trial a Python port of the core beside `Skillmesh.ps1`; migrate core and UI to Python only if it behaves exactly like the PowerShell core, otherwise keep the PowerShell core and write only the UI in Python (user, 2026-11-26) [user].
- Why: every operation currently costs an agent prompt; a PowerShell 5.1 web server is hand-written HTTP and single-threaded, Python (via `uv`, already used) is shorter and concurrent, but the junction logic is the risky part, so it must be proven before it replaces working code [agent].
- If ignored: an unproven port could delete content behind a junction or misclassify rows, breaking the safety rules of `SKM-D4` and `SKM-D6`.
- Page scope: Scan, Doctor, Link, Init; Apply only for the exact scan shown (scan id checked server side, stale scan refused); FOREIGN and `.trash` view only; no config edits from the page [agent].
- Page security: bind `127.0.0.1` only, a random token per start required on every POST, `Host`/`Origin` checked, target and agent whitelisted, names must exist in the shown scan, arguments passed as a list [agent].
- Rejected: Node - may need installing, no gain over Python [agent]. Go - a binary to build and keep for a one-script repo [agent]. Pode - an extra PSGallery module to maintain [agent]. Electron or Tauri - too heavy for five operations [agent]. claude.ai Artifact - runs on the web and cannot touch the local filesystem [agent]. `_winapi.CreateJunction` - CPython internal, not a stable API; use `mklink /J` [agent].
- The migration question left open here was closed by `SKM-D19`.

### SKM-D18: lesson - `os.path.exists` hides a dangling junction

- Mistake: the first Python scan used `os.path.exists(p)` to decide MISSING, copying the shape of PowerShell's `Test-Path -LiteralPath`.
- Why it looked reasonable: both names read as "does this path exist".
- What disproved it: on a sandbox with a junction whose target was deleted, PowerShell reported BROKEN (relink) and Python reported MISSING (link); `Test-Path` is true for the link itself, `exists` follows the link and is false. An Apply on that MISSING row would have failed at `mklink` with the path already present [agent].
- Fix: `os.path.lexists` for the MISSING check in scan and in Link; the result is identical rows on the sandbox [agent].
- Rule kept: a port compares the same fixture on both implementations and never trusts a function name; a dangling-junction fixture belongs to every parity run.

### SKM-D19: the core migrates from PowerShell to Python

- Decision: `scripts\skillmesh.py` becomes the Skillmesh core and the control page of `SKM-D17` is built on it; the PowerShell core and `SKM-D10` (PowerShell 5.1 + junctions) are replaced for the runtime part, the junction link type stays (user, 2026-11-26) [user]. Closes `SKM-Q2`.
- Why: every check of the parity gate (`SKM-P8`, roadmap) passed against the PowerShell core, and the watch scan starts in 0.35 s against 1.9 s [user].
- If ignored: two cores to keep equal, and a UI that either shells out to PowerShell or duplicates its logic.
- Rejected: keeping PowerShell as the core with only the UI in Python - the gate showed no behavioural reason to keep two languages [agent].
- Limit: `Skillmesh.ps1` stays until one full cycle on the Python core is verified and the user approves removing it; Apply of the Python core on the real targets is unverified.
- Limit: the Python core refuses a path with a `cmd` metacharacter (`& | < > ^ % " ! ( )` or a control character) when creating a junction, which PowerShell accepts; a skill directory named that way is reported as an error [agent].

### SKM-D20: Apply is enabled on the control page from the first version

- Decision: the control page offers Apply from its first version, without a start flag; the page and the server still require ticked rows of a scan that the server holds and a fresh scan with the same parameters giving the same scan id (user, 2026-11-26) [user].
- Why: the user chose it over an off-by-default switch [user]; the scan-id check keeps the approval tied to the rows on screen [agent].
- If ignored: not applicable; the risk is the reverse, a click on Apply changes the real targets with a core whose Apply has run only on sandboxes.
- Rejected: Apply behind `--allow-apply`, so the user runs the core's Apply by hand once first - the user chose it on from the start [user].
- Limit: the Python core's Apply is still unverified on the real targets (`SKM-D19`); the page's Apply is verified on a sandbox only.

### SKM-D21: lesson - the CSP blocks inline style attributes, and a refused POST must read its body first

- Mistake: the first page used three `style="..."` attributes while the server sent `style-src 'nonce-...'`; the first server answered a refused POST (415) without reading the request body.
- Why it looked reasonable: a nonce on the `<style>` and `<script>` tags looked like it covered the whole page, and a 4xx reply needs no body.
- What disproved it: in a real browser the console reported three CSP violations and the three styles were dropped; the HTTP test client got `ConnectionAbortedError` instead of the 415, because on Windows closing a socket with unread request data resets the connection [agent].
- Fix: the three styles became classes; `do_POST` reads the declared body (at most 64 KB) before every refusal, and an oversize body closes the connection [agent].
- Rule kept: a page under a nonce CSP uses no `style` attribute; the HTTP test also runs the page in a browser and reads its console, and a refusal test sends a body.

### SKM-D22: lesson - a control placed in a table header vanishes when the header is hidden for phones

- Mistake: the redesign put the select-all checkbox in the table header, and under 640px the header is hidden so rows can stack as cards.
- Why it looked reasonable: on a wide window the header is the usual place for it, and the desktop screenshot showed it working.
- What disproved it: at 390 wide the browser tool timed out on the click, "element is not visible"; a user on a phone would have had no way to tick every row [agent].
- Fix: the box moved into the toolbar above the table, with a visible label, and the header cell keeps only a screen-reader label [agent].
- Rule kept: every control the page offers is reached once at the narrowest width by clicking it in a real browser, not only seen in a wide screenshot.

### SKM-D23: control page design direction from the board rounds

- Decision: the control page follows the frontdoor board choices (user, 2026-11-26) [user]:
  - Brand: the README signature in `assets\source` (Oxanium for names, Share Tech Mono for labels, IBM Plex Sans for text; teal accent, coral signal, light and dark tokens).
  - Scan result page: round 3 A - a status strip that shows only agents needing fixes as nodes (logo, name, fix count) and folds every OK agent into one `+N ok` chip with stacked logos; under it the fix table; beside it the path panel of round 2 D (source, core, junction, the current wrong link, "after Apply").
  - Second view of the same page: the round 3 E matrix (skill rows by agent columns, fixable cells as buttons, all-OK rows folded, a totals row), switchable with the table; only the matrix table is taken from E.
  - Overview page: the round 1 A mesh hub.
  - Rail: no left accent bar on the active nav button; the active state is its background only. The selected table row keeps its bar.
  - Buttons carry icons; each agent shows its real logo as inline SVG (the CSP blocks images from elsewhere); an agent with no published logo gets a letter tile of the same size; agents in the strip and matrix are derived from the scan rows, never hardcoded.
- Why: the old page looked like plain HTML and did not carry the repository's brand [user]; round 3 A keeps one strip height for 3 or 12 agents [user]; the matrix shows a fault pattern across agents [user]; the left bar was not wanted [user].
- If ignored: a page with 8 agents overflows a hub that draws every agent, and the redesign repeats rounds already decided.
- Rejected, round 3 [user]: B (hub with a 4x2 agent grid), C (agents listed in the rail, per-agent scan), D (ring hub of 8 nodes) - not chosen. The user's round 2 notes: a hub drawing every agent does not scale to a large number of agents; a classic table is safest with many agents; the path panel of D has good UX.
- Rejected, round 1 [user]: the three variants other than A (mesh hub) and B (command deck).
- Limit: the round files live in `.frontdoor\board\control-page`, gitignored and never committed; this entry is the only committed record of the choices.
- Limit: the Overview hub draws every agent, the scaling concern the user raised in round 2; Round 4 must show it with 8 agents.

### SKM-D24: brand fonts loaded from the Google Fonts CDN

- Decision: the page loads Oxanium, Share Tech Mono and IBM Plex Sans from Google Fonts; the server CSP adds `style-src https://fonts.googleapis.com` and `font-src https://fonts.gstatic.com` beside the nonces (user, 2026-11-26) [user].
- Why: chosen by the user over vendoring the font files [user]; no font file or font route is added to the repository [agent].
- If ignored: without the CSP sources the browser blocks the fonts and the page falls back to system fonts silently.
- Cost [agent]: every page load contacts Google (the client IP is visible to Google; the server already sends `Referrer-Policy: no-referrer`); offline the page falls back to system fonts, so the CSS font stacks must name fallbacks; the stylesheet is not pinned by a hash, so a change on Google's side reaches the page.
- Rejected: vendored woff2 in `ui\fonts\` with an OFL licence, a fixed-list GET route and `font-src 'self'` - the agent's recommendation, not chosen [user]; fonts as base64 `data:` URIs - large page [agent]; system fonts only - loses the brand [agent].
- Changes the plan line "one static `ui\index.html` without CDN" of `SKM-P9` (roadmap) for fonts only; scripts, styles and logos stay inline.

### SKM-D25: `/api/scan` returns source paths and target folders

- Decision: the scan response gains read-only `sources` (skill name to its winning source path) and `targetPaths` (target name to its folder) (user, 2026-11-26) [user].
- Why: the path panel shows source, junction and current link for every row, and the rows carry the source path only for MISSING and OK [agent].
- If ignored: the path panel cannot be drawn for a WRONG-TARGET or BROKEN row.
- Limit: `scan_id` hashes target, hash setting and rows only, so the new fields do not change it; the Apply rule is unchanged [agent].

### SKM-D26: Round 4 is one screening round of every page, edited in place

- Decision: before the build, design board Round 4 shows every page and state of the app as screens, not lettered variants for comparison; feedback is applied directly in Round 4 instead of opening another round; `ui\index.html` is built only after the user approves it (user, 2026-11-26) [user].
- Why: rounds 1-3 designed only the scan result page; the rest of the app is not designed yet [user].
- If ignored: the build starts on pages nobody has seen, and a round per fix scatters one design across boards.
- Rejected: building `ui\index.html` right after round 3 - the agent's recommendation, not chosen [user].

### SKM-D27: core `--target` accepts any configured target name

- Decision: `--target` of `scripts\skillmesh.py` accepts any target name in the config besides `both` and `all`; done after the UI design is approved (user, 2026-11-26) [user].
- Why: the page scans one agent of eight; the argparse choices name only three targets while `all` already walks every configured one [agent].
- If ignored: a configured fourth target can only be scanned through `all`.

### SKM-D28: pages, states, agents, themes and widths of Round 4

- Decision (user, 2026-11-26) [user]: Round 4 screens the pages Overview (round 1 A mesh hub), Scan result in Table and Matrix view, Output log, Safety rules, Doctor, Link, Init, and the states first run (no config), nothing to fix, scanning, Apply confirm, Apply done, stale scan (409) and server stopped; sample data keeps the 8 agents of round 3; every screen in light and dark; the design is for desktop, and the layout must still hold when the user narrows the browser window. Closes SKM-Q3.
- Why: the page runs on the owner's desktop, but a browser window is resized freely [user].
- If ignored: a layout drawn only at 1440 breaks when the window is snapped to half a screen.
- Rejected: a phone layout (390) as a design target - the page is used on the desktop [user]; light only - the page follows the system theme [user].

### SKM-D29: Round 4 screens approved as the build spec of the control page

- Decision: the 17 screens of design board Round 4 are approved as they are and are the spec the `ui\index.html` build follows; the screen list and per-screen content are in `SKM-P9` (roadmap) (user, 2026-11-26) [user].
- Changes Round 4 made on top of `SKM-D23`, approved with it [user]:
  - The one Scan all button sits at the top of the rail on every page, with the key S; it is disabled while scanning, on first run and when the server is stopped.
  - The status strip has no Scan button; its caption is one small line above the bus (`24 skills - 8 agents - scanned 14:02`).
  - The Overview right column holds Last scan (state pills, Review fixes), Scan options (skip comparing copies) and Doctor and Link status; it has no Scan button of its own.
  - Below about 1200 px wide (shown at 960): the rail folds to icons with a count badge, strip nodes drop the agent name, the path panel becomes a drawer over the table with a close button, Overview puts Last scan in a bar above the hub and hub nodes drop the path.
- Why: at 1280 the strip could not hold four problem agents, the ok chip and a Scan button; the first render had the button covering the chip [agent]. The user approved the screens without changes [user].
- If ignored: the build re-decides layout already reviewed, and a second Scan button per page drifts from the rail one.
- Limit [agent]: three screens show data the server does not return today, so the build needs core or server work, and the user has not ruled on it yet:
  - Link shows LINKED or WILL LINK per project skill and agent; `--mode link` has no preview.
  - Doctor shows grouped checks (config and roots, agent folders, this repository) with a count per root; the core prints only issues.
  - Output log lists the runs of the current server start with their output; the server keeps no run history.
- Limit [agent]: the screens live only in `.frontdoor\board\control-page\round-4` (sources and renders), which is gitignored; a lost working copy loses the visual spec and only this entry and `SKM-P9` remain.
- Known gaps kept on purpose [user]: at 960 the open drawer covers the Agent column and the Apply button until closed; at 1280 six or more problem agents need the narrow strip form; the Overview hub draws every agent and needs another column from about 10 agents; Overview has no per-agent scan until `SKM-D27`.

### SKM-D30: build plan of the control page, five steps

- Decision: the user approved the build plan below and ordered it run from step 1 to step 5 in one pass with no commit (user, 2026-11-26) [user].
  - Step 1, core (`scripts\skillmesh.py`): `doctor_checks(cfg)` returns every check with group, name, ok flag and detail, in three groups (config and roots with a skill count per root, agent folders, this repository); `test_doctor` reuses it so the CLI still prints only issues. `invoke_link` splits into a read-only `plan_link(agents)` (LINKED, WILL LINK, RELINK, SKIPPED per skill and agent, plus the hook state) and the executor that follows that plan; the CLI output is unchanged.
  - Step 2, server (`scripts\skillmesh_ui.py`): CSP adds `style-src https://fonts.googleapis.com` and `font-src https://fonts.gstatic.com` (`SKM-D24`); new `/api/status` (config present, targets with paths, roots, `.trash` count per target, server start time); `/api/scan` adds `sources` and `targetPaths` (`SKM-D25`); `/api/doctor` returns the grouped checks; `/api/link` takes `preview: true` to return only the plan; `/api/log` returns the runs of this server start, kept in memory, at most 50 (time, operation, result, output). Every new route keeps the token, `Host`, `Origin` and body-size guards.
  - Step 3, page (`ui\index.html`): one file rewritten to the 17 Round 4 screens; hash routes `#overview #scan #log #safety #doctor #link #init`; every state drawn from real data (first run, scanning, nothing to fix, Apply confirm, Apply done, stale scan 409, server stopped on a network error); strip, hub and Matrix columns built from scan rows, never a fixed list of 8 agents; fold below about 1200 px; key S runs Scan all; light and dark by `prefers-color-scheme`; logos inline SVG.
  - Step 4: `--target` accepts any configured target name plus `both` and `all` in core and server (`SKM-D27`); Overview gains a scan for one agent.
  - Step 5: verify, then record the result in the pack in the same pass and run `bldh.sh check`.
- Data answers (user, "approve all"): Link preview from a read-only `plan_link` [user]; Doctor groups from `doctor_checks` returning ok checks too [user]; Output log in memory, no file [user].
- Why: the three screens show data the server did not return (`SKM-D29` limit); the read-only plan keeps `--mode link` behaviour and its output as they are; an in-memory log matches the screen caption "since the server started" and writes nothing to disk [agent].
- Test method [user]: the page is checked in a browser with every `/api` call intercepted by mock data (no server, no real target), 17 states at 1280 and 960 px in light and dark, compared with Round 4; server logic is checked by calling the functions in Python on a sandbox config in the scratchpad, not over HTTP and not on the real targets; the user finishes with a click-through on the real server. The agent never calls the running page's `/api` (`AGENTS.md`).
- Single file [user]: `ui\index.html` stays one static file, estimated 1500 to 2000 lines, so the server keeps serving only `/` and the nonce goes on the one inline script and style.
- Rejected:
  - Link without a preview, only the result after clicking, dropping the WILL LINK column: ships less code but departs from the approved s07 screen [user].
  - Doctor listing only issues as the CLI does: loses the groups and ok rows of the approved s06 screen [user].
  - Output log written to `state\ui-log.jsonl`: survives restarts but grows without a bound and writes to disk for a caption that says "since the server started" [user].
  - Letting the agent run the real server with a sandbox config and click through it: closer to reality but loosens the `AGENTS.md` rule that agents never call the page's `/api` [user].
  - Splitting CSS and JS into separate files: needs static routes and a nonce per file for no gain at this size [user].
- What breaks if ignored: a page built before the data exists draws Link, Doctor and Output log from invented values; a second Scan or Apply path drifts from the guarded routes; a mocked page passed off as tested against the server hides a route mismatch.
- Limit [agent]: the mock test proves the page against the shapes the agent wrote, not against the live server; only the user's click-through covers that.

### SKM-D31: lesson - the nonce CSP blocks inline style attributes, and a test page without the CSP hid it

- Mistake [agent]: the first build of `ui\index.html` put positions and column counts in `style="..."` attributes (hub node coordinates, matrix `--cols`, skeleton widths, 37 places); the mock-data test page ran without any CSP, so every screen rendered correctly.
- Why it looked reasonable: the server's policy is `style-src 'nonce-...'` and the page's `<style>` and `<script>` carry the nonce, which reads as "styles are allowed"; the nonce covers only elements, not the `style` attribute, which `style-src-attr` governs and which falls back to `style-src` without `'unsafe-inline'`.
- What disproved it: the same page loaded with the server's policy as a meta tag; a probe inserting `<i style="color:red">` fired a `securitypolicyviolation` for `style-src-attr`. On the real server every positioned element would have lost its coordinates and the hub and matrix would have collapsed.
- Fix [agent]: markup carries `data-st="..."` and `applyStyles()` sets `element.style.cssText` through the CSSOM after each render, which the policy allows; the sprite uses a class. Re-run with the policy: no violation and no console error on the 7 pages.
- Rule kept: a page test that stands in for the server must send the server's CSP; `style-src-attr 'unsafe-inline'` was rejected as a fix because it loosens the policy (`SKM-D24` keeps fonts as the only external host) to save one helper [agent].
- If ignored: a page that passes every mock test shows an unstyled layout on the real server, and the failure appears only in the user's click-through.
