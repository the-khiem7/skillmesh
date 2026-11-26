# Skillmesh

Repo that keeps the skill repos under the configured roots linked to the agent skill directories (`.agents`, `.claude`, `.kiro` under the user profile) with NTFS junctions, so a change in a skill repo is live without reinstalling.

## Read first, in this order

1. `skillmesh.config.json` - the owner's roots, targets, ignore list, known foreign entries, overrides. Gitignored; absent on a fresh clone.
2. The baseline pack `docs\baseline\skillmesh` - the source of truth for scope, decisions with their reasons, phases and source topology. Load it with `baselinedocs-load` and read `skillmesh.hallucination.md` before proposing a change to behaviour.
3. `state\last-scan.json` - result of the last scan, if present. Rerun a scan rather than trust it.

## Operate

- All work goes through `scripts\skillmesh.py` via the project skills in `skills\`: `skillmesh-watch`, `skillmesh-scan`, `skillmesh-sync`, `skillmesh-doctor`.
- Run scripts with `uv run scripts\skillmesh.py --mode <init|scan|apply|doctor|link>`. `--target` is `both` (agents+claude, the default), `all` (every target of the config) or any target name the config holds.
- `--mode scan` is read-only. `--mode apply` changes the filesystem and only runs after the user approves the exact scan output just shown.
- Control page: `uv run scripts\skillmesh_ui.py` starts a local page on `127.0.0.1:8765` (`--port <n>`, `--no-open`). Scan, Doctor, Link and Init are buttons, Output log lists this start's runs, and fonts load from the Google Fonts CDN (the page's only external host); the user ticks rows and confirms Apply there, which is the approval of that scan. Start it only when the user asks, tell them the URL, and stop it with Ctrl+C (or end the process) when they are done. Never call its `/api` endpoints from an agent: the per-start token is for the page alone.

## Set up after a clone

- Personal values (paths, skill and repo names) live only in the gitignored `skillmesh.config.json`; the pack records generic rules and never a personal value. `skillmesh.config.example.json` is the committed template; it uses environment variables such as `%USERPROFILE%`, which the script expands. Never write a user name, an absolute personal path, a personal skill or repo name, or an email into a committed file.
- Run `uv run scripts\skillmesh.py --mode init` once. It copies the example to `skillmesh.config.json` when that file is absent, then edit `roots`, `targets`, `ignore` and `known_foreign` and run `--mode doctor`. Every mode except `link` stops until the config exists.
- The project skills are committed in `skills\`. `.claude\`, `.kiro\` and `.agents\` are gitignored and empty on a fresh clone.
- Run `uv run scripts\skillmesh.py --mode link` (add `--agent claude`, `--agent kiro` or `--agent claude kiro`; default both). It junctions each `skills\<name>` into `.<agent>\skills\<name>` and creates the Claude `SessionStart` hook in `.claude\settings.json` when absent. Rerunning is safe; a real directory in the way is skipped, never deleted.
- `--mode link` only touches this repo's own gitignored agent folders, so it needs no scan approval. Restart the agent session afterwards so it sees the skills.
- Add a project skill by creating `skills\<name>\SKILL.md`, then run `--mode link` again.

## Safety rules

- Never delete a real directory at a target; `Apply` moves it to `<target>\.trash`.
- Remove a junction only as a link (`[IO.Directory]::Delete`, `rmdir`). Never `Remove-Item -Recurse` on a junction.
- Never touch a FOREIGN entry; report it.
- Never run `npx skills update` or `npx skills add` for skills held in the repo; they overwrite junctions with copies.
- Never edit files under a configured root or the targets by hand from here; only `skillmesh.py` changes them.
- Never commit; the user commits.

## Changing config or decisions

- Ask the user with labelled questions first.
- After approval, edit `skillmesh.config.json` (personal values) and record the decision in the baseline pack (generic wording, no personal value) in the same pass, then run `--mode doctor`.
- `state\` is generated; never edit it.

## Files

| Path | Role |
|---|---|
| `scripts\skillmesh.py` | init, scan, apply, doctor, link; run with `uv run` |
| `scripts\skillmesh_ui.py` | local control page server (stdlib `http.server`, `127.0.0.1` only); imports `skillmesh.py` |
| `ui\index.html` | the control page, one static file served by the server |
| `scripts\Skillmesh.ps1` | the earlier PowerShell core; kept until one verified cycle on the Python core and the owner's approval to remove it |
| `skillmesh.config.example.json` | committed template for the config |
| `skillmesh.config.json` | gitignored; the owner's config, created by `--mode init` |
| `docs\baseline\skillmesh\` | baseline pack: source of truth for decisions and development state |
| `skills\` | project skills, the only real copy |
| `.claude\`, `.kiro\` | gitignored; `--mode link` junctions `skills\` into them |
| `.claude\settings.json` | gitignored; `SessionStart` hook for `skillmesh-watch`, created by `--mode link` |
