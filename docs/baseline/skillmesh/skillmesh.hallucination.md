---
baseline_schema: "3.0"
pack: "skillmesh"
document: "hallucination"
status: "active"
updated: "2026-11-22"
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
| SKM-D10 | runtime and link type | closed, part assumed | - |
| SKM-D11 | config and decision record must agree | closed, reversed by SKM-D16 | SKM-D12, SKM-D16 |
| SKM-D12 | guidance and decisions in separate files | closed, record moved to the pack by SKM-D16 | SKM-D11, SKM-D16 |
| SKM-D13 | project skills in skills\ linked into gitignored agent folders | closed | SKM-D8, SKM-D12 |
| SKM-D14 | personal values in gitignored files, committed example config | closed, local decision file dropped by SKM-D16 | SKM-D5, SKM-D11, SKM-D16 |
| SKM-D15 | Kiro as a third target, `all` | closed | SKM-D7, SKM-D8 |
| SKM-D16 | the pack is the only decision record | closed | SKM-D11, SKM-D12, SKM-D14 |

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
