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

### Example rows (delete once real entries exist)

| Date | Area | Agent proposed | Decision | Why |
|---|---|---|---|---|
| 2026-08-08 | worker/retry | Requeue the message immediately on failure | Rejected | Hot loop — no delay between attempts, floods the log and pins the CPU |
| 2026-08-08 | worker/dispatch | Plain lookup for the first available driver | Changed | Two workers can select the same row; needs atomic claim at the database level |
| 2026-08-09 | compose/tests | Fixed wait before starting the test service | Rejected | Flaky by construction; replaced with real service health conditions |

---

## Log

| Date | Area | Agent proposed | Decision | Why |
|---|---|---|---|---|
