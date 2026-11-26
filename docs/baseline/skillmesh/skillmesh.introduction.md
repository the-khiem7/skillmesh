---
baseline_schema: "3.0"
pack: "skillmesh"
document: "introduction"
status: "active"
updated: "2026-11-22"
code_ref: "60ea6eb"
---

# Skillmesh - introduction

## Scope

- Keep the skill repos under the configured roots linked into the agent skill directories with NTFS junctions, so an edit in a repo is live without `npx skills update`.
- Operated by agents; the only reader of the repository's documents that matters is an agent resuming across sessions.
- In scope: discover skills, compare them with both targets, create or repair junctions, warn at session start, check the repository's own consistency.
- Out of scope: skills installed by `npx skills` (they stay with `npx skills`), editing the skill repos, committing, pushing.

## Current truth

| Item | State | Evidence |
|---|---|---|
| Roots and targets | personal, held in the gitignored `skillmesh.config.json`; `skillmesh.config.example.json` shows the shape | `SKM-D14` |
| Scan 2026-11-09 | no MISSING, COPY, WRONG-TARGET, BROKEN or CONFLICT row; one NEW FOREIGN entry was added to `known_foreign` | `Skillmesh.ps1 -Mode Scan -NoHash` |
| Doctor 2026-11-22 | prints `ok` after the decision files were removed | `SKM-D16` |
| Session-start hook | Fired on resumed sessions and printed its summary line | observed 2026-11-06 and 2026-11-09 |
| Backups | `.trash` in each target holds the replaced copies (41 in `.claude`, 40 in `.agents` as of 2026-11-04); never cleaned by this repository | `SKM-D5` |
| Commits | Repository re-initialised with `git init` before publishing; no earlier history | `SKM-D14` |

- This pack is the only decision record (`SKM-D16`); no `DECISIONS.md` or `DECISIONS.local.md` exists.
- `AGENTS.md` holds working guidance only and points at this pack in its read order.

## Target

- Every skill under the roots that carries a `SKILL.md` is a junction in both targets, pointing straight at its source.
- A session opened here is told within its first line if that stops being true.
- No committed file holds a personal value (`SKM-D14`).

## Constraints

- Standard user: no administrator rights, so junctions (no elevation needed) and Windows PowerShell 5.1 only.
- `Apply` is never run without the user approving the exact scan output just shown.
- Never delete a real directory at a target; move it to `<target>\.trash`.
- Remove a junction only as a link, never recursively.
- Never touch a FOREIGN entry.
- Never run `npx skills update` or `npx skills add` for a skill held in the repo.
- Never edit files under a configured root or the targets by hand from this repository.
- No commit unless the user asks; a commit uses `commit-composer-max` or `commit-composer`.
