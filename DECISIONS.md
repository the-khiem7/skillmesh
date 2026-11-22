# Decisions

Status `assumed` = recommended default applied without an explicit answer; confirm or change it.

## D1 - Flat junctions named after the skill directory

- Decision: every skill becomes `<target>\<skill-dir-name>`, regardless of how deep it sits in its source repo (e.g. `<bundle>\skills\<category>\<skill>` becomes `<target>\<skill>`).
- Why: agents read skills one level deep under the skills directory.
- If ignored: skills nested under a category folder are never discovered.
- Rejected: mirroring the category structure in the target - agents would not find the skills.

## D2 - Shallowest source wins on a name clash

- Decision: when one skill name has several sources, the source closest to a root wins. Equal depth is a CONFLICT and nothing is linked until an entry in `overrides` picks one. Example: `<root>\<skill>` beats `<root>\<bundle>\skills\<category>\<skill>`.
- Why: a standalone skill repo is the maintained copy; a skill nested in a bundle repo is a bundle copy.
- If ignored: the bundle copy can shadow the maintained one.
- Rejected: newest-modified wins - changes silently with every edit.

## D3 - Ignore repos that carry no SKILL.md

- Decision: repos listed in `ignore` are never scanned.
- Why: a repo that holds no skill has nothing to link.
- If ignored: noise in every scan.

## D4 - Real copies are moved to trash, then replaced

- Decision: a real directory at the target (an `npx skills` install) is moved to `<target>\.trash\<name>-<timestamp>` and replaced by a junction. The scan reports how the copy differs from the source (files only in source, only in copy, changed). A difference does not stop the move.
- Why: the junction makes the repo the single source of truth; the trash keeps the old copy recoverable.
- If ignored: the copy keeps shadowing the repo and edits in the repo never show up.
- Rejected: deleting the copy - not recoverable. Stopping on every difference - copies almost always differ (the repo carries README and git files an install omits).
- Status: assumed (hash question answered by default).

## D5 - Foreign entries are reported only

- Decision: a FOREIGN entry is one at a target with no source in the roots. It is never touched. Names listed in `known_foreign` are shown as known; anything else is shown as new. Skills installed by `npx skills` stay foreign, are managed by `npx skills` and not by junctions, and are listed in `known_foreign` so the session-start watch stays quiet. A skill that is meant to stay foreign is not moved into a repo. Which names a user lists, and why, is recorded in the gitignored `DECISIONS.local.md` (D13).
- Why: they may be hand-made skills, installs from elsewhere, retired skills or tool state; removing them is irreversible knowledge loss. The name FOREIGN (not "orphan") because most of these are skills installed from outside the repos, not left behind by one.
- If ignored: skills with no repo copy get deleted.
- Rejected: moving `npx skills` installs into a repo - `npx skills` already updates them.
- Trash: the `.trash` directories at the targets are never cleaned by this repo.

## D6 - Wrong or broken junctions point straight at the source

- Decision: a junction targeting anything other than the winning source (for example `.claude` pointing into `.agents`) is removed and recreated against the source, in both targets. Only the link is removed, never the content behind it.
- Why: chaining through `.agents` ends at a copy, not the repo.
- If ignored: edits in the repo do not propagate.

## D7 - Target selectable, default both

- Decision: `-Target agents|claude|both`, default `both`.
- Why: lets one side be applied and verified before the other.

## D7a - Kiro is a third target; `all` covers it, `both` stays two

- Decision: `-Target agents|claude|kiro|both|all`. `kiro` is the Kiro user-level skills directory. `both` keeps meaning agents+claude and stays the default; `all` is all three targets. The `SessionStart` hook (D8) scans `-Target all`.
- Why: Kiro reads user-level skills from `.kiro\skills`, so it must be linked to the same repos as the other two. Keeping `both` and the default unchanged keeps old commands and approvals meaning what they did.
- If ignored: Kiro misses every skill added to a root, and drift there is never reported.
- Rejected: making `both` mean all three - silently widens what an old `-Target both` approval changes. Default `all` - same reason.

## D8 - Session-start watch, project scoped, read-only

- Decision: a `SessionStart` hook in this repo's `.claude\settings.json` runs a read-only scan and injects a one-line summary only when something mismatches. It never fixes anything. Built before the other skills.
- Why: a mismatch is visible at the start of every session opened here without any action.
- If ignored: drift goes unnoticed until a skill misbehaves.
- Limit: sessions opened in other repos get no warning. A user-level hook is out of scope.
- Rejected: user-level hook - outside the project-scoped requirement.
- Status: assumed (scope and ordering questions answered by default).

## D9 - Scan state is not committed

- Decision: `state\last-scan.json` is generated by the script and listed in `.gitignore`.
- Why: every scan would otherwise produce a diff.
- Status: assumed.

## D10 - PowerShell 5.1 and junctions

- Decision: one script, `scripts\Skillmesh.ps1`, written for Windows PowerShell 5.1; links are NTFS junctions.
- Why: 5.1 is what the machine has; junctions need no administrator rights, which the standard-user account requires.
- If ignored: symlinks or newer syntax need elevation or a second runtime.
- Status: assumed for the 5.1 part.

## D11 - Config and this file must agree

- Decision: `skillmesh-doctor` checks that every name in `ignore`, `known_foreign` and `overrides` appears in `DECISIONS.local.md` when that file exists, and that `AGENTS.md`, `DECISIONS.md` and `skills\` exist.
- Why: config carries no reasons; the owner's local decision record is where they live.
- If ignored: config entries accumulate with no recorded reason.

## D12 - Project skills live in `skills\` and are linked into agent folders on demand

- Decision: the project skills are the only real copy, in `skills\<name>`, committed. `.claude\`, `.kiro\` and `.agents\` are gitignored. `-Mode Link [-Agent claude,kiro]` creates one NTFS junction `.<agent>\skills\<name>` -> `skills\<name>` per skill, and creates the Claude `SessionStart` hook (D8) in `.claude\settings.json` when that file is absent. User decision of 2026-11-18.
- Why: a fresh clone gets the workflow by running one command, and an edit to a skill is live for every linked agent with nothing to keep in step.
- If ignored: copies in agent folders drift from `skills\` and the agents run different skill text.
- Rejected: committing `.claude\skills` and `.kiro\skills` - a junction is not stored by git, and a copy drifts. A junction of the whole `.<agent>\skills` folder - a user could not add their own skill beside the project ones. Overwriting an existing `.claude\settings.json` - it may hold the user's own settings.
- Limit: `Link` skips a real directory in the way and never deletes it. Kiro does not read `.claude\settings.json`, so Kiro sessions get no watch warning. The user-level targets in `skillmesh.config.json` are unchanged.

## D13 - Personal values live in gitignored files, a committed example shows the shape

- Decision: `skillmesh.config.json` (roots, targets, ignore, known_foreign, overrides) and `DECISIONS.local.md` (the reasons for those entries and any personal history) are gitignored. `skillmesh.config.example.json` is committed with neutral values and environment variables such as `%USERPROFILE%`; the script expands environment variables in `roots` and `targets`. `-Mode Init` copies the example to `skillmesh.config.json` when it is absent. A committed file never holds a user name, an absolute personal path, a personal skill or repo name, or an email. User decision of 2026-11-18.
- Why: the repository is published, and every clone has its own paths and its own foreign skills.
- If ignored: a published file leaks the owner's paths and skill inventory, and each clone edits a committed file.
- Rejected: keeping the config committed with personal values - leaks them. Committing the real config and asking each user to edit it - every user commits their own paths.
- Limit: `-Mode Link` works without a config; every other mode stops with a message until `-Mode Init` has run.
