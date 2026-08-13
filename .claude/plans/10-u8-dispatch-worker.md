# U8 — Dispatch worker · Implementation Plan

**Phase 3 of the planning protocol in `CLAUDE.md` §2, for the eighth unit in Part 4 of
`03-roadmap.md`.** Decisions are in `02-decisions.md`; nothing here decides anything that
belongs there. Where executing a step needed a call Phase 2 had not made, it is recorded below
under *Readings* rather than left to implementation.

**Gate.** U8's *Decided by* column reads topic 8 — all nine items, 8.1 to 8.9 — and every one is
`[decided]`. The topic closed in pull request #13 and 8.8 reversed in #14. *Depends on* reads U3, U5
and U6, all merged, and U7 (#15) is merged as well, so `pizza/log.py` and `TransactionFailed` are
already on `main`. **There was nothing to decide at this gate**, which is why this unit begins at
Phase 3.

Three open items are touched and none is decided here: 11.2, 11.9 and 11.11 own the Compose service,
the image's `CMD` and the restart policy that 8.8 hands them as requirements; 12.1 owns which
scenarios U10 writes; 12.7 owns how the test directories are invoked. Commit A below corrects a
decided record rather than resolving an open one; §3 states what it found.

---

## 1. What this unit delivers

Part 4 gives U8 the consumer loop, the ack/nack policy, retry and dead-letter handling,
poison-message handling, dispatch logging, and startup/shutdown. It is **the second and last
process**, and the one that closes the loop: after it, an event published by a `PATCH` reaches a
consumer, a driver is claimed, and the assignment is recorded.

**Almost all of it is one file.** `DispatchOrder` has existed since U3, both repositories and the
claim query since U5, the topology and the wire format since U5 and U6. What is missing is the thing
that turns an outcome into an acknowledgement — which is 8.1's whole content — and the process that
holds it.

**Two decided items land ahead of the entry point**, each touching code an earlier unit wrote:

| Item | What it requires | What is on `main` |
|---|---|---|
| [8.6](02-decisions.md) — the dispatch notification names the driver | `DispatchOrder` must report **who** took the order and **when** | it returns a `DispatchOutcome` alone, which names no driver |
| [8.4](02-decisions.md) — the decoding seam | `deserialize_or_none` beside `deserialize`, so the consumer names no infrastructure error | the module holds `serialize` and `deserialize` only |

They are steps 1 and 2 below — numbered work with their own Definitions of Done, not edits made in
passing while wiring. This is the same shape U7 found at its own gate, and the second row is there
because a record pointed the work at a unit that had already shipped; commit A is that correction.

## 2. What this unit deliberately does not deliver

Each line names the item that owns it, so nothing here is silence.

| Not built | Owner | Arrives in |
|---|---|---|
| A signal handler, a reconnect loop, a startup wait for the broker | 8.8 — reversed in #14: the worker retries nothing and handles no signal | not built |
| A parked or dead-letter queue holding an exhausted or undecodable message | 8.3, 8.4 | not built (FW5) |
| A second attempt counter of ours, in a header or in the payload | 7.4 — the broker's `x-death` entry is the budget | not built |
| A stored dispatch notification | 8.6 | not built (FW8) |
| A healthcheck or any HTTP surface on the worker | 8.8's note to 11.2 — the worker speaks no HTTP | not built |
| The Dockerfile, the Compose service, the restart policy and the `CMD` that launches this process | 11.1, 11.2, 11.9, 11.11 | U9 |
| Every assertion on dispatch, retry and exhaustion | 12.3 — the suite speaks HTTP and U10 owns it | U10 |
| A test that runs the callback against a live broker or a live database | 12.3 gives this repository no broker client and no database | not built |
| The README's note that scaling to N replicas needs no code change | 8.5 states it; 13.1 assembles the README | U13 |
| More than one worker replica, or a prefetch above 1 | 8.5, 10.4 | not built (FW7) |
| A correlation identifier carried from the API | 8.7 — correlation is `order_id` | not built (FW6) |

## 3. Branch, commits, and the merge

- **Branch:** `feat/u8-dispatch-worker`, cut from `main` at `028b7b9` (14.2).
- **Commits:** one planning commit, two record commits, then one commit per step (14.3, 14.4).
  Seven in total.
- **Merge:** one pull request, squash-merged, its title ending in `(#16)` (14.2, 14.3). The branch
  is not deleted (14.2).

| # | Type | Title |
|---|---|---|
| B | planning | `docs: plan the dispatch worker` |
| A | correction | `docs: correct where 8.4's decoding wrapper lands` |
| 1 | step | `feat: report who took the order, for the line the dispatch logs` |
| C | amendment | `docs: record why the wire format stays out of the application layer` |
| 2 | step | `feat: turn undecodable bytes into a value every caller must handle` |
| 3 | step | `feat: one attempt per message, and what to do with the message after it` |
| 4 | step | `feat: assemble the dispatch worker` |

**A is not a plan step, and it lands after B rather than before it.** The plan is written against
the corrected reading, so U6's and U5's precedent would have put the correction first; here the plan
was approved before the correction was, and the two texts say the same thing in either order.
8.4's *Realised in* line read *"U6 — the wrapper is part of 7.3's module and lands with the pair it
joins"*. That was written in pull request #13, and **U6 merged in #11, two merges earlier** — so the
record assigned work to a unit that had already shipped, and `deserialize_or_none` is on no branch.
U6's own plan had already filed it under U8, in the row *"The `try`/`except` around `deserialize` …
| 8.4 — open | U8"*, because 8.4 was still open when that document was written. A names U8 for the wrapper and states why, so the two documents
stop disagreeing; **nothing about the seam's shape changes** — the signature, the injection and the
reason the consumer may not name `SerializationError` are 8.4's and are untouched. It rides on this
branch rather than on a gate branch of its own, by the same ruling that placed U2's commit A, U3's
commits A to C, U5's commits A and C and U6's commit A. It carries the `docs/ai-log.md` row for the
same change (§6).

**C is not a plan step either, and it sits where it was raised.** Reviewing step 2 the developer
asked what `deserialize_or_none` buys, and whether `serialization.py` belongs in `application/`
given that it imports no broker library. Both halves of that hold — the wrapper is a consequence of
7.3's placement and of nothing else, and the module does pass 3.1's own test for core code — and
the placement survives on a different test, which 7.3 did not state. What was missing was the
justification rather than the decision, so it lands there and not here: step 2 points at it and does
not restate it.

## 4. The Definition of Done that applies to every step

14.7's U2 row still governs; **U8 raises no bar**, and the next raise is U9's. The five commands are
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
`pika` and `sqlalchemy` have been in `pyproject.toml` and in both requirements files since U1
(2.10), and the `pika.*` type-checker override has been there since U6. **`ruff check .` will not
catch the one layering rule that matters here:** `TID251` exempts all of
`src/pizza/entrypoints/*`, while 3.1 permits only `main.py` to import `infrastructure/`. Steps 3 and
4 therefore carry that check as a diff read, and §5's R-b is what makes it possible to satisfy.
**No documentation changes in this unit** — the README's operational sections are U9's and 13.1
assembles the rest in U13; the one document this unit writes is commit A's `docs/ai-log.md` row.

**Three of the four steps are verified by `mypy` and a diff read, and this is written into each
one.** 12.3 gives the integration suite HTTP only and makes U10 its owner, so nothing under
`entrypoints/worker/` is asserted by a test inside this unit. §5 admits one free unit test — step
3's — and the reason each other step has none is stated in its own Definition of Done rather than
left as a gap.

## 5. Readings — where this plan filled a silence

Recorded here rather than resolved silently (`CLAUDE.md` §2). The boundary is U1 §5's, restated in
U2, U3, U5, U6 and U7: a Phase 3 document may fill a silence Phase 2 left; it may not settle an
ambiguity inside a decided record. The one thing of the second kind is commit A, which corrects a
factual pointer rather than a judgement.

- **R-a — the settings are loaded inside `main()`, not at module import.** U7's R-a loaded at module
  level because `uvicorn` imports `pizza.entrypoints.api.main:app` and there is no earlier moment.
  The worker is launched as a module, so `main()` **is** the first thing that runs and the contract
  U2 §8 states — first action, one line on `stderr`, exit non-zero, no traceback — is reached
  without making the module unimportable. That is exactly `entrypoints/schema/main.py`'s shape, and
  it keeps 10.2's rule that nothing reads the environment at import time literally true for this
  file. `configure_logging(settings.log_level)` is the second statement, before anything can log.
- **R-b — `main.py` owns the connection and the subscription; `consumer.py` owns the callback.**
  3.1 permits `main.py` alone to import `infrastructure/`, and the subscription needs three things
  from there: `declare()`, `DISPATCH_QUEUE`, and `deserialize_or_none`. So the root opens the
  connection and the channel, declares, sets `basic_qos(prefetch_count=1)` (8.5), calls
  `basic_consume` and `start_consuming()`, and holds 8.8's three lines; the consumer receives the
  queue name and the decoder as constructor arguments and holds the message callback alone. **This
  is not the wiring 8.4 rejected** — that rejection was of a `try`/`except` around `deserialize`
  placed in `main.py`, which is logic; a connection built where every other adapter is built is
  composition, and it is the worker's counterpart of the API's `lifespan`.
  *Rejected:* giving `consumer.py` a `run()` that opens its own connection — it cannot, without
  either importing `topology` or receiving `declare` as a third injected callable, which is
  machinery for the same result.
- **R-c — `DispatchOrder` returns the assignment facts, and the consumer renders 8.6's line.** 8.6
  fixes the line as `event=dispatch_notification order_id=… driver_id=… driver_name=… at=…`, and
  `DispatchOutcome` names none of those. `__call__` therefore returns a frozen `DispatchResult`
  carrying the outcome and, on the assigned path, the driver's identifier and name and the instant
  written to the database; the three are `None` otherwise, which the docstring states. Nothing needs
  narrowing at the log site, because every field is rendered with `%s`. The values are read from the
  entities the transaction already holds — the repositories return plain dataclasses, not rows, so
  reading them after the commit costs no query and cannot refresh.
  *Rejected — `DispatchOrder` logging the line itself,* which needs no new type and has a precedent
  one file away in `AdvanceOrderStatus`. It was declined so that all eight of 8.7's lines sit in one
  file with their levels, which is what a reviewer checks that table against; and because the
  application layer's existing lines are prose (`"publish failed for order %s"`) rather than
  `event=` records, so a single `event=` line there would put two log styles side by side in one
  layer — the inconsistency between files that `CLAUDE.md` §6 names.
  **Named rather than dressed up:** this is the closer call of the two, and the reversal cost is one
  return type either way.
- **R-d — the retry budget is read from the header mapping, by a module-level function taking a
  plain `Mapping`.** 7.4 gives the budget to the `x-death` entry for `pizza.orders.dispatch` with
  reason `rejected`, and warns that the wait queue's `expired` entry advances in step with it, so
  summing the two halves the budget in silence. `rejection_count(headers, queue) -> int` scans for
  the one entry and returns `0` when the header is absent, which is a first delivery. It takes the
  mapping rather than the `pika` properties object so that a unit test can call it with a
  dictionary and reach no library at all — the same reason U6 exposed `wait_queue_arguments()`.
  *Two facts checked in pika 1.4.4 rather than assumed:* `BasicProperties.headers` is `None` when
  the message carries no header table, so the absent case is a `None` and not an empty dict; and
  long strings inside a field table are decoded to `str`, so `queue` and `reason` compare against
  our own `str` constants without a decode. The count is returned through `int(...)`, because `pika`
  ships no type information and `strict` mode's `warn_return_any` rejects returning the `Any` a
  subscript of it produces.
- **R-e — one `DispatchOrder` is built for the process and re-entered per message.** U7 §8 handed
  this forward and this is the shape it names: 8.5 runs one consumer at prefetch 1 on the main
  thread, so there is no second thread to overwrite the transaction the API's R-b was written
  against. `SqlAlchemyUnitOfWork` opens a `Session` on each `__enter__` and closes it on each
  `__exit__` — its module docstring states that the same instance can be used again — so a use case
  built once behaves per message exactly as a fresh one would. No factory reaches the consumer, and
  the consumer could not call one anyway: 3.1 forbids it to name the concrete unit of work.
- **R-f — `start_consuming()` returning is treated as a lost subscription and exits non-zero.** 8.8
  states that the worker has **no exit path that returns `0`**, and 11.11 rests on it. Read from
  `BlockingChannel._dispatch_events` in pika 1.4.4 rather than assumed: a `Basic.Cancel` from the
  broker — a queue deleted under the consumer — removes the consumer record, and `start_consuming`'s
  `while self._consumer_infos` loop then ends **without raising**. `main()` would fall off its end
  and exit `0`, and an `on-failure` restart policy would leave a dead container reporting success.
  The root therefore logs `event=broker_connection_lost` and raises `SystemExit(1)` after the call
  returns. 8.7's table gets no ninth line: the subscription being gone is what that line names.
- **R-g — the worker sets no timeout fields on `URLParameters`.** 7.7's three parameters are fed
  from `PIZZA_BROKER_PUBLISH_TIMEOUT_SECONDS`, which 10.1 lists as read by the api alone, and they
  exist to bound a `PATCH` that a person is waiting on. The worker has no caller to bound: 8.8's
  answer to any broker failure is to log one line and exit, and the wait before it is the library's
  own default rather than a number this plan would have to derive.
  *What that leaves in force, stated because 7.7 raises it:* heartbeats stay at pika's default and
  are serviced continuously, since the process sits inside `start_consuming()` — 7.7's stated
  asymmetry with the publisher, and the reason no reconnect exists on this side.
- **R-h — the callback's `except Exception` covers `give_up()` as well as the attempt.** 8.4 puts
  "any other exception" into a class that rejects unboundedly, and says in the same record that the
  exhaustion path is not a special case: with the database down, `give_up()` raises into that class
  and the message keeps circling. So the whole business section — the attempt, the branch on the
  outcome, and the `give_up` the exhausted branch calls — sits inside one `try`, and only the
  acknowledgement itself is outside it. The handler logs the traceback and rejects; it swallows
  nothing, which is the narrowness `CLAUDE.md` §6 requires of a catch this wide.
- **R-i — 8.9's lock ordering is already satisfied on `main`, and this unit checks it rather than
  builds it.** 6.9 handed 8.9 an inversion — the API locks an order and may then touch a driver,
  while the claim locks a driver and then updates an order — and 8.9 records it as unreachable
  *"which rests on `dispatch_order` reading the order before claiming a driver. U8 implements that
  order deliberately; it is not free."* U3 already wrote it in that order, and the order read is
  `get()` rather than `get_for_update()`, so the dispatch path takes exactly one row lock. Step 1
  touches that method and step 1's diff read is where the property is verified.

## 6. Steps

### Step 1 — Report who took the order, for the line the dispatch logs

**File changed:** `src/pizza/application/use_cases/dispatch_order.py`.

`DispatchResult` is added beside `DispatchOutcome` as a frozen dataclass, and `__call__` returns it
instead of the bare outcome (R-c):

```python
@dataclass(frozen=True)
class DispatchResult:
    outcome: DispatchOutcome
    driver_id: UUID | None = None
    driver_name: str | None = None
    at: datetime | None = None
```

The assigned path fills all four fields from the driver it claimed and the instant it wrote; the
other two return the outcome alone. `give_up()` is unchanged, and no rule moves — the use case still
decides nothing about acknowledgement and logs nothing.

**Definition of Done**

1. The type exists, the signature and the docstring state what comes back, and the three fields are
   set on the assigned path and only there.
2. The five commands of §4 exit zero.
3. `pytest tests/unit` still collects seventeen. **No test is added, and the reason is written
   rather than left as a gap:** this is a return type, which `mypy` verifies at the one call site
   step 3 writes, and the only assertion a unit test could make — that the driver reported is the
   driver claimed — needs a fake `UnitOfWork` written to observe it. 12.3 puts the real assertion in
   U10, where a dispatched order answers `GET /orders/{id}` with that driver nested.
4. Read from the diff: the order is still read before the driver is claimed and still read with
   `get()` (R-i); the assignment is still one transaction; `advance_order_status.py`,
   `place_order.py`, `register_driver.py` and `queries.py` are untouched.

---

### Step 2 — Turn undecodable bytes into a value every caller must handle

**File changed:** `src/pizza/infrastructure/broker/serialization.py`.

8.4's third function joins the pair it belongs to:

```python
def deserialize_or_none(raw: bytes) -> OrderReadyEvent | None:
    """Build an event, or return None when the bytes do not describe one."""
```

It calls `deserialize` and converts `SerializationError` — one declared type, and nothing wider —
into `None`. That is the seam 7.7 required, 8.4 shaped and 7.3 justifies: the consumer may not import
`SerializationError`, and a signature returning `… | None` forces every caller to handle the case,
so a bug of ours passes through into 8.4's third class instead of being swallowed here.

**Definition of Done**

1. The function exists, with the signature and the single narrow `except` stated.
2. The five commands of §4 exit zero.
3. `pytest tests/unit` still collects seventeen. **No test:** `test_serialization.py` already
   asserts that five kinds of malformed input — invalid UTF-8, truncated JSON, a missing field, an
   unparseable identifier and a naive timestamp — all leave as `SerializationError`, and this
   wrapper's whole content is the conversion of that one type to `None`. A test of it would assert
   that `except` catches what it names.
4. Read from the diff: `serialize` and `deserialize` are unchanged, and the module still imports
   only the standard library and `application/events.py`.

---

### Step 3 — One attempt per message, and what to do with the message after it

**Files created:** `src/pizza/entrypoints/worker/__init__.py`,
`src/pizza/entrypoints/worker/consumer.py`, `tests/unit/test_rejection_count.py`.

`consumer.py` holds two things and no more.

**`rejection_count(headers, queue) -> int`** per R-d — 7.4's budget, read from the one `x-death`
entry whose `queue` matches and whose `reason` is `rejected`, `0` when there is no header.

**`DispatchConsumer`**, constructed with the use case, the decoder, the queue name and the cap, and
carrying one public method — the `pika` callback, whose four parameters are fixed by the library:

```python
def on_message(self, channel, method, properties, body) -> None
```

Its body is 8.1's four cases and 8.4's three classes, resolved into **two dispositions**:

| Case | Line (8.7) | Disposition |
|---|---|---|
| the bytes do not decode | `event=poison_message body=…` · `ERROR` | `basic_ack` |
| `OrderNotFound` | `event=order_not_found order_id=…` · `ERROR` | `basic_ack` |
| assigned | `event=dispatch_notification order_id driver_id driver_name at` · `INFO` | `basic_ack` |
| nothing to do | — | `basic_ack` |
| no driver, budget remaining | `event=no_driver_available order_id attempt` · `WARNING` | `basic_reject(requeue=False)` |
| no driver, budget spent | `event=dispatch_failed order_id` · `ERROR`, after `give_up()` | `basic_ack` |
| any other exception | `event=dispatch_error order_id`, with the traceback · `ERROR` | `basic_reject(requeue=False)` |

The undecodable case is answered before anything else, because it is the one case with no
`order_id` to correlate on; its body is truncated to **200 bytes and logged as `repr`** (8.7), which
shows a whole well-formed message and the head of anything larger, and does not decode input that
may be malformed UTF-8. Everything after it runs inside one `try` per R-h, and the acknowledgement
is the only statement outside it. `attempt=` is `rejection_count + 1`, so the first delivery reads
`attempt=1`; with 10.4's cap of 8 the last `no_driver_available` line reads `attempt=8` and the
ninth delivery gives up — nine attempts, eight waits, the 64 seconds 10.4 wrote in words so that
this step would not choose.

**File created:** `tests/unit/test_rejection_count.py`, **one test**, free by 5.7's standard — pure
logic, no infrastructure, no double.

| Test | What it asserts | Why it earns its place |
|---|---|---|
| `test_only_rejections_from_the_dispatch_queue_count` | no header is `0`; a header carrying both `x-death` entries returns the `rejected` count from the dispatch queue, not the sum and not the wait queue's `expired` count | This number **is** the retry budget (7.4), and 7.4 names the hazard in the record: the two entries advance together and show the same value, so summing them halves the budget and matching the wrong one doubles or empties it. Every wrong answer still produces truthful log lines — the order is genuinely unassigned — so the fault surfaces as a demo that gives up too early or never gives up, not as an error anyone can locate. It is also the only assertion in this unit no HTTP scenario can make cheaply: F7 observes the budget by waiting out 10.4's 64 seconds |

**Definition of Done**

1. The three files exist, with the content stated. `DispatchConsumer` has one public method.
2. The five commands of §4 exit zero.
3. `pytest tests/unit` collects **eighteen** — the seventeen on `main`, and this one.
4. Read from the diff: this module imports `pika`, `application/` and `domain/errors` and **nothing
   from `infrastructure/`** — the rule `ruff` cannot enforce here (§4); every path through
   `on_message` ends in exactly one `basic_ack` or one `basic_reject`, which is what 8.4 answers
   "can a poison message block the queue" with; `requeue=True` appears nowhere (8.1); no status,
   transition or eligibility rule is re-implemented — the consumer branches on the outcome the use
   case returns.
5. `logger` is `logging.getLogger(__name__)` and no handler or level is configured here — 8.7 gives
   both to `configure_logging`, which U7 built and step 4 calls.

---

### Step 4 — Assemble the dispatch worker

**File created:** `src/pizza/entrypoints/worker/main.py`.

The composition root, and the second entry point in the system. Everything in it is a construction,
a registration, or one of 8.8's three exits:

```
def main() -> None:
    settings = load_service_settings(os.environ)      # R-a; on ConfigurationError,
    configure_logging(settings.log_level)             # stderr and exit 1

    engine   = create_engine(settings.database_url, pool_pre_ping=True)   # U5 §8, 8.8
    factory  = sessionmaker(engine, autoflush=False, expire_on_commit=False)
    consumer = DispatchConsumer(
        dispatch=DispatchOrder(SqlAlchemyUnitOfWork(factory), SystemClock()),   # R-e
        decode=deserialize_or_none,                                             # 8.4's seam
        queue=DISPATCH_QUEUE,
        max_retries=settings.dispatch_max_retries,
    )

    connection = BlockingConnection(URLParameters(settings.broker_url))   # R-g, no timeouts
    channel    = connection.channel()
    declare(channel, settings.dispatch_retry_delay_seconds)               # 7.1, 7.7
    channel.basic_qos(prefetch_count=1)                                   # 8.5
    channel.basic_consume(DISPATCH_QUEUE, consumer.on_message)
    logger.info("event=worker_ready")                                     # 8.8
    channel.start_consuming()
```

**The three exits, and no fourth.** A connection that cannot be opened logs
`event=broker_unreachable` and exits `1`; a connection lost inside `start_consuming()` logs
`event=broker_connection_lost` and exits `1`; `start_consuming()` returning at all logs the same
second line and exits `1` per R-f. Both catches name `(AMQPError, OSError)` — U6's R-e, for the
same reason and no wider. `SIGTERM` takes Python's default disposition and is not caught (8.8), so
the process dies where it stands and 7.4 redelivers the unacknowledged message. No `engine.dispose()`
and no `connection.close()`: there is no path on which the process continues past either.

The module ends with `if __name__ == "__main__": main()`, as `entrypoints/schema/main.py` does, so
11.9's exec-form `CMD` has a module to run.

**Definition of Done**

1. The file exists, with the content stated.
2. The five commands of §4 exit zero.
3. `pytest tests/unit` still collects eighteen. Everything here needs a broker, a database, or a
   broker that fails in a particular way; 12.3 owns all of it and U10 writes what it can reach.
4. `PIZZA_…= python -c "import pizza.entrypoints.worker.main"` with a complete environment succeeds
   with no database and no broker running — the module performs no I/O at import, which is what R-a
   buys and what `python -c "import pizza"` cannot show.
5. Running the module with an **incomplete** environment prints one `invalid configuration:` block
   on `stderr` and exits `1`, with no traceback (U2 §8's contract, checked rather than assumed).
   Running it with a complete environment and **no broker** prints one `event=broker_unreachable`
   line and exits non-zero — 8.8's first exit, and the only one observable before U9.
6. Read from the diff: this is the **second and last** module under `entrypoints/` importing
   `infrastructure/` (3.1); no `async def` appears anywhere under `src/pizza/` but the API's
   `lifespan` (2.4); `prefetch_count=1` is written here and nowhere else; nothing in this file
   catches a domain error or decides an acknowledgement.

## 7. Ordering, and where it is free

Two edges are forced and everything else follows from them.

- **1, 2 → 3:** the callback branches on `DispatchResult` and calls the decoder through the
  signature step 2 gives it.
- **3 → 4:** the root constructs `DispatchConsumer` and passes it `deserialize_or_none` and
  `DISPATCH_QUEUE`.

Steps 1 and 2 are independent of each other and could be taken in either order; they are numbered as
they are so that the two items of §1 sit in the order that table lists them. **No step depends on a
step after it, and no step needs a file a later step creates** — each of steps 1 to 3 type-checks on
its own even though nothing runs until step 4.

## 8. What U8 hands to the units after it

- **U9 (11.9):** the image runs `python -m pizza.entrypoints.worker.main` in **exec form** — 8.8's
  requirement, and the reason is that `sh` would not forward `SIGTERM`. There is no port, no
  healthcheck and no endpoint to probe (8.8's note to 11.2).
- **U9 (11.11):** **every exit of this process is non-zero** — the three in step 4, and `143` for a
  signal. The restart policy must restart on failure, and R-f is what closes the one path pika would
  otherwise have returned `0` on.
- **U9 (11.2):** the worker needs `depends_on` on the schema service (4.6) and needs none on the
  broker for correctness — it will exit and restart a handful of times while RabbitMQ boots, which
  is legibility and 11.2's to weigh. It touches neither dependency before `main()` runs.
- **U9 (10.1):** the service supplies all six `PIZZA_` service variables; it reads five of them and
  carries `PIZZA_BROKER_PUBLISH_TIMEOUT_SECONDS` unread, which 10.1 accepted and stated.
- **U10 (12.3, 12.1):** everything this plan marks "read from the diff" becomes observable over
  HTTP. The assignment scenario proves the whole path — publish, topology, consume, claim, ack —
  and F7's exhaustion proves 8.2's cycle and 8.3's terminal state, at the cost of 10.4's 64 seconds.
  **8.6's log line is not an assertion target**, which 8.6 states in its own words: what a test
  asserts is that the driver is `BUSY`, the order `ASSIGNED`, and the driver nested in
  `GET /orders/{id}`.
- **U13 (13.1, 8.5):** the README says that scaling to N replicas requires no code change — 8.9
  makes the claim safe rather than the replica count, and FW7 records what running several would
  actually buy.
- **U12:** nothing directly.

## 9. After the merge

`main` satisfies 14.7's U2 row unchanged — the five commands of §4 all exit zero on a clean clone,
with **eighteen** unit tests. The bar rises at U9.

The system is now complete as code and cannot be started: both processes exist, every port has one
implementation, and there is no image, no Compose file and no command — which is exactly U9's
content. Every business rule still lives in `domain/`, and `domain/` and `application/` still import
nothing but the standard library and each other.
