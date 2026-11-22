---
name: skillmesh-sync
description: Create or repair the junctions from the configured skill roots into the agent skill directories, moving real copies to trash. Changes the filesystem, so it always shows the scan and waits for approval. Use when the user asks to link, sync, or fix the skill junctions.
---

# skillmesh-sync

Changes the filesystem. Dry run first, always.

1. Run `powershell -NoProfile -File scripts\Skillmesh.ps1 -Mode Scan` for the requested target (`agents`, `claude`, `kiro`, `both` = agents+claude, `all` = all three; default `both`) and show the actionable rows: MISSING (link), COPY (trash+link), WRONG-TARGET and BROKEN (relink). CONFLICT and FOREIGN rows are never acted on.
2. Ask for approval of that exact output as a labelled question, offering to apply one target at a time (recommend `claude` first, then `agents`, then `kiro`). Approval covers only the output just shown.
3. On approval run `powershell -NoProfile -File scripts\Skillmesh.ps1 -Mode Apply -Target <target>`. Copies go to `<target>\.trash\<name>-<timestamp>`; nothing is deleted.
4. The script rescans afterwards. Report the new Summary line. Any row not OK is a failure to report, not to retry.
5. Do not run `npx skills update` and do not commit.
