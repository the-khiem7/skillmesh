---
name: skillmesh-scan
description: Scan the configured skill roots against the agent skill directories and report each skill as OK, MISSING, COPY, WRONG-TARGET, BROKEN, CONFLICT or FOREIGN. Read-only. Use when the user asks which skills are linked, out of sync, or mismatched.
---

# skillmesh-scan

Read-only.

1. Run `uv run scripts\skillmesh.py --mode scan` (add `--target agents|claude|kiro|both|all` or `--name <skill>` to narrow). It also writes `state\last-scan.json`.
2. Summarise by state, not by row. Lead with what needs action; state per target.
3. For COPY rows, report the Detail column (files only in source, only in copy, changed). A copy with "copy-only" files means the live install holds files the repo lacks; say so before any Apply.
4. For FOREIGN rows, show NEW ones to the user; known ones only as a count.
5. For CONFLICT rows, name the competing sources and ask the user which wins (labelled question). A chosen winner goes into `overrides` in `skillmesh.config.json` and a decision in the baseline pack (`docs/baseline/skillmesh`, generic wording only), same pass.
6. Offer `skillmesh-sync` when any MISSING, COPY, WRONG-TARGET or BROKEN row exists.
