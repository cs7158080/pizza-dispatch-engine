# AI Log

A running record of where AI-generated proposals were **rejected, corrected, or accepted
without full verification** during development.

Everything an agent successfully wrote is already visible in the code and in the git
history. What disappears when a session closes is the reasoning that shaped it — what was
proposed, what was thrown away, and why. That is what this file preserves.

## When to add a row

Add a row when, and only when, one of these happens:

1. An agent proposal was **rejected** or **materially changed**.
2. Review **caught an error** in generated output.
3. Something was **accepted without full verification** — so it is known what to revisit.

## When not to add a row

Routine accepted output. "The agent wrote the schemas", "the agent helped with the
Dockerfile" — these carry no information and dilute the rows that do.

## Format

One row per event. Keep each cell to a single line.

| Date | Area | Agent proposed | Decision | Why |
|---|---|---|---|---|

`Decision` is one of: `Rejected`, `Changed`, `Accepted — unverified`.

---

## Log

| Date | Area | Agent proposed | Decision | Why |
|---|---|---|---|---|
| 2026-08-07 | plan/future-work | FW11 — a future-work entry for drivers carrying more than one order | Rejected | Item 5.8 already records the decision and everything it would reopen; a second entry duplicates it |
| 2026-08-07 | plan/scope-ceiling | Item 1.1 to auto-write a Part 5 entry whenever a candidate fails the ceiling test | Changed | Writing the entry is a file change and needs approval per §1; the rule fixes the verdict, not the authority to record it |
| 2026-08-07 | plan/structure | Splitting the planning record into three files by topic | Changed | Cross-references cluster by risk, not by topic, so a topic split would scatter them; split by role instead — questions, answers, plan |
| 2026-08-07 | plan/structure | Reconstructing the question form of the 31 items decided before the inventory was separated | Rejected | Writing a question after knowing its answer is fiction; the gap is stated in the file header instead |
| 2026-08-09 | plan/broker-contract | No retry at all on a failed publish, on the grounds that a down broker stays down longer than any request timeout | Changed | It conflated two failures; a stale long-lived connection is the common one and a single reconnect resolves it, so 7.5 retries once after reconnecting |
| 2026-08-09 | plan/cli | A single `Advance to <next>` action, with the client computing the next status from the transition sequence | Changed | The developer replaced it with a full status menu: the client must hold no part of a rule the core owns, and a reviewer must be able to trigger a `409` from the CLI itself |
| 2026-08-09 | plan/db-access | Imperative mapping costs ~80 lines more than declarative | Changed | The count was wrong by roughly six times — `map_imperatively` needs an explicit `Table`, so only the two mapper functions are saved; the developer's pushback surfaced it, and the corrected near-zero figure is what actually decided 2.5 |
| 2026-08-09 | plan/db-access | Four imprecise claims in the 2.5 draft: `session.get()` never issues a SELECT; Core yields `Row[Any]`; `Session` checks out a connection on creation; `pool_pre_ping` answers Compose startup | Changed | An external reviewer the developer consulted caught all four; each was narrowed to the condition that actually holds. A fifth suggestion — to rest the imperative-mapping rejection on framework coupling — was declined: that mapping adds no import to `domain/`, so the argument fails on inspection |
| 2026-08-09 | plan/architecture | That the event type has no home in the plan, so the publisher port would name a type defined nowhere | Changed | The developer pointed at the `outbox`: 3.5 already places an `OutboxStore` port in `application/ports.py`, so a core-side consumer of the type was already written. The finding narrowed to a placement contradiction — U6 holds "event payload type" while U5 and the U3 ports both need it — and moved from 3.4's blockers to 3.4's agenda |
| 2026-08-10 | plan/process | Closing all 109 inventory items before the first line of code, per the global Phase 3 gate in `02-decisions.md` | Changed | The gate contradicted Part 4 of the roadmap, which already gates each unit on its own topics; the global wording was the newer error and was narrowed. Planning now runs per unit — cost of change decides how early an item is settled, not the calendar. At the observed rate the remaining 54 items would have consumed the budget and left the compose environment and the test suite, the two most-graded rows, for the last hours |
| 2026-08-10 | plan/docker-images | For 3.7, a single image holding everything, resting on 1.1's ceiling test to delete a second build stage | Changed | The developer asked for alignment with what is actually done in production. 1.1's test governs shipped features, not build hygiene — applied that way it would also delete `.dockerignore` and the non-root user. The argument was withdrawn rather than defended, and 3.7 carries a runtime/test split |
| 2026-08-10 | plan/api-contract | Keeping 6.6's 50-order cap on `GET /orders` while designing 3.4's `list_recent(limit)` port method | Changed | The developer asked what happens to the 60th order. The cap had no recorded justification — 6.6 marked it "chosen, not required" — and a cap without paging silently hides the data the endpoint exists to surface. Cap removed; the port method lost its `limit` parameter with it |
