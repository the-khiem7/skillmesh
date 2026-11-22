# Skillmesh

Repo that keeps the skill repos under the configured roots linked to the agent skill directories (`.agents`, `.claude`, `.kiro` under the user profile) with NTFS junctions, so a change in a skill repo is live without reinstalling.

## Read first, in this order

1. `skillmesh.config.json` - the owner's roots, targets, ignore list, known foreign entries, overrides. Gitignored; absent on a fresh clone.
2. The baseline pack `docs\baseline\skillmesh` - the source of truth for scope, decisions with their reasons, phases and source topology. Load it with `baselinedocs-load` and read `skillmesh.hallucination.md` before proposing a change to behaviour.
3. `state\last-scan.json` - result of the last scan, if present. Rerun a scan rather than trust it.

## Operate

- All work goes through `scripts\Skillmesh.ps1` via the project skills in `skills\`: `skillmesh-watch`, `skillmesh-scan`, `skillmesh-sync`, `skillmesh-doctor`.
- Run scripts with `powershell -NoProfile -File scripts\Skillmesh.ps1 -Mode <Init|Scan|Apply|Doctor|Link>`. `-Target` is `agents|claude|kiro|both|all` (`both` = agents+claude, `all` = all three).
- `-Mode Scan` is read-only. `-Mode Apply` changes the filesystem and only runs after the user approves the exact scan output just shown.

## Set up after a clone

- Personal values (paths, skill and repo names) live only in the gitignored `skillmesh.config.json`; the pack records generic rules and never a personal value. `skillmesh.config.example.json` is the committed template; it uses environment variables such as `%USERPROFILE%`, which the script expands. Never write a user name, an absolute personal path, a personal skill or repo name, or an email into a committed file.
- Run `powershell -NoProfile -File scripts\Skillmesh.ps1 -Mode Init` once. It copies the example to `skillmesh.config.json` when that file is absent, then edit `roots`, `targets`, `ignore` and `known_foreign` and run `-Mode Doctor`. Every mode except `Link` stops until the config exists.
- The project skills are committed in `skills\`. `.claude\`, `.kiro\` and `.agents\` are gitignored and empty on a fresh clone.
- Run `powershell -NoProfile -File scripts\Skillmesh.ps1 -Mode Link` (add `-Agent claude`, `-Agent kiro` or `-Agent claude,kiro`; default both). It junctions each `skills\<name>` into `.<agent>\skills\<name>` and creates the Claude `SessionStart` hook in `.claude\settings.json` when absent. Rerunning is safe; a real directory in the way is skipped, never deleted.
- `-Mode Link` only touches this repo's own gitignored agent folders, so it needs no scan approval. Restart the agent session afterwards so it sees the skills.
- Add a project skill by creating `skills\<name>\SKILL.md`, then run `-Mode Link` again.

## Safety rules

- Never delete a real directory at a target; `Apply` moves it to `<target>\.trash`.
- Remove a junction only as a link (`[IO.Directory]::Delete`, `rmdir`). Never `Remove-Item -Recurse` on a junction.
- Never touch a FOREIGN entry; report it.
- Never run `npx skills update` or `npx skills add` for skills held in the repo; they overwrite junctions with copies.
- Never edit files under a configured root or the targets by hand from here; only `Skillmesh.ps1` changes them.
- Never commit; the user commits.

## Changing config or decisions

- Ask the user with labelled questions first.
- After approval, edit `skillmesh.config.json` (personal values) and record the decision in the baseline pack (generic wording, no personal value) in the same pass, then run `-Mode Doctor`.
- `state\` is generated; never edit it.

## Files

| Path | Role |
|---|---|
| `scripts\Skillmesh.ps1` | init, scan, apply, doctor, link |
| `skillmesh.config.example.json` | committed template for the config |
| `skillmesh.config.json` | gitignored; the owner's config, created by `-Mode Init` |
| `docs\baseline\skillmesh\` | baseline pack: source of truth for decisions and development state |
| `skills\` | project skills, the only real copy |
| `.claude\`, `.kiro\` | gitignored; `-Mode Link` junctions `skills\` into them |
| `.claude\settings.json` | gitignored; `SessionStart` hook for `skillmesh-watch`, created by `-Mode Link` |
