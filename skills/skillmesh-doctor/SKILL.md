---
name: skillmesh-doctor
description: Check that this repo's own files agree - roots and targets present, repo files present - and walk the user through BROKEN, CONFLICT and NEW FOREIGN rows. Use after changing skillmesh.config.json, or when a scan shows rows that are not plain MISSING or COPY.
---

# skillmesh-doctor

1. Run `powershell -NoProfile -File scripts\Skillmesh.ps1 -Mode Doctor`. Each issue is one line.
2. Then run a scan and handle the leftover rows one at a time:
   - BROKEN: the source moved or was deleted. Ask whether the skill is gone or relocated.
   - CONFLICT: ask which source wins; record it as an `overrides` entry plus a decision in the baseline pack (`docs/baseline/skillmesh`), with no personal name in the pack.
   - NEW FOREIGN: ask whether to add it to `known_foreign` (with a decision in the pack, generic wording only) or leave it reported.
3. Config and decision edits happen only after the user answers, together, then rerun Doctor.
