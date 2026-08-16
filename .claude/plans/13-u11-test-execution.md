# U11 — Automatic test execution · Implementation Plan

**Phase 3 of the planning protocol in `CLAUDE.md` §2, for the eleventh unit in Part 4 of
`03-roadmap.md`.** Decisions are in `02-decisions.md`; nothing here decides anything that belongs
there. Where executing a step needed a call Phase 2 had not made, it is recorded below under
*Readings* rather than left to implementation.

**Gate.** U11's *Decided by* column reads 11.3–11.6, 12.9 and 12.10, and every one is `[decided]` —
11.3 to 11.6 since topic 11 closed in #18, 12.9 and 12.10 in #19. *Depends on* reads U10, merged in
#25. **There was no gate branch to write**, which is why this unit begins at Phase 3.

**One decided item did not survive contact with the tool, and commit A is the repair.** 11.4 named
`docker compose up --abort-on-container-exit --exit-code-from tests` as the CI-style gate; measured
on Compose v2.31.0 it aborts at `schema`'s zero exit, before `tests` has run. §3 states what A
changed. **This is a return to Phase 2, not a silence filled here** (`CLAUDE.md` §2), and the
document below is written against the amended record.

Four items are open and none is touched: 13.1 to 13.4 own the assembled README, the diagram, the
assumptions register and the trade-off log — U13's.

---

## 1. What this unit delivers

Part 4 gives U11 the test service wired into compose startup, the failure behaviour, and the result
output. It is the unit that makes R15 true: after U10 the suite existed and a person had to type it,
and the assignment asks for a system that tests itself when it starts.

**Two files changed, one of them twice over:**

| File | What it gains | Fixed by |
|---|---|---|
| `tests/integration/conftest.py` | the `pytest_terminal_summary` hook that prints `PASS` or `FAIL` | 11.3, 12.9 |
| `docker-compose.yml` | the seventh service, its command, its two edges | 11.1, 11.2, 11.9, 11.11, 12.9 |
| `README.md` | that the suite runs at `docker compose up`, and the CI gate beside it | 11.3, 11.4, 11.5 |

**Nothing under `src/` is touched, and nothing under `tests/` but the hook.** The suite's code does
not change at all: U10 built it to read its base URL from the environment, so moving the runner
inside the network changes one value and no line (U10's R-a).

## 2. What this unit deliberately does not deliver

Each line names the item that owns it, so nothing here is silence.

| Not built | Owner | Arrives in |
|---|---|---|
| A fifth scenario, or any change to the four | 12.1, 12.2 — four is the ceiling `CLAUDE.md` §5 fixes | not built (FW13) |
| A report file — `junit-xml` or any other | 12.9 — a format nothing here reads | not built |
| An eighth `lint` service, or `ruff`/`mypy` chained into the `tests` command | 12.10, 11.1 | not built |
| The two `docker compose run --rm tests …` verification commands **as README lines** | 12.10 — *"Realised in: nothing; the README line is U13's"* | U13 |
| An isolated test stack, a test-only retry delay, an attempt cap | 11.6, 12.8 — the suite runs the shipped configuration | not built (FW13) |
| A healthcheck on `tests`, or a `restart` key | 11.2, 11.11 — a one-shot's readiness signal is its exit code | not built |
| An `attach: false` on `tests` | 11.1 — the output is the one 11.3 puts the reviewer in front of | not built |
| A direct `tests` → `schema` edge | 11.2 — the guarantee holds transitively through `api` | not built |
| Any change to `.env.example` | 10.3 — `PIZZA_API_BASE_URL` is already there, read by the CLI and the suite; the count stays eleven | not built |
| The assembled README, the diagram, the assumptions register, the trade-off log | 13.1–13.4 | U13 |
| Any new dependency | 2.10 — the hook is pytest's own API | not built |

**The fourth row corrects a forward reference.** U10's plan §2 sends 12.10's two commands to U11.
12.10 itself ends *"Realised in: nothing; the README line is U13's"*, and the decided record wins
over a Phase 3 document's forecast of a later unit. U11 builds nothing for 12.10 and writes no line
for it.

## 3. Branch, commits, and the merge

- **Branch:** `test/u11-test-execution`, cut from `main` at `391b6b8` (14.2), the merge of U10.
- **Commits:** one correction commit, one planning commit, then one commit per step (14.3, 14.4).
  Four in total.
- **Merge:** one pull request, squash-merged, `gh pr merge --squash` **without `--subject`**, so the
  number is appended to the title (14.2, 14.3). The branch is not deleted (14.2).

| # | Type | Title |
|---|---|---|
| A | correction | `docs: replace 11.4's CI gate, which Compose aborts before the suite runs` |
| P | planning | `docs: plan the automatic test execution` |
| 1 | step | `test: print the run's verdict where the launch stream cannot miss it` |
| 2 | step | `build: run the suite at launch, as the seventh service` |

**A is not a plan step, and it lands before P.** 11.4 documented a command that does not do what the
record said it did — `--exit-code-from` stops every container as soon as **any** container exits,
and 11.1's `schema` is a one-shot that exits zero while `tests` is still waiting on 11.2's `api`
edge. Measured on Compose v2.31.0, the gate either kills the suite mid-run or, when `tests` has not
started, returns **zero over a suite that never ran**. The replacement is `docker compose up -d`
then `docker compose wait tests`. Four records carrying the command's name — 11.1, 11.10, 11.11,
12.9 — are amended with it, and every argument they make survives the substitution unchanged. A
rides on this branch rather than on a gate branch of its own, by the same ruling that placed U12's
commit A. It carries the `docs/ai-log.md` row for the same change (§6).

**What A does not touch, recorded as a choice rather than an oversight:** the two merged Phase 3
documents that also name the old command, U9's §2 and U10's §2. They are dated records of what each
unit planned, not live contracts, and both name 11.4 beside the command, so a reader following the
reference lands on the corrected item.

## 4. The Definition of Done that applies to every step

14.7's U2 row and its U9 row govern every step here, and **the U11 row is what step 2 makes
reachable**. The five commands are run from this worktree's virtual environment at the repository
root, and each must exit zero **at every step commit**:

```
ruff format --check .
ruff check .
mypy src tests
python -c "import pizza"
pytest tests/unit
```

**`pytest tests/unit` collects nineteen**, checked by running it. U10's plan says eighteen, which
was true when it was written; U12 added `tests/unit/test_cli_statuses.py` in #24.

`mypy src tests` is the one that does real work in step 1: the hook is inside its scope, and its
three parameter types come from pytest's public surface (R-a).

**14.7's U9 row is in force from step 1**, as it was for U10: from a clean state `docker compose up`
brings every service the file defines to the state 11.2's graph requires, and the stack stays up.
Checked by running `up` and polling `docker compose ps -a` — **no fixed sleep** (`CLAUDE.md` §5).

**The suite is run from the host at step 1 and from inside the network at step 2**, which is the
whole difference between the two steps:

```
PIZZA_API_BASE_URL=http://localhost:8000 pytest tests/integration      # step 1
docker compose up                                                      # step 2
```

**One thing the image forces, and it is the trap in this unit.** 11.9's `test` stage copies `tests/`
at build time, so a change to the suite or to `conftest.py` does not reach the `tests` container
until the image is rebuilt. Every `up` in step 2's Definition of Done is therefore
`docker compose up --build`, and a green run against a stale image would prove nothing about the
code in the commit. **Checked, not assumed:** step 2 verifies the container is running this branch's
hook by making the run red and reading the banner.

A step is done when §8's six conditions hold.

## 5. Readings — where this plan filled a silence

Recorded here rather than resolved silently (`CLAUDE.md` §2). The boundary is U1 §5's, restated in
every unit since: a Phase 3 document may fill a silence Phase 2 left; it may not settle an ambiguity
inside a decided record. **Nothing below comes near that line — the one item that did is commit A,
which went back to Phase 2 instead.**

- **R-a — the hook declares two parameters, not three, and its types are pytest's public ones.**
  pytest 9.1.1's hookspec is
  `pytest_terminal_summary(terminalreporter: TerminalReporter, exitstatus: ExitCode, config: Config)`.
  Pluggy matches hook arguments by name, so a hook may declare a subset; `config` is declared
  nowhere because nothing reads it, and an unused parameter is what `CLAUDE.md` §6 calls dead code.
  The two that stay are annotated `pytest.TerminalReporter` and `pytest.ExitCode` — **verified to be
  exported from the pinned pytest rather than assumed**, because `mypy strict` covers `tests/` and a
  private `_pytest.terminal` import would be a boundary this repository does not cross elsewhere.

- **R-b — the banner is keyed on `exitstatus == pytest.ExitCode.OK`, not on a count of failures.**
  12.9 says *"keyed on pytest's exit status"* and names the case that makes the distinction matter:
  a run that collected no tests exits `5`, and must print `FAIL` rather than a green banner over an
  empty run. `ExitCode.OK` is the only zero in the enum, so equality against it is the whole rule
  and every other exit — failures, interruption, internal error, usage error — is `FAIL`.

- **R-c — no colour markup on the separator.** 12.9 writes `terminalreporter.write_sep("=", "PASS")`
  and `write_sep` accepts markup keywords, so leaving them out is a choice. pytest emits colour only
  to a terminal, and under `docker compose up` the container's stdout is a pipe — so `green=True`
  would be inert in the one place 11.3 wants the banner seen, and visible only in the host run of
  step 1. A full-width separator is what 12.9 already argues meets 11.3, and it works in both.

- **R-d — the `tests` service carries exactly one environment variable,
  `PIZZA_API_BASE_URL: ${PIZZA_API_BASE_URL:-http://api:8000}`.** This is U10's R-b from the other
  side: `ClientSettings` declares `api_base_url` with no default and sets `extra="forbid"`, and the
  loader collects *every* `PIZZA_`-prefixed variable in the environment — so the five service
  variables the `api` and `worker` blocks carry would fail validation here before the first request.
  The shape is the `cli` service's, for the same reason.
  *The default is written even though Compose supplies the value anyway,* matching `cli` and
  keeping the file readable as one style.

- **R-e — the two README lines land in the sections that already exist, and the suite's line is
  added to *Running the system* rather than to *Tests*.** U10 wrote `## Tests` and R-h deliberately
  left out any claim of automatic execution. What changes now is what `docker compose up` does,
  which is where a reader meets it first; `## Tests` gains the gate command and 11.5's sentence,
  beside the manual command that still works. **Neither line names a flag**, which is the point of
  commit A.

- **R-f — the failure the red run is made with is `--scale worker=0`, not an edit to the source.**
  Step 2 has to see the gate return non-zero, and 11.4's whole value is that it does. Removing the
  worker leaves the API healthy and every scenario that waits for an assignment red, which is the
  failure a broken dispatch would actually produce. U10's step 3 used `docker compose stop worker`
  for the same purpose; `--scale worker=0` is its equivalent for a stack being brought up rather
  than one already running.

## 6. Steps

### Step 1 — Print the run's verdict where the launch stream cannot miss it

**File changed:** `tests/integration/conftest.py`.

12.9's hook, and nothing else. It writes a full-width `PASS` or `FAIL` separator keyed on pytest's
own exit status (R-b), so the verdict sits beside that status rather than between it and Compose.

**This step is first because the service that runs the suite must not exist before the thing that
reports its result.** Reversed, the intermediate commit would be a `docker compose up` that runs the
suite and says nothing about it — 14.7's U11 row half-met, which is the state that row was rewritten
on 2026-08-14 to stop producing.

**Definition of Done**

1. The hook is in `tests/integration/conftest.py`, declares the two parameters R-a names, and calls
   `write_sep` exactly once per run.
2. The five commands of §4 exit zero, and `pytest tests/unit` collects nineteen.
3. 14.7's U9 row holds: from a clean state `docker compose up` reaches the state step 3 of U9's plan
   named, and stays up.
4. **Green:** `PIZZA_API_BASE_URL=http://localhost:8000 pytest tests/integration` passes and prints
   `PASS`, and the exit code is zero.
5. **Red, twice, because the two reds come from different places.** `-k` matching nothing exits `5`
   and must print `FAIL` — 12.9 names this case by itself. And with the worker stopped, a real
   failure must print `FAIL` and exit non-zero. A hook keyed on a failure count instead of the exit
   status passes the second and fails the first.
6. **The banner's position is observed and written into the pull request, not corrected.** 12.9
   measured `FAILURES`, the banner, `--durations`, `-ra`, then the counts line, and records that no
   hook placement makes the banner last. This step confirms the order on the pinned pytest and
   stops there.
7. Read from the diff: no shell wrapper anywhere, no `sys.exit`, no writing to a file, and the hook
   reads `exitstatus` directly rather than any state it accumulated during the run.

---

### Step 2 — Run the suite at launch, as the seventh service

**Files changed:** `docker-compose.yml`, `README.md`.

11.1's seventh service, with 12.9's command, 11.2's two edges, and R-d's single variable. This is
the commit that makes `docker compose up` satisfy R15, and 14.7's U11 row with it.

```yaml
tests:
  build: {context: ., target: test}
  image: pizza-test
  command: ["pytest", "tests/integration", "-v", "-ra", "--durations=0", "--tb=short"]
  environment:
    PIZZA_API_BASE_URL: ${PIZZA_API_BASE_URL:-http://api:8000}
  depends_on:
    rabbitmq: {condition: service_healthy}
    api: {condition: service_healthy}
```

Written in the file's existing long form rather than the flow mapping above, which is a sketch.

`README.md` gains two things and no more: a sentence in *Running the system* saying the suite runs
as part of the launch and the stack stays up when it passes (11.3, 11.5), and in *Tests* the CI gate
as 11.4 now writes it, beside the manual command that still works (R-e).

**Definition of Done**

1. The service is as above: `target: test`, `image: pizza-test`, 12.9's command **verbatim and in
   exec form** (11.9), exactly two edges, one environment variable, and **no** `restart`, `attach`,
   `healthcheck` or `ports` key (11.1, 11.2, 11.11).
2. The five commands of §4 exit zero, and `pytest tests/unit` collects nineteen.
3. **14.7's U11 row, which this step exists for:** from a clean state, `docker compose up --build`
   brings the stack up, the `tests` service runs the suite, prints `PASS` in that stream, and exits
   zero. Verified by polling `docker compose ps -a` for the container's exit code — **no fixed
   sleep** (`CLAUDE.md` §5).
4. **11.5 holds after it:** `postgres`, `rabbitmq`, `api` and `worker` are still running once
   `tests` has exited, and the API still answers on the published port. This is what the demo path
   (1.2) starts from.
5. **The gate is measured in both directions**, which is the claim commit A rests on:
   `docker compose up -d` then `docker compose wait tests` returns **0** on a healthy stack and
   leaves it running; brought up with `--scale worker=0` (R-f) it returns **non-zero**. A gate only
   ever seen green is not known to be a gate.
6. **`docker compose logs tests` returns the whole run** after it has exited — named scenarios,
   durations, the banner — which is 12.9's stated reason for writing no report file. Read once by
   hand.
7. **The launch's wall-clock time is measured and written into the pull request:** from
   `docker compose up` to the `PASS` banner. U10 measured the suite at about 21 s against a
   prediction of 30; this number is that plus the stack's own startup, and it is what every launch
   now costs (11.3). Not asserted anywhere.
8. The README says what R-e fixes, names no flag commit A removed, and claims nothing about lint or
   type checks running in the container (12.10).
9. Read from the diff: seven services and no eighth, no report-file flag added to 12.9's command, no
   change to `.env.example`, and nothing under `src/` or `tests/`.

## 7. Ordering, and where it is free

**1 → 2, and it is the only ordering constraint in the unit.** The hook has to exist before the
service that exists to show it; the reverse order commits a launch that runs the suite silently.
Neither step depends on anything the other leaves behind beyond that, and there is no third step to
place.

## 8. What U11 hands to the units after it

- **U13 (13.1, 13.4):** the assembled README inherits three commands rather than two — the launch,
  the CI gate as 11.4 now writes it, and the manual run — plus 12.10's two verification commands,
  which that item leaves to U13 to document and to nobody to build. The measured launch time from
  step 2 is what a reviewer's first `up` will cost, and 13.1 may want it stated.
- **U13 (13.2, 13.3):** the assumptions register inherits 11.6's conditional determinism unchanged,
  now reached by a command a reviewer runs without meaning to — the suite executes at every launch,
  so a stack driven by hand and re-launched without `down` is the case A8 covers.
- **Everything:** 14.7's table is complete. After this merge, "main still runs" means the whole
  system comes up and proves itself, which is the strongest verification this design supports.

## 9. After the merge

`main` satisfies every row of 14.7. `docker compose up` builds what is missing, starts six services
in the order 11.2's graph fixes, runs four scenarios over HTTP against the system it just started,
prints the verdict in the stream the reviewer is already watching, and leaves the stack running for
them to drive.

What is left is the document that explains it — U13, and nothing else.
