---
baseline_schema: "3.0"
pack: "skillmesh"
document: "roadmap"
status: "active"
updated: "2026-11-22"
code_ref: "uncommitted"
---

# Skillmesh - roadmap

## Phases

| Phase | Work | Depends on | Status |
|---|---|---|---|
| SKM-P1 | Scan and compare script | - | complete |
| SKM-P2 | Link both targets to the repos | SKM-P1 | complete |
| SKM-P3 | Session-start watch and project skills | SKM-P1 | complete |
| SKM-P4 | Guidance file and decision record | SKM-P2 | complete |
| SKM-P5 | Convert the documents into this pack | SKM-P4 | complete |
| SKM-P6 | Triage NEW FOREIGN entries | SKM-P2 | complete |
| SKM-P7 | Move personal values into gitignored config | SKM-P5 | active |

### SKM-P1: Phase 1 - scan and compare script

- Delivered `scripts\Skillmesh.ps1` with `Scan`, `Apply` and `Doctor`, `skillmesh.config.json` and `.gitignore` (commit `de953be`).
- Acceptance: every skill under the roots is classified per target as OK, MISSING, COPY, WRONG-TARGET, BROKEN or CONFLICT, and every unmatched entry as FOREIGN.
- Evidence: the first scan on 2026-11-03 classified 128 rows: 76 COPY, 4 MISSING, 4 WRONG-TARGET, 43 FOREIGN, no CONFLICT.

### SKM-P2: Phase 2 - link both targets

- Applied to `claude`, then to `agents`, each after the user approved the exact scan output (`SKM-D4`, `SKM-D6`).
- Acceptance: a rescan shows no MISSING, COPY, WRONG-TARGET, BROKEN or CONFLICT row.
- Evidence: `OK=84` after both applies on 2026-11-04; `OK=100 FOREIGN=43` on 2026-11-09 after more skills were linked later.
- Evidence: a probe file written through a `claude` junction appeared in the source folder and was removed; Claude Code listed newly linked skills while the session ran.

### SKM-P3: Phase 3 - session-start watch and project skills

- Delivered the `SessionStart` hook and `skillmesh-watch`, `skillmesh-scan`, `skillmesh-sync`, `skillmesh-doctor` (commit `ddeacc0`, `SKM-D8`).
- Acceptance: a session opened here prints one summary line when something mismatches and nothing otherwise.
- Evidence: the hook output appeared on resumed sessions (`12 MISSING` on 2026-11-06, `2 FOREIGN` on 2026-11-09).
- Not verified: the hook on a fresh start (not a resume), and the four skills invoked by name.

### SKM-P4: Phase 4 - guidance file and decision record

- Delivered `AGENTS.md` and `DECISIONS.md` (commit `6c29d1f`, `SKM-D12`).
- Acceptance: guidance and reasons sit in separate files and `-Mode Doctor` prints `ok`.

### SKM-P5: Phase 5 - convert the documents into this pack

- Delivered this pack: introduction, roadmap, decisions, source topology.
- Acceptance: every decision from `DECISIONS.md` is present in `skillmesh.hallucination.md` (`D7a` migrated as `SKM-D15`); `SKM-Q1` is closed by `SKM-D16` and `DECISIONS.md` and `DECISIONS.local.md` are removed; `-Mode Doctor` prints `ok`.
- Not verified: `bldh.sh check` after the last edit.

### SKM-P6: Phase 6 - triage NEW FOREIGN entries

- A NEW FOREIGN entry was present in both targets and not in `known_foreign`; the user chose to add it on 2026-11-09 (`SKM-D5`).
- Acceptance: each NEW entry is either added to `known_foreign` or left reported, by the user's choice.
- Evidence: after the edit `-Watch` printed nothing.

### SKM-P7: Phase 7 - personal values into gitignored files

- Delivered: `skillmesh.config.example.json`, `-Mode Init`, environment-variable expansion in `roots` and `targets`, the setup section in `AGENTS.md` (`SKM-D14`).
- Acceptance: a search of every tracked file for the owner's user name, absolute personal paths, personal skill and repo names and email finds nothing; `-Mode Doctor` prints `ok` with the real config; `-Mode Init` on a clone without a config creates one from the example.
- Not verified until run: the clone test.

## Risks

| Risk | Effect | Mitigation |
|---|---|---|
| `npx skills update` run on a linked skill | junction replaced by a copy | rescan shows COPY; `Apply` restores |
| A repo moves or is deleted | junctions become BROKEN | scan reports it; ask whether the skill is gone or relocated |
| Hook output ignored | drift persists | none beyond the one-line summary |

## Next action

- Finish `SKM-P7` verification (the clone test), then run `bldh.sh check` on this pack.
