# Working Agreement

This file defines **how** we work on this project — not what we build.
It applies to every session. Read it before doing anything else.

---

## 1. Roles

- The developer is the **author and reviewer**. The AI agent is a **drafting tool**.
- The agent does not decide scope. It proposes; the developer approves.
- **Nothing is written without explicit approval.** No file is created, edited, deleted, or
  committed until the developer has approved that specific change. This applies equally to
  code, tests, documentation, configuration, and repository files. There is no category of
  change small or obvious enough to be exempt.
- **Discussion is not approval.** Proposing a change, agreeing it is a good idea, or being
  asked a question about it does not authorise writing it. Approval is the developer saying
  to proceed. Absent that, present the change and wait.
- When something is worth doing but unapproved, say so and stop. Do not do it and report it
  afterwards.

---

## 2. Planning Protocol

**No implementation begins before planning is complete and approved.**
Planning happens in four ordered phases. Do not skip or merge phases.

**"Complete" means complete for one unit of work.** Phases 2 to 4 run per
unit: a unit is decided, planned, approved, implemented and merged before
the next unit is planned. An item is resolved when the unit that depends
on it is planned — early for anything expensive to reverse, later for
anything whose cost of change is local. Phase 1 is the exception and runs
once for the whole system, because a unit cannot be identified before the
work is mapped.

### Phase 1 — Planning Inventory
Before deciding anything, produce a list of **everything that must be decided**.
This is a list of open questions, not answers. Cover at minimum:

- Requirements restated in your own words, split into explicit items
- Ambiguities and gaps in the requirements
- Component boundaries and responsibilities
- Data model and state transitions
- Failure modes and edge cases
- Configuration surface
- Verification strategy
- Deliverables and how each is judged

Present the inventory for approval before proceeding.

### Phase 2 — Decisions
Resolve every item in the inventory, one at a time. For each decision record:

- The decision, stated concretely
- Why it was chosen
- What was rejected and why

Ambiguity in the requirements is **never resolved silently** — it is recorded as an
explicit written assumption.
Nothing moves to Phase 3 for a unit while an item that unit depends on is unresolved.

### Phase 3 — Implementation Plan
Convert decisions into an ordered, numbered, step-by-step plan.

Each step must:
- Be small enough to complete and verify in one sitting
- Map to exactly one commit (see §4)
- State its **Definition of Done** and how it is verified
- Depend only on steps already completed

**The plan must be tight enough that implementation contains no decisions.**
If executing a step requires a judgement call that the plan did not make, the plan is
incomplete — stop, return to Phase 2, and fix it. Do not improvise mid-implementation.

### Phase 4 — Approval Gate
The developer reviews and edits the plan. Code is written only after explicit approval.
Re-planning mid-flight is allowed and expected — but it is done by returning to
Phase 2/3, not by writing code and adjusting afterwards.

---

## 3. Architecture Principles

- **Strict component separation.** Each component has one responsibility and a single,
  explicit way to be called. No component reaches into another's internals.
- **Layered structure with a one-directional dependency rule.** Dependencies point
  inward, toward the business core. The core does not know the outside exists.
- **The business core is framework-free.** It does not import transport, storage,
  messaging, or any third-party infrastructure library.
- **Business rules live in exactly one place.** If a rule is enforced in two components,
  the rule is in the wrong place.
- **Explicit typed boundaries.** Data crossing a layer boundary is a defined type, never
  an untyped dictionary. External input is validated at the edge, before it reaches the core.
- **Every entry point uses the same core.** Additional interfaces are thin adapters; they
  never re-implement logic.
- **All configuration comes from the environment**, with a committed example file.
  No secrets, hosts, ports, or credentials hardcoded.
- **Simplicity is a requirement, not a compromise.** Do not add layers, abstractions,
  patterns, or dependencies that the current scope does not require. Over-engineering is
  treated as a defect.

---

## 4. Git

- **No commit, merge, push, branch deletion, or history change without explicit approval**
  for that specific action. Staging files is not permission to commit them.
- Never commit secrets or local environment files. Commit an example instead.
- **One commit per logical unit of work.** Not per hour, not per file.
- **Conventional Commits**, in English:
  `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`, `build:`
- Commit messages state *what changed and why*, never `wip` / `fixes` / `updates`.
- **One branch per plan step or feature**, merged via pull request — even when working alone.
- The history must read as a coherent narrative of how the system was built.
  A single bulk commit containing the whole project is a failure of process.
- Never rewrite pushed history.
- Do not commit generated artifacts, caches, or editor files.
- The main branch is always in a working state.

---

## 5. Verification

- Automated tests are a **graded deliverable**, not an optional extra. The required set is
  small and fixed by the assignment; that number is the ceiling, not a starting point.
- **Two categories, kept separate:**
  - **Integration / end-to-end** — the required deliverable. Exercises the running system
    through its real interfaces, and runs automatically when the environment launches.
  - **Unit** — an addition, permitted only when free: pure logic, no infrastructure,
    written in minutes. Their purpose is to prove the business core is testable in
    isolation. If verifying a business rule requires external services, the rule is in the
    wrong layer.
- The two categories live in separate directories and can be run separately. The required
  scenarios are named in the README so a reviewer finds them without reading the suite.
- Scenarios are chosen by **risk**, not by coverage: each one targets a failure mode that
  would otherwise break silently. Rank candidates by risk and take the top N.
- **No numeric coverage target.** Coverage measures which lines ran, not whether behaviour
  was asserted. A high percentage proves nothing.
- A test earns its place only if it would fail when the behaviour it names breaks.
- Do not build a test pyramid. Tests beyond the risk-ranked set are scope creep.
- Test **behaviour and contracts**, not internal implementation details.
- Failure paths and edge cases are tested, not only the happy path.
- **No timing-based waits in tests.** Wait on a condition with a timeout, never on a fixed sleep.
- Tests are deterministic and independent — order must not matter, and repeated runs must
  produce the same result.
- Each test is documented with what scenario it covers and why it matters.

---

## 6. Working With the AI Agent

- Use plan-first mode for anything non-trivial. Read the proposed plan, correct it,
  then approve. Correcting the plan is cheaper than correcting the code.
- **Ask before adding any dependency.** New libraries require justification.
- The agent does not silently expand scope, refactor unrelated code, or "improve" things
  that were not requested.
- Reject: dead code, unused imports, commented-out blocks, comments restating the obvious,
  broad exception swallowing, inconsistent naming or style between files, speculative
  abstractions, and unrequested extra features.
- Style must be consistent across the whole repository regardless of which session
  produced the file.
- **Log rejected proposals as they happen.** Append one row to `docs/ai-log.md` whenever a
  proposal is rejected or materially changed, whenever review catches an error, or whenever
  something is accepted without full verification. The agent writes the row as part of the
  same change; the developer approves it in the diff. Do not log routine accepted output —
  record only what becomes unrecoverable once the session ends.
- **Flag session boundaries.** One unit of work per session. When the current unit is
  finished, or a request belongs to a different unit, say so and recommend starting a clean
  session instead of continuing in a drifting context.

---

## 7. Documentation

- The README is written for someone who has never seen the project: how to run it,
  how to use it, how to test it.
- Assumptions are listed explicitly and kept up to date.
- Anything deliberately left out of scope is stated as such.
- Documentation is updated in the same commit as the change it describes.

---

## 8. Definition of Done — applies to every step

A step is done only when all of the following hold:

1. It satisfies the Definition of Done written for it in the plan.
2. Its behaviour is verified by a test that would fail if the behaviour broke.
3. Formatting, linting, and type checks pass.
4. Documentation and assumptions are updated.
5. It is committed on its own branch with a conventional commit message.
6. The main branch still runs.
