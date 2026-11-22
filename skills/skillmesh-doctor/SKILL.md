---
name: skillmesh-doctor
description: Check that this repo's own files agree - config entries documented in DECISIONS.local.md when present, roots and targets present, hook file present - and walk the user through BROKEN, CONFLICT and NEW FOREIGN rows. Use after changing skillmesh.config.json or DECISIONS.local.md, or when a scan shows rows that are not plain MISSING or COPY.
---

# skillmesh-doctor

1. Run `powershell -NoProfile -File scripts\Skillmesh.ps1 -Mode Doctor`. Each issue is one line.
2. A config entry missing from `DECISIONS.md` means a decision was never recorded: ask the user for the reason (labelled question), then add it to `DECISIONS.md`. Never delete the config entry to silence the check.
3. Then run a scan and handle the leftover rows one at a time:
   - BROKEN: the source moved or was deleted. Ask whether the skill is gone or relocated.
   - CONFLICT: ask which source wins; record it as an `overrides` entry plus a decision.
   - NEW FOREIGN: ask whether to add it to `known_foreign` (with a decision) or leave it reported.
4. Config and decision edits happen only after the user answers, together, then rerun Doctor.
