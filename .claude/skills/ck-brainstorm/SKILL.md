---
name: ck-brainstorm
description: Extract user intent, explore solution space, and write a design report. Use when the right design is unclear, requirements are vague, or the user asks to brainstorm. Produces one report under plans/reports — never writes implementation code. Always use before ck-plan for novel or ambiguous work. Handoff options after report: /ck:spec (recommended for novel work), /ck:plan --tdd, or /ck:plan.
user-invocable: true
---

# ck:brainstorm

Hard gate: no implementation code, scaffolding, or implementation skill calls.
Ends with a design report and optional `/ck:spec` or `/ck:plan` handoff.

## Principle

Users who brainstorm don't know the technical landscape — that's why they're here.
Never ask technical questions. Scout owns technical discovery. Questions go to intent only.

---

## Step 0 — Scout (silent)

Before saying anything: inspect repo. Map project type, modules, patterns, docs, plans, schemas,
constraints. Do not spawn planner or docs-manager. Do not surface raw findings yet.

---

## Step 1 — Intent Interview

State a hypothesis with confidence number before the first question:

```
HYPOTHESIS: You want X because Y — "feature name" was the word that came to mind.
CONFIDENCE: ~30% — missing: who this is for, what success looks like
```

Then interview one question at a time, each with your guess attached:

```
Q: [one focused question]
GUESS: I think [answer] because [reasoning] — correct me if I'm wrong.
```

Why one at a time: the third question often depends on the answer to the first.
Why attach a guess: users react to a wrong guess faster than they generate from scratch.

**Stop when:** can you predict the user's reaction to the next 3 questions you'd ask? If yes → proceed.
After 5+ rounds with no convergence: "Something foundational is missing — want to step back?"

Never ask:
- "What are the acceptance criteria?" → too technical
- "Which modules are involved?" → scout already knows
- "What are the non-negotiable constraints?" → jargon

If the request spans 3+ independent problems, surface it and ask which to tackle first.

When confident, write a restate the user can confirm line by line:

```
Here's what I understand:
- Outcome:      [one line]
- Who benefits: [one line]
- Why now:      [one line]
- Success:      [one line — testable]
- Not doing:    [one line — explicit scope boundary]

Yes / no / refine?
```

Wait for explicit yes. "Sounds good" and "whatever you think" are not yes — re-ask with two
concrete options if the user deflects.

---

## Step 2 — Diverge

Restate the confirmed intent as a "How Might We" question. Then generate 3-5 variations.
Pick the lenses that fit — don't run all mechanically:

- **Inversion** — what if you did the opposite of the obvious approach?
- **Constraint removal** — what if time, tech, or budget weren't factors?
- **Simplification** — what's the version that's 10x simpler?
- **10x scale** — what would this look like serving 100× the current load or users?
- **Audience shift** — what if this were built for a completely different user?

Push past the first obvious answer. Each variation should feel meaningfully different, not
just a feature tweak. Tell a story for each — not just a bullet.

---

## Step 3 — Analyze & Converge

Cluster variations into 2-3 distinct directions. For each direction:

**User value** — painkiller (users actively seek this, have workarounds, will switch) or
vitamin (nice-to-have, won't change behavior)?

**Feasibility** — what's the hardest part? What must exist first? Time to first working version?

**Differentiation** — what makes this genuinely different from what already exists?

Surface hidden assumptions per direction:

```
Must be true:   [what kills the idea if wrong — validate before building]
Should be true: [what changes the approach if wrong — adjustable]
Might be true:  [secondary bets — validate only after core is proven]
```

Be honest, not supportive. If a direction is weak, say so with a specific reason.

---

## Step 4 — Consensus

Use AskUserQuestion to select or refine. Frame options as outcomes, not technical mechanisms.
Do not finalize while the Step 1 restate has unresolved items.
Obtain explicit approval for the chosen direction.

---

## Step 5 — Report

Write exactly one report: `plans/reports/brainstorm-YYMMDD-HHMM-{slug}.md`

Sections:
1. Problem statement + scouted repo context
2. Confirmed intent (restate from Step 1)
3. Directions explored — why each was kept or dropped
4. Chosen direction + rationale
5. Hidden assumptions (Must / Should / Might be true)
6. **Not Doing** — explicit list of what's out of scope and why
7. Success metrics — testable, not vague
8. Next steps

---

## Step 6 — Handoff

After approval and written report, offer:

1. `/ck:spec {report-path}` — write a formal spec before planning (recommended for novel work)
2. `/ck:plan --tdd {report-path}` — skip spec, plan with TDD
3. `/ck:plan {report-path}` — skip spec, standard plan
4. End session
