# U10 — Integration test suite · Implementation Plan

**Phase 3 of the planning protocol in `CLAUDE.md` §2, for the tenth unit in Part 4 of
`03-roadmap.md`.** Decisions are in `02-decisions.md`; nothing here decides anything that belongs
there. Where executing a step needed a call Phase 2 had not made, it is recorded below under
*Readings* rather than left to implementation.

**Gate.** U10's *Decided by* column reads 12.1–12.5 and 12.8. Every one is `[decided]`: 12.1–12.3
closed with the planning branch, and 12.4, 12.5 and 12.8 closed at this unit's gate, pull request
#23 — which also closed topic 12 whole. *Depends on* reads U9 (#22), merged. **There was nothing
left to decide at this gate by the time Phase 3 began**, which is why this unit begins here.

Two groups of open items are touched and neither is decided here: 11.3–11.6, 12.9 and 12.10 own
how the suite is launched and where its result is printed — U11's; 13.1 to 13.4 own the assembled
README — U13's.

---

## 1. What this unit delivers

Part 4 gives U10 the risk-ranked scenarios, condition-based waiting, and data isolation. It is the
unit that makes the system prove itself without a person watching: after U9 the environment came
up, and every assertion about it was still a human reading a log.

**Three files, all under `tests/integration/`, and one README section:**

| File | What it holds | Fixed by |
|---|---|---|
| `waiting.py` | `wait_until` and `stays`, and the three constants | 12.4 |
| `conftest.py` | the HTTP client, unique naming, and 12.5's absorbing fixture | 12.5, 12.7 |
| `test_scenarios.py` | the four scenarios as five test functions | 12.1, 12.2, 12.7 |
| `README.md` | one section — the four scenario names, and how to run them | `CLAUDE.md` §5 |

`tests/integration/__init__.py` already exists on `main` — 12.7 records that both directories have
been packages since U1, which is why neither is created here.

**Nothing under `src/` is touched.** The suite drives the delivered system through the interface
12.3 fixed and changes none of it. If a scenario fails, the repair is a defect in a merged unit and
is its own commit, not an edit inside a step here.

## 2. What this unit deliberately does not deliver

Each line names the item that owns it, so nothing here is silence.

| Not built | Owner | Arrives in |
|---|---|---|
| The `tests` service in `docker-compose.yml`, its `command`, its two edges | 11.1, 11.2, 12.9 | U11 |
| The `pytest_terminal_summary` hook that prints PASS/FAIL — in this unit's `conftest.py` | 11.3, 12.9 | U11 |
| `--exit-code-from tests`, and the README line that the suite runs at `docker compose up` | 11.4, 11.5 | U11 |
| `docker compose run --rm tests ruff check .` and the `mypy` twin | 12.10 | U11 |
| The assembled README, the sequence diagram, the assumptions register, the trade-off log | 13.1–13.4 | U13 |
| Any unit test | 12.6 — the set is closed to accumulation, and nothing here is free logic | not built |
| A database client, a broker client, container control, an in-process client | 12.3, 2.6 | not built |
| A fifth scenario, in particular retry-budget exhaustion | 12.1 — four is the ceiling `CLAUDE.md` §5 fixes | not built (FW13) |
| An assertion on the dispatch log line, on timestamp values, on echoed input, on the `outbox` row | 12.2, 12.3, 8.6 | not built |
| A `[tool.pytest.ini_options]` section, or `tests/helpers/` | 12.7 | not built |
| Any new dependency — `httpx` and `pytest` are both in the `dev` extra already | 2.6, 2.10 | not built |
| A test-only retry delay or attempt cap | 12.8, 11.6 — the suite runs the shipped configuration | not built (FW13) |

## 3. Branch, commits, and the merge

- **Branch:** `test/u10-integration-tests`, cut from `main` at `99b9a00` (14.2), the merge of this
  unit's own gate.
- **Commits:** one planning commit, then one commit per step (14.3, 14.4). Five in total, plus any
  correction a step's own Definition of Done turns up in a merged unit — this plan expects that to
  be possible rather than planning for it, and §1 above says where such a commit belongs.
- **Merge:** one pull request, squash-merged, `gh pr merge --squash` **without `--subject`**, so the
  number is appended to the title (14.2, 14.3). The branch is not deleted (14.2).

| # | Type | Title |
|---|---|---|
| P | planning | `docs: plan the integration test suite` |
| 1 | step | `test: refuse an illegal transition, and refuse invalid input` |
| 2 | step | `test: an order's whole life, and the driver it releases at the end` |
| 3 | step | `test: dispatch resumes when a driver registers late` |
| 4 | step | `test: one driver, two orders, and the hand-off between them` |

## 4. The Definition of Done that applies to every step

14.7's U2 row and its U9 row both govern every step here. The five commands are run from the
activated virtual environment at the repository root, and each must exit zero **at every step
commit**:

```
ruff format --check .
ruff check .
mypy src tests
python -c "import pizza"
pytest tests/unit
```

`mypy src tests` is the one that does real work in this unit: `tests/` is inside its scope, so every
file written here is type-checked, and 2.6 chose `httpx` partly because it ships `py.typed`.

**`pytest tests/unit` collects eighteen at every step**, and this is checked by running it rather
than reasoned from the fact that nothing was added to that directory. 12.6 closed the unit set to
accumulation; a nineteenth would mean this unit went somewhere it was not sent.

**14.7's U9 row is in force from step 1**, because the suite has nothing to run against otherwise:
`docker compose up` brings every service the file defines to the state 11.2's graph requires, and
the stack stays up. As in U9 it is checked by running `up` in the foreground and polling
`docker compose ps -a` — **no fixed sleep** (`CLAUDE.md` §5).

**The suite itself is run from the host**, against that stack, by the command R-a fixes:

```
PIZZA_API_BASE_URL=http://localhost:8000 pytest tests/integration
```

Every step runs it three ways, and each way checks something a single run does not:

1. **Whole, from a clean start** — `docker compose down` first, so 11.7's guarantee is what is being
   observed rather than a leftover container. Every test written so far passes.
2. **Whole, a second time without `down`** — 12.5's invariant, stated as re-runnability against the
   suite's own residue. A driver left `AVAILABLE` by a broken absorption fails here and nowhere
   else.
3. **The step's own test alone**, by `-k`. 12.5's contract is that any subset meets the same
   precondition; a test that only passes with its predecessors is a test that depends on order.

From step 3 on, one further run: **the tests in reverse declaration order**, by naming their node
ids on the command line in the opposite order, which pytest runs in the order given. §5 says order
must not matter, and this is where that is measured rather than argued.

A step is done when §8's six conditions hold.

## 5. Readings — where this plan filled a silence

Recorded here rather than resolved silently (`CLAUDE.md` §2). The boundary is U1 §5's, restated in
every unit since: a Phase 3 document may fill a silence Phase 2 left; it may not settle an ambiguity
inside a decided record. **R-c is the one that comes closest to the line, and it is flagged rather
than buried.**

- **R-a — during this unit the suite runs from the host, at `http://localhost:8000`.** 12.9 gives
  the `tests` service and its command to U11, so until that merge there is no in-network runner and
  `http://api:8000` resolves from nowhere the developer can type. 11.8 published the API's port for
  a reviewer's browser; the same publication is what makes the suite runnable one unit early. **The
  suite's code does not change at U11** — it reads a base URL from the environment either way, and
  only the value differs.
  *Rejected — writing the `tests` service here so the suite runs in-network from step 1:* it takes
  U11's only content, and 11.1 re-confirmed the six-service split at U9's gate.

- **R-b — the base URL is loaded through `load_client_settings(os.environ)`, and the run therefore
  carries exactly one `PIZZA_` variable.** `ClientSettings` declares `api_base_url` with **no
  default** and sets `extra="forbid"`, and the loader collects *every* `PIZZA_`-prefixed variable
  out of the environment — so a shell that has sourced `.env.example` fails validation on the six
  service variables before the first request. This is R-b of U9's plan read from the other side, and
  it is why §4's command sets the variable inline rather than assuming a configured shell.
  *Rejected — a literal `http://localhost:8000` in the suite:* it would make the suite unable to run
  in the container U11 puts it in, and 10.1 gave the suite a settings class precisely so it can.

- **R-c — the two helpers take the client as their first argument:
  `wait_until(client, order_id, predicate)` and `stays(client, order_id, predicate)`.** 12.4 writes
  them without it. **Named as the closest call in this document:** the record fixes the names
  because it uses them, and the parenthetical beside each is a sketch of what the helper is *about*
  rather than a signature — but it is written as a signature, and a reader may take it as one.
  What forces the widening is that the alternative is worse in a way the codebase already ruled on:
  a module-level `httpx.Client` in `waiting.py` is I/O configured at import time, and `config.py`
  opens with the sentence that nothing there reads the environment at import. A client built once
  per session and handed in keeps that property and keeps the helpers free functions, which is 12.7's
  own reason for putting them outside `conftest.py`.
  **If the developer reads 12.4's parenthetical as binding, this returns to Phase 2 rather than
  being settled here.**

- **R-d — the client is a session-scoped `httpx.Client` fixture in `conftest.py`, with
  `base_url` set and no other configuration.** One connection pool for the whole run, and `httpx`'s
  own 5 s default timeout (2.6) left as it is: it bounds a single request, while 12.4's 20 s bounds
  the wait across many, and the two do not overlap.

- **R-e — the unique string is the order's `customer_name` and the driver's `name`, built by a
  `conftest.py` fixture from `request.node.name`, a short label, and eight random hex characters:**
  `test_one_driver_two_orders-order-3f9a2c71`. 12.5 requires the name to carry its test's name and
  to be for legibility only — identification inside a test is by the id the API returned, since 4.5
  imposes no uniqueness on names and a name could therefore never have carried correctness. What
  uniqueness buys is attribution when a run goes red: 11.6 shares the live database with a
  reviewer's own rows and with the suite's previous run, and `GET /orders` then says which test
  wrote what. **No prefix marks the suite** — `test_` at the front of every name already does, and a
  unit number in runtime data is what `CLAUDE.md` §6 keeps out of source. The absorbing order takes
  the same form with the label `absorb`, which is what 12.5 means by a name that says what it is.

- **R-f — the four scenarios live in `tests/integration/test_scenarios.py`.** 12.7 fixes *one file*
  and does not name it. `test_scenarios.py` is what 12.2 calls them and what the README will list;
  a name drawn from the system's parts — `test_dispatch.py` — would not cover scenario 4, which
  asserts API rules and never reaches the worker.

- **R-g — `stays` returns nothing and `wait_until` returns the order payload.** 12.4 says the
  positive helper returns the payload *"so the test asserts on it without a second read"*, and says
  nothing about the negative one. There is nothing for it to return: it fails at the first
  violation, so on success the only fact it has is the one the caller already asserted by calling
  it.

- **R-h — the README section lands in step 4, once, rather than growing a line per step.** §7 and
  §8.4 put documentation in the step that changes what it describes, and what this section describes
  is *the set of four*. A partial list written at step 1 and amended three times is churn in a file
  U13 assembles anyway. The section names the four scenarios and the command that runs them against
  a running stack — **and says nothing about `docker compose up` running them**, which is 11.3's
  sentence and false until U11.

- **R-i — a failing assertion is left to pytest, with no custom message.** 12.4 already requires a
  timeout failure to carry the last observed order payload, which is the one place the default
  output would be uninformative — a `TimeoutError` naming only the elapsed seconds. Everywhere else
  pytest's own comparison of two values is better than a sentence restating it.

## 6. Steps

### Step 1 — Refuse an illegal transition, and refuse invalid input

**Files created:** `tests/integration/conftest.py`, `tests/integration/test_scenarios.py`.

12.2's scenario 4, as its two functions — `test_illegal_transition_is_refused` and
`test_invalid_input_is_refused` — with the six assertions that record fixes, and no others. With
them arrives the whole harness that has nothing to do with waiting: R-d's client fixture and R-e's
naming fixture.

**This scenario is first because it is the only one that touches no asynchrony.** It reaches the
API, creates an order, and reads three status codes back; if it passes, the suite can talk to the
system, and every later step debugs a race rather than a connection.

**Definition of Done**

1. Both files exist. `conftest.py` holds the client fixture and the naming fixture and **no
   absorbing fixture** — that is 12.5's, and it arrives with the scenario that produces a driver.
2. The five commands of §4 exit zero, and `pytest tests/unit` collects eighteen.
3. 14.7's U9 row holds: from a clean state `docker compose up` reaches the state step 3 of U9's
   plan named, and stays up.
4. The suite runs the three ways §4 lists, and both tests pass every time.
5. `409` and `422` are asserted as **different** codes on the two paths 12.2 separates: a
   non-adjacent transition and a re-sent current status answer `409`; an unrecognised status string
   answers `422`. This is 5.2's whole reason for existing and the one place it is checked.
6. The order is re-read after the refused `PATCH` and its status is unchanged — a `409` that
   partially applied is the failure this assertion exists for.
7. **No driver is registered by either function**, so 12.5's invariant holds trivially and the two
   tests are order-independent by construction. Checked by reading the diff, not by running.
8. Read from the diff: no import of anything under `pizza.infrastructure` or `pizza.domain` — 12.3
   makes this a black-box suite, and importing the enums would couple an assertion to the core's
   spelling rather than to the contract's.

---

### Step 2 — An order's whole life, and the driver it releases at the end

**Files created:** `tests/integration/waiting.py`. **Files changed:** `conftest.py`,
`test_scenarios.py`.

12.2's scenario 1 — `test_complete_order_lifecycle` — with its five assertion rows. With it arrive
12.4's two helpers and three constants, and 12.5's absorbing fixture, each with its first and only
caller.

The fixture yields, and after the test's assertions it places one further order, advances it to
`BAKING`, and waits until it is `ASSIGNED` — which is what leaves the pool empty for every later
test. 12.5 already records what it costs when a test fails partway: the absorbing order is left
unassigned and the fixture ends at 12.4's timeout, noise on an already-red run.

**Definition of Done**

1. `waiting.py` holds exactly `wait_until`, `stays`, and the three constants — 20 s, 3 s, 0.25 s —
   each named and each carrying the one-line reason 12.4 gives it. Nothing else lives there.
2. The five commands of §4 exit zero, and `pytest tests/unit` collects eighteen.
3. The suite runs the three ways §4 lists. **Run 2 is the one that matters at this step**: it is the
   first run whose precondition depends on the previous run having absorbed its driver.
4. The five assertions are the five 12.2's table names, including the negative control after
   `PREPARING` — `driver` still `null`, which fails if the publish trigger ever fires on every
   transition instead of on `BAKING` and `READY` (5.3).
5. `stays` is used after `READY` and `wait_until` after `BAKING`, and **not** the other way round.
   The two fail for opposite reasons (12.4), and swapping them would leave both assertions passing
   on a broken system.
6. The absorbing fixture is verified to have run: after the whole suite, one more order exists whose
   name carries the label `absorb` (R-e), and it is `ASSIGNED`. Read once by hand over `GET /orders`
   — **this is a check on the fixture, not an assertion inside a test**, since no test may read the
   order list (12.5).
7. **The timing is measured once and written into the pull request**, not asserted: 12.4 predicts
   about 4 s for this scenario including the absorption, and a number far from it means the retry
   cycle is being entered where it should not be.
8. Read from the diff: **the only `sleep` in the unit is the poll interval inside `waiting.py`** —
   12.4 forbids a *bare* sleep in a test, and a cadence between two evaluations of a condition is
   the opposite of one, which is the argument that item already makes for 11.2's `interval`. No
   test calls `sleep` directly. `time.monotonic` is what `waiting.py` measures elapsed time with
   (12.4), and a timeout failure carries the last observed order payload.

---

### Step 3 — Dispatch resumes when a driver registers late

**File changed:** `test_scenarios.py`.

12.2's scenario 2 — `test_recovery_when_a_driver_registers` — the scenario 12.1 ranked highest and
the one R9 is about. An order reaches `BAKING` against an empty pool, is observed `PENDING` across
12.4's window, and a driver is then registered. **No further `PATCH` is sent**, which is the whole
difference between a retry and a re-trigger, and it is checked in the diff rather than only
intended.

**Definition of Done**

1. The two assertions are 12.2's two, and the second one carries the scenario: `ASSIGNED` to the
   driver just registered, `driver.status=BUSY`.
2. The five commands of §4 exit zero, and `pytest tests/unit` collects eighteen.
3. The suite runs the three ways §4 lists, **plus the reverse-order run** §4 adds from this step:
   this is the first step at which two scenarios both depend on the pool being empty, so it is the
   first at which order could matter.
4. `PENDING` rather than `FAILED` is asserted at the window (8.3) — the assertion that separates
   "still retrying" from "gave up", and the one that would pass silently if it read only that no
   driver was attached.
5. **The scenario is run once against a deliberately broken system, and observed to fail.** The
   `worker` service is stopped with `docker compose stop worker` before the run; the test must end
   at 12.4's timeout with the last payload showing `PENDING`. This is what proves the test would
   fail if the behaviour it names broke (`CLAUDE.md` §5), and it is cheap here because the failure
   is one command away. The worker is started again afterwards and the suite re-run green.
6. **The elapsed time of this scenario is read** and compared to 12.4's prediction of about 11 s.
   A time near zero would mean the driver was available before the order reached `BAKING`, which
   makes the scenario assert nothing — the exact fault 12.5's invariant exists to prevent.
7. Read from the diff: exactly two `PATCH` calls in this test, both before the driver is registered;
   no polling loop written inline — every wait goes through `waiting.py` (12.4).

---

### Step 4 — One driver, two orders, and the hand-off between them

**Files changed:** `test_scenarios.py`, `README.md`.

12.2's scenario 3 — `test_one_driver_two_orders` — which is the only scenario that composes release
with retry: one driver, two orders at `BAKING`, exactly one assigned, and the other picked up when
the first is delivered. Which of the two wins is deliberately not asserted (12.2) — that would be an
assertion about queue arrival order, which no decision fixes.

`README.md` gains `## Tests`: the four scenario names with one line each, the two directories and
what separates them (`CLAUDE.md` §5), and the command that runs each against a running stack. **It
does not say the suite runs at `docker compose up`** — that is 11.3's sentence and U11's to write
(R-h).

**Definition of Done**

1. The two assertions are 12.2's two, and the first is written so that it fails if **both** orders
   show the same driver — the cross-table invariant 4.3 records as unprotectable in the schema, and
   this is the only place it is checked.
2. The five commands of §4 exit zero, and `pytest tests/unit` collects eighteen.
3. The suite runs the four ways §4 lists — whole from clean, whole again without `down`, this test
   alone, and in reverse order. **This is the run the unit is merged on**: five test functions,
   green, in any order and twice over.
4. The README section is as stated, names all four scenarios, and claims nothing about automatic
   execution.
5. **The winner is not asserted anywhere**, checked in the diff: the test finds whichever order is
   `ASSIGNED` and proceeds from that one, rather than assuming the first.
6. **The whole suite's wall-clock time is measured and written into the pull request.** 12.4
   predicts about 30 s on a healthy system. This is the number U11 inherits — it is what
   `docker compose up` will pay on every launch (11.3), and 11.5 decides what happens when it fails.
7. Read from the diff: `test_scenarios.py` holds five test functions and no more; each carries the
   two-line docstring §5 requires — which scenario, and why it matters; no test asserts on
   `customer_name`, `address`, `items`, or any timestamp value (12.2).

## 7. Ordering, and where it is free

- **1 → 2, 3, 4:** the client and naming fixtures arrive in step 1 and everything uses them.
- **2 → 3, 4:** `waiting.py` arrives in step 2 with its first caller, and scenarios 2 and 3 cannot
  be written without it. 12.5's absorbing fixture also arrives there, and the invariant it enforces
  is the precondition steps 3 and 4 depend on.
- **3 and 4 are free of each other** and are ordered by what they compose: scenario 3 recovers
  through registration, scenario 4 recovers through release, and 12.2 records that the second is the
  only one that composes release with retry. The harder one goes last.

**Scenario 4 is written first and scenario 1 second, which inverts 12.2's numbering**, and the
reason is that step 1 should be the smallest step that proves the suite can reach the system at all.
Scenario 4 touches no asynchrony, needs neither helper nor fixture, and fails loudly if the base URL
is wrong. Every later step then debugs behaviour rather than a connection. **No step depends on a
step after it.**

## 8. What U10 hands to the units after it

- **U11 (11.1, 11.2, 12.9):** a suite that runs green from outside the network, and a `conftest.py`
  to add the `pytest_terminal_summary` hook to. The `tests` service needs `build: target: test` and
  `image: pizza-test` — a stage U9 already built and checked — plus its two edges and no `restart`
  key. The one thing U11 changes about the suite is the value of `PIZZA_API_BASE_URL`, which becomes
  `http://api:8000` because the runner moves inside the network (R-a).
- **U11 (11.5, 14.7):** the measured wall-clock number from step 4's Definition of Done, which is
  what every `docker compose up` will pay, and the U11 row of 14.7 becomes reachable — the suite
  exists, so "runs the suite and exits zero" now names something.
- **U13 (13.1, 13.4):** one README section to fold into the assembled document, and 12.3's accepted
  cost — the broker-unreachable path with no automated test — now demonstrable as a gap with a
  stated reason rather than an omission.

## 9. After the merge

`main` satisfies 14.7's **U2** and **U9** rows unchanged, and gains something neither row measures
yet: five test functions that assert, over HTTP alone, that an order placed at one end comes back
with a driver at the other — including when there was no driver to give it, and including when the
only driver was already busy. The bar rises once more at U11, when `docker compose up` runs them
without being asked.

What is still missing is the menu a reviewer drives the system from, and the assembled document that
explains it.
