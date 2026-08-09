# Planning — Decisions

**Phase 2 of the planning protocol in `CLAUDE.md` §2: every inventory item resolved.** Each
record states the decision, why it was chosen, and what was rejected and why. The questions
these answer are in `01-inventory.md`; the build order is in `03-roadmap.md`.

Item numbering is inherited from the inventory and is stable. Depth follows item 1.3: a full
record where a reviewer would ask "why this?", a single line where no genuine alternative was
weighed.

---

## Status

**Authoritative, and the only place item status is recorded.** `01-inventory.md` carries no
status markers, precisely so that this table cannot be contradicted.

| Topic | Decided | Open |
|---|---|---|
| 1 — Scope and time | 1.1, 1.3, 1.4, 1.5 | 1.2 |
| 2 — Stack and tooling | 2.1, 2.2, 2.3, 2.4, 2.5 | 2.6–2.10 |
| 3 — Architecture and layering | 3.1, 3.2, 3.3, 3.5, 3.6, 3.8 | 3.4, 3.7 |
| 4 — Data model | 4.2, 4.3, 4.4, 4.8 | 4.1, 4.5, 4.6, 4.7 |
| 5 — Business rules | 5.1, 5.2, 5.3, 5.5, 5.6, 5.8 | 5.4, 5.7 |
| 6 — API contract | 6.4, 6.5, 6.6, 6.8 | 6.1, 6.2, 6.3, 6.7, 6.9 |
| 7 — Broker contract | 7.5, 7.6 | 7.1–7.4, 7.7 |
| 8 — Worker | 8.1, 8.2, 8.3, 8.5, 8.6, 8.9 | 8.4, 8.7, 8.8 |
| 9 — CLI | 9.2, 9.6 | 9.1, 9.3, 9.4, 9.5 |
| 10 — Configuration | — | 10.1–10.5 |
| 11 — Docker Compose | 11.3–11.7 | 11.1, 11.2, 11.8–11.11 |
| 12 — Testing | — | 12.1–12.10 *(12.6 partial)* |
| 13 — Documentation | 13.5, 13.6 | 13.1–13.4 |
| 14 — Git and process | 14.5 | 14.1–14.4, 14.6, 14.7 |
| **Total** | **47** | **62** |

Phase 3 does not begin while any item is open (`CLAUDE.md` §2).

---

# Part 1 — Decision records

## Topic 1 — Scope and time

- **1.1 Scope ceiling for the 4-day budget.** `[decided]`
  *Decision:* the delivered system is **exactly R1–R23 and nothing more**. Anything not
  traceable to a numbered requirement ships only if it passes one test:
  **delete it — which named DoD row now fails?** If the answer is "none", it is **not built**,
  and it is **presented as a proposed Part 5 entry** for the developer to approve. Per
  `CLAUDE.md` §1 the entry is written only on approval — this rule fixes the verdict, not the
  authority to record it. What the rule forbids is the third outcome: an item left pending,
  unbuilt and unrecorded, to be "kept in mind".

  *Worked examples — the rule's calibration, not its rejections:*

  | Candidate | DoD row that fails without it | Verdict |
  |---|---|---|
  | `GET /orders` (6.6) | *Interactive CLI* — selecting an order would mean retyping a UUID | **ships** |
  | `GET /health` (6.6) | *Docker Deployment* — readiness would need a fixed sleep, forbidden by §5 | **ships** |
  | Driver release on `DELIVERED` (5.6) | *Interactive CLI* / *Broker & Consumer* — without it the pool empties and the demo stalls permanently | **ships** (a repair, not a feature) |
  | `GET /drivers/{id}/orders` (FW3) | none — the data exists and the endpoint is cheap, but nothing degrades | **Part 5** |
  | Structured `items` — `name` / `quantity` / `toppings` (4.2) | none — the CLI prints the strings it was given | **Part 5 (FW11)** |

  *Why a test rather than a list of exclusions:* a list only answers proposals already
  imagined. A week will produce proposals not yet imagined, and each will look reasonable on
  its own merits — which is exactly how scope grows without any rule ever being broken. A test
  applies to a proposal nobody has made yet. That is the only kind of ceiling that still holds
  on the last day.
  *Side effect, and the reason this item is load-bearing:* the test is only as good as Part 0.
  Applying it exposed that R13 had dropped the brief's "to store orders, drivers, and
  assignment states", leaving 4.4 as the one decision citing the brief directly for want of a
  requirement to cite. R22 and R23 close that.
  *Rejected — alternative rules, not alternative features:*
  **"Implement the brief literally, nothing more."** The cleanest rule available, and it fails:
  it excludes `GET /health`, without which R15 cannot be met at all under §5.
  **"Decide case by case, on merit."** This was the prior state, not an alternative to it. It
  produced two unrequested endpoints, each individually well argued — the failure mode is not
  bad judgement, it is the absence of a rule that judgement is measured against.
  **"A fixed budget — at most N extra endpoints."** Countable and enforceable, but arbitrary:
  it would have permitted a third endpoint of no value and forbidden a fourth that a DoD row
  needed. It counts the wrong thing.
  *Source:* assignment time estimate; `CLAUDE.md` §3, §7. *Governs:* Part 5. *Requires:* R22, R23.

- **1.3 Which decisions carry a full record.** `[decided]`
  *Decision:* two depths, and the test between them is one question:
  **would a reviewer ask "why did you do it this way?"**
  - **Full record** — decision, why, rejected alternatives, accepted costs. Reserved for
    choices with a genuine alternative that a competent reviewer would have weighed.
  - **One line** — the decision alone, no rationale. For choices with no real alternative,
    where a record would document a convention rather than a judgement.
  *Worked examples:* `2.1 RabbitMQ vs Kafka` — full record; the alternative is real and the
  question is certain. `2.8 → ruff + mypy` — one line; nothing is being weighed, and a
  paragraph would document a convention as though it were a judgement.
  *Why:* R23 requires decisions to be defensible verbally, which is what makes the full record
  worth its cost — but only where a question will actually be asked. Applying that depth to a
  formatter choice does not make it more defensible; it buries the ten answers that matter
  among sixty that do not. `CLAUDE.md` §2 requires every item to be **resolved**; it nowhere
  requires every item to be *argued*.
  *Rejected:* **a full record for every item** — the prior practice, and the reason this record
  reached 1,373 lines at 28% complete. **One line for everything** — cheap, and it discards
  exactly the material R23 asks for.
  *Source:* R23, `CLAUDE.md` §2. *Governs the depth of every record in this file.*

- **1.4 Where Phase 2 decisions are recorded.** `[decided]`
  *Decision:* in **`02-decisions.md`** — this file — one record per inventory item, numbered
  from the inventory. The README carries a short trade-off summary, assembled from these
  records in U13 (13.4); it is a derived view, never a second original.
  *Why:* the alternative that was actually in force — recording each decision inline in the
  inventory item — is what this restructure had to undo. It overwrote the question with its
  answer, so Phase 1 left no artifact at all, and the same fact ended up stated in two places
  and eventually disagreed with itself. Separating the two makes each phase readable on its
  own and gives the README exactly one source to draw from.
  *Rejected:* **inline in the inventory** — the prior state, described above.
  **The README's trade-off section as the primary record** — it is written for a reader who
  has never seen the project, so it cannot also carry rejected alternatives and accepted costs
  without becoming unreadable; it is a summary, and a summary cannot be the original.
  *Source:* `CLAUDE.md` §2 Phase 2, §7. *Realised by:* the three-file split, 2026-08-07.

- **1.5 Per-unit time budget.** `[decided]`
  *Decision:* **no time budget and no per-unit estimates.** Volume is controlled by 1.1 (what
  is built) and 1.3 (how much is written about it) — neither depends on a clock.
  *Why:* an estimate here would assume regular availability, so a lost day would break it for
  a reason unrelated to whether the plan was right. The real risk is planning expanding to
  fill the days available — a volume problem, which 1.1 and 1.3 address where the volume is
  created.
  *Rejected:* hour estimates per unit — a guess wearing a number. Relative sizing with
  calibration — more honest, same dependence on regular availability, more ceremony.
  *Source:* assignment time estimate; `CLAUDE.md` §2. *Superseded by:* 1.1, 1.3.



## Topic 2 — Stack and tooling

- **2.1 Broker: RabbitMQ or Kafka.** `[decided]`
  *Decision:* **RabbitMQ.**
  *Why:* R9 is written in RabbitMQ's vocabulary — per-message ack/nack/requeue is a native operation. Delayed retry is available through a dead-letter exchange with a message TTL, with no plugin and no extra topology per delay level. It starts fast, which directly serves R15 (`docker compose up` must also run the test suite).
  *Rejected:* **Kafka** — it has no per-message nack. Retrying one message means either blocking the whole partition or republishing to a dedicated retry topic, which is topology this scope does not justify (`CLAUDE.md` §3 treats over-engineering as a defect). It is also heavier to start, slowing every launch and every test run.
  *Source:* R13, DoD "Broker & Consumer". *Answers:* Q18.

- **2.2 Database: PostgreSQL or MongoDB.** `[decided]`
  *Decision:* **PostgreSQL.**
  *Why:* claiming a driver is the system's one real concurrency problem (F2), and `SELECT … FOR UPDATE SKIP LOCKED` is the canonical primitive for it. "Mark the driver `BUSY` and assign them to the order" spans two records and must be atomic; in PostgreSQL that is one transaction. Unique constraints then act as the last line of defence rather than the only one.
  *Rejected:* **MongoDB** — `findOneAndUpdate` is atomic for a single document, but the assignment touches two. Multi-document atomicity requires a replica set, which adds compose complexity the assignment never asked for.
  *Source:* R13. *Answers:* Q18.

- **2.3 API framework.** `[decided]`
  *Decision:* **FastAPI with Pydantic v2.**
  *Why:* 4.2 already fixed edge validation with explicit bounds and **unknown fields rejected**.
  In Pydantic that is a declaration (`extra="forbid"`), not code — which is exactly what
  `CLAUDE.md` §3 asks for when it says external input is validated at the edge: the type
  declaration *is* the validation, so there is no second place a rule could drift to. 4.2 and
  5.2 also already committed to **`422`** for validation failures, which is FastAPI's default
  code for precisely this case — decisions already approved presuppose this framework. The
  generated OpenAPI document is a free, always-accurate statement of the contract in topic 6,
  which a reviewer can read without reading code.
  *Rejected:* **Flask** — validation would be hand-written or need a second library, there is
  no `422` convention, and the contract would exist only in prose. **Django / DRF** — brings an
  ORM and an ORM-centred layering that contradict 3.1 and `CLAUDE.md` §3, and is far more
  machinery than four endpoints justify. **Litestar** — a good framework that buys nothing over
  FastAPI here and is less familiar to a reviewer, which costs explanation for no gain.
  *Runtime-neutral:* FastAPI supports both synchronous and asynchronous route handlers, so this
  decision does not pre-empt 2.4.
  *Source:* R12, `CLAUDE.md` §3 ("external input is validated at the edge").

- **2.4 Sync or async runtime.** `[decided]`
  *Decision:* **synchronous throughout** — `def` route handlers, a blocking consumer loop, a
  blocking CLI, a synchronous test suite. The two services match, and that is structural rather
  than stylistic: 3.8 gives them one `UnitOfWork` `Protocol`, and one `Protocol` cannot be sync
  in one process and async in another without a second port and a second implementation of every
  repository — which is what 3.3 rejected when it rejected duplicated modules.

  *The rule, written so it can be checked in a diff:* **no `async def` under `src/pizza/`, and
  no `await` under `domain/` or `application/`.** The single exception is the ASGI `lifespan`
  hook in `entrypoints/api/main.py`, which FastAPI defines as an async context manager; it holds
  composition-root wiring only (3.1) and never calls into `application/`. Its blocking
  construction work runs at startup, when nothing is being served.
  *Why the rule earns its place independently of the choice:* FastAPI runs a `def` handler in a
  thread pool and an `async def` handler on the event loop, so a mixed codebase is one careless
  `async def` away from a handler that blocks the loop and serialises every request in the
  process. Naming one colour removes that failure mode instead of managing it.

  *Why synchronous — there is no concurrency to exploit.* 8.5 fixes the worker at one replica
  with prefetch 1, so it holds exactly one message at a time; an event loop exists to overlap
  I/O waits across concurrent tasks, and there is only ever one task. The API serves an
  interactive CLI driven by one person (9.2) and four integration scenarios (A17). Async is
  measured in concurrent connections, and this design has no such number.

  *Why keeping the core uncoloured is the deciding cost.* Stated precisely, because the
  overstatement is available and wrong: `async` is a language keyword, not a library, so an
  async core would still pass 3.1's framework-free test. This is a simplicity argument, not a
  layering one. What it costs is concrete — every port method, every use case and 3.5's `with`
  acquire `async`, and U4's unit tests need an async pytest plugin, so they stop being what
  `CLAUDE.md` §5 permits them as: "pure logic, no infrastructure, written in minutes".
  `domain/` is untouched either way; the entities are values.

  *The cost accepted, not hidden:* 7.5's publish runs inside the request with publisher
  confirms and a bounded per-attempt timeout, so a `PATCH` against an unreachable broker
  occupies one thread-pool thread for up to twice that bound (10.4 defaults it to 5 s). On an
  event loop the wait would cost nothing. Against FastAPI's default pool of 40 threads and the
  concurrency above the thread is affordable — but it is a real cost, not an absent one.

  *The obligation this hands onward, recorded here so it is not improvised in U6:* `pika` is not
  thread-safe, and a synchronous FastAPI serves handlers from a thread pool, so two concurrent
  `PATCH` requests sharing one channel would interleave frames on it. The publisher adapter must
  be safe under the pool — a lock around `publish`, or a connection per publish. 7.7 owns which.

  *Rejected:* **asynchronous throughout** — the coherent alternative, and not a straw one: an
  async core, psycopg's async interface or `asyncpg`, `aio-pika`, an async suite. It is
  FastAPI's idiomatic mode, it frees the thread the publish holds, and its publisher story is
  genuinely cleaner, because one event loop serialises channel access for free and the
  obligation above disappears. It was rejected because the concurrency it optimises does not
  exist here, while its price is paid in the layer R20 is graded on; SQLAlchemy's async support
  additionally pulls in `greenlet`, and 3.5's `Protocol` would need amending.
  **A mixed runtime** — an async API over a sync worker: two ports and two repository
  implementations for one shared core, and it is precisely the arrangement that produces the
  blocked-event-loop bug above.

  *Conditional, and the condition is named:* this holds while concurrency is 1. Raising
  prefetch, adding worker replicas, or putting the API under real concurrent traffic is what
  turns the trade over — **FW12**.
  *Source:* R12, `CLAUDE.md` §3. *Constrained by:* 3.5, 3.8, 8.5. *Constrains:* 2.5, 2.6, 2.7,
  3.4, 7.7. *Deferred to:* FW12.

- **2.5 Database access approach.** `[decided]`
  *Decision:* **SQLAlchemy 2.0, declarative ORM, over the synchronous `psycopg` (v3) driver.**
  Models live in `infrastructure/db/models.py` as **classes separate from the domain entities**;
  repositories convert between them. One `Engine` per process, built at the composition root;
  `UnitOfWork.__enter__` opens a `Session` and `__exit__` closes it. The `Session` does not take
  a connection by itself — SQLAlchemy acquires one from the pool on the first statement and
  returns it when the transaction ends and the session is closed. A unit of work that touches
  nothing therefore costs no connection, and no connection is ever held between requests. The
  API and the worker use the same mechanism — 3.8 settled that, and it is not re-decided here.

  *The two session settings, written explicitly because the defaults are wrong for this design:*

  ```python
  # entrypoints/{api,worker}/main.py — composition root (3.1)
  engine  = create_engine(settings.database_url, pool_pre_ping=True)
  factory = sessionmaker(engine, autoflush=False, expire_on_commit=False)
  ```

  `autoflush=False` — the default flushes pending writes before every query, at a moment the
  caller did not choose. 8.9 is a decision about exactly when a row is locked, and an `UPDATE`
  firing at an unspecified point inside that window is the one thing it cannot tolerate.
  `expire_on_commit=False` — the default marks every loaded object stale after `commit()`, so
  reading a field afterwards issues a fresh `SELECT`.
  **Stated without inflation: neither default causes a defect in any flow decided so far.**
  Repositories return domain entities, so nothing ORM-shaped escapes them, and in
  `dispatch_order` the claim query precedes every write. They are set because relying on "no
  current flow triggers it" is relying on an accident rather than on a rule.
  `pool_pre_ping=True` is set not for startup ordering — 11.2's healthchecks own that — but for
  connections that go bad **while idle in the pool**: a database container restart (11.11), a
  server-side idle timeout, a dropped connection. Without it the failure surfaces on whichever
  request happens to borrow the dead connection, which is both intermittent and misattributed.
  It costs one `SELECT 1` per checkout.

  *Why an ORM, when 3.1 and 6.5 between them remove most of what one is for:* the honest
  starting position is that they do. 6.5 forbids relationship navigation, so `relationship()`,
  lazy loading and N+1 are not risks managed but a feature never used; and 3.1 already assigns
  row→entity conversion to the repository, so an ORM does not remove that step. Two things
  survive, and they are what decided it.

  First, the write-back a separate-entity design needs costs no extra query.
  `session.get()` resolves from the identity map **when the instance is already loaded in that
  session and not expired** — which holds on every write path here, because the use case loads
  the entity through the same `UnitOfWork` before mutating it, and `expire_on_commit=False`
  keeps it valid afterwards. It is a property of this flow, not a guarantee of the API: `get()`
  on an id the session has not seen issues a `SELECT` like any other read.

  ```python
  def save(self, order: Order) -> None:
      # loaded earlier in this Session and not expired, so this resolves from
      # the identity map without a SELECT — it would issue one otherwise
      model = self._session.get(OrderModel, order.id)
      model.status = order.status.value
      ...
  ```

  Second, `Mapped[...]` annotations give the type checker (2.8) a statically known type per
  column. **Not because Core is untyped** — SQLAlchemy 2.0 types `Column` and `TypeEngine`
  generically, and a Core query written against column objects held by reference carries those
  types through. It is the ordinary Core idiom that loses them: `table.c.status` is attribute
  access on a dynamic collection, so a checker sees `Column[Any]` and the resulting `Row`
  follows. Declarative arrives at the same place by construction rather than by discipline,
  which matters most at the row→entity function — the one place where a column/field mismatch
  would otherwise pass unchecked.

  *What it costs, plainly:* two classes per table and a mapper function per direction. Only
  imperative mapping avoids it, and it is 3.1's framework-free rule that creates it, not this
  item.

  *Two units of work, stacked — recorded because it is the likely interview question:* the
  SQLAlchemy `Session` is itself a unit of work with change tracking. 3.5 put ours above it. We
  use only its transaction boundary; the tracking half does nothing, because mutation happens on
  the domain entity and reaches the model only in `save()`. The answer is one sentence — the
  `Session` is an implementation detail of the adapter, the `UnitOfWork` `Protocol` is what the
  core sees, and the core cannot tell there is a `Session` underneath.

  *Rejected — **imperative mapping**, mapping the domain entities themselves to tables.* The
  strongest alternative, and the arrangement *Architecture Patterns with Python* recommends. Its
  claim is that it removes the duplication above; counted, it does not. `map_imperatively`
  requires an explicit `Table` object, so the column list is written either way, and what is
  actually saved is the two mapper functions — about twelve lines against twelve.
  Against that near-zero saving, `start_mappers()` mutates the domain class globally for the
  lifetime of the process, so whether U4 sees a clean `Order` depends on whether anything else
  in the same process has called it. Whether that forces a `clear_mappers()` fixture is **not
  settled here — it turns on 12.7, which is open**: separate pytest invocations per directory
  never start the mappers, a single invocation over both does. That is the objection, stated at
  its real size: an item saving nothing should not change another item's options.
  Two costs that do not depend on 12.7: SQLAlchemy sets state directly when loading rather than
  calling `__init__`, so any invariant 4.1 places in the constructor is silently skipped for
  objects read from the database; and for the same reason a mapped class cannot be a frozen
  dataclass, which moves the question of what an entity may be out of 4.1 and into the
  persistence layer. **What it does not do, and the record says so because the argument would
  otherwise lose:** it adds no import to `domain/`, so 3.1's framework-free test passes under it.
  The coupling is runtime instrumentation, conditional on a call made elsewhere — which is why
  the rejection rests on the two concrete costs above and on the counted saving, not on the
  principle.
  **What it has in its favour, and it is not nothing:** `save()` disappears for updates, which
  makes 4.3's cross-table invariant slightly harder to forget.
  *Rejected — **SQLAlchemy Core alone** (query builder, no ORM).* The same two dependencies, so
  nothing is saved at install; it keeps the pool and the metadata and has none of the ORM's
  session semantics. It loses on the two points above — the write-back needs a hand-written
  cache in place of the identity map, and the typed-column idiom is available but not the
  default one.
  *Rejected — **`psycopg` with hand-written SQL**.* One dependency instead of two, and 8.9 reads
  exactly as it was written. Rejected for a side effect rather than a flaw: with no metadata
  there is no `create_all`, so it would settle 4.6 by elimination instead of by decision.
  *Rejected — **`psycopg2`**:* maintenance-only. **`asyncpg`** is excluded by 2.4.

  *Completes 3.5's deferred half* — "session lifetime, pooling, and what `__enter__` actually
  opens" — as above. Pool sizing stays at SQLAlchemy's defaults; whether it becomes tunable is
  10.4.
  *Leaves 4.6 open:* `Base.metadata` exists, so `create_all()`, Alembic and an init script all
  remain available there. Alembic's autogenerate works from `MetaData`, which a query builder
  would also have provided — declarative buys nothing on that axis and none is claimed.
  *Feeds, does not decide:* 2.10 — `sqlalchemy` and `psycopg[binary]`, to be approved as one
  list; 11.9 — the `[binary]` wheel has no musl build, which surfaces if that item chooses an
  Alpine base; 3.4 — `application/queries.py` sits in a layer that cannot import
  `infrastructure`, so the read path needs a port of its own.
  *Source:* R20, `CLAUDE.md` §3, §6. *Constrained by:* 2.2, 2.4, 3.1, 3.5, 6.5, 8.9.
  *Constrains:* 3.4. *Realised in:* U5.


## Topic 3 — Architecture and layering

- **3.1 Layer definition.** `[decided]`
  *Decision:* **four directories, three layers, one dependency arrow — inward.**

  ```
  pizza/                    # the root package's shape is 3.3, not this item
  │
  ├── domain/               # layer 1 — imports: stdlib only
  │   ├── order.py              Order, OrderStatus, AssignmentState, TransitionResult
  │   ├── driver.py             Driver, DriverStatus
  │   ├── rules.py              rules no single entity owns — none today; trigger in 3.2
  │   └── errors.py             typed domain errors (5.2)
  │
  ├── application/          # layer 2 — imports: domain only
  │   ├── ports.py             signatures fixed in 3.4
  │   ├── queries.py           get_order, list_orders — read paths: no rules, no transaction
  │   └── use_cases/           place_order · advance_order_status ·
  │                            register_driver · dispatch_order — one file each
  │
  ├── infrastructure/       # layer 3, driven — imports: application, domain, libraries
  │   ├── db/                  models, repositories, unit of work, outbox, migrations
  │   ├── broker/              publisher, topology declaration
  │   ├── clock.py             SystemClock
  │   └── ids.py               exists only if 4.7 generates identifiers in the application
  │
  └── entrypoints/          # layer 3, driving — imports: application; wires only at main.py
      ├── api/                 main · deps · schemas · errors · routers/{orders,drivers,health}
      ├── worker/              main · consumer
      └── cli/                 3.6
  ```

  *The rule, written so it can be checked in a diff:* **no module under `domain/` or
  `application/` names `infrastructure` in an import, and outside the two `main.py` files no
  module under `entrypoints/` does either.** `infrastructure/` imports `application/` in order
  to implement its `Protocol`s — the arrow points inward even though the runtime call goes
  outward, and that inversion is the entire content of "dependencies point inward".

  *What framework-free means here, concretely:* `domain/` and `application/` import
  `dataclasses`, `enum`, `datetime`, `uuid`, `typing` — and not `pydantic`, `sqlalchemy`,
  `pika` or `fastapi`. Pydantic is third-party even though it is not infrastructure, and 2.3
  already placed it at the edge. The test is one question: **can `domain/` and `application/`
  run with nothing installed but Python?**

  *Why `domain` and `application` are two layers and not one:* three decided items already
  require a component that is neither a pure rule nor a route. 7.5 publishes "from the
  application layer" after the commit; the constraint it placed on 3.5 gives the transaction to
  the use case; 5.3 has the core report that an event must be emitted while an adapter
  publishes it. If the transaction lives on the entity, the entity is no longer framework-free.
  If it lives in the route, the worker cannot reuse it — which is exactly what 3.8 asks.

  *Why ports sit in `application/ports.py`, not in `domain/`:* the caller of a port is the use
  case, not the entity. `Order` has no reason to know that something stores it. 4.8's clock
  port reaches the domain as an argument (`order.assign_to(driver_id, now)` — no domain
  operation reaches for a time module), so `domain/` declares no ports at all and depends on
  nothing.

  *Composition root:* `entrypoints/api/main.py` and `entrypoints/worker/main.py` are the only
  modules permitted to import `infrastructure/`. They construct the adapters and hand them to
  the use cases; `routers/` and `consumer.py` receive them already built. Inside `api/`,
  `deps.py` is the injection seam and `errors.py` holds the domain-error → HTTP-status table as
  one registered handler, so 5.2's mapping is written once rather than per route.

  *Rejected:* **one `core/` directory** holding entities, rules, ports and use cases — the same
  files, one directory fewer, and at this size it would work; the honest reason to decline is
  narrow. It loses the only thing that makes the inward rule enforceable: inside one directory,
  `order.py` importing `ports.py` breaks no boundary and shows as nothing in a diff.
  **A single `adapters/`** merging driven and driving — correct terminology, and it hides the
  one distinction R20 asks to see. **Feature-first** (`orders/`, `drivers/`, each with its own
  layers) — right at a larger scale; here there are two entities, and R20 names layers, so a
  reviewer would be reading for a structure that is not there. **`interfaces/` as the name of
  the driving layer** — in Python it reads as `Protocol`, and the `Protocol`s live in
  `application/ports.py`; the name would point at the opposite layer.

  *Deliberately left to later items:* how the rules divide between methods on the entities and
  `domain/rules.py` is 3.2 — both live entirely inside `domain/`, so neither changes a layer,
  an arrow, or an import rule. Whether `ids.py` exists follows 4.7. What the root
  package is, and whether the API and the worker share it, is 3.3.
  *Source:* R20, `CLAUDE.md` §3. *Constrained by:* 5.3, 7.5. *Constrains:* 3.2, 3.4, 3.6, 3.8.

- **3.2 What lives in the framework-free core.** `[decided]`
  *Decision:* the rules this item names land as follows.

  | Rule | Where | Form |
  |---|---|---|
  | Status transition (5.1, 5.2) | `domain/order.py` | `order.advance_to(to) -> TransitionResult` |
  | Publish trigger (5.3) | the same operation | `TransitionResult.must_publish` |
  | Driver release (5.6) | the same operation, plus `domain/driver.py` | `TransitionResult.releases_driver` and `driver.release()` |
  | Assignment eligibility (5.5) | `domain/order.py` | `order.can_be_assigned()` |
  | Driver **selection order** | `infrastructure/db/` — see below | the `ORDER BY` inside the claim query (8.9) |

  *Where each rule lives:* a rule that one entity can decide from its own fields is a **method
  on that entity**. A rule that no single entity owns — one that must read two entities to reach
  its verdict, and cannot be expressed as a flag on one entity's own result — is a **free
  function in `domain/rules.py`**. Both are inside `domain/`; the split is about ownership, not
  about layering.
  *Every rule decided so far falls on the method side*, including 5.6: its cross-entity
  appearance is coordination performed by the use case, not a rule spanning two entities.
  `domain/rules.py` therefore holds nothing today and **is not created empty** — `CLAUDE.md` §6
  rejects dead code. The tree in 3.1 marks the slot so that the first such rule has a named
  destination instead of being improvised into whichever entity it half-fits.

  *Why the publish trigger is a returned field and not a second method:* 5.3 already fixed the
  mechanism — the core "reports back that an event must be emitted" — and left only the module
  to this item. A returned value is what reporting back means. A separate `should_publish(order)`
  would let a caller advance the status and never ask the question, which is the failure 5.3
  exists to prevent.

  **The one rule not enforced in the core, stated plainly.** 8.9's claim is
  `SELECT … FOR UPDATE SKIP LOCKED LIMIT 1`, and `LIMIT 1` without an `ORDER BY` is not
  deterministic. That `ORDER BY` is what selects the driver, and it lives in `infrastructure/db/`.
  *Why that is acceptable:* it is not a business rule. R7 asks for "**an** `AVAILABLE` driver"
  and names no preference; the ordering exists only because 4.3 needed a deterministic
  tie-breaker, so that a test can assert on an outcome rather than on a set. A business rule is
  something that can be violated — this one has nothing to violate.
  *Why it cannot simply move inward:* selecting in Python and then locking is a read-then-lock
  race, and 8.9 already rejected the optimistic retry loop that would repair it. The selection
  and the lock must be one statement, so the predicate lives where the statement lives.
  *How it stays visible, without a comment doing the work:* the port's **name** carries the
  convention to every call site rather than hiding it (`claim_next_available_driver`; 3.4 fixes
  the exact signature); its `Protocol` docstring in `application/ports.py` — inside the core —
  states the ordering, why it is a convention, and where a future rule would enter; and the
  behaviour is verified by a test that registers two drivers and asserts which is claimed, so
  the `ORDER BY` cannot be dropped silently.
  *Conditional, and the condition is real:* this holds only while 5.4 chooses an ordering with
  no business content. If 5.4 decides a preference that expresses business intent, the ordering
  becomes a business rule, `CLAUDE.md` §3 applies, and this item reopens.

  *What deliberately does not live in the core* — each of these looks like a rule and is not:

  | Looks like a rule | Lives in | Fixed by |
  |---|---|---|
  | ack / nack selection | `entrypoints/worker/consumer.py` | 8.1 — these are AMQP terms |
  | domain error → HTTP status | `entrypoints/api/errors.py` | 5.2 — the core raises a type, not a code |
  | publish-after-commit ordering | `application/use_cases/` | 7.5 — orchestration, not a rule |
  | the nested-driver response shape | `application/queries.py` and the schemas | 6.5 — "the core never sees this shape" |
  | row locking in the claim | `infrastructure/db/` | 8.9 |

  *Rejected:* **a `DriverCriteria` parameter on the claim port today** — it would not move the
  selection into the core, because 8.9 keeps the predicate inside the statement either way; what
  it buys is runtime-selectable policies, which nothing asks for. Adding it when a filtering rule
  arrives touches four lines across layers that already exist, so there is no discount for buying
  early — and a criteria type with no fields is precisely the speculative abstraction
  `CLAUDE.md` §6 names. **Reading candidate drivers into the core and choosing there** — the
  orthodox layering answer, and it contradicts 8.9. **A `domain/rules.py` holding every rule,
  with the entities as data only** — the Anemic Domain Model: rules separated from the data they
  constrain, which is the arrangement both DDD and `CLAUDE.md` §3 argue against.
  *Source:* `CLAUDE.md` §3, §6, R7. *Constrained by:* 5.3, 5.5, 5.6, 8.9. *Constrains:* 3.4, 3.8.
  *Revisit if:* 5.4 gives the selection order business content.

- **3.3 Code sharing between API and worker.** `[decided]`
  *Decision:* **one importable package, `src/pizza/`, with the service boundary at
  `entrypoints/`.** The API and the worker are two `main.py` files, two containers and two
  processes over one database. They share `domain/`, `application/` and `infrastructure/`, and
  duplicate nothing.

  ```
  repo root/
  ├── src/pizza/            # the one package — 3.1's tree lives here
  │   ├── domain/ · application/ · infrastructure/
  │   └── entrypoints/ api · worker · cli        # ← the service boundary
  ├── tests/ integration/ · unit/                # CLAUDE.md §5; contents are topic 12
  ├── docs/ · .claude/                           # committed, 14.5
  └── docker-compose.yml · .env.example · README.md
  ```

  *Why not two independent services sharing a wire contract* — the orthodox microservice answer,
  and the assignment excludes it as a matter of fact rather than taste. R7 has the worker query
  **the database** for a driver and R8 has it write the assignment, so the two services share a
  schema, not a message format. Routing that through the API instead would also break 8.9:
  claiming a driver is a row lock inside a transaction, and an HTTP call cannot join another
  process's transaction.

  *Worth stating rather than hiding:* a database shared by two services is normally an
  anti-pattern, precisely because it removes the independence that makes them separate. The
  brief uses "microservice" in the loose sense — several services under Compose — and what is
  delivered is exactly the architecture it draws. A24 records the reading.

  *Why not duplicated modules* — its real advantage is independent build and release for
  separate teams, and there are no separate teams here. It puts 5.5's guard in two files, which
  `CLAUDE.md` §3 forbids in one sentence: "if a rule is enforced in two components, the rule is
  in the wrong place."

  *Why `src/pizza/` and not `pizza/` at the repository root:* with a flat layout `import pizza`
  resolves from the working directory, so the suite can pass against the source tree while the
  installed package is broken. Under src-layout the directory holding the package is not itself
  importable, so every run goes through the install. The alternative defence — that 11.3 runs
  the suite inside the built environment — only holds if the image ships the installed package
  rather than a copy of the repository, which is 3.7's call and not yet made. The layout gives
  the guarantee without depending on it.
  *Rejected — `src/` as the package itself* (`from src.domain import …`): the import name then
  carries no information, two such projects cannot coexist in one environment, and it breaks the
  correspondence between distribution name and import name that a project file establishes.

  *The FW2 tension this item was asked to settle:* the shared package is required by
  `CLAUDE.md` §3 and R20 whether or not FW2 ever arrives, so its effect on FW2 is a consequence
  and not a justification. **Nothing generic is built** — no background-process base class, no
  runner, no plugin mechanism. `entrypoints/worker/` is one concrete worker. If the relay ever
  arrives it is `entrypoints/relay/main.py` plus a Compose entry: cheap because the layers
  already exist, not because a slot was left for it.

  *Feeds, does not decide:* 2.9 owns how dependencies are declared and whether there is one set
  or one per service; 3.7 owns the number of images. This item fixes only that there is one
  package for them to package.
  *Source:* R7, R8, R14, R20, `CLAUDE.md` §3. *Constrained by:* 7.5, 8.9. *Constrains:* 2.9,
  3.7, 3.8. *Defines:* A24.

- **3.5 Transaction ownership.** `[decided]`
  *Decision:* the transaction is opened and committed by the **use case**, through a
  `UnitOfWork` port that hands out the repositories bound to it. `domain/` never learns that
  transactions exist; `application/` knows the boundary, not the mechanism.

  ```python
  # application/ports.py — the whole of what the core knows
  class UnitOfWork(Protocol):
      orders: OrderRepository
      drivers: DriverRepository
      outbox: OutboxStore
      def __enter__(self) -> "UnitOfWork": ...
      def __exit__(self, *exc: object) -> None: ...   # leaving without commit rolls back
      def commit(self) -> None: ...

  # application/use_cases/advance_order_status.py
  with self._uow as uow:
      ...
      uow.commit()                       # the commit is a line
  if result.must_publish:
      self._publish_and_mark(event)      # 7.5's "one identified line", relative to it
  ```

  *Why the unit of work holds the repositories rather than receiving them:* if `orders` and
  `drivers` were injected separately, nothing structural would keep them on one transaction —
  atomicity would depend on the composition root having built them from the same session. With
  `uow.orders` and `uow.drivers` that is the type's job. **Without overstating it:** 4.3 records
  its invariant as "enforced by discipline", and this removes only half of that. It guarantees
  that if both writes happen they are atomic; it does not guarantee both happen. The ghost
  driver still depends on the use case not forgetting.

  *Which layer knows what:* `domain/` does not contain the word `transaction` — entities are
  values, and `order.advance_to()` cannot tell whether anything is being persisted at all.
  `application/` knows a transactional **boundary** exists, because 7.5 puts the commit there,
  but it knows it as a `Protocol`. No module under `domain/` or `application/` imports a
  database library; the import appears in exactly one class, the one implementing the port.

  *Read paths use the same unit of work and never commit.* A second, read-only port would exist
  only to avoid a word. It creates no conflict with 6.5's recorded cost either — under
  PostgreSQL's default isolation each statement takes its own snapshot regardless.

  *Rejected:* **a transaction per repository** — two transactions mean a crash between them
  leaves a driver `BUSY` with no order, which is precisely the ghost driver 4.3 already carries
  as an accepted cost; there is no reason to invite a second source of it. **A `@transactional`
  decorator on the use case** — the commit becomes a side effect of returning, so there is no
  line for the publish to be "one identified line relative to", and 7.5 could then be satisfied
  only by moving the publish out of the use case entirely. **Passing a session to every
  repository call** — explicit, widely used, and the default in other languages; it fails here
  on one type. Typed as the real session it puts a database library in `application/ports.py`;
  typed as an opaque token defined in `application/` it is a unit of work with a parameter added
  to every method.

  *Left to 2.5:* session lifetime, pooling, and what `__enter__` actually opens. This item fixes
  the shape, not the driver.
  *Source:* R8, `CLAUDE.md` §3. *Constrained by:* 4.3, 7.5. *Constrains:* 3.4, 8.9.

- **3.6 Where the CLI sits.** `[decided]`
  *Decision:* a **driving adapter in `entrypoints/cli/`, speaking only HTTP to the API.** It
  imports nothing from `domain/` or `application/`, shares nothing with the two services beyond
  the wire contract, holds no business rule, and runs as its own process.

  *What it knows, exhaustively:* the endpoint paths, the request and response shapes, and the
  **names** of the five status values. All of it is published contract — R2 lists the statuses in
  the endpoint description, and 2.3's generated OpenAPI document carries the rest. A client that
  does not know these cannot call the API at all.
  *What it deliberately does not know:* which status may follow which. 9.2 offers all five values
  and lets the API answer, so the transition rule stays in `domain/` alone — and 5.2's `409`
  becomes something a reviewer triggers from the interface rather than reads about in a document.

  *The test this item sets, since 9.4 and 9.5 both defer to it:* **if the CLI held a stale copy
  of some fact, would the system reach a wrong state, or would one screen be less convenient?**
  A wrong state means the fact is a rule and belongs only in the core. Less convenient means it
  is presentation. As decided, the client holds nothing in the first category.

  *Rejected:* **a CLI that imports the core** — `domain/` would then serve two consumers, so an
  API change could no longer be verified through the API alone, and `CLAUDE.md` §3's "additional
  interfaces are thin adapters" would be broken structurally rather than arguably.
  **A CLI holding the transition sequence in order to offer one "advance" action** — the
  arrangement 9.2 originally carried; it needed an argument that the client only *predicts* while
  the core *decides*, and the simpler interface removes the need for the argument along with the
  knowledge.
  *Sets the rule, does not apply it:* 9.4 splits local validation from API rejection; 9.5 decides
  client-side state.
  *Source:* R11, `CLAUDE.md` §3. *Constrained by:* 9.2. *Constrains:* 9.4, 9.5.

- **3.8 Whether the worker uses the same core as the API.** `[decided]`
  *Decision:* **the same core, the same repositories, the same unit of work.** The worker's
  entry point is `entrypoints/worker/`, and everything below it — `dispatch_order`, the ports,
  the entities — is the code the API already runs. There is no second data path: the worker owns
  no SQL of its own and no direct database access outside the repositories.
  *Why this needs no argument:* 3.3 put both services in one package, 3.1 put `dispatch_order`
  in `application/use_cases/`, and 3.5 gave both entry points the same `UnitOfWork`. `CLAUDE.md`
  §3's "every entry point uses the same core" is satisfied by the structure rather than by a
  choice made here.
  *Source:* `CLAUDE.md` §3, R20. *Constrained by:* 3.1, 3.3, 3.5.


## Topic 4 — Data model

- **4.2 Shape and validation of `items`.** `[decided]`
  *Decision:* `items` is a **list of strings**, validated at the edge before the core sees
  anything:
  - `items` — a list, 1 to 20 entries; each entry non-empty after trimming, at most 100 characters
  - `customer_name` — non-empty, at most 100 characters
  - `address` — non-empty, at most 200 characters
  - unknown fields are **rejected**, not stored
  - any violation returns `422`
  *Why strings:* nothing in the system reads `items` — no rule branches on it, no query filters
  by it, the worker never opens it. It is payload carried from the request to the response. A
  structured item type would have been shape without a consumer, and under 1.1 it fails the
  ceiling test: deleting it breaks no named DoD row, because the CLI prints whatever strings it
  was given.
  *Why validated at all, if nothing reads it:* `CLAUDE.md` §3 requires external input to be
  validated at the edge and forbids an unbounded field crossing into the core. Bounds are the
  validation; they are not a feature.
  *The numeric limits are arbitrary* and recorded as an assumption. Their purpose is that no
  field is unbounded, not that 20, 100 and 200 are meaningful.
  *Deferred:* structured items — `name`, `quantity`, `toppings` — see **FW11**.
  *Source:* R1, `CLAUDE.md` §3, 1.1. *Answers:* Q9. *Defines:* F13.

- **4.3 Driver entity fields.** `[decided]`
  *Decision:* `id`, `name`, `status` (**a stored column**, `AVAILABLE` | `BUSY`), `created_at`.
  **No back-reference to the current order** — the relationship is held once, by
  `orders.driver_id` (4.4). No contact details: nothing in the system uses them.
  `created_at` exists because the driver-selection rule (5.4) needs a deterministic
  tie-breaker.
  *Invariant, written and enforced by discipline:* **driver status and order assignment state
  are always written in the same transaction, or neither is written.** Assignment sets
  `orders.assignment_state = ASSIGNED` and `drivers.status = BUSY` together; release at
  `DELIVERED` sets `COMPLETED` and `AVAILABLE` together.
  *Why stored rather than derived:* it keeps the claim query on one table
  (`WHERE status = 'AVAILABLE' … FOR UPDATE SKIP LOCKED`, 8.9), and it matches R8's wording,
  which describes marking the driver rather than creating a record.
  *Rejected:* deriving `status` from the order table — strictly safer on the consistency axis,
  and not much more expensive, but it turns every availability check into a `NOT EXISTS`
  subquery and leaves R8's "marks driver BUSY" with no literal counterpart.
  *Accepted cost, recorded as an assumption:* `drivers.status` duplicates a fact the order row
  already carries. The failure it admits is a **ghost driver** — `status = BUSY` with no
  `ASSIGNED` order — who is silently invisible to dispatch forever. The schema cannot prevent
  this: PostgreSQL has no cross-table `CHECK`, and a trigger is complexity this scope does not
  justify. The single-transaction invariant above is the whole defence.
  *Source:* R3, R4, R8. *Constrained by A10.*

- **4.4 Representation of an assignment.** `[decided]`
  *Decision:* the assignment is **state on the order, not a separate entity**. The order
  carries `assignment_state` (`PENDING → ASSIGNED → COMPLETED`, plus `FAILED`), a nullable
  `driver_id`, and `assigned_at`. `COMPLETED` is set by the same transition to `DELIVERED`
  that releases the driver (5.6). `driver_id` is **never cleared** — release changes the
  driver's own status, not the order's record of who took it.
  *Why:* the brief asks for "assignment **states**", plural, and that is literally what this
  is. It is also a second axis the order status cannot express: `status = READY` with
  `assignment_state = FAILED` means the pizza is ready and nobody is coming for it, which
  neither field alone can say. Because `driver_id` survives, driver history is a single query
  (`orders WHERE driver_id = X`) with no extra table. And because there is a terminal
  `COMPLETED`, the uniqueness constraint in 4.5 can be conditioned on
  `assignment_state = 'ASSIGNED'` alone, without reading order status — keeping the two axes
  independent.
  *Rejected:* a separate `assignments` table — its one real advantage is the history of
  *multiple* assignments per order, and 5.5 plus 5.6 guarantee there is exactly one assignment
  per order ever, so it would buy a join on every read and "which assignment is current" logic
  for a single row. Also rejected: `driver_id` alone with no state field — it cannot
  distinguish "not tried yet" from "trying" from "gave up", and Q6 needs exactly that
  distinction.
  *Known limitation:* attempt history is not kept — only the final state. Recording how many
  retries preceded an assignment would need an attempts table, which nothing requires. If
  reassignment ever enters scope (driver cancels mid-delivery), a single row per order stops
  being sufficient and moving to an `assignments` table is a real migration, not a free
  extension.
  *Source:* assignment §4. *Answers:* Q3.

- **4.8 Timestamp policy.** `[decided]`
  *Decision:* three timestamps, all UTC:
  - `orders.created_at` — no business rule consumes it, but it is what makes the order of
    events readable when debugging the demo, and its absence would be more conspicuous than
    its presence
  - `orders.assigned_at` — required by A6: `assignment_state` says *what*, `assigned_at` says
    *when*, and together they make the driver-history query meaningful
  - `drivers.created_at` — required by 4.3 as the deterministic tie-breaker for driver
    selection (5.4)
  **No `updated_at`** on either table: nothing reads it, and `CLAUDE.md` §6 rejects fields that
  were not asked for. It can be added if a consumer appears.
  The core obtains "now" through a **clock port** (3.4), never by importing a time module —
  otherwise no test asserting on timestamps can be deterministic.
  *Source:* `CLAUDE.md` §5. *Answers:* the timestamp half of Q10's response shape.


## Topic 5 — Business rules

- **5.1 The legal status transition graph.** `[decided]`
  *Decision:* **strictly linear, one step forward at a time.** The only legal transitions are
  `RECEIVED → PREPARING → BAKING → READY → DELIVERED`. `DELIVERED` is terminal. Skipping a
  stage is illegal, moving backwards is illegal, and **re-sending the current status is
  illegal** — it is treated as any other non-adjacent transition.
  *Why:* allowing skips would make `RECEIVED → DELIVERED` legal, so an order could be
  delivered without ever publishing an event or being assigned a driver — turning F12 from an
  edge case into a supported path. Allowing backwards movement lets a delivered order return
  to preparation, which no requirement asks for. Rejecting the same-status update removes the
  question of whether a repeated `PATCH` re-publishes `ORDER_READY`: it never reaches the
  publish step. That leaves one rule ("only the next adjacent status is legal") instead of
  two, and leaves 5.5 to guard only broker-level duplicates, which are outside our control.
  *Rejected:* forward-with-skips (opens the unassigned-delivery hole); free-form transitions
  (no business meaning, untestable as a rule); same-status as an idempotent `200` no-op
  (friendlier for a CLI user, but adds a second rule plus a "no-op does not publish" clause
  for no real gain).
  *Source:* R2, `CLAUDE.md` §5. *Answers:* Q2, Q14. *Defines:* F9.

- **5.2 Behaviour on an illegal transition.** `[decided]`
  *Decision:* the core raises a typed domain error carrying the current status and the
  requested status. The API maps it to **`409 Conflict`**. An unrecognised status string never
  reaches the core — it fails edge validation and returns **`422`**.
  *Why:* the two failures are different in kind. "This value is not a status" is malformed
  input; "you cannot go from `RECEIVED` to `DELIVERED`" is a well-formed request that the
  business rules refuse. Collapsing them into one code would make the illegal-transition test
  unable to distinguish a rule failure from a typo.
  *Rejected:* returning `400` for both — loses that distinction; raising a framework
  exception from the core — the core stays framework-free (`CLAUDE.md` §3).
  *Source:* R2, R18. *Answers:* Q2. *Exact codes confirmed in:* 6.2.

- **5.3 The publish-trigger rule.** `[decided]`
  *Decision:* `ORDER_READY` is emitted on a successful transition **into `BAKING`** and on a successful transition **into `READY`** — R5 taken literally. The condition is evaluated in the core status-transition operation, which reports back that an event must be emitted; the core never publishes. The adapter performs the publish. (Item 3.2 fixes the module this lives in; the rule itself is fixed here.)
  *Why:* it is the only reading that implements R5 as written. Evaluating the condition anywhere other than the core would put a business rule in a transport adapter, which `CLAUDE.md` §3 forbids.
  *Rejected:* publishing only on `BAKING` — it matches the business narrative but leaves an explicit requirement unimplemented, which a reviewer reading R5 will see immediately.
  *Source:* R5, `CLAUDE.md` §3. *Answers:* Q1.

- **5.5 Idempotency of assignment.** `[decided]`
  *Decision:* **assignment is idempotent per order.** The worker assigns a driver only to an
  order that has **no driver yet and has not been delivered**. Any other `ORDER_READY` event
  changes no state and is **acknowledged**, not requeued.
  The "not delivered" clause is one extra condition in the same guard, not a second mechanism.
  It covers the case where the first event *failed* to assign (no driver available) and sat in
  retry while the order was advanced to `DELIVERED`: the order still has no driver, so the
  "already assigned" check alone would let the worker assign one. With driver release tied to
  the `DELIVERED` transition (5.6), that driver would be marked `BUSY` after the only event
  that could ever release them has already passed — a driver leaking out of the pool
  permanently.
  *Why:* R5 guarantees two events per order on the normal path, so this is the default case rather than an edge case. One rule then also covers broker redelivery under at-least-once, a worker crash after marking a driver `BUSY` but before the ack, and a repeated `PATCH` — F3, F6 and F8 collapse into a single behaviour instead of three separate handlers.
  *Rejected:* requeueing the duplicate — it never becomes assignable, so it loops forever; this is the trap the requirement's dual publish sets up. Also rejected: re-dispatching, which assigns a second driver to an order already on its way, with no requirement asking for it.
  *Source:* R5, R6, R8. *Answers:* Q1. *Defines:* F3, F6, F8.

- **5.6 Driver release.** `[decided]`
  *Decision:* **the transition into `DELIVERED` releases the assigned driver back to
  `AVAILABLE`.** The rule lives in the core next to the transition rule, so a status update to
  `DELIVERED` writes both the order and the driver in one transaction (see 3.5). Releasing an
  order that has no assigned driver is a no-op, not an error.
  *Why:* the assignment never states this, but without it the driver pool is consumed once and
  never refilled — after as many orders as there are drivers, the system is permanently in the
  no-driver retry path. A reviewer registering one driver and pushing two orders through would
  see a system that has stopped working. `DELIVERED` is the natural point: it is the only
  terminal state in the lifecycle.
  *Rejected:* no release at all (faithful to the literal text, but produces a system that
  degrades to a stuck state during an ordinary demo); a dedicated driver-status endpoint —
  an unrequested feature, which `CLAUDE.md` §6 forbids.
  *Recorded as an explicit assumption* — it is behaviour the assignment does not specify.
  *Source:* R2, R8. *Answers:* Q4. *Defines:* F12.

- **5.8 Driver capacity — how many orders one driver can carry.** `[decided]`
  *Added during Phase 2*, because it had been settled implicitly rather than decided. R8 says
  the worker marks the driver `BUSY`, and R7 says it looks for an `AVAILABLE` driver — so a
  driver already carrying an order is not selectable. "One active order per driver" was
  therefore assumed by every decision from 4.3 onwards without ever being written down.
  *Decision:* **exactly one active order per driver.** A driver is `BUSY` from assignment
  until the order reaches `DELIVERED`, and is not selectable during that window.
  *Why:* it is what R7 and R8 describe together. Nothing in the assignment mentions capacity,
  load, or batching.
  *What would change if a driver could carry N orders* — recorded because the answer is
  "almost everything", and this is the kind of question an interviewer asks:
  1. `drivers.status` stops working as a two-value enum. Availability becomes
     `active_orders < capacity`, so the field turns into a counter or is derived after all —
     reopening 4.3 and A10.
  2. The partial unique index on `orders(driver_id) WHERE assignment_state = 'ASSIGNED'` (4.5)
     cannot express "at most N". The database backstop weakens from a uniqueness guarantee to
     a `CHECK` on a counter, which only holds if the counter is itself correct.
  3. The claim query in 8.9 changes from "pick an `AVAILABLE` driver" to "pick a driver under
     capacity". Row locking still works, but the invariant is no longer enforced by the
     schema.
  4. Release (5.6) stops being boolean — `DELIVERED` decrements a load instead of freeing a
     driver, and the driver may remain `BUSY` afterwards.
  5. F2 changes shape: the race is no longer "two orders take the last driver" but "two orders
     push one driver past capacity", which a unique index cannot catch.
  6. Capacity itself becomes a new field or configuration value, with its own validation.
  7. The "no driver available" test scenario becomes harder to construct — it requires
     saturating capacity rather than registering nobody.
  *Recorded as an explicit assumption.*
  *Source:* R7, R8.


## Topic 6 — API contract

- **6.4 Driver registration payload.** `[decided]`
  *Decision:* the request body carries **no status field**. Every driver is registered
  `AVAILABLE`. The response — and every later read — includes `status`, whose only two values
  are `AVAILABLE` and `BUSY`, exactly as R3 describes; the system, not the client, owns every
  transition between them.
  *Why:* a driver registered `BUSY` would be unreachable. Release only happens when the order
  a driver is assigned to reaches `DELIVERED` (5.6), and a driver registered `BUSY` has no
  order — so nothing in the system could ever free them. They would be permanently
  unassignable: the same silent-leak class of defect that A4 closed. Removing the field from
  the request removes the state.
  *Why this still satisfies R3:* the sentence is genuinely ambiguous between "the client picks
  one of these two" and "the field has these two values". This takes the second reading, and
  the field does exist with exactly those two values. It is recorded as an assumption rather
  than presented as the only possible reading.
  *Rejected:* accepting a client-supplied status — literal on the request side, but it admits
  a record the system can never repair.
  *Consequence worth naming:* driver status now has exactly one writer — the core assignment
  and release rules. No external actor can set it, so it cannot be driven into a state the
  business rules did not produce.
  *Source:* R3. *Answers:* Q5. *Eliminates:* F11.

- **6.5 Assigned-driver representation in `GET /orders/{id}`.** `[decided]`
  *Decision:* a **nested driver object** — `id`, `name`, `status` — and `null` when the order
  has no driver. The key is always present; it is never omitted. The response also carries
  `assignment_state`, `assigned_at` and `created_at`.
  *Storage is unaffected:* the relationship is stored once, as `orders.driver_id` referencing
  `drivers.id`. The nesting is a response shape assembled by the adapter, never a stored one.
  The core never sees this shape: its rules need only to know whether a driver is assigned,
  not who.
  *How it is read:* **two keyed reads** — fetch the order, then fetch the driver by
  `orders.driver_id`, and skip the second read entirely when it is `null`. Not a join: there
  is exactly one driver to fetch and it is a primary-key lookup, so the join buys only a
  round trip and costs a flattened row with prefixed columns to unpack.
  *The one cost, recorded:* two statements are not one snapshot, so a driver released between
  them could be reported as `AVAILABLE` on an order that still reads `ASSIGNED`. It is a
  display field on a read, not a rule input, so nothing decides anything on it.
  *Revisit if:* Q11 adds an order-list endpoint. Two keyed reads per order becomes N+1 the
  moment more than one order is returned, and a join stops being optional.
  *Why nested rather than an id:* A9 means there is **no** driver-read endpoint, so an id alone
  could not be resolved to a name anywhere in the system. The CLI would print a UUID and the
  reviewer could not tell who is delivering — information lost, not merely inconvenient.
  *Why `assignment_state` must appear:* without it, 8.3's decision to record dispatch failure
  on the order instead of a parked queue loses its entire point — the failure would be in the
  database but invisible to every interface anyone uses.
  *Rejected:* denormalising driver fields onto the order — a third copy of a fact already
  stored twice (4.3); omitting the key when unassigned — forces every consumer to test for key
  presence rather than for `null`.
  *Source:* R4. *Answers:* Q10.

- **6.6 Endpoints beyond the four required.** `[decided]`
  *Decision:* **exactly two endpoints beyond R1–R4, and no others** — `GET /orders` and
  `GET /health`. There is **no** driver listing and **no** driver-history endpoint. Each
  addition passes 1.1's ceiling test — remove it and a named DoD row fails — and nothing else
  proposed does.
  **`GET /orders`.** It returns a light representation —
  `id`, `customer_name`, `status`, `assignment_state`, `created_at` — **without** the nested
  driver object, newest first, capped at the 50 most recent, with no paging and no filters.
  *Why it is not scope creep:* the DoD grades "an easy-to-use console client", and R11 requires
  checking order statuses. Selecting an order by customer name requires a list; the only
  alternative is making a human retype a UUID, which fails the criterion the DoD actually
  names. The endpoint exists to serve a graded requirement, not to round out the API.
  *Why the list omits the driver:* it keeps 6.5's two-keyed-reads decision valid. Nesting a
  driver per row would turn a list of 50 into 51 queries; omitting it means the list is one
  query and the detail endpoint is unchanged.
  *Assumptions recorded:* the cap of 50 and "newest first" are chosen, not required; there is
  no paging because nothing needs it at this scale.
  **`GET /health`.** It returns `200` when the application can reach the database, `503`
  otherwise — no metrics, no version, no uptime, no per-dependency detail.
  *Why it is not scope creep:* it is infrastructure the deliverable requires, not a user-facing
  capability. R15 says the suite runs at launch, 11.2 says readiness is condition-based, and
  `CLAUDE.md` §5 forbids fixed sleeps. Those three can only hold together if something can be
  asked "are you ready" — and Compose's `depends_on: condition: service_healthy` needs a
  healthcheck command to ask it with. PostgreSQL and RabbitMQ ship theirs (`pg_isready`,
  `rabbitmq-diagnostics ping`); the API is the only link we have to supply.
  *Rejected:* a TCP port check — the port opens before the app can serve, and it reports an
  API that 500s on every request as healthy, which is worse than no check because it hides the
  failure; probing an existing endpoint such as `GET /orders/<random-uuid>` and accepting `404`
  — it works, but health would be defined by a not-found, and any later change to that
  endpoint silently changes what "healthy" means.
  *Resolved with 7.5 and 7.6 on 2026-08-09 — this replaces an open coupling recorded here.*
  `/health` reports on the **database only**. 7.6 makes a status update succeed when the broker
  is unreachable, so an API without a broker serves every endpoint correctly and a `503` would
  be false. Compose gates the broker on its own `rabbitmq-diagnostics ping` (11.2), so nothing
  is left unwatched. *Noted:* in plain Compose an unhealthy container is not restarted — a
  healthcheck only gates `depends_on: condition: service_healthy` — so this choice affects
  startup ordering, not runtime restarts.
  *Source:* R11, R14, `CLAUDE.md` §6, 1.1. *Answers:* Q11, Q12.

- **6.8 Authentication.** `[decided]`
  *Decision:* **none.** Every endpoint is open. Recorded in the README under assumptions:
  *"There is no authentication. The API targets an internal network and a demonstration
  environment; public exposure would require an auth layer, which is out of scope."*
  *Why:* the assignment mentions no users, tenants, roles, or tokens anywhere. Adding auth
  would be an unrequested feature (`CLAUDE.md` §6); leaving it unmentioned would be an
  unstated assumption (§7). Stating the absence satisfies both.
  *Source:* `CLAUDE.md` §7. *Answers:* Q15. *Deferred to:* FW9.


## Topic 7 — Broker contract

- **7.5 Publish versus commit ordering.** `[decided]`
  *Decision:* three parts.
  **Ordering** — the `ORDER_READY` publish happens **after** the database transaction commits,
  from the application layer, inside the request. The accepted failure is a **lost event**.
  **Record** — the same transaction that writes the status change also inserts a row into an
  `outbox` table (`event_id`, `event_type`, `payload`, `created_at`, `published_at` nullable).
  A successful publish sets `published_at`. **There is no relay** — nothing acts on unpublished
  rows.
  **Attempt** — publishing uses **publisher confirms**, so failure is detectable. A publish
  that fails on an established connection is retried **exactly once, after reconnecting**;
  failure to establish the new connection is final. Each attempt is bounded by an env-tunable
  timeout (10.4), so a `PATCH` blocks for at most twice that bound.

  *Why after commit:* publishing inside the transaction would hold it open across a network
  call to a second system. `UPDATE orders …` takes a row-level exclusive lock that PostgreSQL
  releases only at `COMMIT`, so the lock — and the pooled connection — would be held for a full
  broker round trip, which confirms make a round trip by definition. The worker's claim path
  (8.9) writes the same rows and would block behind it. That turns a broker fault into a
  database fault: two dependencies that are independent by design become coupled by
  implementation. Committing first keeps the transaction local and short.

  *Why the phantom event was not preferred, despite being benign:* published-then-rollback is
  genuinely mild here — 5.5's guard reads "no driver yet and not delivered" and never reads
  status, so a phantom assigns a driver to an order still at `PREPARING`; the client's retry
  then succeeds, the second event is a no-op, and `DELIVERED` still releases the driver. The end
  state is correct. It is also the more orthodox choice — at-least-once with an idempotent
  consumer — and 5.5 supplies that consumer for free. It was rejected on the locking argument
  above, not on its outcome. **This is the closest call in the record.**

  *Why an outbox table with no relay:* it buys the durable half of FW2 for a fraction of its
  cost. The insert is atomic with the status change, so a lost event leaves a permanent,
  queryable row instead of an `ERROR` line that scrolls past — and FW2 is reduced to writing
  the relay loop.
  *This is an explicit exception to 1.1.* Delete the table and no named DoD row fails, so the
  ceiling test says do not build it. It is built anyway, by decision, because it records the one
  failure this design cannot repair. What 1.1 forbids is an item left unbuilt and unrecorded to
  be "kept in mind" — not a costed decision to spend.

  *The cost this design does not repair, stated in full:* R5 publishes twice, so a single
  failure at `BAKING` is covered by the publish at `READY`, and the reconnect above removes the
  most common failure — a stale connection — before that. But if the broker is unreachable
  across **both** transitions, the event is never published and **no driver is ever dispatched
  for that order**. It reaches `DELIVERED` unassigned. Two things soften this and neither
  repairs it: the order shows `assignment_state = PENDING` while its status advances, which is
  4.4's designed signal and is visible in `GET /orders/{id}`, `GET /orders` and the CLI; and the
  outbox holds a row with `published_at IS NULL` naming exactly which event was lost.
  **Recorded as an explicit assumption and stated in the README.**

  *Rejected:* **publish before commit** — see above. **A transactional outbox with a relay
  (FW2)** — it removes the window entirely and stays out of scope: a relay is a third process
  with its own failure modes, and testing it requires stopping and restarting the broker
  mid-suite, consuming one of the four scenarios R18 allows. **A reconciliation sweeper** — a
  loop republishing orders stuck at `BAKING`/`READY` with `assignment_state = PENDING`. It works
  and costs less than a relay, but it makes `assignment_state` answer two questions at once:
  "no driver yet" is also the normal state of an order legitimately retrying (F7), so the
  sweeper would republish healthy orders and race 8.2's dead-letter retry, resetting its attempt
  budget on every pass. Separating the two needs a threshold timestamp — reopening 4.8 — and a
  marker, at which point it is an outbox. **A `published` flag on the order** — wrong
  granularity: R5 emits two events per order and one boolean cannot say which was lost. Its only
  possible reader was the sweeper; the outbox row records the same fact at the right
  granularity.
  *Source:* R5, `CLAUDE.md` §3, §7. *Answers:* Q21. *Defines:* F4 with 7.6. *Constrains:* 3.3,
  3.4, 3.5, 3.7, 7.2, 7.3, 10.4. *Partly answers:* 7.7 — the publisher's reconnect behaviour
  only; connection lifetime and the consumer side stay open.

- **7.6 Behaviour when the broker is unreachable during a status update.** `[decided]`
  *Decision:* the `PATCH` **succeeds** — `200` with the updated order. The publish failure is
  recorded as one `ERROR` log line and the unpublished `outbox` row (7.5). No `5xx`, and no
  field on the order marking it.
  *Why not an error code:* the commit already happened, so the status genuinely changed. A
  `5xx` would report a failure that did not occur — and the client's natural repair makes it
  worse: the order is already at `BAKING`, and 5.1 makes re-sending the current status illegal,
  so the retry returns `409`. The caller would be told "failed", act correctly on it, and be
  told "illegal". An error the caller cannot recover from is worse than a success that is
  partially incomplete.
  *Why nothing is written to the order:* `assignment_state = FAILED` is the obvious candidate
  and it breaks — the publish at `READY` may still succeed, after which the worker assigns a
  driver, requiring a `FAILED → ASSIGNED` transition that 4.4 does not have. `PENDING` on an
  order whose status has advanced already reads as "no driver is coming", which is the same
  information without a new state.
  *Rejected:* `503` — above; `202 Accepted` — it describes the request as pending when the
  state change is already durable, and nothing later completes it.
  *Source:* R5, `CLAUDE.md` §5. *Answers:* Q21. *Defines:* F4 with 7.5.


## Topic 8 — Worker

- **8.1 Ack / nack policy.** `[decided]`
  *Decision:* four cases, exhaustively:
  1. **Assigned successfully** → ack, after the transaction commits.
  2. **Nothing to do** (order already assigned, or already delivered — 5.5) → ack.
  3. **No driver available** → `reject` with `requeue=false`, which routes the message to the
     retry path in 8.2. Never `requeue=true`.
  4. **Retry budget exhausted** → ack, having recorded `assignment_state = FAILED` (8.3).
  The ack always follows the database commit, never precedes it: a message is only considered
  handled once its effect is durable.
  *Why:* acking before the commit loses work on a crash in the window between them; requeueing
  a message that can never succeed loops forever. Every path here terminates in either a
  durable state change or a bounded retry.
  *Rejected:* `nack(requeue=true)` on the no-driver path — it re-delivers instantly, producing
  a hot loop that saturates CPU and floods the log; this is the trap the requirement's wording
  invites.
  *Source:* R10, DoD "Broker & Consumer". *Unexpected exceptions are covered by 8.4.*

- **8.2 Retry strategy for the no-driver case.** `[decided]`
  *Decision:* **fixed-delay retry via a dead-letter exchange and a queue-level TTL.** The main
  queue dead-letters to a wait queue that has **no consumer**; the wait queue carries
  `x-message-ttl` and dead-letters back to the main queue. A rejected message therefore sits
  idle for the TTL and returns automatically. The delay is env-tunable (10.4).
  *Why:* it is stock RabbitMQ — two topology declarations, no plugin, no timer in our code, no
  dependency. A fixed delay is exactly what a queue-level TTL expresses well.
  *Rejected:* the `rabbitmq_delayed_message_exchange` plugin — its advantage is per-message
  delay, which only matters for exponential backoff; the cost is a custom broker image and a
  plugin version pinned to the broker version, a coupling that breaks silently on upgrade, and
  delayed messages that are invisible in the management UI. Per-*message* TTL — expiry is
  evaluated only at the head of the queue, so one long-lived message blocks shorter ones
  behind it. Sleeping inside the handler — the message stays unacked, prefetch 1 means the
  whole queue stalls for one order, and the broker eventually drops a consumer that holds a
  delivery too long. Republishing from the consumer — moves timing into our code and still
  needs an attempt counter carried in the message.
  *Source:* R9, DoD. *Answers:* Q6. *Constrained by A1.*

- **8.3 Retry bound and terminal state.** `[decided]`
  *Decision:* retries are **capped** (env-tunable, 10.4). On exhaustion the worker sets
  `assignment_state = FAILED` on the order, logs at error level, and **acks** the message.
  There is **no parked or dead-letter queue** holding the failure.
  *Why:* the failure belongs in the domain, not in broker internals. Recorded on the order it
  is visible through `GET /orders/{id}` and the CLI — where someone actually asks "what is
  happening with my order" — instead of only in the RabbitMQ management UI. It also removes a
  queue we have no tooling to drain: without replay (FW5) a parked message is unreachable
  weight. An unbounded retry was rejected because it has no observable terminal state: "no
  drivers for an hour" would appear as an endless drip of warnings, and F7 would have nothing
  to assert against.
  *Rejected:* unbounded retry (no terminal state, no testable outcome, silent operational
  failure); parking in a dead-letter queue (invisible to every interface the reviewer uses,
  and irrecoverable without FW5).
  *Accepted cost, recorded as an assumption:* an order that exhausts its budget is not
  reassigned if a driver registers later. Re-dispatch is deliberately not built.
  *Source:* R9, R17. *Answers:* Q6. *Defines:* F7.

- **8.5 Consumer concurrency.** `[decided]`
  *Decision:* **one worker replica in compose, prefetch 1.** This is a deployment choice, not
  a correctness mechanism — correctness comes from 8.9. The README states that scaling to N
  replicas requires no code change.
  *Why:* a single consumer keeps the integration tests deterministic (`CLAUDE.md` §5) and
  keeps message order per queue trivially preserved. Ordering is not load-bearing anyway,
  since every rule in 5.5 and 5.6 is idempotent.

  *Why prefetch 1 specifically, and not only the replica count:* `prefetch` is a flow-control
  window — the number of unacknowledged messages the broker will hand a consumer — and not a
  parallelism setting. Under 2.4's synchronous consumer the callback still handles one message
  at a time whatever the window is, but a wider window is not therefore without effect: with 1
  the broker withholds the next message until the previous `ack` reaches it and the worker idles
  for that round trip, while with N the next message is already buffered. **A wider window
  raises throughput under two conditions — messages arriving faster than they are processed, or
  a delivery/ack round trip that is significant against the processing time.** This system meets
  neither. The `PATCH` carries 7.5's publisher-confirm round trip and is driven by a person at a
  CLI menu (9.2), so the API produces more slowly than the worker consumes and the queue sits
  empty between events; and broker, worker and database share one Compose host, so the round
  trip is a fraction of a millisecond against a claim-and-assign transaction of a few. A window
  wider than the backlog is inert, and pipelining a negligible latency saves a negligible
  amount.
  *The one case that does produce a backlog, and it argues for 1 rather than against it:* 8.2's
  TTL expiry can return several messages at once, each a no-driver rejection — a claim query and
  no writes. The round trips a wider window would save there are worth single-digit
  milliseconds, against condition-based test timeouts measured in seconds (12.4). Set against
  that saving: messages held in a client buffer are unacked and therefore absent from the queue
  depth, so a wide window hides the backlog from every tool that reports one, and turns 8.2's
  cycle from one legible attempt per line into a burst in the `docker compose up` output that
  8.6's log line is written for.
  *Stated without inflation:* neither setting costs anything measurable at this scale. 1 is
  chosen for observability, and because it is already what fair dispatch needs on the day FW7
  adds replicas — not because throughput required it.
  *Scope of the window:* it governs the main queue only — 8.2's wait queue has no consumer.

  *Rejected:* multiple replicas by default — weakens test determinism to demonstrate a scale
  the assignment never asks for.
  *Source:* R14, DoD. *Answers:* Q13. *Constrains:* 2.4.

- **8.6 The mock dispatch notification.** `[decided]`
  *Decision:* **one structured log line at `INFO`**, emitted after the assignment transaction
  commits, with a fixed field set:
  `event=dispatch_notification order_id=… driver_id=… driver_name=… at=…`
  *Why:* the requirement's own word is "logs". A fake HTTP call needs a stub service and a
  compose entry — a whole piece of infrastructure to simulate something the brief only asks to
  record. A stored notification table adds a table with no reader, already parked as FW8.
  *Rejected:* a stub HTTP receiver; a persisted notification record.
  *Explicitly not a test assertion target — this corrects an earlier note on this item.* A test
  that reads log output couples to a string, and `CLAUDE.md` §5 requires testing behaviour and
  contracts rather than implementation details; a log line is an implementation detail.
  What tests assert is the observable outcome: the driver is `BUSY`, the order is `ASSIGNED`,
  and `GET /orders/{id}` returns the driver. The log line exists for the human reading
  `docker compose up`, which is a real job — just not an assertion's job.
  *Source:* R8. *Answers:* Q7. *Constrains:* 8.7.

- **8.9 Concurrency-safe driver claiming.** `[decided]`
  *Decision:* the claim uses **`SELECT … FOR UPDATE SKIP LOCKED LIMIT 1`** over available
  drivers, inside the **same transaction** that marks the driver `BUSY` and writes the
  assignment. A **uniqueness constraint** in the schema (4.5) backs it as the last line of
  defence. Safety therefore does not depend on how many consumers run.
  *Why:* it costs one SQL clause — no layer, no dependency, no added concept — and in exchange
  the system stops being correct only by deployment accident. `SKIP LOCKED` also means two
  concurrent claimants take two *different* drivers rather than one blocking on the other, so
  contention costs nothing.
  *Rejected:* relying on the single-consumer deployment as the safety argument — it fails
  silently the moment anyone scales the worker, including a reviewer running
  `--scale worker=2`; advisory locks — a second locking concept for no gain; an optimistic
  read-then-update retry loop — more code and more failure paths than the database primitive.
  *Source:* R8, DoD. *Answers:* Q13. *Defines:* F2. *Constrained by A1.*


## Topic 9 — CLI

- **9.2 Menu actions.** `[decided]`
  *Decision:* five actions —
  1. place an order
  2. register a driver
  3. list orders and select one (by customer name, via `GET /orders` — A14)
  4. update the selected order's status — the user picks from the five values
  5. quit
  *Why status update is included:* the entire behaviour of the system is dispatch triggered by
  `BAKING`. Without it the CLI demonstrates half a product — create an order, register a
  driver, then reach for `curl` to make anything happen. The DoD asks for a client that
  "allows manual interaction with the running API services", not for the three calls named in
  R11, and the demo path (1.2) does not run without it.
  *Why the menu offers all five statuses rather than only the legal next one:* because the chain
  is strictly linear (A3), exactly one of the five is legal at any moment, and a single
  `Advance to BAKING` action was the obvious simplification. It was rejected on two counts. It
  would place the transition sequence 5.1 owns inside the client, which 3.6 forbids; and it
  would make the `409` path unreachable from the CLI, so a reviewer could never see the system
  refuse an illegal transition through the interface they were handed. Offering all five keeps
  the client free of business knowledge and makes 5.2 demonstrable rather than merely described.
  *Accepted cost:* at any moment four of the five choices return `409`. The error is displayed,
  not hidden — and showing it is part of the point.
  *Source:* R11, R19. *Answers:* Q19.

- **9.6 Windows and TTY behaviour.** `[decided]`
  Three points of friction between a Windows development host and a Linux container target,
  each with a cheap answer:
  1. **Line endings — already solved.** `.gitattributes` exists and sets `* text=auto eol=lf`,
     which stores and checks out LF even on Windows. Without it, a CRLF shell script inside a
     Linux container fails with `\r: command not found`, which costs half an hour to diagnose.
     *Note:* the file's own comment says Windows checkouts "stay CRLF-friendly", which
     describes the opposite of what `eol=lf` does — the setting is right, the comment should be
     corrected when the file is next touched.
  2. **Entrypoint scripts — none will be written.** Readiness is handled by healthchecks and
     `depends_on` (11.2, A15), so no `wait-for-db` script is needed. Fewer files, and point 1
     stops being able to bite at all.
  3. **TTY for the CLI.** `docker compose run` allocates a TTY by default and works from
     PowerShell and CMD. From **Git Bash** on Windows it commonly fails with
     `the input device is not a TTY`. This is documented in the README — run from PowerShell or
     CMD, or prefix with `winpty` — rather than worked around in code.
  *Dependent on 9.3:* if the CLI runs on the host against a published port instead of in a
  container, point 3 disappears entirely, at the cost of requiring a local Python environment.
  *Source:* R11, development environment. *Answers:* Q20.


## Topic 11 — Docker Compose

- **11.3 How the test suite is auto-executed.** `[decided]`
  *Decision:* a **one-shot test service** in compose that waits for the stack to be healthy
  (11.2), runs the suite, prints an unmissable PASS/FAIL summary to the `docker compose up`
  output, and exits.
  *Why:* it needs no wrapper script, its output lands in the same stream the reviewer is
  already watching, and it reuses the readiness mechanism the other services already need.
  *Rejected:* an entrypoint hook inside the API container — it couples the API's lifecycle to
  the test run and hides the results inside another service's log.
  *Source:* R15, DoD. *Answers:* Q8.

- **11.4 Behaviour when tests fail.** `[decided]`
  *Decision:* plain `docker compose up` does **not** tear the stack down on failure; the
  failure is visible as the test service's non-zero exit and its printed summary. The README
  additionally documents `docker compose up --abort-on-container-exit --exit-code-from tests`
  as the CI-style gate that propagates the exit code.
  *Why:* the two goals are mutually exclusive in one command — `--exit-code-from` stops every
  container as soon as the tests finish, which would leave nothing running to demonstrate
  (R11). Giving each goal its own documented command satisfies both instead of half-satisfying
  each.
  *Rejected:* making `--exit-code-from` the default launch command — it makes the CLI
  deliverable undemonstrable straight after launch.
  *Source:* R15, R19. *Answers:* Q8.

- **11.5 Behaviour after tests pass.** `[decided]`
  *Decision:* the stack **stays up**. Only the test service exits.
  *Why:* R11 requires a live system to drive from the CLI, and the demo path (1.2) begins
  where the test run ends.
  *Source:* R11, R15. *Answers:* Q8.

- **11.6 Test isolation from the live environment.** `[decided]`
  *Decision:* the suite runs **against the live stack**, not an isolated copy. Determinism is
  achieved by unique data per test plus the guarantee of a clean start; the README states the
  boundary explicitly: *the suite is deterministic on a clean `docker compose up`; re-running
  it against a stack that has been driven manually may observe drivers you registered
  yourself — reset with `docker compose down -v`.*
  *Why:* the only genuinely shared state is the driver pool, which is global by nature — a
  "no driver available" scenario cannot be scoped to one test's data. Solving that with full
  isolation means a second database, a second vhost, and a second API+worker pair: double the
  environment to cover the single case of re-running after manual use, which a one-line reset
  already covers. Testing the exact system that ships is also worth more than testing a
  faithful copy of it.
  *Rejected:* a fully isolated test environment — real determinism, but doubles the compose
  file and moves the tested system away from the delivered one.
  *Accepted cost, recorded as an assumption:* determinism here is conditional, and
  `CLAUDE.md` §5 states it unconditionally. The condition is written down rather than glossed
  over.
  *Source:* R15, R18, `CLAUDE.md` §5. *Answers:* Q8.

- **11.7 Volumes and persistence.** `[decided]`
  *Decision:* **no named volumes.** The database and broker write to their containers' own
  filesystems, so `docker compose down` returns the environment to a clean state and the next
  `up` starts empty. The compose file carries a short **explanatory comment** — not commented-
  out YAML — stating that the absence is deliberate and pointing at a README section that
  gives the exact lines to add if persistence is wanted.
  *The mechanics, for the record:* stopping with `Ctrl-C` does not lose data either way, since
  the containers still exist; the difference appears only at `down`, which deletes the
  containers and their filesystems. With a named volume, data would survive `down` and require
  `down -v` to clear.
  *Why:* R15 runs the suite on **every** launch, and the highest-value scenario — no driver
  available, the message retries, a driver registers, assignment happens — requires a starting
  state with no available drivers. The driver pool is global, so persisted data from a
  reviewer's own session makes that scenario fail on a perfectly healthy system. The visible
  result is a red suite at launch, which is the worst possible first impression and the hardest
  to attribute correctly.
  *Rejected:* named volumes plus an isolated test stack (a second API and worker against a
  `pizza_test` database and its own vhost) — genuinely unconditional determinism, and the right
  answer if persistence were required, but it doubles the running services to protect a
  scenario that `docker compose down` already protects; named volumes plus test-owned cleanup —
  the suite would then delete or park the reviewer's drivers on every launch, which defeats the
  point of persisting them.
  *Why a comment and not commented-out YAML:* `CLAUDE.md` §6 rejects commented-out blocks. A
  comment that explains a decision is not the same thing, and it answers the reviewer's
  question ("did they forget volumes?") exactly where the question arises.
  *This is what keeps A8 valid:* 11.6 accepted conditional determinism on the promise of a
  clean start. Without persistence, that promise costs one documented command.
  *Source:* R15, `CLAUDE.md` §5, §6. *Answers:* Q17.


## Topic 13 — Documentation and deliverables

- **13.5 `docs/ai-log.md`.** `[decided]`
  *Decision:* **nothing to decide — the file already exists and defines itself.** It specifies
  a five-column table (`Date`, `Area`, `Agent proposed`, `Decision`, `Why`), a closed set of
  decisions (`Rejected`, `Changed`, `Accepted — unverified`), and explicit rules for when a row
  is and is not warranted. That format is adopted as-is.
  *State:* the first real row was recorded on 2026-08-07 (the rejected FW11 entry), and the
  example rows were removed, as the file's own instructions require once real entries exist.
  *Working rule for the rest of the project:* a row is added only for what becomes
  **unrecoverable** when the session ends. Design proposals that were rejected or changed
  during planning are already preserved in this file's `Rejected:` lines, so they do not earn
  a second record; rejections that leave no trace anywhere else do.
  *Source:* `CLAUDE.md` §6.

- **13.6 Assumptions register.** `[decided]`
  *Decision:* the assumptions live as a **one-line index** in this file — the assumption
  stated, and a pointer to the decision that holds its reasoning. No line restates a decision.
  Entries marked **†** are copied into the README's *Assumptions* section in U13; the rest are
  internal to planning and stay here.
  *How it stays current — and this is the whole mechanism:* by carrying no reasoning. An index
  line can only go stale if the assumption itself changes, and changing an assumption is a
  decision, which updates its record and its line together. The previous form — a paragraph
  per assumption — drifted for exactly the opposite reason: it duplicated the reasoning, so
  A12 went on describing a `LEFT JOIN` after 6.5 had decided on two keyed reads.
  *Rejected:* **a separate document** — 21 index lines do not earn a file, and a reader
  following the pointer would have to leave the file that holds the answer.
  **Full paragraphs, as before** — the form that produced the drift.
  *Source:* `CLAUDE.md` §7. *Realised by:* the Assumptions section of this file.


## Topic 14 — Git and process

- **14.5 Whether `CLAUDE.md`, `.claude/`, and the plans directory are committed.** `[decided]`
  *Decision:* **committed, and named in the README.** `CLAUDE.md`, `.claude/settings.json`,
  `.claude/commands/`, `.claude/plans/` and `docs/ai-log.md` all ship.
  `.claude/settings.local.json` stays ignored — it is machine-local by definition. The plans
  remain in `.claude/plans/` rather than moving to `docs/`: the agreement, the permission
  boundary, the protocol command and its output are one exhibit, and splitting them weakens
  both halves.
  *Why:* the brief permits AI tools and requires the design to be defensible in the interview
  (R23). How the tool was governed is therefore part of the answer, not a disclosure to
  manage. The deny list in `settings.json` and the approval rule in `CLAUDE.md` §1 are its
  substance — they show constraint, which is what separates using the tool from being carried
  by it.
  *The condition that keeps this an asset:* the README must stand alone. Trade-offs,
  assumptions and out-of-scope are summarised there, and the planning record is linked once as
  optional depth. If a reviewer must open the planning documents to understand a trade-off,
  volume has become a requirement instead of an offer.
  *Rejected:* **excluding the planning record** — it is the only evidence that the questions
  were enumerated before they were answered, and R21's "coherent narrative" is thinner without
  it. **Moving the plans to `docs/planning/`** — better placement for engineering documents
  read on their own, and it breaks the grouping that is the whole reason to commit them.
  *Source:* R21, R23, `CLAUDE.md` §4. *Requires:* a "How this repository was built" section in
  the README, written in U13.


---

## Assumptions

**An index, not a record.** Each line states the assumption and points at the decision that
holds its reasoning. Nothing here restates a decision: a fact written in two places is a fact
that will eventually disagree with itself — which is exactly what happened while this section
carried full paragraphs.

**†** marks the ones that go to the README's *Assumptions* section in U13 — the places where
the assignment was silent or genuinely ambiguous and a reading had to be chosen.

| # | Assumption | Recorded in |
|---|---|---|
| **A1** | The stack pair is RabbitMQ + PostgreSQL, chosen together | 2.1, 2.2 |
| **A2** † | `ORDER_READY` fires on both `BAKING` and `READY`; assignment is idempotent per order | 5.3, 5.5 |
| **A3** † | The status chain is strictly linear, single-step and forward-only; `DELIVERED` is terminal | 5.1, 5.2 |
| **A4** † | Drivers are released — the transition into `DELIVERED` returns them to `AVAILABLE` | 5.6 |
| **A5** | One worker replica with prefetch 1, but claiming is safe in code, not by deployment | 8.5, 8.9 |
| **A6** | "Assignment states" is a second axis on the order, not a separate entity | 4.4 |
| **A7** | Fixed-delay retry via a dead-letter exchange and TTL, capped; exhaustion marks the order `FAILED` | 8.1, 8.2, 8.3 |
| **A8** | The suite runs at startup against the live stack, and the stack stays up afterwards | 11.3–11.6 |
| **A9** | No driver-history endpoint — the data exists, the endpoint is not built | 6.6, FW3 |
| **A10** † | Drivers are always registered `AVAILABLE`; the request carries no status field | 6.4 |
| **A11** † | `items` is a list of strings, with arbitrary but explicit bounds | 4.2 |
| **A12** | `GET /orders/{id}` returns a nested driver object, or `null` | 6.5 |
| **A13** † | Exactly one active order per driver | 5.8 |
| **A14** † | `GET /orders` exists — light list, newest first, capped at 50 | 6.6 |
| **A15** † | `GET /health` exists — `200` when the database is reachable, `503` otherwise | 6.6, 7.5 |
| **A16** | The mock dispatch notification is one structured `INFO` log line, and not a test assertion target | 8.6 |
| **A17** † | "3–4 automated tests" means four integration scenarios; unit tests are separate and uncounted | 12.6 *(partial)* |
| **A18** | The CLI covers status updates as well as the three operations R11 names | 9.2 |
| **A19** † | The environment is disposable — no named volumes, `docker compose down` is the reset | 11.7 |
| **A20** † | No authentication or authorisation | 6.8, FW9 |
| **A21** | Windows-to-Linux friction is handled by configuration and documentation, not code | 9.6 |
| **A22** † | `ORDER_READY` is published after the commit; if the broker is unreachable the `PATCH` still returns `200` and the event is lost | 7.5, 7.6 |
| **A23** † | Every event is recorded in an `outbox` table, but nothing replays unpublished rows | 7.5 |
| **A24** † | "Microservice" means separate processes and containers, not separate codebases — the API and the worker are two entrypoints into one package over one database | 3.3 |

*Superseded:* A11 previously read "a list of typed objects — `name`, `quantity`, `toppings`".
It was narrowed on 2026-08-07 when 1.1's ceiling test was applied to it; the structure is now
FW11. A12 previously described the nested driver as produced by a `LEFT JOIN`, which
contradicted 6.5's decision to use two keyed reads. **6.5 is authoritative**; the register no
longer names a read mechanism at all. A15 was narrowed on 2026-08-09: it previously required
the broker to be reachable for `/health` to return `200`, which 7.6 made false.
