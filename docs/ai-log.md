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
| 2026-08-10 | plan/process | Rewriting the Phase 3 gate as a four-line rule inside `02-decisions.md`'s status section, on the strength of a one-word reply | Changed | The developer caught it after the commit. §1 requires explicit approval for the specific change and a one-word reply is not it — the bar is higher for a rule that governs the whole project than for a decision record. The placement was wrong too: a planning file cannot amend the working agreement, and the status section is declared the place item status is recorded. Reverted; the rule now lives in `CLAUDE.md` §2 and the status section carries a one-line pointer |
| 2026-08-10 | plan/dependencies | For 2.9, `pip-tools` as the lock generator, with `uv` rejected on local-tooling friction | Changed | The developer develops locally with `uv`. The swap costs nothing — `uv pip compile` emits a plain pip requirements file, so the image still sees only `pip` — and it removed a defect the proposal carried: both generators resolve for the host platform, so a lock built on Windows for a Linux image can carry Windows-only packages. `uv pip compile --universal` has no `pip-tools` equivalent |
| 2026-08-10 | plan/git-workflow | For 14.2, squash merges, argued from the claim that a merge node adds no information | Changed | The claim was false -- a merge node carries the unit boundary -- and the developer's pushback surfaced a contradiction under it: §2, §8 and §4 put the commit at step grain while Part 4 of the roadmap put it at unit grain, which 14.4 then settled. The record moved to merge commits and back to squash once the count was done honestly: a merge-commit main carries about eighty entries against fourteen, and GitHub's commit list is the first surface a reviewer opens. Squash stands on signal density; the original argument is withdrawn |
| 2026-08-10 | plan/git-workflow | For 14.3, a single planning commit at the head of each unit's own branch | Changed | The developer asked to plan several units in parallel across git worktrees. Under the original form a unit's Phase 2 decisions would sit on a long-lived branch and never reach main, so parallel sessions could not see each other's contracts. Phase 2 now merges promptly on its own gate branch; Phase 3 stays at the head of the unit branch. Part 4's rule 4 was narrowed with it -- it guards implementation plans from going stale, which system-level decisions cannot |
| 2026-08-11 | plan/dependencies | For 2.9, "4.7 already declined the 3.14 pull" as the whole justification for the upper version bound | Changed | 4.7 declined a third-party `uuid7()` dependency and left 3.14 explicitly open, deferring the version to 2.9 — so each record cited the other and neither decided the bound. The developer's question, why 3.14 was *not good* rather than not needed, surfaced it. 2.9 now decides it on PEP 649/749: the whole stack reads annotations at runtime, and 3.14 changed that mechanism. The earlier framing, that a declined 3.14 proved currency, is withdrawn |
| 2026-08-11 | plan/future-work | FW4 as an unbuilt `GET /orders` carrying status filters and paging | Changed | 6.6 ships the endpoint and 1.1's worked-examples table marks it *ships*, so Part 5 understated the delivered scope — in the file a reviewer reads for the scope boundary, and the one 13.4 assembles the README trade-offs from. The developer caught it while reviewing U1's plan. Narrowed to filters and paging; the rewrite erases the stale sentence, so the drift would otherwise leave no trace |
| 2026-08-11 | plan/tooling | For 2.8, ruff with `extend-select = ["I"]` and nothing else, leaving its file scope unstated | Changed | Ruff 0.16 formats `python` blocks inside Markdown, so `ruff format --check .` failed on `02-decisions.md`'s pseudo-code at step 1 — a Definition-of-Done command failing on a planning document, not on source. The plan had no ruling and step 2 forbids formatter settings, so implementation stopped rather than improvising. 2.8 now fixes the scope with `extend-exclude = ["*.md"]`; reformatting the snippets was rejected, since it edits decided records to satisfy a formatter meant for source |
