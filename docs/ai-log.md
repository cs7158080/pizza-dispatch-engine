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
