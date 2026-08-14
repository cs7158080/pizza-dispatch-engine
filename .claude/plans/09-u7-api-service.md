# U7 — API service · Implementation Plan

**Phase 3 of the planning protocol in `CLAUDE.md` §2, for the seventh unit in Part 4 of
`03-roadmap.md`.** Decisions are in `02-decisions.md`; nothing here decides anything that
belongs there. Where executing a step needed a call Phase 2 had not made, it is recorded below
under *Readings* rather than left to implementation.

**Gate.** U7's *Decided by* column reads 2.3, 2.4, 3.9, 6, 7.5, 7.6 and 8.7. All are `[decided]`.
Topic 6 closed in pull request #12 and 8.7 in #13; **3.9 is the exception and it is already on this
branch** — it was settled in the session that opened U7, and its record commit is the branch's
first, by the ruling that placed U2's commit A and U5's commits A and C on their unit branches
rather than on gate branches of their own. *Depends on* reads U3, U5 and U6, all merged.

Four open items are touched and none is decided here: 8.4 owns the worker's malformed message, 11.x
owns every Compose service and the command that launches this one, 12.1 owns which scenarios U10
writes, and 12.7 owns how the test directories are invoked.

---

## 1. What this unit delivers

Part 4 gives U7 the routes, the edge validation, the error format, the status-update endpoint
including the publish trigger, and the wiring of core, repositories and publisher. It is **the
first unit that produces a process**: every port has had an implementation since U6, and nothing
has ever constructed one.

**It is not only wiring, and that is this plan's central finding.** Three decided items land ahead
of the entry point and each touches code U3 or U5 wrote:

| Item | What it requires | What is on `main` |
|---|---|---|
| [6.1](02-decisions.md) — request and response schemas | `advance_order_status` returns the order **with its driver**, because `PATCH` answers with the full representation | it returns an `Order` alone |
| [6.9](02-decisions.md) — concurrent `PATCH` | `OrderRepository.get_for_update`, and the write path using it | the port has `add`, `get`, `save`, `list_all` |
| [3.9](02-decisions.md) — what `commit()` may raise | `TransactionFailed` on the port, translated in the adapter, caught at the outbox mark | nothing; `commit()` declares no error |

They are steps 1 to 3 below — numbered work with their own Definitions of Done, not edits made in
passing while wiring. U3 §8 anticipated exactly this shape of finding: *"`PlaceOrder` returns a
`UUID`, because 4.7's sample does. If 6.1's `201` shape needs the entity, that is a return to Phase 2
over one line here, not a judgement U7 makes while wiring."* That return happened while this plan was
being reviewed and **it ended the other way**: 6.1 reversed on 2026-08-13 and both creations now
answer with the identifier alone, so `PlaceOrder` and `RegisterDriver` keep the signatures U3 gave
them. `AdvanceOrderStatus` is the one that changes, and for the `PATCH` body rather than the `POST`.

The unit also builds `pizza/log.py`, which 8.7 places here because this is the first entrypoint, and
which U8 imports unchanged.

## 2. What this unit deliberately does not deliver

Each line names the item that owns it, so nothing here is silence.

| Not built | Owner | Arrives in |
|---|---|---|
| The consumer loop and everything the worker does with a message | topic 8 | U8 |
| The worker's own composition root, which calls the same `configure_logging` | 8.7, 8.8 | U8 |
| Dockerfiles, Compose services, healthcheck wiring, and the `uvicorn` command that launches this app | 3.7, 11.1, 11.2, 11.9 | U9 |
| Every assertion on these six routes | 12.3 — the suite speaks HTTP and U10 owns it | U10 |
| A test that drives the app in-process through `TestClient` | 12.3 fixes the interface as HTTP over the network; an in-process client is a second seam with no owner | not built |
| The CLI that consumes this contract | 3.6, topic 9 | U12 |
| The README's API section, the sequence diagram, the assumptions register | topic 13 | U13 |
| Authentication on any route | 6.8 | not built (FW9) |
| Filtering and paging on `GET /orders` | 6.6 | not built (FW4) |
| A driver listing or driver history endpoint | 6.6, A9 | not built (FW3) |
| Any relay over unpublished outbox rows | A23, 7.5 | not built (FW2) |
| A deliberate `5xx` anywhere | 6.2 — `503` on `GET /health` is the only server-side code, and it is not an error path of the domain | — |

## 3. Branch, commits, and the merge

- **Branch:** `feat/u7-api-service`, cut from `main` at `0443ce4` (14.2).
- **Commits:** one decision commit already present, one planning commit, then one commit per step
  (14.3, 14.4). Eleven in total.
- **Merge:** one pull request, squash-merged, its title ending in `(#15)` (14.2, 14.3). The branch
  is not deleted (14.2).

| # | Type | Title |
|---|---|---|
| A | decision | `docs: settle 3.9 — what UnitOfWork.commit() may raise` — **already committed** |
| B | planning | `docs: plan the api service, and reverse 6.1 to an id-only creation response` — the plan and the amendment it is written against, in one commit |
| 1 | step | `feat: return the order with its driver, for the body a PATCH answers with` |
| 2 | step | `feat: lock the order a status update is about to write` |
| 3 | step | `feat: declare what a commit may raise, and catch it where it lands` |
| 4 | step | `feat: one log format for both services` |
| 5 | step | `feat: the request and response schemas of the API contract` |
| 6 | step | `feat: map every domain error to its status, over one error body` |
| 7 | step | `feat: the seam the routes receive their use cases through` |
| 8 | step | `feat: the six routes` |
| 9 | step | `feat: assemble the api service` |

**A is not a plan step and B is written against it.** 3.9 was settled after the gate opened, in the
session that read U7's inventory, and it is a Phase 2 record rather than a Phase 3 reading — which
is why it is a commit of its own and why step 3 realises it rather than deciding it.

## 4. The Definition of Done that applies to every step

14.7's U2 row still governs; **U7 raises no bar**, and the next raise is U9's. The five commands are
run from the activated virtual environment at the repository root, and each must exit zero **at
every step commit**:

```
ruff format --check .
ruff check .
mypy src tests
python -c "import pizza"
pytest tests/unit
```

Each step below adds its own checks on top of these. A step is done when §8's six conditions hold.

**Three notes so no step improvises.** **No dependency is added and neither lock file changes** —
`fastapi`, `pydantic>=2` and `uvicorn` have been in `pyproject.toml` and in both requirements files
since U1 (2.10), and this unit is the first to import any of them. **`ruff check .` will not catch
the one layering rule that matters here:** `TID251` exempts all of `src/pizza/entrypoints/*`, while
3.1 permits only `main.py` to import `infrastructure/`. Every step that touches `entrypoints/`
therefore carries that check as a diff read, and §5's R-c is what makes it possible to satisfy.
**No documentation changes in this unit**, and the absence is deliberate rather than an omission:
the README's operational sections describe running the system, which is U9's, and 13.1 assembles the
API section in U13. The one document this unit may write is a `docs/ai-log.md` row, and only if
something is rejected or materially changed (§6).

**Most steps are verified by `mypy` and a diff read, and this is written into each one.** 12.3 gives
the integration suite HTTP only and makes U10 its owner, so nothing in `entrypoints/api/` is
asserted by a test inside this unit. §5 admits one free unit test — step 6's — and the reason each
other step has none is stated in its own Definition of Done rather than left as a gap.

## 5. Readings — where this plan filled a silence

Recorded here rather than resolved silently (`CLAUDE.md` §2). The boundary is U1 §5's, restated in
U2, U3, U5 and U6: a Phase 3 document may fill a silence Phase 2 left; it may not settle an
ambiguity inside a decided record.

- **R-a — the composition root loads the settings at module import; the lifespan constructs the
  adapters.** U2 §8 requires the root to call the loader **as its first action** and, on
  `ConfigurationError`, to write the message to standard error and exit non-zero; 7.7 requires the
  ASGI lifespan hook to construct the publisher and close it at shutdown; 2.4 admits that hook as
  its single `async def`. The two fit together only one way. `uvicorn` imports
  `pizza.entrypoints.api.main:app`, so a module-level load runs before anything else in the process
  and reaches U2's contract exactly — one line on `stderr`, exit `1`, no traceback.
  *Checked rather than assumed, because the alternative is the more idiomatic one:* loading inside
  the lifespan does exit non-zero, but not that way. Starlette 1.6.0 catches `BaseException` there,
  sends `lifespan.startup.failed` carrying `traceback.format_exc()`, and uvicorn logs that and calls
  `sys.exit(STARTUP_FAILURE)` — **exit code 3, with a traceback**, and our own message printed
  beside it. Read from `starlette/routing.py` and `uvicorn/config.py`. A reviewer with a mistyped
  variable in `docker compose up` reads one line under this reading and a stack trace under the
  other. `configure_logging` is called at module level for the same reason: it must be in force
  before anything can log.
  *Two things this does not trade away, distinguished because they read alike.* **A process that
  cannot start without its configuration is the behaviour U2 §8 asks for**, not a cost — the same
  behaviour `entrypoints/schema/main.py` already has. What module-level loading adds is narrower:
  the **module** cannot be imported without a full environment. 10.2's rule guards one command,
  `python -c "import pizza"` (14.7), and `src/pizza/__init__.py` is empty — verified, not assumed —
  so that command imports no entrypoint and the rule is untouched rather than overridden. The one
  residual is an offline import of the app object, such as dumping the OpenAPI document without
  running the service, which needs placeholder variables. Nothing decided asks for it.
- **R-b — the unit of work is built per request, and it is a correctness argument rather than a
  style one.** `SqlAlchemyUnitOfWork` holds `self._session`, which `__enter__` assigns and `__exit__`
  clears. 2.4 serves `def` handlers from a thread pool and 6.9 states that two simultaneous requests
  genuinely run in parallel, so one shared instance would have two threads overwriting one attribute
  — the transaction isolation 3.5 and 6.9 both rest on would not exist. The composition root
  therefore places a **factory** in the wiring, and each request builds its own. The publisher is
  the opposite case and is shared: U6 §8 states it is thread-safe by its own lock.
- **R-c — the wiring crosses to `deps.py` as a frozen dataclass of ports and callables, so that no
  module but `main.py` imports `infrastructure/`.** 3.1 permits the import in one file and makes
  `deps.py` the injection seam; those two only coexist if the seam names types the core declares.
  `Wiring` holds `new_unit_of_work: Callable[[], UnitOfWork]`, `clock: Clock`,
  `publisher: EventPublisher` and `database_reachable: Callable[[], bool]` — four fields, every one
  of them a `Protocol` from `application/ports.py` or a plain callable. It is defined in `deps.py`
  and instantiated in `main.py`, which is the direction 3.1 draws.
  *Where it is kept:* `app.state`, read as `request.app.state.wiring` through one annotated local.
  Starlette's `State.__getattr__` returns `Any`, and `strict` mode's `warn_return_any` rejects
  returning that directly — the annotated local is what makes the seam typed rather than a `cast`.
- **R-d — `AdvanceOrderStatus` returns an `OrderDetail`, and the driver is read inside the
  transaction that changed it.** 6.1 gives the `PATCH` response the same nine keys as every other
  order response, 6.5's nested driver among them, so something must load that driver. The use case
  is already inside a transaction holding the order, and on the `DELIVERED` path it already loads
  the driver in order to release them (5.6) — so the read is free there and one keyed `SELECT`
  otherwise, with no `FOR UPDATE` and therefore no bearing on the lock-ordering question 6.9 handed
  to 8.9. `OrderDetail` is `application/queries.py`'s own type, which the use case imports across
  one layer-2 module to another; the core still never sees a response shape (6.5).
  *Rejected — the router re-reading through `queries.get_order` after the use case returns.* This
  plan proposed it first and it is duplication: the order row would be read twice per `PATCH` and
  the driver row twice on the `DELIVERED` path, in a third transaction, so the response would
  describe the state after the commit rather than the state the commit produced. The argument for
  it — that a write path should not carry a read no rule of its own needs — is true and smaller than
  what it costs.
  *What it does not reach:* the creations. Since 6.1's reversal they answer with `{"id": …}`, so
  `PlaceOrder` and `RegisterDriver` keep returning a `UUID` and no response is assembled from an
  entity there at all.
- **R-e — the two domain error messages are brought to 6.3's text, rather than rebuilt at the
  edge.** 6.3 fixes the bodies literally: `"Order <id> not found"` and `"Cannot advance order from
  BAKING to PREPARING"`. The domain errors already format a sentence from the same values, so
  `errors.py` renders `{"detail": str(exc)}` and the sentence exists once. The alternative — a
  per-type formatter table in `errors.py` — writes the same sentence a second time from the same
  attributes, which is 13.6's drift in the file 6.3 wrote to prevent it. 6.3 calls this "message
  design, not data collection", and a domain error's message has always been addressed to a person.
- **R-f — a handler for `Exception` is registered, and it is not a `5xx` contract.** 6.3 promises
  `detail` on **every** error response. Without a handler Starlette answers an unhandled exception
  with `PlainTextResponse("Internal Server Error")` — read from
  `starlette/middleware/errors.py`, not assumed — which carries no `detail` key and would leave 9.4's
  CLI reading a body that does not exist. The handler returns `{"detail": "Internal server error"}`
  with `500`. **It hides nothing:** the same middleware re-raises the exception after the response is
  sent, precisely so the server still logs it, and 6.2's ruling stands unchanged — a `500` is a
  defect, not a covered path. 3.9 already assumed this handler exists when it stated that a failure
  at the first commit "reaches the entry point's `Exception` handler and returns 6.3's body".
- **R-g — the database probe is an infrastructure function reaching the router as a callable.** 6.6
  makes `GET /health` report on the database only, and the router may not import SQLAlchemy (3.1).
  `infrastructure/db/probe.py` holds `database_reachable(engine) -> bool`, which runs `SELECT 1` and
  translates `SQLAlchemyError` into `False` — the same translation duty U5 §8 named for the
  repositories. `main.py` binds the engine into it and puts the result in `Wiring`.
  *Rejected:* a closure in `main.py` — it would put a `try`/`except` in a file that otherwise only
  constructs; and relying on `pool_pre_ping` alone, which makes the check's meaning depend on a pool
  setting rather than on a statement.
- **R-h — `get_for_update` is `Session.get(..., with_for_update=True)`.** Verified against
  SQLAlchemy 2.0.51's signature rather than written as a second `select()`: it is the same
  primary-key path `get` already takes, with the lock added, so the two methods differ by one
  argument and cannot drift in how they load a row.
- **R-i — the three string fields are declared with `strip_whitespace=True`.** 4.2 requires each
  `items` entry to be "non-empty after trimming", which is a trim followed by a length bound; the
  same constraint is applied to `customer_name` and `address` so that `"   "` is `422` on all three
  rather than on one. The values are stored trimmed, which is the only reading under which the
  declaration *is* the validation (2.3).
- **R-j — the routers are `def` and the lifespan is the only `async def` in the repository.** 2.4's
  rule, checked in the diff. The exception handlers are `def` as well, which is not an oversight:
  Starlette runs a synchronous handler through `run_in_threadpool` on both the
  `ExceptionMiddleware` and the `ServerErrorMiddleware` path — read from
  `starlette/_exception_handler.py` and `starlette/middleware/errors.py`.
- **R-k — the paths are written in full on one `APIRouter` per resource, with no `prefix`.** 6.7
  fixes the paths as R1–R4 write them; a prefix would produce identical URLs while making a reviewer
  assemble them from two places to check that.

## 6. Steps

### Step 1 — Return the order with its driver, for the body a `PATCH` answers with

**File changed:** `src/pizza/application/use_cases/advance_order_status.py`.

`AdvanceOrderStatus.__call__` returns an `OrderDetail` instead of an `Order`: the driver is loaded
whenever `order.driver_id` is set rather than only on the release path, and the existing release
branch is folded into that read (R-d). **`PlaceOrder` and `RegisterDriver` are not touched** — 6.1's
reversal leaves both creations answering with the identifier they already return.

**Definition of Done**

1. The signature and the docstring state what comes back.
2. The five commands of §4 exit zero.
3. `pytest tests/unit` still collects sixteen. **No test is added, and the reason is written rather
   than left as a gap:** this is a return type, which `mypy` verifies at every call site, and the
   only assertion a unit test could make — that the driver returned is the one stored — needs a fake
   `UnitOfWork` written to observe it. 12.3 puts the real assertion in U10, where a `PATCH` into
   `DELIVERED` answers with the driver already released.
4. Read from the diff: the driver read takes no lock, and it is the only read added — the order is
   still loaded once per transaction. `place_order.py`, `register_driver.py`, `dispatch_order.py`
   and `queries.py` are untouched.

---

### Step 2 — Lock the order a status update is about to write

**Files changed:** `src/pizza/application/ports.py`,
`src/pizza/infrastructure/db/repositories.py`,
`src/pizza/application/use_cases/advance_order_status.py`.

`OrderRepository` gains `get_for_update(self, order_id: UUID) -> Order | None`, declared beside
`get` with a docstring stating that it locks the row for the rest of the transaction and belongs to
write paths only (3.4's amendment, 6.9's decision). `SqlAlchemyOrderRepository` implements it per
R-h. `AdvanceOrderStatus` calls it in place of `get`; **no other call site changes** — `queries.py`,
6.5's two keyed reads and `DispatchOrder` keep `get`, which is why 6.9 made it a second method
rather than a flag.

**Definition of Done**

1. The port, the implementation and the one call site are as stated.
2. The five commands of §4 exit zero. `mypy` passing is the substantive check on the port: the
   adapter names `OrderRepository` as its base class (U5's R-b), so a missing or mistyped method
   fails at the class definition.
3. `pytest tests/unit` still collects sixteen. The lock's behaviour needs two concurrent
   transactions against PostgreSQL, which 12.3 gives no test in this repository; 6.9 records F14 as
   an HTTP-observable candidate — one `200`, one `409` — and leaves the choice to 12.1 in U10.
4. Read from the diff: `queries.py` and `dispatch_order.py` are untouched, and no read path acquires
   a lock by accident.

---

### Step 3 — Declare what a commit may raise, and catch it where it lands

**Files changed:** `src/pizza/application/ports.py`,
`src/pizza/infrastructure/db/unit_of_work.py`,
`src/pizza/application/use_cases/advance_order_status.py`.

`TransactionFailed` is defined above `UnitOfWork` in `ports.py`, by that module's own rule that a
port error sits above the port that raises it, and `commit()`'s docstring names it.
`SqlAlchemyUnitOfWork.commit()` translates `SQLAlchemyError` into it **and nothing else** — the
narrow catch `CLAUDE.md` §6 requires and the twin of `OutboxWriteFailed` and `PublishFailed`.
`__exit__` is not translated, per 3.9: its `rollback()` runs during unwinding, where an error would
replace the exception already in flight.

`_publish_and_mark`'s catch becomes `except (OutboxWriteFailed, TransactionFailed)`. That is 3.9's
whole behavioural content: the `UPDATE` in `mark_published` leaves with the transaction because 2.5
turned autoflush off, so before this change the `except` guarded the `SELECT` and never the write
the method is named for.

**Definition of Done**

1. The type, the translation and the widened catch are as stated.
2. The five commands of §4 exit zero.
3. `pytest tests/unit` still collects sixteen. The window is a database fault between two adjacent
   statements — 3.9 says so in those words — and no test in this repository can produce one.
4. Read from the diff: the first `commit()` in each use case is **not** wrapped. 3.9 fixes that a
   failure there means the write did not happen, and 6.2 admits no deliberate `5xx`, so it reaches
   step 6's `Exception` handler and returns 6.3's body with `500`.

---

### Step 4 — One log format for both services

**File created:** `src/pizza/log.py`.

`configure_logging(level: str) -> None` calls `logging.basicConfig` with 8.7's record line,
`"%(asctime)s %(levelname)-8s %(name)s %(message)s"`, and the level it is given. Nothing else: the
default stream stands (8.7), no per-library level is curated, and no handler is built by hand.

It sits beside `config.py` rather than inside one of 3.1's four directories, for the reason 10.2
gave that file — it is neither core nor adapter, and both composition roots call it.

**Definition of Done**

1. The file exists, with one public function and no module-level side effect.
2. The five commands of §4 exit zero.
3. `pytest tests/unit` still collects sixteen. **No test:** the function's whole content is one
   standard-library call, and a test asserting that `basicConfig` was called with our format string
   would assert the implementation §5 forbids testing. What it produces becomes visible in
   `docker compose up`, which is 1.2's own reading step.
4. Read from the diff: `uvicorn` configures the `uvicorn.*` loggers and no root logger, with
   `disable_existing_loggers: False` — read from `uvicorn/config.py` — so this call and uvicorn's
   own configuration coexist in either order, and our records reach `stderr` through the root
   handler.

---

### Step 5 — The request and response schemas of the API contract

**File created:** `src/pizza/entrypoints/api/schemas.py`, with `__init__.py` for the package.

6.1's three request and five response models, every request model declared `extra="forbid"` (2.3):

| Model | Content |
|---|---|
| `CreateOrderRequest` | `customer_name` 1–100, `address` 1–200, `items` 1–20 entries of 1–100 characters — 4.2's bounds, R-i's trimming |
| `UpdateStatusRequest` | `status: OrderStatus` — the domain enum, so an unrecognised value is `422` before the core sees it (5.2) |
| `RegisterDriverRequest` | `name` 1–100 (6.4) |
| `Created` | `{id}` — the body of both creations, since 6.1's reversal |
| `OrderResponse` | 6.1's nine keys, `driver` nested or `null` (6.5) |
| `OrderSummary` | 6.6's five fields, no driver |
| `DriverResponse` | `{id, name, status}` — 6.5's nested object, and nothing else carries it |
| `HealthResponse` | `{"status": "ok"}` |

`OrderResponse.of(detail: OrderDetail)` and `OrderSummary.of(order: Order)` build the responses from
the types the application layer returns — `GET /orders/{id}` and `PATCH` both hand over the
`OrderDetail` they were given (R-d). Timestamps are not pinned to a spelling (6.1) — Pydantic v2's
default serialization, no custom serializer.

**Definition of Done**

1. The file exists, with the eight models and the two constructors.
2. The five commands of §4 exit zero.
3. `pytest tests/unit` still collects sixteen. **No test, and the boundary is worth naming:** what a
   test here could assert is that a `dataclass` field reaches a Pydantic field of the same name,
   which `mypy` already checks, or that a bound rejects a value, which asserts Pydantic's behaviour.
   Every assertion that names a behaviour of ours — the nested driver, `assignment_state`, the
   `422` — is a scenario in 12.3's table and lands in U10 over HTTP.
4. Read from the diff: this module imports `pydantic`, `pizza.domain` and `pizza.application`, and
   nothing from `infrastructure/` — the rule `ruff` cannot enforce here (§4).

---

### Step 6 — Map every domain error to its status, over one error body

**File created:** `src/pizza/entrypoints/api/errors.py`. **Files changed:**
`src/pizza/domain/errors.py` (R-e). **File created:** `tests/unit/test_error_mapping.py`.

`errors.py` carries 6.3's table and the two response declarations beside it, so the status number is
written once:

```python
_STATUS   = {OrderNotFound: 404, IllegalTransition: 409}
NOT_FOUND = {404: {"description": "Order not found"}}
CONFLICT  = {409: {"description": "Illegal transition"}}
```

`install(app)` registers **one** handler for every key in `_STATUS` — 3.1's "one registered handler",
which is what keeps 5.2's mapping out of the routes — and one handler for `Exception` per R-f. Both
return `JSONResponse({"detail": …})`, both are `def` (R-j). The domain handler renders `str(exc)`,
whose two sentences step 6 brings to 6.3's wording in `domain/errors.py`. Pydantic's `422` handler is
**not** overridden (6.3).

**File created:** `tests/unit/test_error_mapping.py`, **one test**, free by 5.7's standard — pure
logic, no infrastructure, no double.

| Test | What it asserts | Why it earns its place |
|---|---|---|
| `test_every_domain_error_has_a_status` | every `Exception` subclass defined in `pizza.domain.errors` is a key in `_STATUS` | A domain error added later without a row here does not fail: it falls through to R-f's handler and returns `500` with a body that says nothing, on a request the rules refused deliberately. 6.2 calls a `500` a defect rather than a contract, and this is the one way the system could produce one by omission. It is also the only assertion in this unit that no HTTP scenario in U10 can make, because the failure is about an error that does not exist yet |

**Definition of Done**

1. The three files are as stated.
2. The five commands of §4 exit zero.
3. `pytest tests/unit` collects **seventeen** — the sixteen on `main`, and this one.
4. Read from the diff: `_STATUS` holds exactly two rows; no route mentions a status number; the
   `Exception` handler returns a response and does not swallow — Starlette re-raises after sending,
   so the traceback still reaches the log.
5. The two domain messages read as 6.3 writes them, and no other domain module changes.

---

### Step 7 — The seam the routes receive their use cases through

**File created:** `src/pizza/entrypoints/api/deps.py`.

`Wiring` per R-c — a frozen dataclass of four fields — and one dependency function per thing a route
needs, each exported as an `Annotated[…, Depends(…)]` alias so the routers name a type rather than a
call:

```python
WiringDep       = Annotated[Wiring, Depends(_wiring)]           # request.app.state.wiring
UnitOfWorkDep   = Annotated[UnitOfWork, Depends(_unit_of_work)] # a fresh one per request — R-b
PlaceOrderDep, AdvanceOrderStatusDep, RegisterDriverDep
```

Each use-case dependency constructs its use case from the wiring, taking a new unit of work and the
shared clock and publisher. `AdvanceOrderStatus` is the only one that receives the publisher, which
is 7.5's ordering expressed in the wiring rather than restated in a route.

**Definition of Done**

1. The file exists, with `Wiring` and the five aliases.
2. The five commands of §4 exit zero. `mypy` passing is the substantive check: the aliases resolve to
   the concrete use-case classes, so a router that asks for the wrong one does not type-check.
3. `pytest tests/unit` still collects seventeen. Nothing here is testable without either a running
   app (U10) or a double for every port, which would assert that a constructor was called.
4. Read from the diff: **no import from `infrastructure/`**, and no module-level state — the wiring
   is read from the request, so nothing is bound at import time.

---

### Step 8 — The six routes

**Files created:** `src/pizza/entrypoints/api/routers/__init__.py`,
`routers/orders.py`, `routers/drivers.py`, `routers/health.py`.

6.6's endpoint list, at 6.7's paths, with 6.2's codes and 6.3's declarations:

| Route | Code | Response | Declares |
|---|---|---|---|
| `POST /orders` | `201` | `Created` | — |
| `PATCH /orders/{order_id}/status` | `200` | `OrderResponse`, over the `OrderDetail` the use case returns (R-d) | `NOT_FOUND`, `CONFLICT` |
| `GET /orders/{order_id}` | `200` | `OrderResponse` | `NOT_FOUND` |
| `GET /orders` | `200` | `list[OrderSummary]` | — |
| `POST /drivers` | `201` | `Created` | — |
| `GET /health` | `200` / `503` | `HealthResponse`, or 6.3's body | — |

`order_id` is typed `UUID`, so a malformed identifier fails FastAPI's own path validation and
returns `422` — 6.2's row, and the one a reviewer may expect to be `404`. No route catches a domain
error: they leave as exceptions and step 6's handler answers them, which is the whole reason that
table exists. No route touches the publisher — 7.6's `200` on an unreachable broker needs no code
here, because `AdvanceOrderStatus` already catches `PublishFailed` (U6 §8). `GET /health` calls
`wiring.database_reachable()` and raises `HTTPException(503, "Database unreachable")` when it is
false, which produces 6.3's key by FastAPI's own default.

**Definition of Done**

1. The four files are as stated, six routes in total and no others.
2. The five commands of §4 exit zero.
3. `pytest tests/unit` still collects seventeen. Every route needs a database and a running server;
   12.3 owns all of it and U10 writes it.
4. Read from the diff: every handler is `def` (2.4); no module imports `infrastructure/`; no status
   number is written in a router except `201` and `503`, both of which 6.2 names; no route
   re-implements a rule — `PATCH` passes the requested status to the use case and 5.1 decides.

---

### Step 9 — Assemble the api service

**Files created:** `src/pizza/entrypoints/api/main.py`,
`src/pizza/infrastructure/db/probe.py`.

`probe.py` holds R-g's `database_reachable(engine: Engine) -> bool`.

`main.py` is the composition root, and everything in it is either a construction or a registration:

```
settings = load_service_settings(os.environ)   # module level — R-a; on ConfigurationError,
configure_logging(settings.log_level)          # stderr and exit 1

@asynccontextmanager                           # 2.4's single async def
async def lifespan(app):
    engine  = create_engine(settings.database_url, pool_pre_ping=True)        # U5 §8
    factory = sessionmaker(engine, autoflush=False, expire_on_commit=False)   # U5 §8
    publisher = PikaEventPublisher(settings.broker_url,                       # U6 §8 — three
                                   settings.broker_publish_timeout_seconds,   # values, no I/O
                                   settings.dispatch_retry_delay_seconds)
    app.state.wiring = Wiring(new_unit_of_work=partial(SqlAlchemyUnitOfWork, factory),
                              clock=SystemClock(),
                              publisher=publisher,
                              database_reachable=partial(database_reachable, engine))
    yield
    publisher.close()                          # 7.7's shutdown half
    engine.dispose()

app = FastAPI(title="Pizza Dispatch", lifespan=lifespan)
errors.install(app)                            # step 6
app.include_router(...)                        # step 8's three routers
```

**Startup touches neither dependency.** `create_engine` opens no connection and
`PikaEventPublisher` performs no I/O, which is 7.7's requirement and the property U9 relies on when
it writes `depends_on`.

**Definition of Done**

1. Both files exist, with the content stated.
2. The five commands of §4 exit zero.
3. `pytest tests/unit` still collects seventeen.
4. `PIZZA_…= python -c "import pizza.entrypoints.api.main"` with a complete environment succeeds
   with no database and no broker running — the strongest check available before U9, and the one
   that proves construction performs no I/O.
5. The same import with an incomplete environment prints one `invalid configuration:` block on
   `stderr` and exits `1`, with no traceback. This is U2 §8's contract, checked rather than assumed.
6. Read from the diff: this is the **only** module under `entrypoints/` importing `infrastructure/`
   (3.1); the `lifespan` is the only `async def` under `src/pizza/` (2.4); nothing in it calls into
   `application/`; `close()` and `dispose()` are both after the `yield`.

## 7. Ordering, and where it is free

Two chains are forced and everything else follows from them.

- **1 → 8** and **2, 3 → 8:** a route cannot answer with an entity a use case does not return, and
  step 8's `PATCH` is written against the locked read and the declared commit error.
- **5, 6, 7 → 8 → 9:** the routers import the schemas, the response declarations and the dependency
  aliases; `main.py` imports the routers and the handler installer.

Steps 1 to 4 are independent of one another and could be taken in any order; they are numbered as
they are so that the three items of §1 sit together, ahead of the first file this unit creates.
**No step depends on a step after it, and no step needs a file a later step creates** — which is
what makes each of steps 5 to 8 type-check on its own even though nothing runs until step 9.

## 8. What U7 hands to the units after it

- **U8 (8.7, 10.2, U2 §8):** `configure_logging(level)` is importable from `pizza.log` and the
  worker's root calls it with the same field, so the two services cannot diverge in format. The
  loader contract is the same one this unit implements — first action, `stderr`, non-zero — and the
  worker has no lifespan to weigh it against, so it is `main()` from the first line.
- **U8 (3.9):** `TransactionFailed` now exists and `commit()` declares it. The consumer is **not**
  required to catch it: 8.4's third class already covers a database that falls over mid-message by
  letting the message circle, and this type joins that class rather than opening a fourth.
- **U8 (R-b):** the per-request unit of work is the API's constraint and not the worker's — 8.5 runs
  one consumer at prefetch 1 on the main thread, so one instance per message is a loop variable
  rather than a factory. The reason is written here so U8 does not copy a shape it does not need.
- **U9 (11.1, 11.9):** the image runs `uvicorn pizza.entrypoints.api.main:app --host 0.0.0.0 --port
  8000` in **exec form** (8.8's requirement to 11.9), on 10.4's fixed internal port. The api starts
  after the schema service exits zero (4.6) and **needs no `depends_on` on the broker** — 7.7 and
  this unit's step 9 keep startup free of it.
- **U9 (6.6, 11.2):** `GET /health` is the healthcheck command's target and reports on the **database
  only**, deliberately: 7.6 makes a status update succeed without the broker, so a `503` for an
  unreachable broker would be false. A bad environment exits `1` before the port opens, so a
  misconfigured api fails its healthcheck rather than serving errors.
  *Handed here unverified, measured while closing step 9:* the probe carries **no connect
  timeout**, and against a database that refuses the connection it answered `False` after 130
  seconds on Windows — the delay is libpq's, and a refusing database is exactly the container
  that has not finished starting. U9 is the first unit that sees this on Linux, and it writes
  `interval` and `timeout` beside it. The row in `docs/ai-log.md` carries the measurements.
- **U10 (12.3, 12.1):** the six routes and their bodies are the whole surface the suite drives.
  Everything this plan marks "read from the diff" becomes observable here — 6.5's nesting, 6.9's
  lock through F14 if 12.1 selects it, and 7.6's `200` only if 12.3's reopen condition is ever met,
  which it is not today.
- **U12 (6.3, 6.7, 3.6):** the contract is frozen and the generated OpenAPI document describes it,
  including `404` and `409` through step 6's constants. Every error carries `detail` — a string on
  `404`, `409` and `503`, Pydantic's per-field list on `422` — which is the shape 9.4 branches on.
- **U13 (13.1):** the assumptions this unit realises are already registered — A27 for the response
  bodies the brief does not specify, and 6.8's stated absence of authentication. Nothing new is
  assumed here.

## 9. After the merge

`main` satisfies 14.7's U2 row unchanged — the five commands of §4 all exit zero on a clean clone,
with **seventeen** unit tests. The bar rises at U9.

The repository now holds a service that can be started, and nothing starts it: there is no image, no
Compose file and no command, which is exactly U9's content. Every business rule still lives in
`domain/`, every port still has one implementation, and `domain/` and `application/` still import
nothing but the standard library and each other — enforced by `ruff check .` since U5, and by this
plan's diff reads wherever `TID251` cannot reach.
