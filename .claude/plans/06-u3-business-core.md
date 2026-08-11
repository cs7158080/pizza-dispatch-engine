# U3 — Business core · Implementation Plan

**Phase 3 of the planning protocol in `CLAUDE.md` §2, for the third unit in Part 4 of
`03-roadmap.md`.** Decisions are in `02-decisions.md`; nothing here decides anything that
belongs there. Where executing a step needed a call Phase 2 had not made, it is recorded below
under *Readings* rather than left to implementation.

**Gate.** U3's *Decided by* column reads 3.2, 3.4, 3.5, 4.1–4.4, 4.7–4.9, 5 and 7.2. All are
`[decided]` in the status table of `02-decisions.md`. 7.2 reached `main` as pull request #7 —
merged where U3 first needs it, which is what 14.3 fixes — and the column itself was corrected by
commit A below, because it named no topic 7 item while this unit's content includes the event
type. U1 and U2 are merged, so both dependencies are real rather than nominal. No open item is
touched: 12.6 owns how far the unit set may go and this unit writes only the free ones; 8.4 owns
what the consumer does with an unexpected exception and this unit only names the exception; 6.1
owns the response shapes and this unit returns entities.

---

## 1. What this unit delivers

Part 4 gives U3 five things: the `Order` and `Driver` entities, the status transition rules, the
driver-selection and assignment rules, the port interfaces, and the `ORDER_READY` event type —
framework-free, no infrastructure. Per the scope ruling recorded in commit A's discussion, that
means both inner layers of 3.1: `domain/` and `application/`, including the four use cases 3.1
names and `queries.py`.

After U3 the repository holds **every business rule the system has, and can run none of them.**
There is no adapter, no entry point, no database and no broker. What can be run is the test
suite: the rules 5.7 marks provable against `domain/` alone are proved, with no double of any
kind.

The two layers are checkable rather than asserted — 3.1 wrote its rule so it could be read in a
diff, and §4 below turns it into a command that runs at every step.

## 2. What this unit deliberately does not deliver

Each line names the item that owns it, so nothing here is silence.

| Not built | Owner | Arrives in |
|---|---|---|
| `domain/rules.py` | 3.2 — every rule decided so far belongs to one entity, and `CLAUDE.md` §6 rejects an empty module | the first rule that spans two entities |
| `SystemClock`, the concrete `UnitOfWork`, the three repositories, the outbox store | 3.1 places them in `infrastructure/`; 2.5, 4.5, 4.6, 8.9 | U5 |
| `serialize` / `deserialize`, the topology, the publisher | 7.1, 7.3, 7.7 | U6 |
| ack / nack selection, the `x-death` read, dispatch logging | 8.1, 7.4, 8.6 | U8 |
| The domain-error → HTTP status table, edge validation of `items`, the nested driver shape | 5.2, 4.2, 6.5 — 3.2's table classifies all three as things that look like rules and are not | U7 |
| Composition roots, and the `load_service_settings` call U2 §8 contracted for | 10.2 | U7, U8, U12 |
| Unit tests beyond 5.7's free set | 12.6 — open | U4 |
| `[tool.pytest.ini_options]`, and how the two test directories are invoked separately | 12.7 — open | U4 |
| A logging handler, format, or level | 8.7 — open; this unit only calls `logger.error` where 7.6 requires it | U7, U8 |

## 3. Branch, commits, and the merge

- **Branch:** `feat/u3-business-core`, cut from `main` at `fb1f60e` (14.2).
- **Commits:** three amendment commits, one planning commit, then one commit per step (14.3,
  14.4). Eleven in total.
- **Merge:** one pull request, squash-merged, its title ending in `(#8)` (14.2, 14.3). The branch
  is not deleted (14.2).

| # | Type | Title |
|---|---|---|
| A | amendment | `docs: file 7.2 under the unit that realises it` |
| B | amendment | `docs: let the unit that writes a rule write its free test` |
| C | amendment | `docs: give the outbox mark a failure type of its own` |
| D | planning | `docs: plan the business core` |
| 1 | step | `feat: give the order a lifecycle with exactly one legal move` |
| 2 | step | `feat: give the driver a two-state life` |
| 3 | step | `feat: declare what the core asks of the outside world` |
| 4 | step | `feat: place an order and register a driver` |
| 5 | step | `feat: advance an order, and report when to publish` |
| 6 | step | `feat: assign a driver to an order, once` |
| 7 | step | `feat: read one order with its driver, and list them` |

**None of A, B or C is a plan step**, and all three amend records rather than filling silences —
the boundary U2 §5 drew and 14.7 stated first. They ride on this branch rather than on a
`plan/u3-gate` branch of its own, by the same ruling and for the same reason that put U2's
commit A on its unit branch: each was found while opening the unit, and each is one cell, one
line or one exception type. **All three precede D** because D cites them, and a plan cannot cite
a decision the history does not yet contain; that is U1's ordering rule, applied again.

*What A changed:* U3's *Decided by* cell gained 7.2, and U6's lost it — the same contract was
claimed by two units, which is what made an ordinary contract dependency read as an inverted unit
dependency.
*What B changed:* 5.7's *Realised in* line named U4 alone. §8 gives every step a test that would
fail when its behaviour breaks, and 5.7's own table marks these rules provable with no double, so
U3 gets there first — exactly the ordering 14.7 recorded when the `pytest` row moved from U4 to
U2. U4's row in the unit table is untouched.
*What C changed:* 3.4 had fixed that a failed `mark_published` is logged rather than raised and
left the type unnamed, which left this plan writing `except Exception` in `application/`. 3.4's
own `PublishFailed` was already the answer and had not been applied. The amendment adds
`OutboxWriteFailed` beside `OutboxStore` and states the placement rule both now follow.

## 4. The Definition of Done that applies to every step

14.7's U2 row still governs; **U3 raises no bar**, and the next raise is U9's. The five commands
are run from the activated virtual environment at the repository root, and each must exit zero
**at every step commit**:

```
ruff format --check .
ruff check .
mypy src tests
python -c "import pizza"
pytest tests/unit
```

**One check this unit adds for itself**, which is not a 14.7 amendment and does not travel past
this branch — it is 3.1's import rule in the form 3.1 asked for, "written so it can be checked in
a diff":

```
grep -rnE "^(from|import) (pizza\.(infrastructure|entrypoints)|pydantic|sqlalchemy|pika|fastapi)" \
     src/pizza/domain src/pizza/application
```

It must print nothing. The positive form of the same rule is 3.1's one question — can `domain/`
and `application/` run with nothing installed but Python — and every import in this unit is
stdlib or a sibling module.

Each step below adds its own checks on top of these. A step is done when §8's six conditions
hold.

*One mechanical note so no step improvises:* U1's editable install is a `.pth` file naming
`src`, so a new subpackage is importable the moment its `__init__.py` exists. No reinstall.

## 5. Readings — where this plan filled a silence

Recorded here rather than resolved silently (`CLAUDE.md` §2). The boundary is U1 §5's, restated
in U2 §5: a Phase 3 document may fill a silence Phase 2 left; it may not settle an ambiguity
inside a decided record. Anything of the second kind became commit A, B or C before this
document existed — including the one this section carried in its first draft, R-j.

- **R-a — `domain/errors.py` grows with its callers.** `IllegalTransition` in step 1,
  `OrderNotFound` in step 5. Creating both up front would put an unraised exception in the tree,
  which `CLAUDE.md` §6 rejects as dead code. There is no `DriverNotFound`: A9 gives drivers no
  read endpoint and no path ever looks one up by an identifier it did not just claim.
- **R-b — `errors.py` imports `OrderStatus` only for type checking.** `order.py` raises
  `IllegalTransition`, so a runtime import back would be a cycle. `from __future__ import
  annotations` plus a `TYPE_CHECKING` block gives the typed signature 5.2 asks for with no
  runtime edge.
- **R-c — `Driver.new()` exists, by 4.9's own argument.** 4.9 names `mark_busy` and `release` and
  is silent on construction. Its reason for `Order.new()` — that the initial state is a rule and
  belongs in the core — applies unchanged to a registered driver being `AVAILABLE`, and the
  alternative is `register_driver` writing that value in `application/`.
- **R-d — use cases are classes with constructor injection and one `__call__`.** 4.7's and 3.5's
  samples already show `self._uow` and `self._clock`, so the shape is transcribed rather than
  chosen. What this fixes is only that the operation is `__call__` and not a named method, so
  every call site reads the same.
- **R-e — `queries.py` holds two functions, not two classes.** 3.1 names them `get_order` and
  `list_orders`. They have exactly one dependency and no state, so a class would be a constructor
  and nothing else; the `UnitOfWork` is the first parameter. 3.5's "read paths use the same unit
  of work and never commit" is what they implement.
- **R-f — `DispatchOrder` returns an outcome; the consumer maps it to an ack.** 8.1 enumerates
  four exhaustive cases and 3.2 places the ack/nack selection in
  `entrypoints/worker/consumer.py`. A returned `DispatchOutcome` is the only shape that satisfies
  both: the use case reports what happened, and the AMQP verb stays outside the core. Its three
  values are 8.1's cases 1 to 3.
- **R-g — case 4 is `DispatchOrder.give_up()`, in the same module.** 3.1's tree names exactly
  four use-case files, so exhaustion gets no file of its own. It is not a value of the outcome
  enum either: exhaustion is read from the broker's `x-death` header (7.4), which is knowledge
  the consumer has and the core must never acquire.
- **R-h — the use case takes `order_id`, not the event.** 7.2 carries identifiers only precisely
  because 5.5 requires the current row to be read, so the identifier is the whole of what the
  message may be trusted for. Taking the event would let a later field be read from a message
  that may be minutes old.
- **R-i — a missing order raises rather than acking.** The outbox row and the status change are
  written in one transaction (7.5), so an event naming an order that does not exist is a broken
  invariant, not a race. `NOTHING_TO_DO` would ack it and erase the only evidence. 8.4 owns what
  the consumer does with an unexpected exception, and 8.4 is open.
- **R-j — withdrawn, and it became commit C.** This section first read that the failed outbox
  mark is caught as `except Exception`, since 3.4 named no type. That is a decided record's
  silence about a type, not about behaviour — but the fix belongs in the record rather than
  here, because a plan cannot introduce an exception a port does not declare. 3.4 now declares
  `OutboxWriteFailed`, and step 5 catches it by name.
- **R-k — `logging.getLogger(__name__)` at module level.** 7.6 requires one `ERROR` line and 8.7
  is open. A module logger is stdlib, needs no configuration to be correct, and leaves the
  handler, the format and the level exactly where 8.7 will put them.

## 6. Steps

### Step 1 — Give the order a lifecycle with exactly one legal move

**Files created:** `src/pizza/domain/__init__.py` (empty), `src/pizza/domain/errors.py`,
`src/pizza/domain/order.py`.

`errors.py` holds `IllegalTransition`, carrying the current and the requested status (5.2), with
the `TYPE_CHECKING` import of R-b.

`order.py` is 4.9 transcribed: `OrderStatus` and `AssignmentState` as plain `Enum` with explicit
string values; `_NEXT` as the four-entry mapping, so terminality is a missing key; the frozen
`TransitionResult` carrying `must_publish` and `releases_driver`; and the mutable `Order`
dataclass with 4.1's nine fields in that order. Five operations: `new()` (the only place
`RECEIVED` and `PENDING` are written), `advance_to()`, `can_be_assigned()`, `assign_to()` and
`mark_dispatch_failed()`. Each guard is 4.9's — `advance_to` raises, `assign_to` does not, and
`mark_dispatch_failed` returns early unless `can_be_assigned()`.

**File created:** `tests/unit/test_order.py`, five tests. Each is chosen by the failure it would
catch (`CLAUDE.md` §5) and carries that reason as its docstring.

| Test | What it asserts | Why it earns its place |
|---|---|---|
| `test_the_lifecycle_walks_forward_once_per_step` | the four legal moves in order, and that `must_publish` is true at exactly `BAKING` and `READY` while `releases_driver` is true at exactly `DELIVERED` | 5.1, 5.3 and 5.6 in one pass. A publish trigger that fired on the wrong transition would dispatch an order that is not baking yet, and nothing downstream could tell |
| `test_skipping_reversing_and_repeating_are_all_refused` | `RECEIVED → BAKING`, `BAKING → PREPARING` and `BAKING → BAKING` each raise `IllegalTransition` carrying both statuses, and leave the status unchanged | 5.1's three halves and 5.2's payload. A skip would make delivery-without-dispatch a supported path (F12); a repeat that succeeded would re-publish `ORDER_READY`, which 5.1 exists to prevent |
| `test_an_order_admits_exactly_one_driver` | `can_be_assigned()` is true when new, false after `assign_to`, and false once `DELIVERED` | 5.5, both clauses. Dropping the "not delivered" clause leaks a driver out of the pool permanently, which no interface reports |
| `test_a_failed_dispatch_survives_delivery` | `mark_dispatch_failed()` then `advance_to(DELIVERED)` leaves `FAILED`, not `COMPLETED` | 4.9's conjunct. Without it the one record that dispatch gave up is erased by an unrelated status update |
| `test_giving_up_is_ignored_once_a_driver_is_assigned` | `mark_dispatch_failed()` after `assign_to` changes nothing | 4.9 calls this guard load-bearing: R5 puts two messages per order in flight, so one can exhaust after the other has assigned |

Each test builds its `Order` with `Order.new`; none imports anything outside `pizza.domain`.

**Definition of Done**

1. The four files exist, with the content stated.
2. The five commands of §4 exit zero, and the layering command prints nothing.
3. `pytest tests/unit` collects ten tests — the five from U2 and these five.
4. `python -c "import pizza.domain.order"` succeeds with nothing installed but the package.

---

### Step 2 — Give the driver a two-state life

**File created:** `src/pizza/domain/driver.py` — `DriverStatus` (`AVAILABLE` | `BUSY`), the
`Driver` dataclass with 4.3's four fields, `new()` per R-c, and `mark_busy()` / `release()` per
3.2. No back-reference to an order: 4.3 holds the relationship once, on `orders.driver_id`.

**File created:** `tests/unit/test_driver.py`, one test —
`test_a_registered_driver_starts_available_and_returns_to_it`: `new()` yields `AVAILABLE`,
`mark_busy()` makes it `BUSY`, `release()` makes it `AVAILABLE` again. It earns its place because
5.6 exists to stop the pool being consumed once and never refilled; a `new()` that started `BUSY`,
or a pair of methods written the wrong way round, produces a system that stops dispatching after
as many orders as there are drivers — the failure 5.6 says a reviewer would hit during an
ordinary demo.

**Definition of Done**

1. Both files exist, with the content stated.
2. The five commands of §4 exit zero, and the layering command prints nothing.
3. `pytest tests/unit` collects eleven tests.
4. `driver.py` imports nothing from `pizza.domain.order` — the two entities do not know each
   other, which is what makes 4.9's "an `Order` may not mutate a `Driver`" structural.

---

### Step 3 — Declare what the core asks of the outside world

**Files created:** `src/pizza/application/__init__.py` (empty),
`src/pizza/application/events.py`, `src/pizza/application/ports.py`.

`events.py` is 7.2 transcribed: `OrderReadyEvent`, a frozen dataclass with `EVENT_TYPE` as a
`ClassVar` and three fields — `event_id`, `order_id`, `occurred_at`.

`ports.py` is 3.4 and 3.5 transcribed: `Clock`, `OrderRepository`, `DriverRepository`,
`OutboxStore`, `EventPublisher` and `UnitOfWork` as `Protocol`s, plus the two port errors —
`OutboxWriteFailed` and `PublishFailed`, each immediately above the port that raises it, which is
the placement rule C states. Two docstrings carry conventions that would otherwise live in a comment nobody reads:
`list_all` states newest-first (6.6), and `claim_next_available_driver` states — inside the core,
which is 3.2's requirement — that the ordering is a convention rather than a business rule, that
the returned driver is locked and not yet marked, and where a future rule would enter.

**Definition of Done**

1. The three files exist, with the content stated.
2. The five commands of §4 exit zero, and the layering command prints nothing.
3. `pytest tests/unit` still collects eleven tests — **this step adds none, and that is the
   step's own finding.** A `Protocol` has no behaviour to break; what can break is a mismatch
   between a port and an adapter, and there is no adapter until U5. `mypy` checking this file and
   `mypy` checking U5's implementations against it are the two halves of that verification, and
   §8.2 is answered by the second half rather than by a test asserting that a declaration
   declares.
4. `python -c "import pizza.application.ports"` succeeds, proving no infrastructure import
   arrived with the type names.

---

### Step 4 — Place an order and register a driver

**Files created:** `src/pizza/application/use_cases/__init__.py` (empty),
`place_order.py`, `register_driver.py`.

Both follow R-d: a class holding `_uow` and `_clock`, one `__call__`. `PlaceOrder` builds an
`Order` with `uuid4()` and `clock.now()`, adds it, commits, and returns the identifier — 4.7's
sample line for line, including its point that the identifier is known before the transaction
opened. `RegisterDriver` is the same shape over `Driver.new`.

**Definition of Done**

1. The three files exist, with the content stated.
2. The five commands of §4 exit zero, and the layering command prints nothing.
3. Neither module imports `uuid` for anything but `uuid4`, and neither imports a time module —
   4.7 and 4.8 in the file where they could be broken.
4. `pytest tests/unit` still collects eleven. Use case behaviour is covered by 12.2's four
   scenarios over HTTP, which 5.7 already decided rather than by a fake `UnitOfWork` here.

---

### Step 5 — Advance an order, and report when to publish

**Files changed:** `src/pizza/domain/errors.py` gains `OrderNotFound`.
**File created:** `src/pizza/application/use_cases/advance_order_status.py`.

`AdvanceOrderStatus` holds `_uow`, `_clock` and `_publisher`, and `__call__(order_id, to)`
returns the updated `Order` — which is what 7.6's `200` needs. Inside one transaction it loads
the order, raises `OrderNotFound` if there is none, calls `advance_to` and lets
`IllegalTransition` escape to the caller (5.2), saves the order, and then acts on the two flags:
`releases_driver` loads and releases the assigned driver when there is one — a no-op otherwise,
per 5.6 — and `must_publish` builds the `OrderReadyEvent` and adds it to the outbox. Then it
commits.

The publish is the one identified line **after** the commit (7.5, 3.5): on success the outbox row
is marked published in a second transaction, which is why 3.4 requires the `UnitOfWork` to be
re-enterable; on `PublishFailed` it logs one `ERROR` line and returns, because 7.6 makes the
`PATCH` succeed either way. The mark itself catches `OutboxWriteFailed` and logs — 3.4's "logged,
not raised, since nothing acts on unpublished rows", now with a type to name.

`occurred_at` is the **single** `Clock.now()` read of the invocation, per 7.2 — one read, two
destinations, since 7.5's outbox row takes its `created_at` from the same value.

**Definition of Done**

1. Both files exist, with the content stated.
2. The five commands of §4 exit zero, and the layering command prints nothing.
3. The publish call appears **after** `uow.commit()` in the source, and no line between them
   touches the transaction. This is 7.5's whole decision, and it is the one line in this unit a
   later edit could reverse without any test noticing until U10.
4. `pytest tests/unit` still collects eleven.

---

### Step 6 — Assign a driver to an order, once

**File created:** `src/pizza/application/use_cases/dispatch_order.py`, holding `DispatchOutcome`
and `DispatchOrder`.

`__call__(order_id)` opens one transaction, loads the order, raises `OrderNotFound` per R-i, and
returns `NOTHING_TO_DO` when `can_be_assigned()` is false — 5.5's guard, evaluated in the core.
It then claims a driver; `None` returns `NO_DRIVER_AVAILABLE` with nothing written. Otherwise it
marks the driver busy, assigns the order, saves both and commits — 4.3's invariant, which is why
both writes are inside one `with` and there is no path that saves one without the other. Returns
`ASSIGNED`.

`give_up(order_id)` is R-g: load, `mark_dispatch_failed()`, save, commit. The entity's own guard
makes it a no-op on an order that has since been assigned or delivered.

**Definition of Done**

1. The file exists, with the content stated.
2. The five commands of §4 exit zero, and the layering command prints nothing.
3. The module contains no AMQP word — no `ack`, `nack`, `reject` or `requeue`. 3.2 puts that
   selection in the consumer, and this is the check that keeps it there.
4. `pytest tests/unit` still collects eleven.

---

### Step 7 — Read one order with its driver, and list them

**File created:** `src/pizza/application/queries.py`, holding the frozen `OrderDetail`
(`order`, `driver | None`) and the two functions of R-e.

`get_order(uow, order_id)` is 6.5's two keyed reads: fetch the order, raise `OrderNotFound` if
absent, and fetch the driver only when `driver_id` is not `None`. `list_orders(uow)` returns
`uow.orders.list_all()` — one query, no driver, which is what keeps 6.5's decision valid for a
list (6.6). Neither commits (3.5).

**Definition of Done**

1. The file exists, with the content stated.
2. The five commands of §4 exit zero, and the layering command prints nothing.
3. `queries.py` contains no `commit`, and `OrderDetail` carries entities rather than a response
   shape — 6.5's "the core never sees this shape" checked where it could be broken.
4. `pytest tests/unit` collects eleven, and `git status --short` is clean.

---

## 7. Ordering, and where it is free

Three edges are forced, and the rest is chosen:

- **1 and 2 before 3.** `ports.py` names `Order` and `Driver` in its signatures.
- **3 before 4, 5 and 6.** Every use case takes a `UnitOfWork` and a `Clock`.
- **5 before 7.** `get_order` raises the `OrderNotFound` that step 5 creates.

Everything else is free, and is ordered for a reader rather than by dependency. **1 before 2**
because the order is the entity every later step touches, and 2 alone would leave the driver with
nothing to be busy for. **4 before 5 before 6** by increasing weight — 4 establishes the use case
shape on the two paths that only create, 5 adds the transaction that coordinates two entities and
the publish outside it, and 6 adds the claim. Reversing any of them would compile and pass.

No step depends on a step after it, and no step needs a file a later step creates.

## 8. What U3 hands to the units after it

- **U4 (12.6):** `tests/unit/` holds eleven tests, six of them the free core set. What remains
  for U4 is whatever 12.6 opens beyond free — and 12.6 is open, so U4 is not plannable yet. The
  three rows 5.7 marks unprovable (5.4, 5.8, and the coordination half of 5.6) are U10's, not
  U4's.
- **U5 (2.5, 4.5, 4.6, 8.9):** four `Protocol`s to implement, and three obligations the
  signatures carry rather than state. `claim_next_available_driver` returns a **locked and
  unmarked** driver — the marking is the use case's, in the same transaction. The `UnitOfWork`
  must be **re-enterable**, each `__enter__` opening a fresh session, because step 5 marks the
  outbox row after the commit. `list_all` is newest first. The outbox `payload` is written with
  U6's `serialize` (7.3), which is why that module imports stdlib only. **And one translation
  obligation:** `mark_published` raises `OutboxWriteFailed`, so the adapter converts its
  database library's exception rather than letting it through — the same duty U6 owes
  `PublishFailed`, and the reason `application/` never imports that library.
- **U6 (7.3):** `OrderReadyEvent` is importable from `pizza.application.events`, its
  `EVENT_TYPE` is a `ClassVar` rather than a field, and its three fields are `UUID`, `UUID`,
  `datetime`. `serialize` and `deserialize` take and return `bytes`, and neither may import
  anything from `entrypoints/`.
- **U7 (5.2, 6.1–6.3, 6.5):** two exceptions to map — `IllegalTransition` to `409` and
  `OrderNotFound` to `404` — as one registered handler in `entrypoints/api/errors.py`, per 3.1.
  `AdvanceOrderStatus` returns the updated `Order`; `GetOrder` returns an `OrderDetail` for 6.5
  to nest. **One thing to check rather than assume:** `PlaceOrder` returns a `UUID`, because
  4.7's sample does. If 6.1's `201` shape needs the entity, that is a return to Phase 2 over one
  line here, not a judgement U7 makes while wiring.
- **U8 (8.1, 8.3, 8.4):** `DispatchOutcome`'s three values are 8.1's cases 1 to 3, and case 4 is
  `give_up()` followed by an ack. The consumer decides exhaustion from the `x-death` entry for
  `pizza.orders.dispatch` with reason `rejected` (7.4); the core never learns the count. A
  missing order raises `OrderNotFound`, which is 8.4's to place.
- **U10 and U12:** nothing directly. The rules they exercise reach them through the API.

## 9. After the merge

`main` satisfies 14.7's U2 row unchanged — `ruff format --check .`, `ruff check .`,
`mypy src tests`, `python -c "import pizza"` and `pytest tests/unit` all exit zero on a clean
clone. The bar rises at U9, and the two layers this unit created still import nothing but the
standard library.
