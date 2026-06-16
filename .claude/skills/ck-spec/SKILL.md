---
name: ck-spec
description: Write a structured specification from a brainstorm report or feature brief before planning. Use after /ck:brainstorm, when the user has a clear idea but needs a formal spec, or before /ck:plan for any non-trivial feature. Bridges intent to plan — outputs a spec file at plans/specs/ and hands off to /ck:plan. Trigger on "write a spec", "formalize requirements", "before we plan", or when ck-brainstorm suggests it.
user-invocable: true
---

# ck:spec — Specification Before Planning

Writes the shared source of truth between you and the user before any planning or code.
Hard gate: no implementation code, no plan files. Output is a spec document only.

## Principle

A spec surfaces misunderstandings before code gets written. Its value is forcing clarity early —
not as documentation after the fact. Assumptions not written down don't exist.

## Step 0 — Load Context

If a brainstorm report path was provided: read it fully.
Otherwise: quick scout (project type, tech stack, existing patterns, conventions).

## Step 1 — Surface Assumptions

Before writing anything, list what you're assuming and ask the user to correct:

```
ASSUMPTIONS I'M MAKING:
1. [assumption about tech stack / runtime]
2. [assumption about target users or scale]
3. [assumption about scope boundary]
→ Correct me now or I'll proceed with these.
```

If the brainstorm report covers these clearly, abbreviate to only the gaps.

## Step 2 — Clarify Gaps

Use AskUserQuestion (max 1 round, max 3 questions) for anything the report or scout didn't resolve.
Focus on: testable success criteria, build/test commands if not obvious, explicit boundaries.
Do not ask about modules, files, or architecture — scout and the report cover those.

## Step 3 — Write Spec

Six areas. All six are required. Omitting one means a decision gets made silently during planning.

**1. Objective**
What are we building and why? Who is the user? What does success look like?
Reframe vague requirements as testable criteria:
```
Vague:    "make it faster"
Specific: Dashboard LCP < 2.5s on 4G; initial data load < 500ms
```

**2. Commands**
Build, test, lint, dev — full commands with flags. Read from repo if available.
```
Build: npm run build
Test:  npm test -- --coverage
Lint:  npm run lint --fix
Dev:   npm run dev
```

**3. Project Structure**
Only the directories relevant to this feature — not the full repo map.

**4. Code Style**
One real code snippet showing the pattern to follow beats three paragraphs describing it.
Include naming conventions only if they'd surprise a new contributor.

**5. Testing Strategy**
Framework, where tests live, coverage expectations, which test levels for which concerns.

**6. Boundaries**
```
Always do:  [conventions that must be followed without asking]
Ask first:  [decisions that need human input — schema changes, new deps, CI config]
Never do:   [hard limits — no secrets in code, no skipping tests, etc.]
```

Example entries (replace with project-specific):
```
Always do:  Parameterize all DB queries; validate input at route handler; use httpOnly cookies
Ask first:  Storing new PII categories; adding external service integrations; changing auth logic
Never do:   Log passwords or tokens; store auth tokens in localStorage; expose stack traces to users
```

Also include **Open Questions** — anything unresolved that blocks planning.

## Step 4 — Validate & Save

Present the spec. Wait for explicit approval — not "looks good" or silence.

If the user corrects something: update and re-present the affected section only.

Save to: `plans/specs/spec-YYMMDD-{slug}.md`
Commit alongside the plan and code — it's the source of truth, not a scratchpad.

## Step 5 — Handoff

Output the exact plan command:

```
/ck:plan [--tdd] plans/specs/spec-YYMMDD-{slug}.md
```

Add `--tdd` when: spec involves critical logic, a refactor, or the user requested tests-first.
For large scope or multiple approaches, suggest `--two` or `--hard`.
