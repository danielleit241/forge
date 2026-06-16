---
name: ck-plan
description: "Create a phased implementation plan with pre-check, cross-plan scan, research, red-team review, validation, task hydration, and cook handoff. Modes: --fast, --hard, --deep, --parallel, --two. Flags: --tdd, --no-tasks."
user-invocable: true
---

# ck:plan — Structured Planning Pipeline

## Mode Reference

| Mode         | Research                         | Red-Team     | Validate     | Cook handoff                  |
| ------------ | -------------------------------- | ------------ | ------------ | ----------------------------- |
| `--fast`     | —                                | —            | —            | `/ck:cook --fast`             |
| `--hard`     | 2 researchers                    | ✓            | optional     | `/ck:cook`                    |
| `--deep`     | 2-3 + per-phase scout            | ✓            | required     | `/ck:cook [--tdd]`            |
| `--two`      | 2 researchers (one per approach) | ✓ both plans | pick A or B  | `/ck:cook [user-chosen mode]` |
| `--parallel` | 2 researchers                    | ✓            | optional     | `/ck:cook --parallel`         |
| no mode      | Auto-detect from scope and risk  | Follows mode | Follows mode | Ask before cook               |

**`--deep`** uses 2-3 researchers, per-phase scout context, forced validation,
and evidence-backed phase justification. Recommended with `--tdd`.

**Auto-detect** (no mode given): Fast if single-file, familiar, and low risk;
Hard for meaningful constraints; Deep for major refactors, 5+ areas, or
dependency-heavy architecture.

**Flag defaults**: `--tdd` and `--no-tasks` are both off.

---

### Step 1 — Context Scan

1. Detect active, suggested, or absent plan context. Ask whether to continue an active plan.
2. Read frontmatter from every unfinished `plans/*/plan.md`.
3. Detect overlapping files and shared dependencies.
4. Record `blockedBy` and `blocks` relationships bidirectionally when a real dependency exists.

If a spec file exists at `plans/specs/*.md`: read it fully — it replaces the need
to prompt for requirements in Step 2.

---

### Step 2 — Scope Challenge

Detect mode and challenge scope:

```
# Scope Challenge:
#   Exists?     → [does this feature already exist in the codebase?]
#   Minimum?    → [smallest impl that satisfies requirements]
#   Complexity? → [Fast | Hard | Two | Parallel | Auto]
#
# Mode: [detected or explicit]
# Test:  [default | --tdd]
# Tasks: [default | --no-tasks]
```

If scope is too large: suggest splitting and **wait for user confirmation**.

If `--hard` / `--two` / `--parallel` and novel/ambiguous with no brainstorm report and no spec file:
"No brainstorm found. Run `/ck:brainstorm` first? [Y/n]" — if Yes, stop; if No, proceed.

---

### Step 3 — Dependency Graph

Map the build order from the spec or brainstorm report:

```
Foundation: [DB schema / data models / shared utilities — must exist first]
Features:   [API endpoints / business logic / services]
Surface:    [UI components / CLI handlers / public contracts]
```

Pass this dependency chain to the planner in Step 5 as an implementation order constraint.
Foundation must be in the earliest phases; surface-layer work goes last.
If the dependency order is unclear, note it as a risk and continue.

---

### Step 4 — Research

**`--fast`**: skip entirely.

**`--hard` / `--parallel`**: spawn **2 `researcher` agents in parallel**:
- Instance A — role: `Primary` — recommended approach and best practices
- Instance B — role: `Alternative` — alternative approach and tradeoffs

**`--two`**: spawn **2 `researcher` agents in parallel**, each investigating one distinct approach:
- Instance A — role: `Approach A` — first viable approach (architecture, tradeoffs)
- Instance B — role: `Approach B` — second viable approach (meaningfully different strategy)

```
// Researcher A: [approach] → [verdict]
// Researcher B: [approach] → [verdict]
```

---

### Step 5 — Plan Creation

Spawn the **`planner` agent** with the feature description or spec/brainstorm report,
mode, research reports, test flag, and the dependency chain from Step 3.

**After planner returns**: capture the plan directory path from its "Directory: plans/{date}-{slug}/" line — you'll need it in Step 6.

Planner must follow these constraints:

**Vertical slicing** — each phase delivers one complete working path, not a horizontal layer.
Bad: Phase 1 = all DB, Phase 2 = all API, Phase 3 = all UI.
Good: Phase 1 = user can register (schema + API + UI), Phase 2 = user can login.

**Phase sizing** — a phase touches ≤8 files. If larger: split into sub-phases.
S (1-2 files) / M (3-5) / L (5-8) / XL → must split.

**Checkpoint phases** — insert a checkpoint after every 2-3 implementation phases:
```
## Checkpoint: After Phase N
- [ ] All tests pass, build succeeds
- [ ] Core path works end-to-end
- [ ] Review with user before continuing
```

- **`--tdd`**: planner adds `### Tests to Write First` to each phase
- **`--two`**: planner writes `plan-a.md` + `plan-b.md` (one per approach) — no `plan.md` yet
- **`--parallel`**: planner adds `## File Ownership` section to each phase file

Output structure:
```
plans/{slug}/
  plan.md            ← all modes except --two
  plan-a.md          ← --two only
  plan-b.md          ← --two only
  phase-01-{name}.md
  phase-02-{name}.md
  ...
```

---

### Step 6 — Red-Team Review

**`--fast`**: skip.

**All other modes**: before spawning `plan-reviewer`, **verify plan files exist on disk** using Glob:
- Normal modes: `plans/{date}-{slug}/plan.md` must exist
- `--two` mode: `plans/{date}-{slug}/plan-a.md` + `plans/{date}-{slug}/plan-b.md` must exist

If files are missing: **stop** — output `"Planner failed to write files. Do not proceed."`
Do not fall back to writing the plan inline.

Spawn **`plan-reviewer`** with all plan files and the brainstorm report when one was provided.

**`--two`**: reviewer evaluates both plan-a and plan-b — flag risks in each separately.

Adjudicate each finding:
- `ACCEPTED` → edit the relevant plan file immediately
- `NOTED` → append to Risks section of `plan.md`
- `REJECTED` → document reason

If `plan-reviewer` returns `BLOCK`: revise the flagged phase and re-run before proceeding.

---

### Step 7 — Validation + Handoff

**`--fast`**: skip questions — output cook command immediately.

**`--two`**: present a side-by-side comparison, then wait for the user to pick:

```
## Approach Comparison
Plan A: {1-line summary}
  Pros: {key strengths}  |  Cons: {key tradeoffs}

Plan B: {1-line summary}
  Pros: {key strengths}  |  Cons: {key tradeoffs}

Which approach? [A/B]
```

After selection: ask 2–3 targeted questions about the chosen plan. Merge chosen plan into
`plan.md`, delete the rejected file.

**`--hard` / `--parallel`**: validation is optional; ask when material uncertainty remains.
**`--deep`**: always validates.

After validation: hydrate Claude tasks per phase and critical step unless `--no-tasks` is set.

Output the exact cook command:

| Mode         | Cook command                                       |
| ------------ | -------------------------------------------------- |
| `--fast`     | `/ck:cook --fast [--tdd] plans/{slug}/plan.md`     |
| `--hard`     | `/ck:cook [--tdd] plans/{slug}/plan.md`            |
| `--deep`     | `/ck:cook [--tdd] plans/{slug}/plan.md`            |
| `--two`      | `/ck:cook [--fast] [--tdd] plans/{slug}/plan.md`   |
| `--parallel` | `/ck:cook --parallel [--tdd] plans/{slug}/plan.md` |

With no explicit mode, ask the user to validate, red-team again, run `/ck:cook`, or end.
Never auto-start cook.

---

## Agents

| Agent           | Step | Modes                                               |
| --------------- | ---- | --------------------------------------------------- |
| `researcher`    | 4    | `--hard`/`--parallel`/`--two` (×2), `--deep` (×2-3) |
| `scout`         | 4    | `--deep` only — per-phase context gathering         |
| `planner`       | 5    | All                                                 |
| `plan-reviewer` | 6    | All except `--fast`                                 |
