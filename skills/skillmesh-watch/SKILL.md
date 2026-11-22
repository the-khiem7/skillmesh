---
name: skillmesh-watch
description: React to the SessionStart line "Skillmesh: ... mismatch" in this repo, or check on demand whether the skill junctions have drifted. Read-only. Use when a session opens with a Skillmesh warning or the user asks if the skills are still linked.
---

# skillmesh-watch

Read-only. Never fixes anything.

1. The `SessionStart` hook in `.claude\settings.json` runs `scripts\Skillmesh.ps1 -Mode Scan -Watch`. It prints nothing when every skill is OK, and one line like `Skillmesh: 2 MISSING, 1 COPY - see skillmesh-scan / skillmesh-sync` otherwise. FOREIGN rows listed in `known_foreign` do not count.
2. On that line, tell the user the counts and offer `skillmesh-scan` for detail. Do not run `skillmesh-sync` unprompted.
3. On demand, run `powershell -NoProfile -File scripts\Skillmesh.ps1 -Mode Scan -Watch` and report its output, or "no mismatch" when empty.
4. The hook fires only for sessions opened in this repo (decision SKM-D8 in the baseline pack).
