# U6 — Broker adapter · Implementation Plan

**Phase 3 of the planning protocol in `CLAUDE.md` §2, for the sixth unit in Part 4 of
`03-roadmap.md`.** Decisions are in `02-decisions.md`; nothing here decides anything that
belongs there. Where executing a step needed a call Phase 2 had not made, it is recorded below
under *Readings* rather than left to implementation.

**Gate.** U6's *Decided by* column reads 2.1, 2.7, 7.1 and 7.3–7.7. All are `[decided]`, and topic
7 closed whole in pull request #7 from `plan/u6-gate` — that branch is squash-merged and its head
is not an ancestor of `main`, so nothing is reopened or merged from it. *Depends on* reads U2, U3
and U5, all merged, so the three dependencies are real rather than nominal. **There was nothing to
decide at this gate**, which is why this unit begins at Phase 3.

Four open items are touched and none is decided here: 8.4 owns what happens to a malformed message,
8.7 owns the log's handler, format and level, 8.8 owns startup waiting and shutdown, and 12.7 owns
how the test directories are invoked. Commit A below amends a decided record rather than resolving
an open one; §3 states what it found.

---

## 1. What this unit delivers

Part 4 gives U6 three things: the topology declaration (7.1), the publisher implementation (7.5,
7.6) and the connection lifecycle (7.7).

That is **the last of the driven adapters**. After this unit every `Protocol` in
`application/ports.py` has an implementation the type checker has verified, and `infrastructure/`
is complete in both of its halves — `db/` from U5, `broker/` from U5's serialization module and
this unit's two. What is still missing is a **process**: nothing constructs an adapter, nothing
calls a use case, and no message moves. U7 is the first unit that runs anything.

It is also the first code in the repository to import `pika`, which is what makes step 1 the step
that teaches the type checker about an untyped dependency (2.7).

## 2. What this unit deliberately does not deliver

Each line names the item that owns it, so nothing here is silence.

| Not built | Owner | Arrives in |
|---|---|---|
| `broker/serialization.py` — imported, not written | 7.3, as U5's commit A filed it: *Realised in:* U5 (the module), U6 (the wire) | already on `main` |
| The consume loop, `basic_qos`, `basic_consume`, the ack/nack policy, and reading the `x-death` header | 7.7's consumer half, 8.1, 8.3, 7.4 | U8 |
| The `try`/`except` around `deserialize`, which 7.7 requires to sit on the infrastructure side of 3.1's seam | 8.4 — open | U8 |
| The composition roots that construct the publisher and close it at shutdown | 3.1 places them; 7.7 fixes the lifespan hook's two duties | U7, U8 |
| How long to wait for the broker at startup, at what cadence, and how to shut down without losing an in-flight message | 8.8 — open. 7.7 fixed only that reconnection exists and what it consists of | U8 |
| Logging configuration — handler, format, level. **This unit logs nothing** | 8.7 — open | U8 |
| The Compose services and the broker's healthcheck | 11.1, 11.2 — open | U9 |
| Any test that reaches a broker | 12.3 — the suite speaks HTTP and holds no broker client | U10 |
| The README's operational note on `PRECONDITION_FAILED` | 7.1 carries it to the README, and its repair names a Compose environment this unit does not create | U9 or U13 |
| A bounded wait for the publisher confirm | FW17, written by commit A | not built |
| A relay over unpublished outbox rows | A23, FW2 | not built |

## 3. Branch, commits, and the merge

- **Branch:** `feat/u6-broker-adapter`, cut from `main` at `f435fac` (14.2).
- **Commits:** one amendment commit, one planning commit, then one commit per step (14.3, 14.4).
  Four in total.
- **Merge:** one pull request, squash-merged, its title ending in `(#11)` (14.2, 14.3). The branch
  is not deleted (14.2).

| # | Type | Title |
|---|---|---|
| A | amendment | `docs: bound the whole connection bring-up, and file the unbounded wait as future work` |
| B | planning | `docs: plan the broker adapter` |
| 1 | step | `feat: declare the topology both services will find already there` |
| 2 | step | `feat: publish the event, and once more on a fresh connection` |

**A is not a plan step.** It amends a record rather than filling a silence — the boundary U2 §5
drew and 14.7 stated first — and it rides on this branch rather than on a gate branch of its own,
by the same ruling that placed U2's commit A, U3's commits A to C and U5's commits A and C. **A
precedes B** because B is written against the corrected record.

*What A changed, and it is the same shape as U5's commit C — a decided expression the chosen
library does not support.* 7.7 named `socket_timeout` and `blocked_connection_timeout` as the two
parameters bounding a publish in time, and gave the first of them "connection establishment and
socket operations". In pika 1.4.4 `socket_timeout` is documented as the `socket.connect()` timeout
alone; the whole TCP-then-handshake-then-channel bring-up is bounded by a third parameter,
`stack_timeout`, whose default is 15 s. A broker answering the TCP connect and then stalling the
handshake would therefore have held a `PATCH` for 30 s against the 10 s 7.5 promises. All three
parameters are now fed from 10.4's single timeout; **no variable is added and 10.4 is untouched.**

A also files **FW17**: nothing we can configure bounds the wait for a publisher confirm on a
connection that is established and then goes quiet, and Part 5 is where §7 requires a deliberate
exclusion to be stated.

## 4. The Definition of Done that applies to every step

14.7's U2 row still governs; **U6 raises no bar**, and the next raise is U9's. The five commands
are run from the activated virtual environment at the repository root, and each must exit zero
**at every step commit**:

```
ruff format --check .
ruff check .
mypy src tests
python -c "import pizza"
pytest tests/unit
```

Each step below adds its own checks on top of these. A step is done when §8's six conditions hold.

*Three mechanical notes so no step improvises.* **No dependency is added by this unit and neither
lock file changes** — `pika==1.4.4` is already in `pyproject.toml` and in both requirements files,
approved with the whole list at U1 (2.10). **`ruff check .` permits `import pika` here and would
not permit it one directory inward:** U5's step 1 banned it through `TID251` and lifted the ban for
`src/pizza/infrastructure/*`, so the layering rule is enforced by the linter rather than by this
plan. And **`mypy src tests` fails on the first `import pika` until step 1 adds the override** —
verified against the installed package rather than predicted: pika 1.4.4 ships no `py.typed`
marker, so the checker reports `import-untyped`.

## 5. Readings — where this plan filled a silence

Recorded here rather than resolved silently (`CLAUDE.md` §2). The boundary is U1 §5's, restated in
U2 §5, U3 §5 and U5 §5: a Phase 3 document may fill a silence Phase 2 left; it may not settle an
ambiguity inside a decided record. The one thing of the second kind became commit A before this
document existed.

- **R-a — the `pika` type-checker override rides in step 1 rather than in a step of its own.** U5's
  step 1 earned a step because the code its rule governs arrived two steps later, and a rule added
  afterwards would have left that unit's own imports as the only ones it never guarded. Here the
  override's subject is the very import step 1 writes, so a separate commit would carry
  configuration with no subject and a Definition of Done nothing could verify. Its scope is
  `module = "pika.*"` per 2.7, and 2.8 owns the form: a per-module `ignore_missing_imports`, never
  a loosening of `strict`.
- **R-b — each adapter names its `Protocol` as a base class.** U5's R-b, unchanged and for the same
  reason: `PikaEventPublisher(EventPublisher)` makes `mypy` compare the class to the port at its
  definition rather than only where a composition root assigns it, which is U7's file.
- **R-c — the three timeout fields are set on a `URLParameters` instance.** 10.1 supplies
  `broker_url` as one string, so the adapter builds `pika.URLParameters(url)` rather than
  `ConnectionParameters(host=…, port=…)`. Both are subclasses of `pika.connection.Parameters` and
  both carry the three fields as settable properties — checked against pika 1.4.4, which is also
  the reading commit A's amendment is written in.
- **R-d — a failure to open the **first** connection is final, and is not the retry 7.5 grants.**
  That record grants a retry to "a publish that fails on an **established** connection … after
  reconnecting", and says in the same breath that "failure to establish the new connection is
  final". A lazy first open that fails is the second sentence, not the first: there is nothing to
  reconnect **from**, and the failure the retry exists to repair — 7.7's connection that the broker
  closed while the API sat idle — cannot be present on a connection being opened for the first
  time. Retrying it would repeat an identical attempt with nothing changed in between, and would
  cost two connection timeouts instead of one on the likeliest first-publish failure, a broker that
  is not up yet. The publisher therefore branches on whether it already holds a channel, and that
  branch **is** 7.5's distinction expressed rather than a rule of this plan's own.
- **R-e — the publisher catches `(AMQPError, OSError)` and nothing wider.** `AMQPError` is the root
  of pika's connection and channel errors, `UnroutableError` (7.1's `mandatory=True`) and
  `NackError` among them. `OSError` is added because pika unwraps a transport-setup failure to the
  exception underneath it, which can be an `OSError` rather than an `AMQPError` — read from
  `_reap_last_connection_workflow_error` in pika 1.4.4, not assumed. Two named families, not the
  `except Exception` §6 rejects.
- **R-f — `declare()` takes the retry delay as an argument; no module under `infrastructure/` reads
  configuration.** This is U5 §8's rule for the database adapters ("the adapters take a factory and
  a session, never a URL"), applied here. U2 §8 left "which process declares the topology, and
  therefore reads the delay" to 7.1, and 7.1's answer is both — so each composition root passes the
  value from the `ServiceSettings` it already loads.
- **R-g — the seconds-to-milliseconds conversion is exposed as `wait_queue_arguments()`, so that a
  test can see it.** 10.4's `dispatch_retry_delay_seconds` is in seconds and `x-message-ttl` is in
  milliseconds, a seam U2 §8 handed forward explicitly. A missing factor of 1000 burns the whole
  64-second retry budget in 64 milliseconds while every log line stays truthful — "no driver
  available" — so the fault presents as a demo that cannot recover rather than as an error.
  Building the wait queue's arguments in a named function is what gives that arithmetic a caller a
  unit test can reach.
  *Asked and answered rather than assumed:* whether the variable should simply be in milliseconds,
  which would delete the conversion instead of testing it. It stays in seconds — `.env.example` is
  read by a person, 10.4 chose `8 × 8 = 64 s` for "one number to remember", and a second unit of
  measure in that file costs more than one multiplication at the boundary where the unit genuinely
  changes. Computing it inside `config.py` was rejected with it: that module is a general input
  boundary, and it would have to know what RabbitMQ measures in.
- **R-h — the publisher declares the topology on every connection it opens, the first included.**
  7.7 spells this out for the reconnect and for the consumer. For the publisher's first connection
  it follows from 7.1: publishing to an exchange that does not exist closes the channel with a 404,
  so the API must declare before it publishes, not only after a reconnect.
- **R-i — the publisher logs nothing.** 7.6 places the single `ERROR` line in `AdvanceOrderStatus`,
  where U3 already wrote it. An adapter that logged as well would record one failure twice and
  would settle 8.7's level by accident, in a unit that does not own it.
- **R-j — `close()` exists on the concrete class only, and is best-effort.** 3.4 fixes "no
  lifecycle on `EventPublisher`", so the port keeps its one method and the composition root, which
  holds the concrete type (3.1), calls `close()` from the lifespan hook. Closing a connection that
  is already closed raises `ConnectionWrongStateError`, which is not a failure of shutdown, so it
  is swallowed at that one call — the same narrowness R-e requires everywhere else.

## 6. Steps

### Step 1 — Declare the topology both services will find already there

**File changed:** `pyproject.toml`. **Files created:**
`src/pizza/infrastructure/broker/topology.py`, `tests/unit/test_topology.py`.

`pyproject.toml` gains the override R-a describes:

```toml
[[tool.mypy.overrides]]
module = ["pika.*"]
ignore_missing_imports = true
```

`topology.py` holds 7.1's four objects. The six names are module-level constants and this is the
only place they appear:

```python
ORDERS_EXCHANGE      = "pizza.orders"
DISPATCH_QUEUE       = "pizza.orders.dispatch"
RETRY_EXCHANGE       = "pizza.orders.retry"
WAIT_QUEUE           = "pizza.orders.dispatch.wait"
ORDER_READY_KEY      = "order.ready"
ORDER_READY_WAIT_KEY = "order.ready.wait"
```

`wait_queue_arguments(retry_delay_seconds: int) -> dict[str, object]` returns the wait queue's
three arguments per R-g — `x-message-ttl` in milliseconds, and the dead-letter pair that returns an
expired message to `ORDERS_EXCHANGE` on `ORDER_READY_KEY`.

`declare(channel: BlockingChannel, retry_delay_seconds: int) -> None` declares 7.1's table in
order: both exchanges as `direct` and `durable=True` (7.4); the dispatch queue `durable=True`,
carrying the dead-letter pair that sends a rejection to `RETRY_EXCHANGE` on `ORDER_READY_WAIT_KEY`;
its binding on `ORDER_READY_KEY`; the wait queue `durable=True` with `wait_queue_arguments(...)`;
its binding on `ORDER_READY_WAIT_KEY`. It is idempotent by construction — that is 7.1's reason for
having both services call it — and it is the whole of what closes 8.2's cycle.

**File created:** `tests/unit/test_topology.py`, **one test**, free by 5.7's standard — pure logic,
no infrastructure, no double.

| Test | What it asserts | Why it earns its place |
|---|---|---|
| `test_the_wait_queue_holds_a_message_for_the_configured_delay` | `wait_queue_arguments(8)["x-message-ttl"] == 8000` | The one unit boundary in the unit: 10.4 configures seconds, RabbitMQ reads milliseconds (U2 §8). Without the factor the 64-second retry budget expires in 64 milliseconds, and nothing looks broken — every log line still reads "no driver available", so the fault surfaces as a demo that cannot recover rather than as an error anyone can locate |

**Definition of Done**

1. The three files exist or are changed, with the content stated.
2. The five commands of §4 exit zero. `mypy src tests` passing is the substantive check on the
   override: without it the first `import pika` fails, which was verified against pika 1.4.4 before
   this step was written.
3. `pytest tests/unit` collects sixteen tests — the fifteen on `main`, and this one.
4. **No test asserts what `declare()` sends, and the reason is written rather than left as a gap.**
   A fake channel recording calls would assert that the code calls what it calls, which §5 rules
   out as testing an implementation detail; a real declaration needs a broker, which 12.3 gives no
   test in this repository. The cycle is exercised end to end by U10's exhaustion scenario over
   HTTP.
5. `topology.py` imports `pika` and the standard library only. It names transport objects and
   knows nothing about events — no import from `application/` or `domain/` appears in it.

---

### Step 2 — Publish the event, and once more on a fresh connection

**File created:** `src/pizza/infrastructure/broker/publisher.py`.

`PikaEventPublisher`, naming `EventPublisher` as its base per R-b, constructed with
`(broker_url: str, publish_timeout_seconds: float, retry_delay_seconds: int)`. **The third argument
is not decoration:** 7.7's reconnect re-declares the topology, and `declare()` needs the TTL. It
holds a `threading.Lock` (7.7) and a connection and channel that are `None` until the first
publish — construction performs no I/O, which is what lets 7.7 keep startup free of the broker.

`publish(event)` serializes outside the lock, because `serialize` is pure and reaches nothing, then
takes the lock for the whole operation — send, confirm, and reconnect-and-retry — exactly as 7.7
requires:

```
body = serialize(event)
with self._lock:
    if self._channel is None:          # nothing established: R-d, no retry
        self._open()
        self._send(body)
    else:
        try:
            self._send(body)
        except (AMQPError, OSError):   # 7.5's single retry, after reconnecting
            self._reconnect()
            self._send(body)
```

Every failure above leaves as `PublishFailed` with the pika error chained — the translation duty
U5 §8 named as the twin of `OutboxWriteFailed`, and the reason `application/` never imports a
broker client.

- `_open()` builds `URLParameters` and sets the three timeout fields from `publish_timeout_seconds`
  (R-c, and commit A's amendment), opens a `BlockingConnection`, opens a channel, calls `declare()`
  per R-h, then `confirm_delivery()`. `connection_attempts` is left at its default of 1.
- `_reconnect()` closes the old connection best-effort and calls `_open()` — 7.7's list, in its
  order.
- `_send(body)` is one `basic_publish` to `ORDERS_EXCHANGE` on `ORDER_READY_KEY`, with
  `mandatory=True` (7.1) and properties `content_type="application/json"` (7.3) and
  `delivery_mode` persistent (7.4).
- `close()` per R-j.

Heartbeats are left at pika's default, which 7.7 decided and explained: an idle publisher's
connection **is** expected to be closed by the broker, and the retry above is what makes that
invisible to the caller.

**Definition of Done**

1. The file exists, with the content stated.
2. The five commands of §4 exit zero. `mypy` passing is the substantive check here: with R-b the
   class is compared to `EventPublisher` method by method, so **every `Protocol` in
   `application/ports.py` now has an implementation the checker has verified** — the last of what
   U3's step 3 deferred and U5's step 8 half-completed.
3. `pytest tests/unit` still collects sixteen. Every path in this file needs a live broker, and
   12.3 puts the assertions in U10: the assignment scenario proves a message left, arrived and was
   consumed, which is this file working end to end.
4. Read from the diff at the step, because no test can see any of it before U10: the lock covers
   send, confirm and reconnect-and-retry; `_send` can run at most twice per call, so the retry is
   exactly once (7.5); no `except Exception` appears; the three timeout fields are set and
   `connection_attempts` is not.
5. `python -c "import pizza.infrastructure.broker.publisher"` succeeds with no broker running,
   which is 7.7's "startup touches the broker not at all" checked at the only level available
   before U7.

## 7. Ordering, and where it is free

One edge is forced and there is nothing else to order: **1 before 2.** The publisher imports
`declare`, `ORDERS_EXCHANGE` and `ORDER_READY_KEY` from `topology.py`, and the type-checker
override must exist before the first `import pika` or step 1's own Definition of Done cannot pass.

No step depends on a step after it, and no step needs a file a later step creates.

## 8. What U6 hands to the units after it

- **U7 (3.1, 7.7):** the composition root builds
  `PikaEventPublisher(settings.broker_url, settings.broker_publish_timeout_seconds,
  settings.dispatch_retry_delay_seconds)` — three values, never the settings object, and no I/O —
  and calls `close()` in the ASGI lifespan's shutdown half. **The adapter is thread-safe by its own
  lock**, so nothing at the root serialises access to it and one instance serves every request.
- **U7 (7.6):** a failed publish raises `PublishFailed` and nothing else escapes.
  `AdvanceOrderStatus` already catches exactly that and returns the updated order, so the `200` on
  an unreachable broker needs no router code.
- **U8 (7.1, 7.7):** `declare(channel, retry_delay_seconds)` is the same function, called on the
  worker's own connection before `basic_consume`, and the six constants are importable from
  `topology.py`. **U6 sets no `basic_qos`** — 8.5's prefetch governs a consumer and this unit has
  none.
- **U8 (8.8):** the reconnect here is one attempt on the publish path and **must not be read as a
  startup-retry loop**. 7.7 fixed that reconnection exists and what it consists of; how long to
  wait for a broker at startup and at what cadence is still 8.8's, and unanswered.
- **U8 (8.4):** `deserialize` and `SerializationError` are already on `main` in
  `broker/serialization.py`. This unit adds no consumer-side decoding and leaves 7.7's constraint —
  that the `try`/`except` sits on the infrastructure side of 3.1's seam — exactly where it was.
- **U9 (11.1, 11.2):** **neither service touches the broker at startup**, so no service in this
  system needs a broker healthcheck to have passed before it starts. That is 7.1 and 7.7 deleting
  the ordering dependency rather than managing it, and it is a property U9 can rely on when it
  writes `depends_on`.
- **U9 or U13 (7.1):** the operational note — changing an argument of a queue that already exists
  fails with `PRECONDITION_FAILED` (406) and closes the channel, and the repair is
  `docker compose down -v` (11.7) — is carried to the README by whichever owns that section. It is
  not written here because the environment its repair names does not exist until U9.
- **U10 (12.3):** as with U5, nothing in this unit is asserted by a test inside it. What lands here
  as "read from the diff" becomes observable over HTTP: the assignment scenario exercises the
  publish, the topology and the consume as one path, and F7's exhaustion exercises the wait queue's
  TTL and both halves of 8.2's dead-letter cycle. **FW17's window is the one thing that stays
  unobservable**, which is why it is a Part 5 entry rather than an accepted cost in prose.
- **U12:** nothing directly.

## 9. After the merge

`main` satisfies 14.7's U2 row unchanged — `ruff format --check .`, `ruff check .`, `mypy src
tests`, `python -c "import pizza"` and `pytest tests/unit` all exit zero on a clean clone, with
sixteen unit tests. The bar rises at U9.

Every port in `application/ports.py` now has a verified implementation, and layer 3's driven side
is complete. `domain/` and `application/` still import nothing but the standard library and each
other, enforced by `ruff check .` since U5. The system can now be assembled; it has not been.
