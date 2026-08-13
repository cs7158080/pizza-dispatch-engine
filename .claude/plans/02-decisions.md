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
| 1 — Scope and time | 1.1, 1.2, 1.3, 1.4, 1.5 | — |
| 2 — Stack and tooling | 2.1–2.10 | — |
| 3 — Architecture and layering | 3.1–3.8 | — |
| 4 — Data model | 4.1–4.9 | — |
| 5 — Business rules | 5.1–5.8 | — |
| 6 — API contract | 6.4, 6.5, 6.6, 6.8 | 6.1, 6.2, 6.3, 6.7, 6.9 |
| 7 — Broker contract | 7.1–7.7 | — |
| 8 — Worker | 8.1, 8.2, 8.3, 8.5, 8.6, 8.9 | 8.4, 8.7, 8.8 |
| 9 — CLI | 9.2, 9.3, 9.6 | 9.1, 9.4, 9.5 |
| 10 — Configuration | 10.1–10.5 | — |
| 11 — Docker Compose | 11.1–11.11 | — |
| 12 — Testing | 12.1, 12.2, 12.3 | 12.4–12.10 *(12.6 partial)* |
| 13 — Documentation | 13.5, 13.6 | 13.1–13.4 |
| 14 — Git and process | 14.1–14.7 | — |
| **Total** | **88** | **22** |

Phase 3 for a unit does not begin while an item that unit depends on is open (`CLAUDE.md` §2,
and Part 4 of `03-roadmap.md`).

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

- **1.2 The demo path.** `[decided]`
  *Decision:* **one sequence, thirteen steps, two terminals, one tool.** It is the path the
  README documents, and the only one it documents.

  | # | Terminal | Action | What it shows |
  |---|---|---|---|
  | 1 | 1 | `docker compose up` | stack starts, suite runs, PASS/FAIL summary (11.3) |
  | 2 | 2 | `docker compose run --rm cli` | the menu (9.3) |
  | 3 | 2 | place an order | `RECEIVED`, `assignment_state: PENDING` |
  | 4 | 2 | list orders, select by customer name | R11 without retyping a UUID (A14) |
  | 5 | 2 | advance to `PREPARING` | `200` |
  | 6 | 2 | advance to `BAKING` | publish (5.3); **T1:** worker warns "no driver", rejects to the wait queue (8.1, 8.2) |
  | 7 | 2 | register a driver | `AVAILABLE` (6.4) |
  | 8 | 1 | wait one retry cycle | **T1:** the dispatch line (8.6) |
  | 9 | 2 | re-read the order | nested driver, `ASSIGNED`, `assigned_at` (6.5) |
  | 10 | 2 | advance to `READY` | second publish; **T1:** worker acks, changes nothing (5.5) |
  | 11 | 2 | attempt `BAKING` again | `409` (5.2) |
  | 12 | 2 | advance to `DELIVERED`, re-read | `COMPLETED`, driver back to `AVAILABLE` (5.6) |
  | 13 | 2 | quit, then `docker compose down` | clean reset (11.7) |

  *Why the missing-driver path is demonstrated by hand, and the one thing it depends on:* R9 is
  the most interesting behaviour in the assignment, and step 6 buys it for free — simply by not
  registering a driver first. It depends on there being no `AVAILABLE` driver when step 6 runs,
  and 11.6 runs the suite against the same live stack over a global driver pool.
  **Recorded as a dependency on 12.1, not as a requirement on it.** The likely risk-ranked set
  leaves the pool empty already: successful dispatch, no-driver retry and duplicate-event
  scenarios all end with the driver `BUSY`, and an illegal-transition scenario registers no
  driver at all. A scenario dedicated to release at `DELIVERED` would break it — and adding a
  trailing step to that scenario purely so the demo works is a test doing work for a non-test
  reason, which `CLAUDE.md` §5 forbids. If 12.1 chooses such a scenario, this item reopens.
  *What removes the silence, independently of the above:* the README states **both** outcomes of
  step 6 — if a driver is already available the assignment is immediate, and that is correct
  behaviour rather than a failure. A step that degrades legibly needs no guarantee behind it.

  *Why one order and not two:* step 12's re-read already returns the driver nested with
  `status: AVAILABLE` (6.5), which is the proof that 5.6 released them. A second order proves
  the same fact a second time for three more menu actions.

  *What is deliberately not in the path:*
  **The broker-down path (7.6)** — the strongest interview material in the record, and it needs
  `docker compose stop` plus a look at the `outbox` row, so it needs psql or a published port.
  It goes to the README trade-offs (13.4), where it costs nothing and reopens no item.
  **The OpenAPI document at `/docs`** — the demo stays one tool. 9.3 freed 11.8 of any CLI
  dependency and this item does not put one back.
  **The `409`, by contrast, is in** — after `READY` it is one menu action, and it turns 5.2 from
  something a reviewer reads about into something they trigger (9.2).

  *Step 0 and the last step:* there is **no step 0**. `git clone` then `docker compose up`, which
  is what 10.5 already asserts a reviewer must be able to do; `.env.example` is the override
  surface, not a precondition. Teardown is `docker compose down` **without** `-v`, per 11.7.
  *Noted:* the README sentence quoted in 11.6 says `down -v`; it predates 11.7's decision to use
  no named volumes, and U13 writes `down`.

  *Constrains, and these are the reason this item is decided before them:*
  **11.1** — `attach: false` on postgres and rabbitmq, so terminal 1 carries api, worker and
  tests only. **10.4 with 8.3** — the retry TTL must be short enough that step 8 feels immediate
  (single-digit seconds), and `TTL × cap` must exceed the time a person needs to complete step 7;
  a floor of 60 s. Without it the order reaches `FAILED` in front of the reviewer and reads as a
  defect. **10.3 / 10.5** — compose supplies working defaults; no step 0. **13.2 / 13.3** — the
  diagram's covered sequence is steps 3–12, which is also every path R17 names.
  *Source:* R11, R17, R19. *Constrained by:* 5.1, 5.2, 5.3, 5.5, 5.6, 6.5, 6.6, 9.2, 9.3,
  11.3–11.7. *Constrains:* 10.3, 10.4, 11.1, 13.1, 13.2, 13.3. *Depends on:* 12.1.

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
  `infrastructure`, so the read path reaches the database only through a port.
  *Source:* R20, `CLAUDE.md` §3, §6. *Constrained by:* 2.2, 2.4, 3.1, 3.5, 6.5, 8.9.
  *Constrains:* 3.4. *Realised in:* U5.

- **2.6 Test framework and clients.** `[decided]`
  *Decision:* **`pytest`, with `httpx` as the only client.** No broker client and no in-process
  client: 12.3 fixed the suite at HTTP only, and 11.6 runs it from its own container against the
  live stack, so `fastapi.testclient` is excluded by those items rather than declined here.
  *Why `httpx` over `requests`:* it ships `py.typed`, so 2.8's checker needs no `types-requests`
  stub, and it applies a 5 s default timeout where `requests` applies none.
  *Source:* R18, DoD "Test Automation". *Constrained by:* 2.4, 11.6, 12.3. *Feeds:* 2.10.

- **2.7 Broker client library and retry mechanism.** `[decided]`
  *Decision:* **`pika`**, the same client in both services.
  The retry half of this item is not a library question: 8.2 put fixed-delay retry in the broker
  topology — "no plugin, no timer in our code, no dependency" — so only the client name remains,
  and 2.4 settled it in passing when it recorded that `pika` is not thread-safe and handed the
  obligation to 7.7.
  *Noted for U6:* `pika` offers `BlockingConnection` and no automatic reconnection. 7.7 owns
  connection lifetime and reconnection on both sides; no library is added for it.
  It also ships no type information, so the first `import pika` fails `mypy src tests`. **2.8
  owns the remedy** — a per-module `ignore_missing_imports`, not a global loosening of `strict`.
  U1 deliberately did not write it early, because 2.8 confirms that list on the first run rather
  than guessing it, and an unnecessary override is something mypy never flags.
  *Rejected:* `aio-pika` — excluded by 2.4. `kombu` — an abstraction over AMQP at exactly the
  point where 8.2 needs direct topology declaration.
  *Source:* R9, R10, `CLAUDE.md` §6. *Constrained by:* 2.4, 8.2. *Constrains:* 7.7.

- **2.8 Formatter, linter, type checker.** `[decided]`
  *Decision:* **`ruff` for formatting and linting, `mypy` in `strict`**, both configured in
  `pyproject.toml`, both run from a local virtual environment before every commit:
  `ruff format .` while working, then `ruff check .` and `mypy src tests`.
  Ruff's rule set is **exactly `E4`, `E7`, `E9`, `F` and `I`** for import order, and nothing else,
  written as `select = ["E4", "E7", "E9", "F", "I"]`.
  *Named with `select` rather than left to the default, corrected on 2026-08-11.* This item
  previously read "its default — `E4`, `E7`, `E9`, `F` — plus `I`", written as
  `extend-select = ["I"]`. **That description is false for the pinned ruff 0.16.2:** its default
  set contains `UP` among others — counted, 414 rules across 38 families were active, against the
  61 this item intended — so `extend-select` was enforcing rules nobody chose. It
  surfaced mid-step in U2, where `UP047` demanded PEP 695 type parameters for a generic function —
  a rule that fires only because 2.9 pinned `requires-python = ">=3.12"`, which ruff reads as its
  target version, and which stayed silent through U1 because U1 wrote no generic function. Two
  decided items met in a place neither had looked at. Naming the five codes makes the set what
  this item chose, in any ruff version.
  *What is given up, stated plainly:* whatever the wider default would have caught. The loss is
  real and it is accepted, because a rule set nobody selected — and that changes with a tool
  upgrade — cannot sit inside a Definition of Done that must hold at every commit (14.7).
  *What this frees rather than decides:* `UP047`'s suggestion, 3.12's `def f[T: Base](...)` in
  place of a `TypeVar`, stays available as a choice instead of a demand. U2 keeps the `TypeVar`
  form its plan was written with.
  *Not `extend-select` with an `ignore` list:* it names the rules switched **off**, so every ruff
  upgrade may add one more that has to be discovered by a failing command and then silenced.
  `select` names what is on, which is the property that does not decay.
  *The earlier rejection of `select = ["E", "F", "I"]` stands untouched:* spelling `E` in full
  additionally enables `E501`, and `ruff format` cannot shorten a long string, URL or comment — so
  `ruff format --check .` and `ruff check .`, two of 14.7's Definition-of-Done commands, would
  disagree about the same file, and a `line-length` this item never chose would be forced. `E4`,
  `E7` and `E9` named individually do not contain `E501`, which is why the corrected form is not
  that rejected one.
  *`E501` selected on 2026-08-12, reversing the last sentence above.* The paragraph is kept
  because the rest of it holds; what it got wrong is treating the two commands as contradicting
  each other when they **divide the work**. `ruff format` owns code layout and already imposes 88
  columns on everything it can reformat, so the `line-length` this item believed it never chose
  has been in force from the first commit. `E501` covers only what the formatter will not touch —
  strings, URLs, comments and docstrings — and three of those four are ours to write short.
  *What forced it:* twenty docstring lines written during U3 sat between 89 and 94 columns and no
  command noticed; a review did. This item chose `select` for "the property that does not decay",
  and that was decay.
  *The accepted cost is the one the rejection named, unchanged:* a URL or string literal that
  genuinely cannot be shortened has no automatic fix and takes a `# noqa: E501`. The repository
  holds none today, and the rule set is now `E4`, `E7`, `E9`, `E501`, `F`, `I`.
  **Ruff's file scope excludes Markdown**, written as `extend-exclude = ["*.md"]` under
  `[tool.ruff]`. Ruff 0.16 formats fenced `python` blocks inside `.md` files by default, so
  `ruff format --check .` — one of 14.7's four commands — fails on this file's pseudo-code
  snippets, whose aligned comments and elided bodies are written to be read, not executed.
  *Not reformatting the snippets,* which edits decided records to satisfy a formatter meant for
  source, and subjects every future documentation example to it; *and not narrowing the
  command's path,* which 14.7 fixes.
  `strict` covers `src/pizza/` and `tests/` alike. A per-module `ignore_missing_imports` is added
  only for a dependency that ships no type information — `pika` is the expected case, and the
  list is confirmed on the first run rather than guessed.
  *Why `strict` and not the default:* 3.4 defines five `Protocol` ports, and a `Protocol` is
  structural — nothing declares conformance, so without a static check a renamed adapter method
  surfaces only at runtime, in the worker, under a message. 2.5's `Mapped[...]` argument assumes
  the same checker.
  *Left to others:* whether the checks also gate `docker compose up` — 12.10; whether they run in
  CI — follows 14.3. **No `pre-commit`:** a framework, a config file and git hooks, to run two
  commands that §8.3 already requires per step.
  *Source:* `CLAUDE.md` §8. *Constrains:* 2.9, 2.10. *Left to:* 12.10, 14.3.

- **2.9 Dependency management and pinning.** `[decided]`
  *Decision:* **`pyproject.toml` is the single declaration; two fully pinned requirements files
  are generated from it and committed.**

  ```toml
  [project]
  requires-python = ">=3.12"
  dependencies    = [ ... ]          # the list 2.10 approves
  [project.optional-dependencies]
  dev = [ ... ]
  [build-system]
  requires      = ["setuptools>=68"]
  build-backend = "setuptools.build_meta"
  ```

  ```
  uv pip compile pyproject.toml --universal --python-version 3.12 -o requirements.txt
  uv pip compile pyproject.toml --universal --python-version 3.12 --extra dev -o requirements-dev.txt
  ```

  *The problem this item exists to solve.* 3.7 asked for a dependency layer "before the source is
  copied, so a source edit does not reinstall — the mechanism is 2.9's". `pip install .` needs the
  source present, so under a `pyproject.toml`-only declaration **no such file exists** and the
  cached layer is unobtainable. A generated requirements file is a file that can be copied alone:

  ```dockerfile
  COPY requirements.txt .
  RUN  pip install -r requirements.txt     # source-independent — this is the answer
  COPY src/ ./src/
  RUN  pip install --no-deps .
  ```

  *Why generated rather than hand-written.* `pyproject.toml` can pin the seven direct dependencies
  but not the eighteen transitive ones, which are the ones nobody chose and nobody watches.
  Writing them by hand would be maintaining a resolution a tool computes in one second, and it
  would put the same fact in two hand-edited places — 13.6's failure mode exactly. A derived file
  cannot disagree with its source, because it is regenerated rather than edited.
  *What it buys, and it is a graded row:* the reviewer builds the image on their machine, possibly
  weeks later. Without a lock the resolution is recomputed then, and a breaking release anywhere in
  the transitive tree fails a build in which not one line of our code changed. It is the hardest
  failure here to diagnose, because everyone who built earlier cannot reproduce it.

  *Why `uv pip compile` and not `pip-compile`.* The generator is a local preference and the
  artifact is not: `uv pip compile` emits a plain pip requirements file, so the image, the reviewer
  and any future CI see `pip` alone, and `pip-compile` would regenerate the same format if `uv`
  disappeared. `uv` is therefore a developer tool and **not a dependency** — it appears nowhere in
  2.10. One thing does turn on it: both generators resolve for the host platform by default, so a
  lock built on Windows for a Linux image can carry Windows-only packages or omit Linux-only ones.
  `--universal` resolves across platforms with environment markers, and `pip-tools` has no
  equivalent.

  *Rejected — `pip install .` with a BuildKit cache mount and no generated file.* The strongest
  alternative, and it adds nothing to the list. It recovers much of the build speed, since the
  wheel cache survives between builds. It gives no reproducibility at all — every build re-resolves
  — and its cache lives in the build host rather than in a committed artifact, so on the reviewer's
  first build there is no cache at all.
  *Rejected — exact pins on the seven direct dependencies, no lock.* The right cut if this item
  were ever cut: it defends most of the risk at zero cost and is defensible in an interview. It
  leaves transitive releases uncovered and gives no cached layer.
  *Rejected — `uv.lock`.* uv's own format requires uv to consume, which would put the tool in the
  image; `uv pip compile` keeps the artifact tool-neutral.
  *Rejected — `poetry`* (restructures the project for seven modules); ***`setuptools` over
  `hatchling`*** — the default, it detects src-layout unaided, and nothing is weighed;
  ***extras over PEP 735 `[dependency-groups]`*** — the group form is cleaner in principle since
  dev dependencies never reach published metadata, but this package is never published, and
  `pip install ".[dev]"` works on every pip while `--group` needs pip 25.1.

  *`requires-python = ">=3.12"`.* R12's floor is 3.10; one version is fixed for the local
  environment and the base image alike, which closes the class of failure where `mypy` passes on
  one and fails on the other.
  *Why 3.12 and not 3.13.* Nothing in the design distinguishes them: no decision uses a feature
  one has and the other lacks, both are inside upstream security support, and both carry wheels
  for all seven runtime distributions. Which of the two is pinned is a **convention**, and 1.3
  gives a convention one line rather than a rationale manufactured after the fact.
  *Why not 3.14 — the upper bound, decided here rather than borrowed.* 3.14 defers the evaluation
  of annotations (PEP 649/749) and exposes them through a new `annotationlib`. Every
  infrastructure library on 2.10's list reads annotations at runtime: Pydantic builds its
  validators from them and FastAPI derives dependency injection and the OpenAPI document from
  them (2.3), and SQLAlchemy's declarative mapping reads `Mapped[...]` to type each column, which
  is half of 2.5's reason for choosing an ORM at all. **Stated at its real size, this is risk
  appetite and not breakage:** 3.14 shipped in October 2025 and all three have supported it for
  months. The point is that a four-day assignment does not take the release that changed the one
  mechanism its entire stack is built on, for nothing it needs. A second consequence, smaller: a
  3.14 base makes stdlib `uuid7()` free and reopens 4.7.
  *An earlier attribution, corrected.* This item previously read "4.7 already declined the 3.14
  pull". It did not. 4.7 declined **a third-party dependency for `uuid7()`** and left 3.14
  explicitly open — "if U1 settles on a 3.14+ base image it becomes free and can be
  reconsidered" — while deferring the version itself to this item. Each record pointed at the
  other and neither decided the bound; the paragraph above decides it.
  *Failure mode, recorded:* a stale lock. Adding a dependency without regenerating leaves the image
  without it, and `--no-deps` will not complain. **The declaration and the generated files are
  always the same commit** — §7's rule for documentation, applied to a derived artifact. The window
  is narrow because §6 requires approval for any new dependency.
  *Constrains 11.9:* the base image is a `python:3.12` family, and layer ordering is 11.9's; this
  item supplies only the fact that a source-independent file exists.
  *Source:* R14, R20, `CLAUDE.md` §3, §6. *Constrained by:* 2.8, 3.3, 3.7.
  *Constrains:* 2.10, 11.9. *Realised in:* U1.

- **2.10 Full dependency list for approval.** `[decided]`
  *Decision:* **ten libraries, approved as one list, declared once in `pyproject.toml` during
  U1.** The approval is a single up-front act, not an accumulating one: no further approval round
  occurs inside a unit.

  | Runtime — one set for all three services (3.7) | Why | Owner |
  |---|---|---|
  | `fastapi` | the API framework | 2.3 |
  | `pydantic>=2` | edge schemas and `extra="forbid"`; imported directly, so declared directly | 2.3, 4.2 |
  | `uvicorn` | **the ASGI server — decided here** | 2.10 |
  | `sqlalchemy>=2.0` | declarative ORM; the bound is 2.5's semantics | 2.5 |
  | `psycopg[binary]` | the synchronous PostgreSQL driver | 2.5 |
  | `pika` | the synchronous AMQP client | 2.7 |
  | `httpx` | **the CLI's HTTP client — decided here**; the suite uses the same one | 2.10, 2.6 |

  | Dev group | Why | Owner |
  |---|---|---|
  | `pytest` | the runner | 2.6 |
  | `ruff` | format and lint | 2.8 |
  | `mypy` | type checking in `strict` | 2.8 |

  No stub packages: every entry ships type information except `pika`, which 2.8's override rule
  covers.

  *`uvicorn` and not `uvicorn[standard]`.* The extra adds `uvloop`, `httptools`, `watchfiles`,
  `websockets` and `python-dotenv`. `uvloop` accelerates the event loop, and 2.4 recorded that
  there is no concurrency here to exploit — one CLI user (9.2) and four sequential scenarios;
  `watchfiles` serves `--reload`; websockets are unused. Five packages for nothing.
  *Rejected:* `hypercorn`, `granian` — both sound, both needing explanation to a reviewer, neither
  buying anything over FastAPI's documented default.

  *One `httpx` for both consumers.* 12.3 handed 2.6 "one HTTP client, and nothing else", and 3.6
  made the CLI a thin HTTP adapter. Two libraries would be two lines for one job.
  *Rejected:* `requests` — no `py.typed`, so 2.8 would need `types-requests`; and no default
  timeout, where `httpx` applies 5 s.

  *Two conditional lines, and why they are approved now rather than later.* Two open items can each
  require a library, and neither is in U1:

  | Conditional | Decided by | Unit | Outcome |
  |---|---|---|---|
  | `pydantic-settings` | 10.2 — a typed settings object or raw environment reads | U2 | **dropped.** 10.2 chose `pydantic` alone, so no dependency is added and neither lock file changes |
  | `alembic` | 4.6 — migration tool, `create_all` at startup, or an init script | U5 | **dropped.** 4.6 chose `create_all` from a one-shot service, so no dependency is added and neither lock file changes |

  They enter `pyproject.toml` in the same commit as the decision that requires them, and
  `uv pip compile` is re-run. **"Not incremental" governs the act of approval, not the file being
  frozen** — what it forbids is a fresh approval round mid-unit, which conditioning them now
  prevents. Withholding them until 10.2 and 4.6 close would leave this item open and U1 blocked on
  it. There is no separate `python-dotenv` either: 10.3 has the application parse no `.env` file at
  all, and Compose reads it for interpolation only.

  *Not on the list, and each has an owner:* `uv` — a local tool, not a dependency (2.9);
  `pip-tools` — dropped with the generator (2.9); `pre-commit` — 2.8; `pytest-asyncio`, `aio-pika`,
  `asyncpg`, `greenlet` — 2.4; `celery` / `kombu` — 2.7; `tenacity` or any retry library — retry is
  broker topology (8.2); `structlog` — 8.6 is one `key=value` line and stdlib `logging` covers it;
  `testcontainers` or the docker SDK — 12.3 rejected container control from the suite;
  `black` / `isort` / `flake8` — replaced by `ruff`; `requests` — above.

  *Carried forward to 11.9:* `psycopg[binary]` has no musl wheel, so an Alpine base breaks this
  list. 2.5 recorded it; it is repeated here because the list is where it will be read.
  *Source:* `CLAUDE.md` §6. *Constrained by:* 2.3, 2.5, 2.6, 2.7, 2.8, 2.9, 3.6, 3.7, 12.3.
  *Constrains:* 11.9. *Both conditional lines are now closed, each by declining:* 10.2 and 4.6.
  *Realised in:* U1.


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
  │   ├── db/                  models, repositories, unit of work, outbox, schema creation (4.6)
  │   ├── broker/              publisher, topology declaration, serialization (7.3)
  │   └── clock.py             SystemClock
  │
  └── entrypoints/          # layer 3, driving — imports: application; wires only at main.py
      ├── api/                 main · deps · schemas · errors · routers/{orders,drivers,health}
      ├── worker/              main · consumer
      ├── cli/                 3.6
      └── schema/              main — the one-shot schema creator (4.6)
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
  rather than a copy of the repository. 3.7 has since decided exactly that, so both defences now
  hold — but the layout gave the guarantee without depending on it, which is why it was chosen
  before 3.7 was made.
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

- **3.4 The interfaces the core exposes to adapters.** `[decided]`
  *Decision:* **five `Protocol` ports in `application/ports.py`**, plus 3.5's `UnitOfWork`, not
  restated here. Repositories reach a use case as `uow.orders`, `uow.drivers`, `uow.outbox`;
  `Clock` and `EventPublisher` are injected directly. `domain/` declares no ports (3.1). No
  `IdGenerator` — 4.7 removed it. No read port — see below.

  ```python
  # application/ports.py
  class Clock(Protocol):
      def now(self) -> datetime: ...                 # timezone-aware UTC (4.8)

  class OrderRepository(Protocol):
      def add(self, order: Order) -> None: ...       # returns nothing — 4.7
      def get(self, order_id: UUID) -> Order | None: ...
      def save(self, order: Order) -> None: ...
      def list_all(self) -> list[Order]: ...         # newest first; docstring carries it

  class DriverRepository(Protocol):
      def add(self, driver: Driver) -> None: ...
      def get(self, driver_id: UUID) -> Driver | None: ...
      def save(self, driver: Driver) -> None: ...
      def claim_next_available_driver(self) -> Driver | None: ...   # 8.9 locks, 5.4 orders

  class OutboxWriteFailed(Exception): ...

  class OutboxStore(Protocol):
      def add(self, event: OrderReadyEvent) -> None: ...
      def mark_published(self, event_id: UUID, now: datetime) -> None: ...   # raises it

  class PublishFailed(Exception): ...

  class EventPublisher(Protocol):
      def publish(self, event: OrderReadyEvent) -> None: ...        # raises PublishFailed

  # application/events.py   — OrderReadyEvent, a frozen dataclass; its fields are 7.2's
  # application/queries.py  — OrderDetail(order: Order, driver: Driver | None)
  ```

  *Why the event type is in `application/`, not `domain/`.* Ownership, not layering — a stdlib
  dataclass passes 3.1's test either way. 3.2 has the transition return a flag,
  `TransitionResult.must_publish`, not an object, so `domain/` never builds an event; 4.7
  generates `event_id` in the application layer; both consumers are ports in `ports.py`. The DDD
  alternative — the entity appending events, the use case draining them — would force `domain/`,
  but reaching it means reopening 3.2 and giving entities the mutable buffer 3.5 and 2.4 both
  rule out. *This corrects U6*, which held the type and cannot: `application/` may not import
  `infrastructure`. Serialization is untouched by this and stays there (7.3), where U5 writes it.

  *Why no read port, though 2.5 said one was needed.* Its actual requirement — `queries.py`
  never touching `infrastructure` — is met through the `UnitOfWork`. A **new** port is what is
  not needed: 6.5's two keyed reads are `orders.get` and `drivers.get`, which the write paths
  already require, and `GET /orders` adds one method to a repository that exists. `queries.py`
  returns `OrderDetail` and the API schemas nest and select — 6.5 and 3.2 together — which also
  keeps 6.6's field list off the port.

  *Why a failed publish raises.* A `bool` is silent by default: ignore it and an unpublished
  event is marked published. `PublishFailed` sits beside its port, not in `domain/errors.py` —
  an unreachable broker is not a violated rule. The use case catches it, not the router, since
  7.6 returns `200` either way.

  *`OutboxWriteFailed`, added 2026-08-11 — the same reason, and the pattern was already in this
  item.* The line below fixes that a failed `mark_published` is "logged, not raised" and leaves
  its **type** unnamed, which leaves the use case with `except Exception`. That is the broad
  swallowing `CLAUDE.md` §6 rejects, and here it is worse than untidy: a bug of ours lands in the
  same net and leaves a row asserting the event was lost when it was published, so the record 7.5
  built precisely to be trusted would lie. A narrower catch is unavailable in `application/` by
  construction — the exception actually raised belongs to a database library 3.1 forbids this
  layer to import — so the type is declared here and U5's adapter translates into it, exactly as
  U6's does for `PublishFailed`. Found while writing U3's plan.
  *The placement rule the two now share, stated so it is not read as habit:* an error naming a
  **port's** failure lives beside that port. `domain/errors.py` holds business outcomes, which
  cross every layer to the client and are enumerated by one registered handler (5.2, 3.1); a port
  error travels one layer inward and stops, and each has exactly one call site that catches it by
  name. **The condition that would change it:** an application-layer error caught in more than one
  place, or something needing to enumerate them, earns `application/errors.py`. Neither holds
  today, and a file grouping two unrelated exceptions for tidiness would have no reader.

  *One line each:* 7.5 publishes after the commit, so `mark_published` runs in a second
  transaction and **the `UnitOfWork` must be re-enterable**, each `__enter__` opening a fresh
  `Session` (2.5); a failure there is logged, not raised, since nothing acts on unpublished rows.
  Identifiers are plain `UUID`, no `NewType` — a static check on our own code in a two-entity
  codebase, and 4.7's sample is corrected to match. `Protocol` not `ABC`, following 3.5. A
  missing row returns `None`, which the use case turns into a domain error that 5.2 maps.
  `claim_next_available_driver` returns a locked driver without marking it; the use case marks
  and saves in the same transaction (8.9). **No lifecycle on `EventPublisher`** — the composition
  root holds the concrete adapter (3.1) — which *constrains* 7.7 rather than waiting on it.

  *Source:* `CLAUDE.md` §3 ("explicit typed boundaries"), §2 Phase 3. *Constrained by:* 2.4, 2.5,
  3.1, 3.2, 3.5, 4.7, 4.8, 5.4, 6.5, 6.6, 7.5, 7.6, 8.9. *Constrains:* 7.7. *Corrects:* U3/U6,
  2.5's "a port of its own", 4.7's sample line. *Realised in:* U3.

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

- **3.7 Number of Docker images.** `[decided]`
  *Decision:* **one Dockerfile, one build context, two stages.** A `runtime` stage carries the
  installed package and the runtime dependency set; a `test` stage derives from it and adds the
  dev dependencies and `tests/`. Four compose services: api, worker and cli run the `runtime`
  image and differ only in `command`; the one-shot `tests` service (11.3) builds `target: test`.

  ```
  Dockerfile — one context, two stages
    FROM python:3.x-slim AS runtime
      <dependency layer>           # before the source is copied, so a source edit does not
                                   # reinstall — the mechanism is 2.9's, not this item's
      COPY src/ ./src/             # 3.3's one package
      RUN  pip install .           # installed, never run from the working directory
      USER app                     # not root
    FROM runtime AS test           # derived, not a sibling
      <dev dependency layer>
      COPY tests/ ./tests/

  compose
    api · worker · cli   → runtime, one command each
    tests                → build target: test
  ```

  *Why the package is installed and not copied-and-run:* 3.3 chose src-layout, under which the
  directory holding the package is not importable. An image doing `COPY . /app` and running from
  the working directory cannot `import pizza` at all, and the one escape — `PYTHONPATH=/app/src`
  — reconstructs exactly the failure src-layout was chosen to prevent: a suite passing against
  the source tree while the installed distribution is broken. **This is not a judgement left
  open; 3.3 settled it and this item records it.** What 3.3 left genuinely free is the *number*
  of images, on which it deliberately took no position.

  *Rejected — an image per service* (api / worker / cli / tests). Its real use is services that
  are separate repositories or have genuinely divergent runtimes; neither holds here. 3.3 made
  this one package with two processes over one schema, so four near-identical Dockerfiles would
  imitate a microservice split the architecture does not have — and the per-service delta is one
  or two pure-Python wheels: the API publishes to the broker (7.5, 7.6) so it needs the AMQP
  client, and the worker writes through the same core (3.8) so it needs SQLAlchemy. The union is
  almost the whole set. Four build contexts and four caches would buy megabytes.

  *Rejected — a single stage holding everything.* Shipping `pytest` inside the image the API
  runs is the one thing here a production review would reliably flag, and not for size: it is a
  supply-chain and attack-surface habit, and the habit is what carries to the next project where
  the dev dependency is a compiler or a cloud SDK holding credentials. The second stage costs
  about five lines and one `target:` key.

  *Why `test` derives from `runtime` rather than standing beside it:* 11.6 already paid for the
  principle when it ran the suite against the live stack — *"testing the exact system that ships
  is also worth more than testing a faithful copy of it."* A derived stage means the suite
  exercises the same installed package the services run. Two sibling stages would test a
  parallel build of it, which is the copy 11.6 declined.

  *Stated plainly, because it is a real cost:* the `runtime` image is the union of three
  services' needs, so the CLI — a thin HTTP adapter by 3.6 — carries SQLAlchemy and the AMQP
  client it never imports. That is inherent in one package with one dependency set, and it is
  accepted rather than engineered around.

  *The build steps this item owns*, per the inventory's "shapes the build steps": dependency
  layer before source so the cache survives a source edit; a `.dockerignore`; a pinned `slim`
  base; a non-root `USER`; and **exec-form `CMD`**, which is not cosmetic here — shell form puts
  a shell at PID 1 and the signal never reaches the process, so whatever 8.8 decides about
  shutting down without losing an in-flight message would be unimplementable. This item supplies
  the precondition; 8.8 still owns the behaviour.

  *What FW2 costs, closing 7.5's question through 3.3:* the relay is `entrypoints/relay/main.py`
  plus a compose entry running the `runtime` image with a different command. **No new image, no
  new stage, no change to this record.**
  *Closes 9.3's deferral:* the CLI needs the package and an HTTP client, which `runtime` is.

  *Feeds 2.9, and corrects the axis it was written on:* the inventory offers 2.9 "one dependency
  set or one per service". Neither is the answer — the split this item needs is **runtime versus
  dev**, one set for all three services plus a dev group for the suite. 2.9 still owns
  declaration, pinning, and whether there is a lockfile.
  *Left to others:* where the image is tagged so four services do not build four times, and the
  `build`/`target` keys themselves — 11.1. Healthchecks and readiness ordering — 11.2.
  Environment variables reaching the containers — topic 10.
  *Source:* R14, R15. *Constrained by:* 3.3, 7.5, 9.3, 11.3, 11.6. *Constrains:* 2.9, 11.1.

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

- **4.1 Order entity fields.** `[decided]`
  *Decision:* nine fields, each fixed by the item beside it — `id` (4.7), `customer_name` and
  `address` (R1), `items` (4.2), `status` (5.1), `assignment_state`, `driver_id`, `assigned_at`
  (4.4), `created_at` (4.8). Checked against 6.6's light list and 12.2's assertion tables: neither
  needs a field this list lacks.
  *Nothing was weighed here.* By the time this item was reached every field had an owner; the
  residue — the shape the fields sit in — is 4.9.
  *Source:* R1, R4. *Constrained by:* 4.2, 4.3, 4.4, 4.7, 4.8, 5.1. *Realised in:* U3.

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
  *Amended by 4.9 on 2026-08-10, in two places.* **`FAILED` is not terminal.** R5 publishes twice, so
  an order whose first event exhausted its retry budget can still be assigned by the second —
  `FAILED → ASSIGNED` occurs on an ordinary path, and the arrow notation above does not show it.
  **`COMPLETED` is not written unconditionally.** The transition into `DELIVERED` writes it unless the
  state is `FAILED`, which survives; the reasoning is 4.9's and is not restated here.
  *Source:* assignment §4. *Answers:* Q3.

- **4.5 Uniqueness and integrity constraints.** `[decided]`
  *Decision:* **three tables, two constraints that are not keys, and no index beyond the primary
  keys and the one 8.9 requires.**

  ```
  orders
    id                uuid         PK
    customer_name     text         NOT NULL
    address           text         NOT NULL
    items             jsonb        NOT NULL
    status            text         NOT NULL    CHECK — the five values of 5.1
    assignment_state  text         NOT NULL    CHECK — the four values of 4.4
    driver_id         uuid         NULL        → drivers.id
    assigned_at       timestamptz  NULL
    created_at        timestamptz  NOT NULL

    UNIQUE (driver_id) WHERE assignment_state = 'ASSIGNED'             -- 8.9's backstop
    CHECK  (assignment_state <> 'ASSIGNED'
            OR (driver_id IS NOT NULL AND assigned_at IS NOT NULL))    -- 4.9's backstop

  drivers                              outbox
    id          uuid         PK          event_id      uuid         PK
    name        text         NOT NULL    event_type    text         NOT NULL
    status      text         NOT NULL    payload       jsonb        NOT NULL
                CHECK — AVAILABLE|BUSY   created_at    timestamptz  NOT NULL
    created_at  timestamptz  NOT NULL    published_at  timestamptz  NULL
  ```

  No `server_default` on any column: identity is generated in the application (4.7) and every
  timestamp is one `Clock.now()` read (4.8, 7.2), so a database default would be a second clock
  no test can control.

  *The organising principle, and everything below follows from it:* **the schema enforces what a
  single writer cannot guarantee for itself under concurrency. Every rule one writer can hold
  stays in the layer that owns it.** Without it each line below is taste; with it, the two
  constraints are the two places the application genuinely cannot be trusted alone.

  *Why the uniqueness constraint is partial and not plain.* 4.4 never clears `driver_id`, so
  `UNIQUE (driver_id)` would say a driver may carry one order in their entire history — it would
  reject the second order of a driver who was correctly released, which is ordinary behaviour.
  Conditioning it on `assignment_state = 'ASSIGNED'` is what 4.4 bought when it kept the two axes
  independent, and 5.8 already writes it in this form.

  *Why 4.9's backstop is one-directional, which is not the obvious shape.* The tempting form is
  the biconditional — assigned exactly when there is a driver — and it is **false against a state
  this design produces deliberately**: an order whose event was lost (7.5) reaches `DELIVERED`
  having never been dispatched, and 4.9 writes `COMPLETED` on it with `driver_id` still null. The
  implication that holds in every direction the design allows is the narrow one: `ASSIGNED` implies
  a driver and a time. It was checked against all six reachable combinations, including
  `FAILED → ASSIGNED`, which R5's second publish makes an ordinary path.

  *Enum storage — `text` with a `CHECK`, not a native PostgreSQL `ENUM` type.* Three enum types
  are three schema objects, and adding a value to one is `ALTER TYPE`, which does not compose with
  the rest of the DDL inside a transaction — an operational cost for exactly the protection a
  `CHECK` already gives. The `CHECK` also prints the legal values in `\d orders`, so the schema
  documents itself to a reviewer reading it directly. 4.9 fixed a plain `Enum` with explicit string
  values and had the mapper write `.value`, so the column holds that string and the repository owns
  the conversion — no ORM-level enum type is involved in either direction.

  *`items` as `text[]`.* The column says what the data is, and the annotation the repository already
  carries — `Mapped[list[str]]` — becomes a statement the database enforces rather than one it
  merely permits: `jsonb` accepts an object, a number or a scalar in that column, and nothing would
  notice. The earlier tie-breaker, one JSON type in the schema instead of two, is withdrawn: it
  counted type names rather than concepts, and `payload` is a document while `items` is a list of
  strings whichever spelling is chosen. Nothing reads `items` (4.2), so no query distinguishes them
  and this is a statement about correctness at the boundary, not about access.
  *Rejected:* **`jsonb`** — above. **`VARCHAR(n)` on the text columns** stays rejected for the
  reason below: a type does not drift, a bound written twice does.

  *`payload` as `jsonb` — 7.3's recommendation, accepted on its own argument.* The single question
  the table is ever asked is which orders lost their dispatch, and 7.2 gives the row no `order_id`
  column of its own, so that question is `payload ->> 'order_id'` over rows with
  `published_at IS NULL`. Byte-exactness has no consumer, and FW2's relay would rebuild the message
  from the content.

  *No `VARCHAR(n)`, anywhere.* 100 and 200 are 4.2's bounds and are enforced at the edge.
  `CLAUDE.md` §3 puts a rule in exactly one place; a length written in the schema as well is the
  same rule in two, and the copy that drifts is the one nothing exercises.

  *One foreign key, and no second one.* `orders.driver_id → drivers.id`, with no `ON DELETE`
  clause: nothing in the system deletes a driver, so the default — refuse — is the correct
  behaviour rather than an unconsidered one. The outbox has no foreign key to `orders`: its link to
  the order lives inside the payload, and a constraint there would make the evidence of a failure
  depend on the row it is evidence about.

  *No index beyond the primary keys and the constraint above.* Four candidates were weighed and all
  four fail 1.1's ceiling test under 11.7's disposable environment, where the volume that would
  justify an index never arrives: `orders(created_at)` for 6.6's newest-first list — FW4 already
  holds the volume story; `drivers(status, created_at)` for 8.9's claim query — a handful of rows,
  scanned; `orders(driver_id)` for driver history — FW3 is not built (A9), and the partial unique
  index covers the assigned rows anyway; `outbox(published_at) WHERE published_at IS NULL` for a
  relay that does not exist (A23).

  *What the schema does not protect — and the three kinds of "not" are different, which is the
  point of stating them together:*

  | Not protected | Kind | Where the defence is |
  |---|---|---|
  | The ghost driver — `drivers.status = BUSY` with no `ASSIGNED` order | **Impossible.** No cross-table `CHECK` exists and 4.3 rejected a trigger | 4.3's single-transaction invariant, held by 3.5's `UnitOfWork` |
  | An illegal status transition (5.1) | **Impossible.** A `CHECK` sees one row and never its previous value | `domain/`, where 4.9 put `_NEXT` |
  | The bounds on `items`, `customer_name`, `address` (4.2) | **Possible, and forbidden** — `CLAUDE.md` §3, one rule one place | Edge validation (2.3) |
  | That an outbox row was written at all | **Possible, and not worth it** — a constraint can forbid a row, never require one | Nothing. 12.3 already records this as the lowest-consequence failure in the design, because A23 gives the table no reader |

  Collapsing these into one list of "things we chose not to constrain" would be the misleading
  version: two of them were never available, one is available and would be a defect, and only the
  fourth is a judgement about cost.

  *Rejected:* **a native `ENUM` type per enum** — above. **`VARCHAR` bounded to 4.2's limits** —
  above. **A biconditional `CHECK` on the assignment triple** — false against the `COMPLETED`
  without a driver that 7.5's lost event produces. **`text[]` for `items`** — a near-tie, decided on
  having one JSON type in the schema instead of two. **A `CHECK` on `outbox.event_type`** — one
  legal value, written from a class constant (7.2). **Any of the four indexes** — above.
  *Accepted cost:* the two constraints are the only automated defence 4.5 supplies, and neither is
  loaded by the test suite — 12.3 fixed the suite at HTTP with no database client, so an integrity
  violation would surface as a `500` rather than as a named assertion. The uniqueness constraint is
  a last line of defence behind 8.9's row lock; it is expected never to fire.
  *Source:* R8, DoD "Broker & Consumer". *Constrained by:* 4.1–4.4, 4.7–4.9, 5.1, 5.8, 7.2, 7.5,
  8.9. *Accepts the recommendation of:* 7.3. *Realised in:* U5.

- **4.6 Schema creation strategy.** `[decided]`
  *Decision:* **`Base.metadata.create_all()`, run once by a one-shot Compose service, before any
  other service starts.** No migration tool and no dependency.

  ```
  postgres                                    healthcheck is 11.2's
      ↓  condition: service_healthy
  schema        entrypoints/schema/main.py — builds the Engine, calls
                infrastructure/db/schema.py:create_schema(engine), exits 0
      ↓  condition: service_completed_successfully
  api · worker · tests
  ```

  The service runs the `runtime` image with a different `command` — **no new image and no new
  stage**, which is the arrangement 3.7 already recorded for FW2's relay. 11.1's service list
  already reserves the slot ("any init/migration service"); this item fills it and fixes the
  contract, while **11.1 wires it and 11.2 owns the healthcheck it waits on**.

  *Verified before choosing, because otherwise the choice is forced rather than made:* every
  constraint 4.5 decided is expressible in SQLAlchemy metadata — the partial unique index through
  `postgresql_where`, the row-level `CHECK`, `jsonb`, `timestamptz`, the foreign key. Had one
  required hand-written DDL, `create_all` would have been unavailable and this record would read
  differently.

  *Why a service of its own, and the race it removes is not hypothetical.* `create_all` inspects
  the catalogue and then issues plain `CREATE TABLE` for what it did not find. Two processes that
  both inspect before either creates therefore both proceed, and the loser gets "relation already
  exists" — so running it from the api and the worker, which Compose starts together, is a genuine
  race rather than a tidiness argument. **Stated at its real size:** the window is small and the
  failure intermittent, which makes it worse than a deterministic one, not better — it would pass
  every time it was tried here and fail on the reviewer's machine, inside the single command R15
  is graded on.
  *Why not "the api creates it and the worker waits":* 3.8 made them peers over one core. A
  `worker → api` dependency is a hierarchy with no other reason to exist, and it would read as an
  architectural claim rather than as a way around a race.

  *What this also answers, which is half the item:* the inventory asks how a container behaves when
  it starts before the database is ready. It does not start. If PostgreSQL is not healthy the
  one-shot does not run; if schema creation fails, nothing downstream starts and the failure is one
  service's non-zero exit rather than three services emitting connection errors at once, which is
  the form that hides its own cause. **No step waits on a duration** — `CLAUDE.md` §5 forbids it,
  and every edge above is a condition.

  *Why not Alembic — and the argument is not 1.1's ceiling test.* That test governs delivered scope,
  and applying it to build machinery is a mistake this record already made once and withdrew
  (`docs/ai-log.md`, 2026-08-10). Alembic is neither scope nor hygiene: it is the operational
  ability to change a schema that holds data which must survive the change. **11.7 removed the
  object of that ability** — with no named volumes the schema is created from empty on every launch,
  so there is never a second version and `versions/` would hold exactly one revision describing a
  capability nothing uses. It also does not solve the ordering problem: `alembic upgrade head` needs
  the same one-shot service from the same place, so the topology above is what either choice buys.
  *What is given up, and it is not nothing:* a reviewer of a backend assignment may expect
  migrations, and their absence can read as a shortcut rather than a decision. The README states it
  as a trade-off with the condition that reverses it, and the reversal is cheap — `Base.metadata` is
  already the single source, so `alembic revision --autogenerate` produces the first revision from
  it (2.5). **FW16** holds the entry and the chain of preconditions behind it.

  *Why not an init script in the image's `docker-entrypoint-initdb.d`.* It is the strongest
  alternative on the axis this item is about: PostgreSQL runs it before it accepts external
  connections, so there is no race, no extra service, and no ordering to design at all. It is
  rejected on a different axis — the schema would be hand-written SQL beside the models that already
  describe it, and **nothing would ever compare them**. 12.3 gives the suite no database client, so
  the drift has no detector even in principle; and the script works only inside Compose, so a schema
  created any other way is created by different code. One source of truth is worth more here than
  the ordering it would have simplified.

  *`entrypoints/schema/` is an entrypoint by the composition-root rule rather than by the
  definition of a driving adapter,* and the record says so rather than blurring it: it drives no use
  case and touches no `application/` module. It sits there because it must import `infrastructure/`
  and 3.1 permits that in `main.py` files only.

  *Two behaviours that follow, both worth writing so U5 does not choose:* `create_all` skips a table
  it finds, so a second `up` after `Ctrl-C` — where the container keeps its filesystem (11.7) — is a
  no-op rather than an error. **By the same mechanism it does not repair a partially created
  schema**, which is safe only because 11.7 guarantees the two states are empty or complete.
  And api, worker and tests do **not** check the schema for themselves:
  `service_completed_successfully` is a hard guarantee, and a second check is one rule in two places.

  *Rejected:* **Alembic** — above. **An init script** — above. **`create_all` in each service's
  composition root** — the race. **`create_all` in the api alone** — the hierarchy. **The command
  inline in `docker-compose.yml` as a `python -c`** — code in YAML, reachable by no test and by no
  type checker.
  *Corrects two texts that presupposed migrations:* 3.1's tree, where `db/` read "…, outbox,
  migrations" and gains the fourth entrypoint; and Part 4's U5 row in `03-roadmap.md`, which read
  "Schema and migrations". Both are narrowed in this change, as 4.7 narrowed 3.1's `ids.py` slot.
  The inventory's own wording at 4.5 is left alone — a question is not rewritten once its answer is
  known.
  *Closes 2.10's second conditional line:* `alembic` is dropped exactly as that item provides for,
  and neither lock file changes.
  *Revisit if:* the environment stops being disposable. That is A19, and it reopens only through
  FW13 — which is the chain **FW16** records.
  *Source:* R14, R15. *Constrained by:* 2.5, 3.1, 3.7, 3.8, 4.5, 11.1, 11.2, 11.7, 12.3.
  *Constrains:* 11.1. *Closes:* 2.10's conditional. *Deferred to:* FW16. *Realised in:* U5.

- **4.7 Identifier scheme.** `[decided]`
  *Decision:* **UUID version 4, generated in the application layer and passed into the entity as
  an argument.** There is **no `IdGenerator` port and no `infrastructure/ids.py`** — the use case
  calls `uuid4()` directly; `uuid` is stdlib, which 3.1's import rule admits. Stored as a native
  PostgreSQL `uuid` column with no `server_default`; carried in URLs, JSON and logs as the
  canonical hyphenated string. `event_id` (7.2) uses the same scheme and the same generation site.

  ```python
  # application/use_cases/place_order.py   — layer 2: 3.4 names UUID directly, no NewType
  order = Order.new(id=uuid4(), now=self._clock.now(), ...)
  with self._uow as uow:
      uow.orders.add(order)                # add returns None
      uow.commit()
  return order.id                          # known before the transaction opened
  ```

  *Why not a sequential integer — the alternative at its real strength.* It is genuinely easier
  to retype; it keeps 8.6's dispatch log line readable, where two UUIDs cost eighty characters of
  noise; and monotonic keys land at the right edge of the B-tree while `uuid4` scatters inserts
  across it. The third holds under write volume this system does not have. The first applies to a
  flow the CLI does not perform — 9.2 selects an order from `GET /orders` by customer name, so no
  identifier is ever typed by a human.

  *What decides it is when the identifier exists, not what it looks like.* A sequential integer
  is in practice a choice of **database** generation — a counter shared by the API and the worker
  without a `SEQUENCE` is a race — and database generation costs four things, each in a layer a
  closed item already fixed:
  - 2.5 keeps models separate from entities, so an identifier populated on the model at flush has
    to be copied back onto the domain entity by the adapter, after the write. The alternatives are
    `Order.id: Optional[...]`, tested for `None` everywhere it is never `None` after a save, or an
    `add()` returning an identifier instead of `None`.
  - Reading it before the commit requires an explicit `flush()` — a session term. 3.5 fixed the
    `UnitOfWork` at `orders`, `drivers`, `outbox`, `__enter__`, `__exit__` and `commit`, and stated
    that the core knows a boundary and not a mechanism.
  - 7.5 publishes after the commit and marks the outbox row by `event_id`, so that value must be
    held across the transaction boundary. Generated in the application it is already a variable;
    generated by the database it must be read back.
  - U4's unit tests stop being free: `CLAUDE.md` §5 admits them only as pure logic with no
    infrastructure, and an entity that cannot be constructed complete without a database is not
    that.

  *Why no port, when 4.8 gave the clock one — the asymmetry is deliberate.* 3.1 lists `uuid` among
  the modules `domain/` and `application/` may import, so a direct call breaks no layering rule and
  a port could be justified only by test determinism. That is precisely what justifies the clock:
  tests assert on timestamps and on their ordering. No test asserts on the *value* of an
  identifier — the assertion is that the one returned by `POST` is the one returned by `GET`, which
  holds under any value. A port enabling no assertion is the speculative abstraction `CLAUDE.md` §6
  names. Generation sits in `application/` rather than in `Order.new()` for the same reason 4.8
  passes "now" as an argument: identity and time enter the entity the same way.

  *Why `uuid4` and not `uuid7`.* Time-ordered identifiers would recover the index locality conceded
  above, and stdlib `uuid` gained `uuid7()` only in Python 3.14 — under R12's 3.10 floor it means a
  third-party dependency requiring approval under §6, bought for a property this scale cannot
  measure. If U1 settles on a 3.14+ base image it becomes free and can be reconsidered; that is not
  a reason to take a dependency now. *2.9 has since fixed the floor at 3.12, so this does not arise.*

  *Rejected:* **UUID generated by the database** (`DEFAULT gen_random_uuid()`) — it keeps the type
  and inherits every cost of database generation above, for nothing the application call does not
  already give. **Generation inside `domain/`** — legal under 3.1's import list, and rejected on the
  symmetry with 4.8 alone.
  *Accepted cost:* identifiers are 36-character strings in URLs and log lines.
  *Resolves:* 3.1's conditional `ids.py` slot — the file is not created, and the tree is corrected
  in the same change. *Removes* the id generator from the list of ports 3.4 defines.
  *Left to 3.4:* whether signatures name `UUID` directly or a `NewType` per entity — a question
  about the typed boundary, which is 3.4's subject.
  *Source:* R1, R4, R11, R12. *Constrained by:* 2.5, 3.1, 3.5, 4.8, 7.5. *Constrains:* 3.4, 4.1,
  4.5, 4.6, 7.2.
  *Revisit if:* a test needs to predict an identifier, or an identifier acquires business meaning —
  a human-readable order number, say. Either introduces an `IdGenerator` port, and its adapter then
  lands beside `clock.py` under the rule 3.1 already demonstrates.

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
  *Amended after 7.5:* the outbox row carries two further timestamps — `created_at` and the
  nullable `published_at` — so the count above covers the two entities, not the whole schema.
  They are adapter bookkeeping on a table nothing reads (7.5), not business time.
  *Source:* `CLAUDE.md` §5. *Answers:* the timestamp half of Q10's response shape.

- **4.9 Entity shape and operations.** `[decided]`
  *Added during Phase 2 on 2026-08-10:* 4.1's field list is fixed entirely by closed items; what
  was open is the shape those fields sit in, which 2.5 and 3.2 presuppose without deciding.

  *Decision:* **mutable dataclasses, two construction paths, no constructor invariant, six
  operations, plain `Enum` with explicit string values.**

  ```python
  # domain/order.py — layer 1 (3.1): stdlib only
  _NEXT = {RECEIVED: PREPARING, PREPARING: BAKING, BAKING: READY, READY: DELIVERED}

  @dataclass(frozen=True)
  class TransitionResult:
      must_publish: bool                  # 5.3
      releases_driver: bool               # 5.6

  @dataclass
  class Order:                            # the nine fields are 4.1
      @classmethod
      def new(cls, id, customer_name, address, items, now) -> "Order"   # sets RECEIVED / PENDING

      def advance_to(self, requested_status: OrderStatus) -> TransitionResult:
          if _NEXT.get(self.status) is not requested_status:
              raise IllegalTransition(self.status, requested_status)    # 5.2 → 409
          self.status = requested_status
          if self.status is DELIVERED and self.assignment_state is not FAILED:
              self.assignment_state = COMPLETED
          return TransitionResult(must_publish=self.status in (BAKING, READY),
                                  releases_driver=self.status is DELIVERED)

      def can_be_assigned(self) -> bool     # driver_id is None and status is not DELIVERED — 5.5
      def assign_to(driver_id, now) -> None # writes driver_id, ASSIGNED and assigned_at together
      def mark_dispatch_failed() -> None    # returns early unless can_be_assigned() — 8.3

  # domain/driver.py — layer 1 · fields are 4.3
  def mark_busy() -> None   ·   def release() -> None                   # 3.2
  ```

  *Mutable, not frozen:* 3.2 fixed `advance_to(to) -> TransitionResult` and `driver.release()`, and
  under frozen the new state has no way out of either method without reopening 3.2. Equality stays
  the dataclass default; nothing in the design compares entities.

  *Two construction paths:* `new()` is the only place R1's initial `RECEIVED` is written; the
  generated `__init__` is what 2.5's row→entity mapper calls with all nine fields. A single
  constructor either lets the mapper omit `status` silently, or moves the `RECEIVED` rule out of the
  core and into `application/`.

  *No invariant in either:* bounds are 4.2's and are enforced at the edge; the
  `driver_id`/`assignment_state`/`assigned_at` triple is written by `assign_to` in one statement,
  with 4.5 as the schema backstop; timezone-awareness is a property of a `timestamptz` column.
  *Cost:* nothing stops the mapper building an incoherent `Order` — the defence is that exactly one
  function builds them.

  *Two operations had no owner before this item:* `mark_dispatch_failed()`, which 8.3's exhaustion
  path writes, and `driver.mark_busy()`, the counterpart of `release()` that 4.3's cross-table
  invariant needs — an `Order` may not mutate a `Driver`. 4.3 and 3.2 are closed and this is the
  last open item in U3's gate, so there is no later place for them to land.

  *Guards differ per method, and 8.1 is the reason:* `advance_to` raises, because 5.2 maps its error
  to `409`. `assign_to` does not — 8.1 enumerates **four exhaustive** ack cases and a raise here is a
  fifth path; its one caller asks `can_be_assigned()` in the line before. `mark_dispatch_failed`
  returns rather than raises, as 5.6 does for release. That guard is load-bearing: R5 puts two
  messages per order in flight, so one can exhaust after the other has assigned or after delivery,
  and no item fixes the order in which the consumer evaluates 8.1's cases 2 and 4.

  *One line each.* Plain `Enum`, not a `str` mixin — the mapper writes `.value` anyway, the mixin
  makes `OrderStatus.READY == "READY"` true and lets a raw string cross a typed boundary, and
  `StrEnum` needs 3.11 against R12's 3.10 floor. `_NEXT` rather than an ordered tuple — terminality
  becomes a missing key, and all three halves of 5.1 including the illegal same-status resend fall
  out of one condition. *Weakens two costs stated in 2.5* — the skipped `__init__` and "cannot be
  frozen" are both hypothetical under this item; 2.5's conclusion is unaffected.

  *`COMPLETED` on `DELIVERED`, except from `FAILED`.* `assignment_state` describes the dispatch.
  `PENDING` is derivable from `driver_id IS NULL`, so overwriting it loses nothing; `FAILED` is the
  only value on this axis 8.3 wrote deliberately and the only one with no copy anywhere a reader
  looks. *Accepted cost:* with no driver available, a customer collecting **before** the retry budget
  expires leaves `COMPLETED` and one collecting **after** leaves `FAILED` — one real story, two
  records, separated by a timer. Recorded in FW1.
  *Rejected:* **unconditional `COMPLETED`**, which is 4.4's current wording — it erases the only
  record that dispatch gave up, to save one conjunct. **`COMPLETED` only from `ASSIGNED`** — leaves
  `PENDING` asserting a wait on an order that will never move again.

  *`FAILED` is not terminal:* R5 publishes twice, so `FAILED → ASSIGNED` occurs on an ordinary path.
  Corrected in 4.4 and 7.6.

  *The transition parameter is `requested_status`, renamed 2026-08-12 — a name and nothing else.*
  It read `to`, which is clear beside the method's own name and vague everywhere else: the use
  case, the API edge and `IllegalTransition` were carrying three names for one value. `requested`
  is the accurate word rather than `next`, because a caller may ask for a status that is not the
  adjacent one — that path is 5.2's whole subject, and 9.2 makes it the ordinary case at the CLI.
  The signature, the guards and the behaviour are untouched. Found by review of U3's code.
  *Source:* R1, R4, `CLAUDE.md` §2, §3. *Constrained by:* 2.5, 3.2, 4.2–4.4, 4.7, 4.8, 5.1–5.6, 8.1,
  8.3. *Narrows:* 4.4. *Voids one argument in:* 7.6. *Realised in:* U3.


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

- **5.4 Driver selection rule.** `[decided]`
  *Decision:* **the earliest-registered `AVAILABLE` driver** — `ORDER BY created_at ASC, id ASC`
  inside 8.9's claim statement. The rule is deterministic and carries **no business content**: it
  is a tie-breaker, chosen so that a test can assert which driver was claimed rather than which
  set it came from.
  *Why oldest-first rather than any other total order:* R7 asks for "**an** `AVAILABLE` driver"
  and names no preference, so every total order satisfies it equally. `created_at` is the column
  4.3 already added for exactly this purpose, and first-registered-first-served is what a reader
  assumes without being told. `id` is the second key so the order is total even when two rows
  share a timestamp.
  *Note for 12.1 and U10:* a tie broken by `id` falls to a `uuid4` (4.7) — deterministic for a
  given dataset, but not predictable before the rows exist. A test that asserts *which* driver is
  claimed must therefore register them at distinct times, not rely on the second key.
  *Rejected:* **random selection** — it satisfies R7 equally and destroys the assertion 3.2 relies
  on to keep the `ORDER BY` from being dropped silently. **Proximity or load** — the interesting
  rule, and the one the assignment did not ask for; it needs data the claim statement does not
  have, and would reopen 3.2, 8.9 and 5.8 together. It is FW10.
  *This closes 3.2's condition rather than firing it.* The reasoning for why an ordering with no
  business content may live in `infrastructure/db/` is 3.2's and is not restated here; the only
  fact added is that 5.4 chose such an ordering. 3.4's claim signature therefore takes no criteria
  argument.
  *Source:* R7, `CLAUDE.md` §5. *Constrained by:* 3.2, 4.3, 8.9. *Constrains:* 3.4.

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

- **5.7 Which rules are unit-testable without infrastructure.** `[decided]`
  *Decision:* **the subset provable against `domain/` alone, with no test double of any kind.**

  | Rule | Provable against `domain/` alone | Where it lives |
  |---|---|---|
  | **5.1** transition graph | **yes** | `_NEXT` + `advance_to` (4.9) |
  | **5.2** illegal transition | **the raise, yes;** the `409`/`422` mapping, no | `advance_to` / `entrypoints/api/errors.py` |
  | **5.3** publish trigger | **yes** | `TransitionResult.must_publish` |
  | **5.4** driver selection | **no** | the `ORDER BY` inside 8.9's claim |
  | **5.5** assignment idempotency | **yes** | `can_be_assigned()` |
  | **5.6** driver release | **both flags, yes;** the coordination, no | `releases_driver`, `driver.release()` / the use case |
  | **5.8** one active order per driver | **no** | `WHERE status = 'AVAILABLE'` + 4.5's index |

  *Why `domain/` alone and not `application/` with fakes.* A fake `UnitOfWork`, clock and publisher
  contain no infrastructure, so the literal reading admits them — but `CLAUDE.md` §5 sets three
  conditions together, and "written in minutes" is the one a fixture module fails. 3.5 made the
  `UnitOfWork` a `Protocol`, so a fake is genuinely cheap; cheap is not the written test, and
  `domain/` alone already proves what §5 asks to be proved — that the core is testable in isolation.
  Use case behaviour is covered by 12.2's four scenarios over HTTP, against the real thing rather
  than against a simulation.
  *This item does not touch §5.* Staying inside "free" is what keeps the amendment 12.6 flags
  unnecessary. How far the unit set may go stays 12.6's; this item only supplies the candidates.

  *The whole unprovable remainder is one SQL statement.* 5.4 is its `ORDER BY` and 5.8 is its
  `WHERE` — both inside 8.9's single claim, which must be one statement because selecting in Python
  and then locking is the read-then-lock race 8.9 rejected. 3.2 already recorded why an ordering with
  no business content may live in `infrastructure/db/`, and the same argument carries 5.8: it is not
  a rule the core evaluates but a consequence of `drivers.status` being a two-value enum. **§5's "if
  verifying a business rule requires external services, the rule is in the wrong layer" is therefore
  answered rather than conceded** — there is no core function here that could be wrong.
  *The unprovable halves of 5.2 and 5.6 are not exceptions:* 3.2's table already classifies the
  domain-error → HTTP mapping and publish-after-commit ordering as things that look like rules and
  are not.

  *Rejected:* **`application/` use cases with fakes** — above. **No unit set at all**, which §5
  permits since unit tests are an addition rather than a requirement: rejected because four rules are
  provable with zero setup and A17 already put them outside R18's count, so declining them forfeits
  §5's demonstration and saves nothing.
  *Source:* `CLAUDE.md` §5. *Constrained by:* 3.2, 3.5, 4.9, 8.9, 12.2. *Constrains:* 12.6.
  *Realised in:* **U3 for the rules it writes** — §8.2 gives every step a test that would fail when
  its behaviour breaks, and these are exactly the free ones — **and U4 for whatever 12.6 opens
  beyond them.** The same ordering 14.7 recorded when the `pytest` row moved from U4 to U2: U4 is
  the unit named for `tests/unit/`, and the unit that writes the rule gets there first.

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
  driver object, newest first, with no cap, no paging and no filters.
  *Why it is not scope creep:* the DoD grades "an easy-to-use console client", and R11 requires
  checking order statuses. Selecting an order by customer name requires a list; the only
  alternative is making a human retype a UUID, which fails the criterion the DoD actually
  names. The endpoint exists to serve a graded requirement, not to round out the API.
  *Why the list omits the driver:* it keeps 6.5's two-keyed-reads decision valid. Nesting a
  driver per row would turn a list of N into N+1 queries; omitting it means the list is one
  query and the detail endpoint is unchanged.
  *Assumptions recorded:* "newest first" is chosen, not required. There is **no cap and no
  paging** — deliberately as a pair. A cap without paging is the worse half of both: it pays
  paging's price, data that silently falls out of reach, without buying the mechanism that
  brings it back — and an order the list cannot show is exactly the retyped UUID this endpoint
  exists to prevent. Unbounded is affordable here because 11.7 resets the environment on
  `docker compose down`, so the table holds one session's orders, and a row is five short
  fields. Paging is FW4 if volume ever becomes real.
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

- **7.1 Topology.** `[decided]`
  *Decision:* **four objects, two `direct` exchanges, and a closed dead-letter cycle.** Both
  services declare all of it, from one function.

  | Object | Kind | Arguments |
  |---|---|---|
  | `pizza.orders` | direct exchange | — |
  | `pizza.orders.dispatch` | queue, bound on `order.ready` | `x-dead-letter-exchange: pizza.orders.retry`, `x-dead-letter-routing-key: order.ready.wait` |
  | `pizza.orders.retry` | direct exchange | — |
  | `pizza.orders.dispatch.wait` | queue, bound on `order.ready.wait`, **no consumer** | `x-message-ttl:` 10.4, `x-dead-letter-exchange: pizza.orders`, `x-dead-letter-routing-key: order.ready` |

  The cycle 8.2 specified: the worker rejects with `requeue=false` → `pizza.orders.retry` → the
  wait queue → the TTL expires → `pizza.orders` → the main queue. The names are module-level
  constants at the head of `infrastructure/broker/topology.py` (3.1), which is also the only
  place they appear; publisher and consumer reference them by name. They are **not**
  configuration: `CLAUDE.md` §3 forbids hardcoded secrets, hosts and ports, and a logical name is
  none of those, while an environment variable opens the case where the two sides read different
  values. The TTL is the one tunable in the path.

  *Why both services declare, which is the only real choice here:* declaration is idempotent, so
  the two calls cost nothing — and it **deletes the startup-ordering dependency rather than
  managing it**. Neither service cares which came up first.
  *Why `direct` and two exchanges:* a `direct` exchange delivers to **every** queue whose binding
  matches, so a single exchange carrying both queues on one key would deliver each event to both
  at once and re-deliver forever — a loop that assigns drivers twice and reports nothing. Two
  exchanges make the separation structural.
  *`mandatory=True` on the publish.* Publisher confirms (7.5) prove the broker accepted the
  message, not that any queue received it; an unroutable message is discarded and confirmed. With
  confirm mode enabled, `pika` surfaces the return as `UnroutableError`, so the flag costs one
  keyword and a topology fault arrives on 3.4's existing `PublishFailed` path instead of
  vanishing.
  *Rejected:* **`topic`** — wildcards subscribe to a family of events; there is one event and one
  consumer, so the pattern would be a rule nobody reads. **`fanout`** — ignores the routing key,
  which is what keeps the two paths apart. **Declaration by the worker alone** — publishing to a
  missing exchange closes the channel with a 404, so the API must declare at least the exchange;
  once it declares one, one shared function is simpler than split ownership.
  *Operational note, carried into the README:* changing a TTL or any other argument of a queue
  that already exists fails with `PRECONDITION_FAILED` (406) and closes the channel. The repair is
  `docker compose down -v` (11.7).
  *One line on the explicit dead-letter routing keys:* they are not required for correctness —
  RabbitMQ preserves the original key by default, and the exchanges are separate — but with them
  each queue names its own destination, so the direction is read rather than reconstructed.
  *Source:* R5, R6, R14. *Constrained by:* 2.1, 3.1, 8.2. *Constrains:* 7.4, 7.7. *Realised in:* U6.

- **7.2 `ORDER_READY` payload schema.** `[decided]`
  *Decision:* **three fields, identifiers only.** 3.4 placed the type and left its fields here.

  ```python
  # application/events.py
  @dataclass(frozen=True)
  class OrderReadyEvent:
      EVENT_TYPE: ClassVar[str] = "ORDER_READY"

      event_id:    UUID        # uuid4, generated in the application layer (4.7); the outbox key
      order_id:    UUID
      occurred_at: datetime    # UTC-aware, from the Clock port (4.8)
  ```

  *Why identifiers and not a snapshot — the first reason decides it.* 5.5's guard asks whether the
  order already has a driver, which is a fact that can change after the message is sent; under
  8.2's retry cycle the message may be minutes old. The consumer is therefore **required** to read
  the current row, and a snapshot would be data nobody is permitted to trust. Second, a `status`
  field on the message invites branching on it, which is the business rule living in two places
  that `CLAUDE.md` §3 forbids. Third, R5 publishes twice, so the second message would carry a
  different snapshot of the same order and nothing would say which wins.
  *`EVENT_TYPE` is a class constant, not an instance field:* a field with one possible value is not
  data, it is a declaration that can be written wrong. It reaches the wire and the outbox column
  from the constant.
  *What `occurred_at` is, and the reason it is not decoration.* It is the **single** `Clock.now()`
  read the `advance_order_status` use case takes for that invocation. 3.4 fixed
  `OutboxStore.add(event)` with no time parameter, and 7.5 requires the outbox row to carry
  `created_at`; taking it from the event is what satisfies both without either adding a parameter
  to a settled port or letting PostgreSQL supply a `server_default now()` — a second clock, which
  4.8 rules out because no test can control it. One read, two destinations, equal by construction.
  It also makes the wait-queue latency readable from one service's log rather than by correlating
  two.
  *No attempt counter in the payload:* the message is written once and never republished by us —
  8.2's cycle moves the same bytes. 7.4 names where the count comes from.
  *No duplication into AMQP properties:* the payload is the only contract and the deserializer
  never reads properties, so there is one source of truth. `delivery_mode` (7.4) and
  `content_type` (7.3) are set, and describe the transport rather than the event. Filling
  `message_id` and `type` is FW14.
  *Rejected:* **a full snapshot** — above. **A partial snapshot for 8.6's dispatch line** — it
  prints `order_id`, `driver_id`, `driver_name`, and is written after a transaction that has
  already loaded the driver. **A `triggered_by_status` field** — weighed seriously, because the
  outbox holds two `ORDER_READY` rows per order that differ only by `event_id` and `created_at`.
  It is declined because the repair the row exists for does not need it: the row says the dispatch
  of order X was never sent, and FW2's relay republishes from `order_id` alone. The two events are
  interchangeable by design — that is why R5 publishes twice — so the field would add exactly the
  branchable status the paragraph above warns against.
  *Clarifying 7.5, not contradicting it:* that record says the row names "exactly which event was
  lost". With two interchangeable events per order, what it names is **which order** lost its
  dispatch, which is the fact the repair needs.
  *Source:* R5, R6, R17, `CLAUDE.md` §3. *Constrained by:* 3.4, 3.8, 4.7, 4.8, 5.5, 7.5.
  *Constrains:* 7.3. *Deferred to:* FW14, FW15. *Realised in:* U3 (the type), U6 (the wire).

- **7.3 Serialization and version marker.** `[decided]`
  *Decision:* **JSON encoded UTF-8**, `content_type="application/json"`, produced by two pure
  functions in `infrastructure/broker/serialization.py` (3.1; 3.4 kept the format here when it
  moved the type to `application/`):

  ```python
  class SerializationError(Exception): ...

  def serialize(event: OrderReadyEvent) -> bytes: ...
  def deserialize(raw: bytes) -> OrderReadyEvent: ...   # SerializationError on any invalid input
  ```

  The module imports **stdlib only** — not `pika` — which is what lets the database adapter import
  it for the outbox row: the dependency is on a format, not on a broker. `UUID` is the canonical
  hyphenated string and `datetime` is ISO 8601 with an explicit offset, both already fixed by 4.7
  and 4.8.

  *U5 writes the module, not U6.* The outbox row needs `serialize` and U5 does not depend on U6,
  so the unit that reaches it first builds it; the publisher (U6) and the consumer (U8) import it
  afterwards. It stays under `broker/` because the format is the wire contract and not a general
  one — the outbox stores a copy of the message, and `deserialize` has no reader but the consumer.
  That makes `db/ → broker/` an edge inside layer 3, which 3.1's checkable rule does not cover and
  no lint catches; it is written here so that it is not later read as drift.

  *The same function produces both copies*, the wire message and the stored `payload`. That is the
  whole point of the outbox row: it is evidence of what was meant to go out, and two functions
  producing approximately the same thing would make it a guess. The database adapter writes
  `json.loads(serialize(event).decode("utf-8"))` — the bytes come from the one producer, the decode
  cannot fail on bytes we produced, and the parse hands the `jsonb` column the structure it stores.
  *The expression this record first carried, the decode alone, does not survive the stack 2.5
  chose.* SQLAlchemy's `JSONB` runs `json.dumps` over whatever it is given, so a string that already
  holds JSON is encoded a second time and the row keeps a JSON **string** rather than an object.
  `payload ->> 'order_id'` — the one query 4.5 keeps the column for — then returns null, and the
  insert succeeds either way, so the fault would surface only when someone came to read the
  evidence. Found in U5's step 4, against the dialect rather than from memory.
  *Both signatures take and return `bytes`, deliberately.* UTF-8 decoding belongs inside the
  boundary: with a `str` parameter, malformed bytes raise `UnicodeDecodeError` before
  `deserialize` is entered, and 8.4's poison-message path would have to catch two families of
  error instead of one. The module owns the entire conversion from untrusted bytes to a valid
  event.
  *No version field.* A version buys one capability — letting one side change while the other is
  still old. Both services are built from one repository and started by one `docker compose up`,
  so there is no rolling deploy and no second consumer, and no moment at which the versions can
  differ. **The tolerant reader is the other half of the same decision:** unknown fields are
  ignored, required fields missing or invalid raise. That is what makes a later field addition
  safe without coordination, and it is why a marker is only needed the day a field **changes
  meaning or disappears** — the condition that reopens this item.
  *Rejected:* **a binary format** (Protobuf, Avro) — buys size and speed that have no consumer
  here, and pays in an external schema and a build step. **The database adapter building its own
  JSON** — two formats that drift. **`OutboxStore.add` taking pre-serialized bytes** — pushes a
  wire format into the application layer; 3.4 fixed `add(event)`.
  *Left to 8.4:* what happens to the malformed message itself — discarded, parked, or blocking.
  7.3 fixes only that the deserializer raises rather than returning something partial.
  *Recommendation carried to 4.5, which owns the column:* store `payload` as `jsonb`. The one
  question ever asked of the table is which orders lost their dispatch, and `jsonb` makes it a
  single query; the byte-exactness `text` preserves has no consumer, since FW2's relay rebuilds
  the message from the content and whitespace is not the content.
  *Revisit if:* a caller needs `OrderReadyEvent` in JSON for a purpose of its own — displaying,
  reporting, exporting — rather than as the message going onto the wire or the one that came off
  it. Reading the stored copy is not the test: FW2's relay does exactly that and still has only
  the wire as its purpose. What changes is that the format acquires a second author, and the
  module moves to `infrastructure/serialization.py`. **If persistence arrives with such a reader
  (A19, FW13), the no-version decision above reopens with it** — a stored row can outlive the code
  that wrote it, which a wire message never does.
  *Source:* R5, R6. *Constrained by:* 3.1, 3.4, 4.7, 4.8, 7.2. *Constrains:* 7.7, 8.4.
  *Recommends to:* 4.5. *Realised in:* U5 (the module), U6 (the wire).

- **7.4 Durability.** `[decided]`
  *Decision:* **durable exchanges, durable queues, persistent messages** (`delivery_mode=2`).
  The two switches are independent and neither is worth anything alone: `durable` keeps the
  *definition* across a broker restart, `delivery_mode=2` writes the *message* to disk. A durable
  queue holding transient messages comes back empty.

  *The alternative, at its strongest.* 7.5 already accepted a lost event as a failure mode, and R5
  publishes twice — at `BAKING` and at `READY` — so a single loss is covered. On that reading a
  broker restart is one more window in a family already conceded, and the disk write buys
  insurance we declined to buy elsewhere.

  *What that misses is where the messages are sitting.* The messages resident in the broker for
  any length of time are the ones circling 8.2's wait queue — orders that found no driver, with
  part of their retry budget already spent. The full scenario: an order publishes at `BAKING`, no
  driver, the message enters the cycle; the order advances to `READY` and publishes again, also
  into the cycle; the broker restarts; **both are gone**. The order reaches `DELIVERED` with
  `assignment_state = PENDING`, no driver, and **no error recorded anywhere** — from the API's
  side both publishes succeeded and both outbox rows are marked `published_at`, and 8.3's `FAILED`
  is never written because nothing is left to count attempts. That is a wholly silent failure, and
  it is categorically worse than the one 7.5 accepted, which at least leaves an unpublished row
  naming the order. The price is a disk write on a two-hundred-byte message a few times a minute,
  in a system driven by a person at a CLI menu.
  *Rejected:* **transient messages** — above. **Quorum queues** — replication across cluster nodes,
  and compose runs one broker; replicating to replicas that do not exist buys nothing.

  *What it gives, in the three cases that occur:*
  - **A connection drops while the worker holds an unacknowledged message.** The broker requeues
    and redelivers it, flagged `redelivered`. This is safe because two other items already closed
    it: 8.1 acks only after the commit, and 5.5 makes the consumer idempotent. Either the
    transaction committed and redelivery is a no-op, or it did not and redelivery is a correct
    retry. There is no third case.
  - **The broker restarts with messages in the wait queue.** They survive. Expiry is computed from
    the moment the message entered the queue and is stored with it, so **the TTL does not reset** —
    downtime counts toward it, and a message whose TTL elapsed while the broker was down is
    dead-lettered on recovery. The retry cycle resumes where it was.
  - **What it does not give, stated plainly:** 7.5's window is untouched — a publish that never
    left is beyond any broker mechanism. And this is single-node durability: it survives a
    restart, not the loss of the disk.

  *The retry counter 8.3 relied on and never named.* 8.3 capped retries; 8.2 listed "an attempt
  counter carried in the message" among its rejections. Both hold because **we do not carry one** —
  RabbitMQ maintains it. Each time a message is dead-lettered the broker updates an `x-death`
  header holding one entry per *(queue, reason)* pair, each with a `count`. Our cycle produces two:

  | Queue | Reason | What it counts |
  |---|---|---|
  | `pizza.orders.dispatch` | `rejected` | worker rejections — **this is the retry budget** |
  | `pizza.orders.dispatch.wait` | `expired` | TTL expiries |

  The worker reads the **`pizza.orders.dispatch` / `rejected`** entry and compares it to the cap. A
  message on first delivery carries no `x-death` header at all, which is zero attempts. Three
  properties make this the right mechanism: the payload stays immutable, so the outbox row remains
  an exact record; the header is persisted with the message, so the count survives a restart along
  with everything else; and no code of ours counts.
  **The hazard worth naming:** the two entries advance together and show the same number. Summing
  them halves the budget silently. The pair is named explicitly above for that reason.
  *Semantics of the cap, which 8.3 left open:* the configured value is the number of **retries**;
  the first delivery is not a retry; the worker gives up when the `rejected` count reaches it. A
  cap of 3 therefore yields four deliveries.
  *Rejected:* **a counter column on the order** — a write on a path that otherwise only reads and
  rejects, duplicating state the broker already holds. **A counter in the payload with
  republishing** — already rejected by 8.2, and it would give every attempt a new `event_id`.
  *This completes 8.3 rather than reopening it:* the cap, the terminal `FAILED` state and the ack
  on exhaustion stand exactly as decided there.
  *Source:* DoD "Broker & Consumer". *Constrained by:* 7.1, 8.1, 8.2, 8.5, 5.5. *Completes:* 8.3.
  *Realised in:* U6 (topology), U8 (reading the header).

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
  *One argument here is void, noted 2026-08-10.* The paragraph above rejects
  `assignment_state = FAILED` partly because it would require "a `FAILED → ASSIGNED` transition that
  4.4 does not have". 8.3 writes `FAILED` on retry exhaustion and R5's second publish then assigns,
  so that transition occurs on an ordinary path regardless; 4.4 is amended accordingly.
  **The decision is unaffected** — it stands on the second argument, that `PENDING` on an order whose
  status has advanced already reads as "no driver is coming".
  *Source:* R5, `CLAUDE.md` §5. *Answers:* Q21. *Defines:* F4 with 7.5.

- **7.7 Connection lifecycle.** `[decided]`
  *Decision:* **publisher — one long-lived connection and one channel in confirm mode, opened
  lazily, guarded by a `threading.Lock`. Consumer — one connection, one channel, the consume loop
  on the main thread.** This is where 2.4's debt lands: FastAPI serves synchronous handlers from a
  thread pool, so two concurrent `PATCH` requests are two threads, and `pika` is not thread-safe —
  two threads on one connection corrupt the protocol stream, which surfaces as a mangled frame or
  a closed connection rather than a clean crash.

  *The lock covers the whole publish operation* — send, wait for the confirm, and the
  reconnect-and-retry — so publishes serialise. Each holds one round trip to a broker on the same
  compose host, against a system driven by a person at a CLI menu.

  *Why long-lived rather than a connection per request — and the alternative is genuinely good.*
  A private connection per request is thread-safe **by construction**: no lock, no shared state,
  no staleness. It is rejected first because **7.5 already fixed** that a failed publish is retried
  "exactly once, after reconnecting", which presupposes a connection that persists between
  requests and can go stale; per-request the sentence has no meaning, and that item is closed.
  Second, it pays a TCP handshake, an AMQP handshake, a channel open and a confirm-select on every
  status update.
  *Rejected:* **thread-local connections** — an unbounded pool with no owner; threads appear under
  load and nothing closes their connections at shutdown. **A dedicated publisher thread with an
  internal queue** — what `pika`'s own documentation recommends, and correct under real
  concurrency; here it adds a thread, a queue, and a mechanism to return the publish result to the
  request thread. §3 treats that as a defect at this scale.

  *The connection opens lazily, on the first publish; startup touches the broker not at all.*
  7.6 fixed that an unreachable broker still returns `200`, and a service that refuses to start
  without the broker contradicts that one layer down — it makes `docker compose up`
  order-sensitive, which is exactly what 7.1 declined to be. The ASGI `lifespan` hook — 2.4's
  single async exception, reserved for composition-root wiring — **constructs the adapter** (local,
  no I/O) and closes the connection at shutdown if one was opened.

  *What actually bounds the publish in time.* 7.5 promised a bounded attempt and a `PATCH` blocked
  for at most roughly twice it. **A timer of ours cannot deliver that:** a blocking socket call in
  Python cannot be interrupted from another thread without closing the socket underneath it. The
  bound must come from the library's own parameters, both fields of `pika.ConnectionParameters`
  and both fed from 10.4:

  | Parameter | What it bounds |
  |---|---|
  | `socket_timeout` | connection establishment and socket operations — a broker that does not answer |
  | `blocked_connection_timeout` | the broker signalling `Connection.Blocked` under memory or disk pressure; without it a publish waits **indefinitely**, a failure that presents as a hang rather than an error |

  `connection_attempts` stays at its default of 1, so the bound remains one attempt and one
  timeout; the worker's startup retries are a different question and belong to 8.8.

  *Heartbeats stay at `pika`'s default, and the reason is worth stating.* `BlockingConnection`
  services heartbeats only while the application is **inside** a `pika` call. An API that publishes
  once every few minutes is outside it almost always, so the broker will close the connection on
  missed heartbeats. **This is the designed path, not a defect** — it is precisely the stale
  connection 7.5 called the common failure, and `pika` raises immediately on the next publish, at
  which point the single reconnect opens a fresh connection and publishes. The caller sees nothing.
  *Rejected:* `heartbeat=0` — the broker would never close an idle connection, but a connection
  that dies for a real reason then goes undetected, the socket appears open, and the next publish
  blocks until the operating system's TCP timeout. Minutes, which breaks 7.5's bound.
  *Asymmetry worth noting:* the worker never has this problem. It sits inside `start_consuming()`,
  so its heartbeats are serviced continuously.

  *What the single reconnect does:* close the old connection best-effort, open a new connection and
  channel, **re-declare the topology** through 7.1's `declare()`, re-enter confirm mode, publish
  once. Failure there is final — `PublishFailed`, and 7.6 takes it from there. Re-declaring is not
  ceremony: it is idempotent and cheap, and it is the only path by which a broker that came up on
  an empty volume gets its topology back without restarting a service.

  *The consumer.* One connection, one channel, `basic_qos(prefetch_count=1)` per 8.5,
  `basic_consume` then `start_consuming()` on the main thread; the order read, the claim and the
  ack all happen inside the callback on that same thread. **There is no thread-safety problem on
  this side at all** — there is no second thread, which is the direct dividend of 2.4's synchronous
  runtime. Every connection, first or subsequent, declares the topology before subscribing.
  *Boundary with 8.8, which stays open:* 7.7 fixes that reconnection exists and what it consists
  of. **How long to wait for the broker at startup, at what cadence to retry, and how to shut down
  without losing an in-flight message are 8.8's**, deliberately left there.
  *Constraint handed to 8.4:* 3.1 forbids `entrypoints/worker/consumer.py` from importing
  `infrastructure/`, so it can import neither `deserialize` nor the `SerializationError` needed to
  catch it (7.3). The `try`/`except` around decoding therefore has to sit on the infrastructure
  side of that seam; 8.4 decides its shape.
  *The lock is a consequence of 2.4, and FW12 removes it:* a single event loop serialises channel
  access by construction, so an async runtime needs no lock. That entry already records this from
  its side; this is the reference back.
  *Source:* R5, R10. *Constrained by:* 2.4, 2.7, 3.1, 3.4, 7.1, 7.3, 7.5, 7.6, 8.5.
  *Constrains:* 8.4, 8.8. *Deferred to:* FW12. *Realised in:* U6, U8.


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
  *The counter this cap is measured against is 7.4's* — the broker's `x-death` entry for
  `pizza.orders.dispatch` with reason `rejected`, not a field of ours. 7.4 also fixes the
  semantics this record left open: the configured value counts **retries**, so the first delivery
  is not one.
  *Source:* R9, R17. *Answers:* Q6. *Defines:* F7. *Completed by:* 7.4.

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

- **9.2 Menu actions.** `[decided]` · **reopen requested for U12's gate, 2026-08-12**

  **The developer has asked to re-decide the status action.** The record below stands and
  governs until U12's gate revisits it — this is a request to re-open, not a repeal, and no
  other unit is affected: the core takes a requested status and decides, and does not care who
  chose it or how. What is reopened is the fourth action alone — whether the CLI offers all five
  status values, or a single "advance" that moves the order to the next one.
  *What any new form has to answer, because neither objection has gone away:* it must not put
  5.1's transition sequence inside the client, which 3.6 forbids in one sentence; and it must
  leave the `409` path reachable from the interface a reviewer is handed, or 5.2 becomes
  something read about rather than demonstrated.

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

- **9.3 How the CLI is run.** `[decided]`
  *Decision:* **`docker compose run --rm cli`.** The CLI is a service in the one compose file,
  marked `profiles: ["cli"]` so `docker compose up` does not start it, and reached only through
  `run`. It joins the compose network and addresses the API by service name, so it needs no
  published port. It receives the API base URL from **one environment variable**, defaulting to
  the compose service name; the canonical variable name is registered in 10.1, not here. **The
  README documents this one way and no other** — no host-run path, no `exec` variant.

  *Why it is not started by `up`:* the api and the worker are daemons and nothing types at them;
  the CLI is an interactive foreground program whose whole body is a prompt loop. A service
  without `profiles` starts at `up` with no terminal attached, reads EOF from stdin at its first
  prompt, and exits — printing a failed container into the very stream 11.3 puts the PASS/FAIL
  summary in. `profiles` is two words meaning "not at `up`"; in every other respect the service
  is defined exactly as the api and the worker are.

  *Checked against the brief, because the wording is close:* R14 asks for one
  `docker-compose.yml` launching **API, worker, broker, and database** — the CLI is not on that
  list, so not launching it is the requirement rather than a deviation from it. The list is a
  floor and not a closed set: 11.3's `tests` service is not on it either and does start, because
  R15 requires it. Keeping the CLI inside the same file is also what keeps R14 literal; a second
  compose file for it would be the reading that strains "one `docker-compose.yml`". R11's
  "against the running system" and the DoD's "manual interaction with the running API services"
  both describe a client used after launch, which is what `run` is.

  *Imposes nothing on 3.7:* the CLI needs an image holding `src/pizza/` and an HTTP client, which
  is what the api and worker images already are. One image or three stayed 3.7's call, which
  settled on one `runtime` image for all three services.
  *Left to others:* `depends_on` and whether noisy infrastructure is silenced with
  `attach: false` — 11.1, 11.2. Whether any port is published — 11.8, now free of any CLI
  dependency. What the reviewer types in the menu — 1.2. How an unreachable API is displayed —
  9.4.
  *Assumption:* `profiles` requires Compose v2; 11.10 confirms it.
  *Source:* R11, R14, R16. *Constrained by:* 3.6, 9.2, 9.6. *Constrains:* 1.2, 11.8.
  *Feeds:* 3.7, 11.1.

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


## Topic 10 — Configuration

- **10.1 The complete environment variable list.** `[decided]`
  *Decision:* **seven variables the application reads, all carrying the `PIZZA_` prefix, in two
  settings classes; five more that only the vendor images and Compose interpolation read.** This
  table is the authority — `.env.example` (10.3) and `docker-compose.yml` (U9) transcribe it, and
  neither is a second original.

  **Read by our code.** Every field is required, because 10.2 gives the settings classes no
  defaults, so the *Value* column is what `docker-compose.yml` supplies as `${VAR:-…}`.

  | Variable | Type | Value Compose supplies | Read by | Owner |
  |---|---|---|---|---|
  | `PIZZA_DATABASE_URL` | non-empty `str` | `postgresql+psycopg://${POSTGRES_USER:-pizza}:${POSTGRES_PASSWORD:-pizza}@postgres:5432/${POSTGRES_DB:-pizza}` | api, worker | 2.5 |
  | `PIZZA_BROKER_URL` | non-empty `str` | `amqp://${RABBITMQ_DEFAULT_USER:-pizza}:${RABBITMQ_DEFAULT_PASS:-pizza}@rabbitmq:5672/` | api, worker | 2.7 |
  | `PIZZA_LOG_LEVEL` | one of `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | `INFO` | api, worker | 10.4 |
  | `PIZZA_BROKER_PUBLISH_TIMEOUT_SECONDS` | `float` > 0 | `5` | api | 7.5 |
  | `PIZZA_DISPATCH_RETRY_DELAY_SECONDS` | `int` > 0 | `8` | worker, and whichever process declares the topology (7.1) | 8.2 |
  | `PIZZA_DISPATCH_MAX_RETRIES` | `int` ≥ 1 | `8` | worker | 8.3 |
  | `PIZZA_API_BASE_URL` | `str`, `http(s)` scheme, no trailing slash | `http://api:8000` | cli, tests | 9.3 |

  **Read by the infrastructure, never by our code:** `POSTGRES_USER`, `POSTGRES_PASSWORD`,
  `POSTGRES_DB`, `RABBITMQ_DEFAULT_USER`, `RABBITMQ_DEFAULT_PASS` — all `pizza` (10.5). Compose
  reads those same five to assemble the two URLs above, so **no credential is written twice**. The
  broker vhost stays `/`, the image's default, and is not a variable because nothing varies it.
  What is deliberately *not* configuration — prefetch, pool sizing, the internal port — is 10.4.

  *Two classes, and why not one:* `ServiceSettings` holds the first six and is loaded by the api
  and the worker; `ClientSettings` holds `api_base_url` alone and is loaded by the CLI and the
  integration suite, which speak HTTP and nothing else (3.6, 12.3). A single class over all seven
  would force the CLI container to supply a database URL it never opens, since every field is
  required.
  *Rejected — one class per concern* (`DatabaseSettings`, `BrokerSettings`, `DispatchSettings`, …):
  four more classes to save one unread field in each of two services, which is the speculative
  abstraction `CLAUDE.md` §6 names. The cost is accepted and stated instead — the api carries the
  retry delay and the worker carries the publish timeout, one value each that it does not read.
  *Rejected — pydantic's URL types* (`PostgresDsn`, `AmqpDsn`, `AnyHttpUrl`) for the three
  addresses. They validate more, and here they cost more than they buy: in v2 they do not inherit
  from `str`, so every consumer converts; they append a trailing slash when there is no path, which
  turns `http://api:8000` into `http://api:8000/` and every `f"{base}/orders"` into a double slash;
  and `PostgresDsn`'s allowed-scheme list is a pydantic-version fact that has to keep including
  `postgresql+psycopg` (2.5). SQLAlchemy and `pika` parse their own URLs and report a better error
  than ours would. `api_base_url` instead carries a validator requiring an `http(s)` scheme and
  stripping a trailing slash, so U10 and U12 join paths directly and the papercut never arrives.

  *Naming rules, so U5 to U9 invent no variants:* the `PIZZA_` prefix for everything our code reads
  and nothing else; the unit in the name (`_SECONDS`), because 8.2's `x-message-ttl` is in
  milliseconds and the conversion is a multiplication by 1000 at the declaration site; no
  abbreviations; and a new variable requires a decision record — one added to Compose without a
  field in `config.py` fails 10.3's drift test.

  *What this hands forward, so no value returns as a blocker:* **U5** reads `PIZZA_DATABASE_URL`
  only, and Alembic — if 4.6 chooses it — takes that same variable rather than one of its own.
  **U6** gets the broker URL and the delay with its unit fixed; only *who declares* the topology
  stays open (7.1). **U8** gets the cap's exact meaning (10.4). **U9** supplies each variable per
  service exactly as *Read by* says, and may add one Compose-only variable if 11.8 chooses a
  variable host port — which our code never reads. **U10** and **U12** get a base URL guaranteed
  without a trailing slash.
  *Source:* R16, `CLAUDE.md` §3, DoD "Code Quality". *Constrained by:* 1.2, 2.5, 2.7, 3.6, 7.5,
  8.2, 8.3, 9.3, 12.3. *Constrains:* 10.2, 10.3, 10.4, 10.5, and every unit from U5 onward.

- **10.2 Configuration loading mechanism.** `[decided]`
  *Decision:* **`pydantic` alone — no new dependency.** `src/pizza/config.py` declares two frozen
  `BaseModel`s with `extra="forbid"`, and one loader per class collects the `PIZZA_`-prefixed
  variables out of a mapping and validates them:

  ```python
  # src/pizza/config.py
  _PREFIX = "PIZZA_"

  class ServiceSettings(BaseModel):                     # api, worker
      model_config = ConfigDict(extra="forbid", frozen=True)
      database_url: str
      ...                                               # 10.1's first six fields

  def load_service_settings(env: Mapping[str, str]) -> ServiceSettings:
      return ServiceSettings.model_validate(
          {k.removeprefix(_PREFIX).lower(): v for k, v in env.items() if k.startswith(_PREFIX)}
      )
  ```

  *Three properties, and each is the reason for one line of it.* The environment holds only
  strings, so `"8"` reaching an `int` field is coerced while `"abc"` is an error. `ValidationError`
  reports **every** fault at once, which is what a startup failure should print rather than the
  first missing variable. And `extra="forbid"` over a dict we assembled ourselves rejects
  `PIZZA_LOG_LEVL=DEBUG` instead of ignoring it. The loader takes the mapping as an argument rather
  than reaching for `os.environ` itself, so its test passes a dict and touches no process state,
  which is what `CLAUDE.md` §5 asks of a deterministic test.

  *Where the module lives:* `src/pizza/config.py`, beside 3.1's four directories rather than inside
  one of them. It is not `domain/` or `application/` — the core must not know an environment exists
  — and it is not `infrastructure/`, because adapters receive their values as constructor
  arguments. **The rule, written so it can be checked in a diff: no module under `domain/` or
  `application/` imports `pizza.config`.** 3.1 already left file placement to later items
  ("whether `ids.py` exists follows 4.7"), and this file changes no layer, no arrow and no import
  rule.
  *Nothing instantiates it at import time* — there is no `settings = load_service_settings(...)` at
  module level. 14.7 makes `python -c "import pizza"` a Definition-of-Done command, and a module
  that read the environment on import would make that command require a full environment. Loading
  is a call, made once by each composition root: `entrypoints/api/main.py`,
  `entrypoints/worker/main.py`, `entrypoints/cli/main.py`, and the integration suite.

  *Rejected — `pydantic-settings`,* the conditional line 2.10 pre-approved for exactly this item,
  and the choice a reader of the FastAPI ecosystem would expect to find. It removes the collector,
  and it was declined on a checked fact: its `extra="forbid"` is enforced by the **dotenv** source,
  while the environment source walks the declared fields and never sees a variable that maps to
  none. Under Compose the application parses no `.env` file (10.3), so a mistyped `PIZZA_` variable
  would be ignored in silence and the service would start on a default nobody chose. What remains
  of its advantage — name-to-field mapping, and parsing a file we do not read — is the eight lines
  above, and it would cost a dependency plus a regeneration of both lock files (2.9).
  *Rejected — the standard library alone,* `os.environ` into a frozen dataclass. Zero dependencies,
  against about forty lines of required-field checks, `int`/`float` parsing, range checks and error
  aggregation, which then need tests of their own — re-implementing in code what a dependency
  already in the project performs from a declaration.
  *Source:* `CLAUDE.md` §3, §6. *Constrained by:* 2.3, 3.1, 10.1, 14.7. *Constrains:* 10.3.
  *Closes 2.10's conditional line.* *Realised in:* U2.

- **10.3 `.env` versus `.env.example`.** `[decided]`
  *Decision:* three roles. 14.6 already verified the two mechanical facts this rests on — `.env` is
  ignored, `.env.example` is not — so neither is re-decided here.

  | File | In git | Who reads it | What it does |
  |---|---|---|---|
  | `.env` | no | Compose only | substitutes `${…}` **inside `docker-compose.yml`**. It is never passed into a container, and the application never parses it |
  | `.env.example` | yes | nobody, at runtime | the catalogue of the surface, and the template for `cp .env.example .env` |
  | `docker-compose.yml` | yes | Compose | the one place a default value is written (10.1) |

  *The distinction worth stating, because it is where this is usually got wrong:* a variable reaches
  a process only through a service's `environment:` block. `.env` feeds interpolation, not
  containers — which is exactly why every default is written `${VAR:-value}`. Without a `.env` the
  default applies, so a reviewer needs no step 0 (1.2); with one, the reviewer's value wins.
  *Rejected — `env_file:` on the api and worker services.* It would pass `.env` straight into the
  containers and remove the interpolation entirely, but a missing file is an error unless the entry
  carries `required: false`, which needs Compose 2.24 — and 11.10 has not fixed a version floor.
  Interpolation buys the same override surface with no version requirement at all.

  *`.env.example` carries eleven active `NAME=value` lines* — 10.5's five vendor variables, 10.4's
  four tunables, `PIZZA_API_BASE_URL`, and 11.8's `API_HOST_PORT` — each with the value Compose
  defaults to, so the file is a complete and valid environment. **This read "ten" until 11.8 closed**,
  which is the Compose-only variable 10.1 pre-authorised this item to gain. `PIZZA_DATABASE_URL` and `PIZZA_BROKER_URL` appear in **one prose
  comment** naming both and stating that Compose assembles them from the values above, so setting
  them in the file has no effect.
  *Rejected — writing those two as commented `# NAME=value` lines.* In an env file that form reads
  as an invitation to uncomment, and here uncommenting would change nothing whatever: a line that
  invites an action with no result is worse than no line. The comment answers the same question — a
  reader who found `database_url` in `config.py` and grepped for it — without pretending to be
  settable.

  *What keeps the file from drifting:* 13.6 warns that a fact written twice will eventually disagree
  with itself, and `.env.example` is a second place. U2 therefore carries one unit test that scans
  every `PIZZA_[A-Z_]+` token in the file — comments included — and compares that set to the fields
  declared in 10.2's two classes. A renamed field, an undocumented new variable, and a documented
  name that nothing reads all fail it. The vendor variables carry no `PIZZA_` prefix and are outside
  the comparison.
  *Source:* R16, `CLAUDE.md` §3, §4. *Constrained by:* 1.2, 10.1, 10.2, 14.6. *Leaves to U9:* the
  `environment:` blocks that transcribe 10.1. *Realised in:* U2.

- **10.4 Which values are tunable.** `[decided]`
  *Decision:* **four variables, and everything else fixed.**

  | Variable | Value | Fixed by |
  |---|---|---|
  | `PIZZA_BROKER_PUBLISH_TIMEOUT_SECONDS` | `5` | this item's own brief in the inventory; 7.5 bounds a `PATCH` at twice it |
  | `PIZZA_DISPATCH_RETRY_DELAY_SECONDS` | `8` | 8.2 — the wait queue's `x-message-ttl` |
  | `PIZZA_DISPATCH_MAX_RETRIES` | `8` | 8.3 — the retry bound |
  | `PIZZA_LOG_LEVEL` | `INFO` | here; the log's *format* is 8.7 and stays open |

  *Where 8 and 8 come from, because the two numbers are one decision.* 1.2 puts two opposing demands
  on the same product. Step 8 waits one cycle for the dispatch line, so the delay must be
  single-digit seconds; step 7 is a person registering a driver by hand, so the whole budget must
  exceed 60 s. 8 × 8 = 64 s satisfies both, with one number to remember instead of two.
  **The cap counts redeliveries, not total attempts** — nine attempts in all, eight waits, 64 s from
  the first rejection to `FAILED`. Read the other way it is seven waits and 56 s, under 1.2's floor:
  an off-by-one that would surface only when somebody ran the demo. It is written here in words so
  that U8 does not choose.
  *Why the floor matters more than it looks:* 8.3 records as an accepted cost that an order which
  exhausts its budget is **not** reassigned when a driver registers later. A budget expiring in the
  middle of step 7 therefore does not merely look wrong — the demo cannot recover from it, and the
  reviewer has to place a new order.
  *Not a code invariant.* The settings classes do not enforce `delay × retries > 60`. Enforcing it
  would forbid the short test-only tuning FW13 describes, and would turn a property of the demo path
  into a law of the configuration. What is enforced is per field: a timeout above zero, a delay
  above zero, a cap of at least one, and a log level from the five names.
  *The one condition under which the cap could drop is named:* **FW13**. There is a single
  `TTL × cap` product, 11.6 gives the suite the shipped configuration, and the demo and an
  exhaustion scenario pull that number in opposite directions. Nothing else reopens it — in
  particular **FW1 does not**, because it removes the keystroke at `DELIVERED` and not the one at
  step 7, which is where the floor comes from.

  *Fixed, and each with an owner:*

  | Value | Why it is not a variable |
  |---|---|
  | `prefetch = 1` | 8.5 decided it with a full rationale, and FW7 records that a wider window becomes actively harmful the moment there is more than one consumer. An environment knob invites exactly that setting |
  | SQLAlchemy pool sizing | 2.5 left "whether it becomes tunable" to this item. It does not: the library defaults stand, and `pool_pre_ping=True` is code, not configuration |
  | the API's internal port, `8000` | a constant in the image's command. Publishing a host port is 11.8, which may add a Compose-only variable that our code never reads |
  | `httpx`'s client timeout | the library's own 5 s default (2.6). Nothing has asked to change it |
  | exchange, queue and routing-key names | 7.1 — constants. They do not differ between environments, so they are not configuration |

  *Source:* R16, `CLAUDE.md` §5. *Constrained by:* 1.2, 2.5, 2.6, 7.5, 8.2, 8.3, 8.5.
  *Answers:* 2.5's deferred pool-sizing question. *Deferred to:* FW13.

- **10.5 Local credentials.** `[decided]`
  *Decision:* **`pizza` throughout** — the PostgreSQL user, password and database name, and the
  RabbitMQ user and password; vhost `/`. They live in `docker-compose.yml` as
  `${POSTGRES_PASSWORD:-pizza}` and are catalogued in `.env.example`. Nothing under `src/` carries
  them (10.2).
  *Why they must be set at all, rather than left to the images:* PostgreSQL refuses to initialise
  without `POSTGRES_PASSWORD`, and RabbitMQ's built-in `guest` may connect only from localhost —
  the api and the worker connect from other containers, so `guest` would be refused. Explicit
  credentials are a requirement here, not a preference.
  *Why this does not commit a secret.* §4 forbids committing a secret or a local environment file;
  what is committed is a non-secret local default. These values authorise nothing outside an
  environment that `docker compose down` destroys, because 11.7 defines no named volumes (A19).
  **Stated deliberately, because 14.1 makes it permanent:** the repository is public and §4 forbids
  rewriting pushed history, so a secret committed once cannot be withdrawn. This record asserts
  that these are not secrets, and names the conditions that assertion depends on.
  *Reopen condition — the assertion stands on two legs, not one.* It holds while the environment is
  disposable (A19) **and** no published port carries these credentials (11.8, open). Named volumes
  break the first — FW13's second point already records that A19 reopens with them — and publishing
  `5432` to the host breaks the second. If either changes, this item is decided again.
  *Rejected — distinct random values:* they would have to be committed anyway, or "step 0" returns
  against 1.2, so the randomness buys nothing and makes the assembled URLs unreadable.
  *Rejected — `POSTGRES_HOST_AUTH_METHOD=trust`,* no password at all: a broader deviation than one
  known local password, and it reads worse to a reviewer.
  *Source:* `CLAUDE.md` §4, DoD "Docker Deployment". *Constrained by:* 1.2, 11.7, 14.1.
  *Constrains:* 10.1, 10.3. *Defines:* A25. *Revisit if:* named volumes arrive, or 11.8 publishes
  the database port.


## Topic 11 — Docker Compose

- **11.1 Service inventory.** `[decided]`
  *Decision:* **seven services, and not one of their names is chosen here.**

  | Service | Image | Named by |
  |---|---|---|
  | `postgres` | `postgres:16` | 2.2; the name by 10.1's `@postgres:5432` |
  | `rabbitmq` | `rabbitmq:3.13` | 2.1; the name by 10.1's `@rabbitmq:5672` |
  | `schema` | `pizza-runtime`, one-shot | 4.6, which writes both the service and its name |
  | `api` | `pizza-runtime` | 3.7; the name by 10.1's `http://api:8000` |
  | `worker` | `pizza-runtime` | 3.7; the name by 4.6's diagram |
  | `tests` | `pizza-test` (`target: test`) | 3.7, 11.3; the name by 11.4's `--exit-code-from tests` |
  | `cli` | `pizza-runtime`, `profiles: ["cli"]` | 9.3, which writes `docker compose run --rm cli` |

  *Every name in the third column is already load-bearing somewhere else* — inside a URL our code
  parses, or inside a command the README hands a reviewer. This item transcribes them; renaming
  one is a change to the record that fixed it, not to this one.
  *The list is closed at seven.* The inventory's "any init/migration service" is one slot and 4.6
  filled it. FW2's relay would be the eighth and is not built.

  *The two vendor tags — a convention, and the pin is not.* **This item left both unwritten when it
  first closed**, which would have left U9's Phase 3 plan to invent them, and `CLAUDE.md` §2 forbids a
  plan that contains a decision. Nothing in the design distinguishes recent majors: 8.9's
  `SKIP LOCKED` and every constraint in 4.5 have been PostgreSQL features for a decade, and 7.1's
  direct exchanges, dead-lettering and `x-message-ttl` as long in RabbitMQ. So 1.3 gives the choice
  one line rather than a rationale assembled after the fact, exactly as 2.9 did between Python 3.12
  and 3.13. **What is decided is the `major.minor` pin itself:** `latest` would hand a reviewer
  building two months from now a different version from the one this was built against, and 7.1
  already records the shape that failure takes — an argument change on an existing queue fails with
  `PRECONDITION_FAILED` (406) and closes the channel. Conservative rather than newest, on 2.9's stated
  ground that a four-day deliverable does not spend risk on a release it needs nothing from.

  **The build arrangement, which 3.7 handed here in one sentence** — *"where the image is tagged so
  four services do not build four times, and the `build`/`target` keys themselves — 11.1"*. **Every
  service that runs our code carries both its own `build:` block and an explicit `image:` tag**, and
  there are two tags across the five:

  ```yaml
  api     { build: {context: ., target: runtime}, image: pizza-runtime }
  worker  { build: {context: ., target: runtime}, image: pizza-runtime }
  schema  { build: {context: ., target: runtime}, image: pizza-runtime }
  cli     { build: {context: ., target: runtime}, image: pizza-runtime }
  tests   { build: {context: ., target: test},    image: pizza-test    }
  ```

  The shared tag is what makes "one image" a fact rather than an expectation; the repeated `build:`
  is what makes every service buildable on its own.

  *Rejected — one service declaring `build:` and the rest naming the tag alone.* Four lines shorter,
  and it breaks a command the README promises. A service carrying `image:` without `build:` whose
  image is not on the machine sends Docker to a registry, and `pizza-runtime` is in none. 9.3 hands
  the reviewer `docker compose run --rm cli`; on a clean clone before the first `up` — which is when
  somebody reads a README in order — that fails on a failed pull instead of starting the CLI.
  *Rejected — a YAML anchor* (`x-runtime: &runtime`) folding the repetition away. It would merge
  four lines into services that already differ in `command`, `environment`, `depends_on`, `restart`
  and `profiles`, compressing the smallest part of each at the cost of one indirection before a
  reader knows what a service actually is.
  **`attach: false` on `postgres` and `rabbitmq`**, which 9.3 left open here and **1.2 had already
  fixed** — its *Constrains* line reads *"`attach: false` on postgres and rabbitmq, so terminal 1
  carries api, worker and tests only"*. The demo path is thirteen steps across two terminals, and at
  steps 6 and 8 the reviewer is told to watch terminal 1 for the worker's "no driver" warning and its
  dispatch line. Those are the worker's own lines, and vendor startup noise is what buries them.
  *What it does not cost, because the objection is the obvious one:* the logs are still collected —
  `attach: false` removes a service from the `up` stream, not from `docker compose logs postgres`. A
  stack that fails to come up is diagnosed with the same command either way.
  *Assumption:* `attach:` requires a Compose version floor, as 9.3 assumed for `profiles`; **11.10
  confirms it**.
  *Rejected — a declared network.* Compose's default network already resolves a service by its name,
  which is what 10.1's three URLs assume. Declaring one adds lines and changes no behaviour.

  *What this item does not own:* `depends_on`, its conditions, and every healthcheck — 11.2.
  Published ports — 11.8. `restart` — 11.11. The `command` each service runs, including the
  exec-form requirement 8.8 hands on — 11.9, so that one form is fixed in one place. The
  `environment:` blocks are none of these: they transcribe 10.1's table, which 10.3 already left to
  U9 by name.
  *Source:* R14, R15. *Constrained by:* 1.2, 2.1, 2.2, 3.7, 4.6, 9.3, 10.1, 10.3, 11.3, 11.4.
  *Constrains:* 11.2, 11.9, 11.10. *Realised in:* U9.

- **11.2 Readiness and ordering.** `[decided]`
  *Decision:* **Compose conditions alone. Nothing under `src/` waits for anything.** The inventory
  offers healthchecks, in-app retry loops, or both; three records had already answered in three
  places without anyone stating the rule — 9.6 writes no entrypoint script, 4.6's one-shot does not
  wait because it is not started, and 8.8's worker exits rather than retrying. It is one rule and it
  is written here: **readiness is a condition Compose evaluates, never a loop of ours.** 2.5's
  `pool_pre_ping` is not an exception and that record says so — it replaces a connection that went
  bad while idle, which is a different problem from starting up.

  **Three healthchecks, on the infrastructure and the API.**

  | Service | Test | Why this one |
  |---|---|---|
  | `postgres` | `pg_isready -h 127.0.0.1 -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"` | 6.6 named `pg_isready`; the `-h` is this item's |
  | `rabbitmq` | `rabbitmq-diagnostics ping` | 6.6 |
  | `api` | `python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"` | 6.6's `/health`, called with what is already in the image |

  *Why `-h 127.0.0.1`, which is the finest detail in this item and the one that would have bitten.*
  The postgres image runs a **temporary server during first initialisation**, started with no
  external listener, and `pg_isready` reaching it over the local socket reports success. The
  container would be marked healthy while the real server is not yet accepting connections — and
  4.6's entire arrangement rests on the opposite, since the schema service connects over TCP from
  another container and 4.6 gives it nothing to retry with. Forcing the check through TCP means it
  answers the question the dependent service is actually asking. The user and database come from the
  container's own environment (10.1), so a reviewer who overrides them does not break the check;
  `$$` is Compose's escape for a literal `$`.
  *Why the API's check is a `python -c` and not `curl`:* the base is `python:3.x-slim` (3.7), which
  ships no `curl`. The alternative is a package in the image every service ships, added for a
  diagnostic — against one line using the interpreter that is already the reason the image exists.
  `urlopen` raises on 6.6's `503`, so the exit code needs no logic of ours.
  *No healthcheck on `worker`* — 8.8 records that it speaks no HTTP and offers nothing to probe, and
  a check invented for it would be a mechanism with one caller. *None on `schema` or `tests`* —
  both are one-shot, and their readiness signal is the exit code.

  **The graph.**

  ```
  postgres ──healthy──> schema ──completed 0──> api
                                          └───> worker
  rabbitmq ──healthy───────────────────────────> worker
           └──healthy──────────────────────────> tests
  api      ──healthy───────────────────────────> tests
           └──healthy──────────────────────────> cli
  ```

  *The worker waits for the broker, which 8.8 handed here as legibility to be weighed.* Taken: the
  restarts it prevents are not hypothetical — RabbitMQ takes tens of seconds to boot, and without
  the edge the reviewer's **first** `up` prints a run of `ERROR` lines and a container with a restart
  count, in the same stream 11.3 puts the PASS/FAIL summary in. That is the reasoning 11.7 already
  used about a red suite at launch: the worst first impression is the one hardest to attribute
  correctly. **It replaces nothing that 8.8 decided.** `depends_on` gates startup only, so a broker
  that dies later is still answered by the exit and 11.11's policy, exactly as 8.8 specified — the
  edge buys a clean first launch and gives up no resilience.
  *The API does not wait for the broker, and the asymmetry is the design's own.* 7.1 declares the
  topology from both sides precisely because that *"deletes the startup-ordering dependency rather
  than managing it"*, and 6.6 made `/health` report the database alone on 7.6's ground that an API
  without a broker serves every endpoint correctly. An edge here would contradict two records to buy
  nothing, since everything that reads a dispatch result waits for the broker on its own account.
  *The suite waits for the broker, and this is the edge that prevents a silent failure rather than
  noise.* A22 is explicit: with the broker unreachable a `PATCH` still returns `200` and the event is
  lost. A scenario running in that window would see a success, assert nothing wrong, and then fail
  waiting for an assignment that was never requested — a red suite on a healthy system, reported at
  the wrong place entirely.
  *The suite does not wait for the worker, and nothing is lost by it.* The worker has no healthcheck
  to wait on, and `service_started` would prove only that a process exists, not that it subscribed.
  It is not needed: 7.1 has the publisher declare the topology, so the queue exists when the API
  publishes, and a message published before the worker subscribes waits in it.
  *`tests` carries no direct edge to `schema`, though 4.6's diagram draws one.* The guarantee holds
  transitively — `tests` waits on `api`, which cannot be healthy before it started, and it cannot
  start before `schema` exited zero. What 4.6 requires is preserved; the redundant edge is a second
  statement of it that could later disagree.
  *`cli` waits on the API* (9.3 left `depends_on` here), so `docker compose run --rm cli` works
  whether or not the stack is already up.

  **The intervals.**

  | | `interval` | `timeout` | `retries` | `start_period` |
  |---|---|---|---|---|
  | `postgres` | 5s | 5s | 12 | 10s |
  | `rabbitmq` | 5s | 10s | 12 | 30s |
  | `api` | 5s | 5s | 12 | 10s |

  RabbitMQ gets the longer pair because `rabbitmq-diagnostics` starts an Erlang CLI, which is slow
  both to boot and to answer. **None of these is the fixed wait `CLAUDE.md` §5 forbids:** each is the
  cadence at which a condition is tested, and `start_period` is a window in which failures are not
  counted — neither is an assumption that the system is ready after N seconds. Compose starts
  everything the graph allows in parallel, so the waits overlap rather than sum.

  **No `stop_grace_period` is written, for any service.** 8.8 handed it here and fixes that the
  worker stops after the message in hand, which takes milliseconds — so the default is never reached
  and a value here would be a number nothing derives. `stop_signal` on `postgres` is left alone on
  the same ground: a slower shutdown costs a few seconds at `down`, and 11.7 discards the data
  regardless.

  *Rejected:* **an in-app wait loop** in any service — 9.6 already removed the entrypoint script that
  would carry it, and it would put startup ordering in two places. **A healthcheck on the worker** —
  no surface to probe. **`pg_isready` without `-h`** — above. **`curl` in the runtime image** —
  above. **A direct `tests` → `schema` edge** — above.
  *Assumption:* long-form `depends_on` conditions require Compose v2, as 9.3 assumed for `profiles`;
  **11.10 confirms it**.
  *Source:* R14, R15, `CLAUDE.md` §5. *Constrained by:* 2.5, 4.6, 6.6, 7.1, 7.6, 8.8, 9.3, 9.6,
  10.1, 11.3, 11.7. *Holds:* 8.8's three hand-offs. *Constrains:* 11.10, 11.11. *Realised in:* U9.

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
  *Source:* R15, R18, `CLAUDE.md` §5. *Answers:* Q8. *Deferred to:* FW13.

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

- **11.8 Published host ports.** `[decided]`
  *Decision:* **one published port, the API's, and it is variable on the host side:**
  `${API_HOST_PORT:-8000}:8000`. Nothing else is published.

  *The question this item was written for no longer exists, and saying so is half the record.* The
  inventory ties this to "host-side CLI use (9.3)"; 9.3 then put the CLI in a container and recorded
  that 11.8 is *"now free of any CLI dependency"*, 12.3 keeps the suite inside one too, and 1.2
  removes the last two demand-side reasons by name — `/docs` is out of the demo path because *"the
  demo stays one tool"*, and the broker-down path, which *"needs psql or a published port"*, goes to
  13.4's documented trade-offs *"where it costs nothing and reopens no item"*. **Every named consumer
  therefore works with no port published at all.** What follows is decided on top of that, not
  against it.

  *Why the API's port is published anyway.* 2.3 chose FastAPI partly on a claim it made in writing —
  the generated OpenAPI document is *"a free, always-accurate statement of the contract in topic 6,
  which a reviewer can read without reading code"*. Unpublished, that claim is not true of the
  delivered system. 1.2 excluded `/docs` from the **demo path**, which is a different statement from
  excluding it from existence: the path stays one tool, and the door exists for a reviewer who wants
  more than the menu. It costs one line and carries no credential.

  *Why the host side is a variable and the container side is not.* 10.4 fixed `8000` inside the
  image as a constant, and 10.1 pre-authorised *"one Compose-only variable if 11.8 chooses a variable
  host port — which our code never reads"*. The asymmetry has a rule under it: **a value becomes
  configuration when something outside our control can force it to differ.** Inside the network
  nothing can — each container has its own namespace, so `8000` collides with nothing, and the value
  is transcribed in three of our own places (the API's command, 10.1's `http://api:8000`, and 11.2's
  healthcheck) where a variable would be one fact in three copies. On the host something can: 8000 is
  heavily used on development machines, and a reviewer who has it must otherwise edit the file we
  handed them.
  *`API_HOST_PORT` carries no `PIZZA_` prefix*, by 10.1's own naming rule — the prefix marks what our
  code reads, and nothing reads this. It therefore also sits outside 10.3's drift test, exactly as the
  five vendor variables do. *This item amends 10.3*, whose count of active `.env.example` lines moves
  from ten to eleven.

  *`5432` is not published, and this is the check 10.5 asked for by name.* 10.5 rests its "these are
  not secrets" assertion on two legs — a disposable environment (A19) **and** no published port
  carrying the credentials — and names publishing `5432` as what breaks the second. Nothing needs it:
  12.3 gives the suite no database client at all, and 1.2 already moved the one path that wanted it
  into 13.4. **10.5 is therefore not reopened, and both of its legs stand.**
  *Rejected — `5672`.* Nothing on the host speaks AMQP.
  *Rejected — `15672`, the management UI.* The tempting one, since it would show the wait queue
  holding a message. 11.1's `attach: false` is what makes it redundant: 1.2 has the reviewer watch
  terminal 1 at steps 6 and 8 for the worker's "no driver" warning and its dispatch line, so the retry
  cycle is already demonstrated by the mechanism 1.2 chose. It would also force the management variant
  of the vendor image, and under 1.1's ceiling test no named DoD row fails without it.
  *Rejected — a fixed `8000:8000`* — it makes the one collision we cannot prevent unfixable without
  editing a delivered file; *an ephemeral host port* — the README could then name no URL.
  *Source:* R14, R19. *Constrained by:* 1.1, 1.2, 2.3, 9.3, 10.1, 10.3, 10.4, 10.5, 11.1, 12.3.
  *Amends:* 10.3's line count. *Confirms:* 10.5 stays closed. *Realised in:* U9.

- **11.9 Image build strategy.** `[decided]`
  *Decision:* **one `Dockerfile`, base `python:3.12-slim`, pinned by tag; two stages; two installs;
  and no build step before `up`.** 3.7 fixed the shape and 2.9 handed over the rest in one line —
  *"the base image is a `python:3.12` family, and layer ordering is 11.9's"*.

  ```dockerfile
  FROM python:3.12-slim AS runtime

  ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

  RUN adduser --system --group app && mkdir -p /app && chown app:app /app
  WORKDIR /app

  # Dependencies before source: editing code must not reinstall them.
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt

  # The package itself; its dependencies are already installed and pinned above.
  COPY pyproject.toml .
  COPY src/ ./src/
  RUN pip install --no-cache-dir --no-deps .

  USER app
  CMD ["uvicorn", "pizza.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "8000"]


  FROM runtime AS test

  USER root
  COPY requirements-dev.txt .
  RUN pip install --no-cache-dir -r requirements-dev.txt
  COPY --chown=app:app tests/ ./tests/
  USER app
  ```

  **The file carries the two purpose comments above and nothing else.** `CLAUDE.md` §6 rejects item
  numbers in source; the mapping from each line to the record that fixed it lives here.

  *Two things 2.9's four-line sketch omits, and without either the build does not do what it says.*
  `pip install --no-deps .` builds our package and therefore needs `pyproject.toml` in the context,
  which that sketch copies only `src/` for. And **the non-root switch has one correct position**:
  after both installs, because `pip` writes into root-owned `site-packages`. The `test` stage
  inherits `USER app` from `runtime` and must return to root to install the dev group — a build-time
  state that ends before the stage does, so the test container runs non-root like every other.
  *Rejected — installing the dev group before dropping the user in `runtime`:* it would put `pytest`,
  `ruff` and `mypy` in the image the API runs, which is the one thing 3.7 split the stages to
  prevent. *Rejected — `pip install --user`:* `app` is a system account with no home, and it would
  split the install across two locations.

  *Why `/app` is owned by `app`, folded into the `adduser` layer rather than given a `chown` of its
  own.* `pytest` writes its cache into the rootdir, which is `/app` itself and not the `tests/`
  directory — so `COPY --chown` on the tests does not reach it, and a root-owned `/app` costs a
  warning in the stream 11.3 wants clean. **Stated at its real size: a warning, not a failure.**
  Folding `mkdir` and `chown` into the layer that already exists costs no layer at all, and the
  ownership weakens nothing, because 3.3's src-layout means the running code is the installed
  distribution in `site-packages` — `/app/src` is a copy nothing imports once the build is done.

  *`PYTHONUNBUFFERED=1` is load-bearing, not hygiene.* Python block-buffers stdout when it is not a
  terminal, so without it `docker compose up` shows nothing until a buffer fills — which would land
  on 11.3's PASS/FAIL summary and on 8.6's dispatch line, the two outputs the reviewer is watching
  for.

  *The base, and the one hole left open deliberately.* `slim` is 3.7's and the 3.12 family is 2.9's;
  **Alpine is unavailable rather than declined** — 2.5 and 2.10 both record that `psycopg[binary]`
  ships no musl wheel, so an Alpine base breaks the approved list. The tag is **not** pinned to a
  digest: 2.9's two generated requirements files already lock everything we chose, and what a
  floating tag still brings is OS security patches. A digest would trade those for a reproducibility
  nothing here consumes, in an environment `docker compose down` destroys (A19). *This is a real gap
  and it is chosen, not missed:* a base rebuilt months later is not byte-identical to the one this
  was developed against.
  *Rejected — a third "builder" stage* installing into a separate prefix and copying only the result
  into a clean final image. Its purpose is to leave a compiler toolchain behind, and **there is never
  one to leave**: `psycopg[binary]` was chosen precisely so that nothing compiles. A third stage with
  no output.

  *`.dockerignore`, as a deny list:* `.git`, `.venv`, `__pycache__/`, `*.pyc`, `.mypy_cache/`,
  `.ruff_cache/`, `.pytest_cache/`, `.env`, `.claude/`, `docs/`. **`.env` is the one that matters
  beyond build speed** — 10.3 has it feed Compose interpolation and reach no container ever, and a
  copy baked into the image would contradict that silently.

  **Exec form, in both places — and the second is where the exposure actually is.** 8.8 requires the
  image's `CMD` to be exec form. 11.1 then gave every service its own `command:`, which **overrides
  that `CMD` entirely**, so the worker never runs the command 8.8's requirement protects. Both are
  therefore fixed here as list form, and the requirement stands on three legs rather than one:
  `uvicorn` needs the signal to finish in-flight HTTP requests; under shell form every service is
  force-killed at the end of the grace period on every `down`; and 8.8's shutdown handler needs it.
  **It survives the loss of the third** — recorded because 8.8 is under a reopen request.

  | Service | `command` |
  |---|---|
  | `api` | `["uvicorn", "pizza.entrypoints.api.main:app", "--host", "0.0.0.0", "--port", "8000"]` |
  | `worker` | `["python", "-m", "pizza.entrypoints.worker.main"]` |
  | `schema` | `["python", "-m", "pizza.entrypoints.schema.main"]` |
  | `cli` | `["python", "-m", "pizza.entrypoints.cli.main"]` |
  | `tests` | **not fixed here** — 12.9 is open and U11's; this item binds only the form |

  The literal `8000` is 10.4's, which fixed the internal port as a constant in the image's command
  rather than a variable. The `CMD` is the API because a bare `docker run` should do something
  coherent; all five services override it.

  **No build step before `up`.** 11.1's `build:` blocks mean `docker compose up` builds what is
  missing, so the launch R15 is graded on stays one command. The README documents
  `docker compose up --build` for a rebuild after a source change, which is a second command for a
  case the reviewer's first run does not contain. First-run cost is answered by the three mechanisms
  above — the dependency layer before the source, the `.dockerignore`, and a `slim` base — and not by
  a fourth.
  *Source:* R14, DoD "Docker Deployment". *Constrained by:* 2.5, 2.9, 2.10, 3.3, 3.7, 8.8, 10.4,
  11.1, 11.3. *Extends:* 8.8's exec-form requirement to Compose's `command:`. *Leaves to U11:* the
  `tests` command (12.9). *Realised in:* U9.

- **11.10 Compose command form.** `[decided]`
  *Decision:* **`docker compose` — the v2 plugin — with a documented prerequisite of
  v2.24 or later, and no top-level `version:` key in the file.**
  *Why there is no real alternative:* `docker-compose` v1 is a separate end-of-life Python tool, and
  none of the three features this design rests on is fully available in it.

  **This item exists to confirm three deferred assumptions and to set the floor 10.3 recorded as
  missing.** 9.3 assumed v2 for `profiles`, 11.1 for `attach:`, and 11.2 for long-form `depends_on`
  conditions; all three are confirmed.

  *Where the number comes from, and why it is above the true minimum.* Of the features in use,
  `attach:` is the newest at **v2.20** — `profiles`, long-form `depends_on` and
  `service_completed_successfully` are all older, and 11.4's `--exit-code-from` and Compose's
  `${VAR:-default}` interpolation older still. **v2.24 is named deliberately above that floor**, on
  two grounds: it is the one Compose version already written in this record (10.3), so the repository
  states one floor rather than two; and a prerequisite errs safely upward — a reviewer above it loses
  nothing, while one below it gets a README line instead of an unexplained parse error.
  *10.3's 2.24 does not itself raise the floor:* it belongs to `env_file: required: false`, which that
  item **rejected**, and a declined feature sets no requirement.
  *No top-level `version:` key.* It is a v1 artefact that v2 warns about on every run — one more line
  in the stream 11.1's `attach: false` exists to keep clean.
  *What the floor actually does:* it documents rather than constrains, since Docker Desktop has
  shipped well past it for years. Its value is that an old machine produces a sentence in the README
  instead of a YAML error that explains nothing.
  *Source:* R14, R19. *Constrained by:* 10.3, 11.1, 11.2, 11.4, 9.3. *Confirms:* 9.3's, 11.1's and
  11.2's version assumptions. *Realised in:* U9.

- **11.11 Restart policies.** `[decided]`
  *Decision:* **`on-failure`, uncapped, on the four services meant to stay up; nothing written on the
  three one-shots.**

  | Service | `restart` |
  |---|---|
  | `postgres`, `rabbitmq`, `api`, `worker` | `on-failure` |
  | `schema`, `tests`, `cli` | the default — the key is absent |

  *This is what 8.8 handed here as a requirement:* the worker's resilience **is** this policy, since
  nothing in its code retries a broker it cannot reach.
  *Why `on-failure` and not `always` — and the honest answer is narrower than the one first written
  here.* This record originally argued that 8.8 gave the exit code a meaning, `0` separating "leave
  me" from "restart me". **8.8 is under a reopen that removes the `SIGTERM` handler**, and that
  meaning goes with it: `start_consuming()` returns only when `stop_consuming` is called, which was
  the handler's whole work. The worker is then left with two exits — a non-zero code on a broker it
  cannot reach, and `143` on `SIGTERM` — and exit `0` becomes unreachable, so the distinction the
  argument honoured stops existing.
  *What actually separates the two values, at its real size:* **in every path this system has, almost
  nothing.** Docker applies no restart policy to a container stopped deliberately — `down`, `stop`,
  or `Ctrl-C` on a foreground `up` — so the `143` never triggers a restart under either value. One
  narrow difference survives, and it is real here: `always` revives a manually stopped container when
  the Docker daemon restarts, and 13.4 documents a manual `docker compose stop` for the broker-down
  path. Beyond that the choice is what the word states — `on-failure` names the condition that
  warrants a restart, which is also the rule the three one-shots below are the exception to.
  *Why uncapped:* 11.2 already prevents the startup crash-loop, since the worker does not start until
  the broker is healthy. What remains is a broker that dies later, and a cap would abandon one that
  comes back after the last attempt. Docker's own increasing delay between attempts is what bounds
  the cost, and 8.8 named it.
  *Recorded because it is the obvious worry and it does not apply:* a restart loop cannot mask a bug
  of ours. 8.4 catches every exception inside the consumer callback and ends in a `reject`, so the
  process does not fall over — a worker that exited means infrastructure.

  *The same policy on the API and the two vendor services*, as one rule rather than three. 2.5
  already assumed it, naming *"a database container restart (11.11)"* as one of the cases
  `pool_pre_ping` exists for. What it buys concretely: a transient crash heals itself, and a
  permanent one — a rejected environment variable at startup (10.2) — appears as a mounting restart
  count in `docker compose ps` with the same error repeating in the log, which is diagnosable rather
  than silent.

  *The three one-shots carry no policy, and for `schema` that is load-bearing rather than tidy.*
  `depends_on: condition: service_completed_successfully` waits for a successful exit, and a service
  that restarts never reaches one — the whole stack would hang instead of failing. It is also what
  4.6 asked for: a failed schema creation should be **one service's clear non-zero exit**, not a
  loop. For `tests`, a restart would re-run the suite indefinitely and break 11.4's
  `--exit-code-from tests`, which reads the exit of a service that is expected to stay exited.

  *What this does not cover, stated so nothing is assumed:* a container that is alive and not working.
  6.6 already recorded the mechanism — plain Compose does not restart an unhealthy container, and a
  healthcheck only gates `depends_on`. No self-healing exists here for that case and none is built.
  *Rejected:* **`always`** and **`unless-stopped`** — above; **`on-failure:N`** — above; **a policy on
  the one-shots** — above.
  *Source:* R14, DoD "Docker Deployment". *Constrained by:* 2.5, 4.6, 6.6, 8.4, 8.8, 11.2, 11.4.
  *Holds:* 8.8's restart requirement. *Realised in:* U9.


## Topic 12 — Testing

- **12.1 Risk ranking.** `[decided]`
  *Decision:* **four scenarios**, and the rule that selected them.

  *The criterion:* **risk = silence × consequence.** A failure that announces itself — `404`,
  `409`, `422`, a crash — is not a candidate on risk grounds, because the first person to run the
  system finds it. A failure that is silent but harmless is not one either: that is the reasoning
  that kept the `outbox` out of 12.3. Both factors must be present, which makes it a product and
  not a sum. **Cost does not enter the ranking; it breaks ties** — and it broke exactly one.

  | # | Scenario | What only this one asserts | Failure modes |
  |---|---|---|---|
  | **1** | **A complete order, `RECEIVED` to `DELIVERED`**, driver registered first | assigned at `BAKING`; **the same** driver after `READY`, not a second; `AVAILABLE` again after `DELIVERED` | F3, F8, F12 |
  | **2** | **No driver, retry, recovery** — `BAKING` against an empty pool, then a driver registers | the order stays `PENDING`; the message is neither lost nor fatal; assignment follows registration | F7 (recovery) |
  | **3** | **One driver, two orders** — scarcity and hand-off | no driver is assigned to two orders; a released driver reaches the order waiting for it | F2 (outcome), A13 |
  | **4** | **API rule enforcement** | `409` on a non-adjacent transition, `422` on invalid input | F9, F13 |

  *Why one scenario may carry several failure modes:* F3, F8 and F12 are not separate events —
  they are **successive states in the life of one order**. R5 publishes at `BAKING` and again at
  `READY`, so the duplicate is not an edge case a test has to construct; it is what every order
  does. Splitting them would build the same order three times to assert one fact each, which is
  the pyramid `CLAUDE.md` §5 forbids. Scenario 1 is therefore written as the normal path, and
  collects the failure modes that lie along it.

  *Why scenarios 1 and 2 are not one test:* they share a single assertion — that assignment
  happens — and nothing else. Scenario 2's subject is what the worker does while it **cannot**
  assign: the message survives, the consumer does not die on it, and the order is visibly
  `PENDING` meanwhile. Scenario 1 never enters that state. An earlier draft merged them, arguing
  that a happy path is a strict subset of the retry path; that holds only for a happy path
  stopping at `BAKING`. Carried through to `DELIVERED` it asserts two things — the duplicate
  no-op and the release — that the retry path never reaches.

  *What was ranked and left out:*

  | Candidate | Why not |
  |---|---|
  | Retry budget exhausted, `assignment_state = FAILED` (F7 terminal) | a genuine risk, and the one tie the cost rule broke: 1.2's floor puts `TTL × cap` above 60 s and 11.6 gives the suite the shipped configuration, so it would add about a minute to **every** `docker compose up`. FW13 is where it becomes affordable |
  | Broker unreachable (F4), malformed message (F10) | 12.3 admits neither interface |
  | Concurrent `PATCH` on one order (F14) | 6.9 is open — there is no decided behaviour to assert against |
  | Unknown order id (F1) | loud, and a single status code |
  | Database down mid-assignment (F5), worker crash before ack (F6) | both need process control; F6's partially-applied state is covered by 5.5's guard, which scenario 1 exercises |
  | The **ghost driver** (4.3) | the inventory flags it as a candidate, and it is not one: it is a **defect state, not a behaviour**. No sequence of legal calls produces it, so there is nothing for a test to drive. What is testable is that assignment writes both sides, which scenario 1 asserts |

  *What this hands to 12.5, and it is a real problem rather than a formality:* scenario 1 ends
  with a released, `AVAILABLE` driver, while scenarios 2 and 3 both need scarcity. Run in that
  order their premise dissolves — so **order matters**, and §5 says it must not. 11.6 already
  named the cause: the driver pool is global, and a "no driver available" scenario cannot be
  scoped to one test's data. 12.5 owns the resolution; truncating between tests is not available
  to it, because 12.3 admits no database client and truncation would not clean the wait queue
  that scenario 2 deliberately leaves occupied.

  *What no scenario covers, stated because the gap is real:* 8.9's row locking is never
  contended. 8.5 runs one consumer at prefetch 1, so two events are claimed in sequence and
  scenario 3 would pass with `FOR UPDATE SKIP LOCKED` removed. FW7 is where the mechanism is
  verified rather than argued.

  *Left to 12.2:* the assertions themselves and the rationale for each. This item ranks and
  selects; it does not write the tests.
  *Source:* R18, `CLAUDE.md` §5. *Constrained by:* 11.6, 12.3, A17. *Constrains:* 12.2, 12.4,
  12.5, 12.8. *Depended on by:* 1.2.

- **12.2 The chosen scenarios.** `[decided]`
  *Decision:* four scenarios, five test functions, and the assertion set for each. 12.1 selected
  them; this item states what each one asserts and why each assertion earns its place.

  *Where the rationale lives — three homes at three resolutions, following 13.6's rule that a
  record which carries no reasoning cannot go stale:*

  | Home | Contents |
  |---|---|
  | **This record** | the assertion tables below and the reason for each. **Authoritative** |
  | **A docstring above each test** | two lines — which scenario, and why it matters (§5) |
  | **The README** (13.1) | the four scenario names and one line each. **Names only, no reasoning** |

  *The bar every assertion below had to clear:* **assert the state the rule produces, never the
  response.** An assertion earns its place only if it would fail when the behaviour it names
  breaks (§5). Over-assertion is the failure mode here, not under-assertion: a test that checks
  every field breaks on every contract change while catching nothing.

  ---

  **Scenario 1 — Complete order lifecycle.** `test_complete_order_lifecycle`
  *Description:* register a driver, place an order, and advance it `RECEIVED → PREPARING →
  BAKING → READY → DELIVERED`.
  *Goal:* the normal path end to end, and the two failure modes that lie along it — the duplicate
  event at `READY`, and the release at `DELIVERED`.

  | After | Assertion | Why it earns its place |
  |---|---|---|
  | creation | `status=RECEIVED`, `assignment_state=PENDING`, `driver` is `null` | fixes the initial state R1 names, and proves 6.5's key is present-and-`null` rather than absent |
  | `PREPARING` | `driver` still `null` | the **negative control for 5.3**: if the publish trigger fired on every transition instead of on `BAKING`/`READY`, a driver would already be attached |
  | `BAKING`, after waiting (12.4) | `assignment_state=ASSIGNED`, `driver.id` is the registered driver, `driver.status=BUSY`, `assigned_at` present | R5 through R8 in one assertion — publish, consume, claim, assign, mark busy |
  | `READY`, over a bounded observation window (12.4) | still the same `driver.id`, still `ASSIGNED` | R5 publishes a **second** event on every order. If 5.5's guard broke, a second driver would be claimed or the assignment overwritten. This is the only place the duplicate is exercised |
  | `DELIVERED` | `status=DELIVERED`, `assignment_state=COMPLETED`, `driver.id` **unchanged**, `driver.status=AVAILABLE` | 5.6's release together with 4.4's "`driver_id` is never cleared". Asserting both is what distinguishes a release from an unassignment |

  ---

  **Scenario 2 — Recovery when no driver is available.**
  `test_recovery_when_a_driver_registers`
  *Description:* with no `AVAILABLE` driver, place an order and advance it to `BAKING`; observe;
  then register a driver. **No further `PATCH` is sent** — that is what makes this a retry rather
  than a re-trigger.
  *Goal:* R9 and R10 — the worker neither loses the message nor dies on it, and dispatch resumes
  on its own.

  | After | Assertion | Why it earns its place |
  |---|---|---|
  | `BAKING`, over a bounded window | `assignment_state=PENDING`, `driver` is `null` | proves the worker invented no assignment when none was possible. `PENDING` rather than `FAILED` also separates "still retrying" from "gave up" (8.3) |
  | registering a driver, after waiting | `assignment_state=ASSIGNED`, `driver.id` is that driver, `driver.status=BUSY` | **the whole scenario rests here.** It is the only observable evidence that the rejected message returned from 8.2's wait queue instead of being dropped, and that the consumer was alive to receive it. "The worker did not crash" is not a separate assertion — over HTTP it has no witness, and this outcome is its proof |

  ---

  **Scenario 3 — One driver, two orders.** `test_one_driver_two_orders`
  *Description:* register exactly one driver; place two orders and advance both to `BAKING`; then
  advance the assigned one to `DELIVERED`.
  *Goal:* A13 — one active order per driver — and the composition of release with retry.

  | After | Assertion | Why it earns its place |
  |---|---|---|
  | both reach `BAKING`, once settled | **exactly one** order is `ASSIGNED` with that driver; the other is `PENDING` with `driver` `null` | if the claim ignored `status='AVAILABLE'`, or if the assignment failed to mark the driver `BUSY` in the same transaction, **both** orders would show the same driver. This is the assertion that fails if 4.3's cross-table invariant breaks |
  | the assigned order reaches `DELIVERED`, after waiting | the waiting order becomes `ASSIGNED` to the same driver, `driver.status=BUSY` again | proves release **feeds dispatch**: 5.6 does not merely flip a status, it returns the driver to the claimable pool, and 8.2's wait queue really re-delivers. Scenario 1 releases with nobody waiting; scenario 2 recovers through registration. Neither composes the two |

  *Which of the two orders wins is deliberately not asserted* — that would be an assertion about
  queue arrival order, which no decision fixes.
  *This scenario depends on a generous retry budget:* the waiting order must not exhaust its
  attempts before the delivery happens. 1.2's `TTL × cap ≥ 60 s` floor, which cost 12.1 the
  exhaustion scenario, is what makes this one safe.

  ---

  **Scenario 4 — API rule enforcement.** Two functions.
  *Goal:* the two rules this project **invented** rather than inherited — A3's strictly linear,
  single-step chain, and 4.2's edge validation.

  `test_illegal_transition_is_refused`

  | Request | Assertion | Why it earns its place |
  |---|---|---|
  | `RECEIVED → BAKING` | `409` | 5.1 forbids skipping. R2 lists the chain in a way that makes a skip look permissible, so this is the reading a reviewer will probe |
  | then read the order | `status` still `RECEIVED` | a `409` that partially applied would be worse than no rule at all |
  | current status re-sent | `409` | 5.1's least obvious half — re-sending the current status is illegal. It is what removes the "does a repeated `PATCH` re-publish" question, and nothing else exercises it |

  `test_invalid_input_is_refused`

  | Request | Assertion | Why it earns its place |
  |---|---|---|
  | order with `items: []` | `422` | 4.2's bounds are the only thing standing between an unbounded field and the core |
  | order carrying an unknown field | `422` | 4.2 chose `extra="forbid"`, which is a **declaration, not code** — exactly the kind of thing that vanishes silently in a schema rewrite, with nothing else in the system noticing |
  | `PATCH` with an unrecognised status string | `422`, **not** `409` | this is why 5.2 exists. If both returned one code, the illegal-transition test above could no longer tell a rule failure from a typo |

  ---

  *What is never asserted, and why each is deliberate:*
  the dispatch log line — 8.6 rules it out explicitly; timestamp **values** — only `assigned_at`'s
  presence matters, and 4.8 gives the core a clock port precisely so nothing depends on wall time;
  echoed input (`customer_name`, `address`, `items`) — no rule reads them (4.2), so an assertion
  would test the framework; the `outbox` row — 12.3.

  *Depends on, and each is resolved before U10 by `CLAUDE.md` §2:* 6.2 for the success codes on
  creation — the tables above name only the codes 5.2 and 4.2 already fixed; 12.4 for the waiting
  primitive and the bounded observation window; 12.5 for the precondition scenarios 2 and 3 share
  — no `AVAILABLE` driver beyond the ones they register themselves.
  *Source:* R18, DoD "Test Automation". *Constrained by:* 12.1, 12.3, A17. *Constrains:* 12.4,
  12.5, 12.7, 13.1. *Answers:* Q16 in full.

- **12.3 Interface each test drives.** `[decided]`
  *Decision:* **HTTP only — for assertions and for arranging state.** The integration suite
  speaks to the API over HTTP and to nothing else: no database client, no broker client, no
  control over containers. 12.4's waiting primitive polls `GET /orders/{id}`.

  *Why HTTP is not merely sufficient, but the surface this system was built to expose:* 6.5 and
  6.6 were decided so that internal state is observable from outside — the nested driver object,
  `assignment_state`, `assigned_at`, the order list. Reading the same facts with SQL would go
  around a surface that exists for exactly this purpose. It is also the contract the CLI speaks
  (3.6) and the one a reviewer can reproduce with `curl`, so a failed assertion is a failure they
  can repeat by hand rather than one the suite has to explain.

  *What HTTP covers — counted, not asserted:*

  | Behaviour | Observed as |
  |---|---|
  | Successful dispatch (R7, R8) | nested driver, `ASSIGNED`, `assigned_at` (6.5) |
  | No driver, retry, then assignment (R9) | `PENDING`, then `ASSIGNED` |
  | Retry budget exhausted (8.3) | `assignment_state: FAILED` |
  | Driver release at `DELIVERED` (5.6) | `driver.status: AVAILABLE` |
  | Idempotence against the duplicate event (5.5) | the same driver, not a second one |
  | Illegal transition (5.2) | `409` |
  | Race for the last driver (F2) | two orders, one driver, exactly one wins |

  *The one thing it cannot see, and why that is acceptable:* the `outbox` row (7.5). A23 states
  that nothing replays it, so inside the system the table has no reader at all — a forgotten
  `INSERT` breaks in total silence, and with no consequence. No DoD row degrades, no behaviour
  changes, no interface reports differently. `CLAUDE.md` §5 ranks candidates by risk, and risk is
  not silence alone; this is the lowest-consequence failure in the record. If FW2's relay is ever
  built it becomes a reader, and this changes.

  *Arranging state needs no other interface either:* 11.6 already chose unique data per test over
  truncation between tests, resting on the clean start 11.7 supplies. There is nothing for a
  database client to set up.

  *What this costs, stated plainly:* the broker-unreachable path (7.6) gets no automated test. It
  is the highest-consequence failure mode in the design (F4) and the likeliest interview
  question, and it stays a documented trade-off (13.4) instead of a scenario. Covering it would
  need both interfaces this item rejects — the `outbox` read, and a way to make the broker
  unreachable from inside the test container. 1.2 left the same path out of the demo path for the
  same reason; the two exclusions agree by construction rather than by coincidence.

  *Rejected — **HTTP plus database inspection**.* The orthodox integration-test arrangement, and
  the strongest alternative. Its only unique yield here is the `outbox`, which is the item above.
  **The rejection rests on the boundary, not on the dependency:** 3.7 runs the suite from a stage
  derived from the services' own image, so SQLAlchemy is present and the read costs no install —
  and it is still declined, because an assertion against a column couples the test to a schema that
  `CLAUDE.md` §5 calls an implementation detail, and a rename would then fail a test whose named
  behaviour did not break.
  *Rejected — **direct broker publication**.* Only a poison-message scenario needs it, and 8.4 is
  still open. It carries a defect of its own: the message is composed by the test, so the suite
  can pass against a shape the API never emits.
  *Rejected — **container control from inside the suite***, mounting `/var/run/docker.sock` in
  order to stop the broker mid-run. A real privilege expansion in a compose file handed to a
  stranger, for one scenario out of the four R18 allows.
  *Rejected — **driving the CLI***. 3.6 made it a thin adapter with no logic over this same
  contract, so the test would assert on terminal output, which is presentation.

  *Reopen condition, written as a rule rather than a list:* a non-HTTP interface is admitted only
  when a behaviour 12.1 selects has **no HTTP-observable effect at all**. Two candidates exist
  today — the poison message (8.4) and the broker-unreachable path (7.6) — and if 12.1 chooses
  either, this item reopens.
  *Hands to 2.6:* one HTTP client, and nothing else; topic 12 adds nothing to 2.10's list.
  *Source:* `CLAUDE.md` §5. *Constrained by:* 6.5, 6.6, 11.6, 11.7. *Constrains:* 2.6, 12.1,
  12.2, 12.4, 12.5. *Feeds:* 13.4.


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

- **14.1 Public remote.** `[decided]`
  *Decision:* **`https://github.com/cs7158080/pizza-dispatch-engine`, public** — the link R21 asks
  for. It already carries the history, so the inventory's timing concern is answered by fact. A
  clean repository for delivery would discard what 14.5 ships it for.
  *Consequence, and why 14.6 was verified rather than assumed:* §4 forbids rewriting pushed
  history, and a public repository exposes its whole past — so a secret committed once stays.
  *Source:* R21. *Constrained by:* 14.5. *Constrains:* 14.6.

- **14.2 Branch convention and merge style.** `[decided]`
  *Decision:* **`<type>/u<N>-<slug>`** — `chore/u1-foundation`, `feat/u3-business-core` —
  **squash-merged; branches are not deleted.** `<type>` is §4's conventional-commit set, and the
  number makes 14.4's map readable from the branch list. The two branches predating the unit
  table keep their names.
  *Why squash, when 14.4 puts a real commit on every step.* The step commits stay on the retained
  branch; squash decides only what reaches `main`. Counted, a merge-commit `main` would carry
  about eighty entries — some fifty step commits, thirteen merge nodes with GitHub's default
  message, and eighteen planning commits — against fourteen under squash. GitHub's commit list is
  the surface a reviewer opens first, and there fourteen unit-level lines beat eighty mixed ones
  for a reading measured in minutes.
  *What it costs and how it is paid:* step grain is not visible from `main`. 14.5 already requires
  a README section on how the repository was built; one sentence there points at the unit
  branches — the same verification, in the place a reviewer is already reading. GitHub also
  carries the step messages into the squashed commit body.
  **This record reached squash twice by different routes.** The first form argued it from the
  claim that a merge node carries no information. That is false — it carries the unit boundary —
  and the claim is withdrawn. The decision stands on signal density alone.
  *Rejected:* **merge commit** — the more faithful history, and the better choice in a project
  whose history is not itself a deliverable read under time pressure. **Rebase merge** — every
  step on `main` with no unit boundary at all.
  *Branches are kept:* §4 requires separate approval per deletion, and after squash they are where
  step grain survives.
  *Source:* `CLAUDE.md` §4. *Constrained by:* 14.4. *Requires:* one README sentence (13.1, 14.5).

- **14.3 How much of the branch-per-unit workflow is executed.** `[decided]`
  *Decision:* **a pull request per unit — thirteen for code, one for the planning branch — with
  no self-review stage and no CI.** `gh` is installed locally, so a merge is two commands; like
  `uv` it is a tool, not a dependency.
  *Why the pull requests stay:* §4 says "even when working alone", which already answers this
  item's objection — and that agreement ships (14.5), so departing from it is visible.
  *No self-review, stated rather than dressed up:* the value is the record, not a review pause a
  person performs against themselves.
  *No CI:* R15 already has `docker compose up` run the suite and 11.3 print PASS/FAIL, which
  outweighs a lint badge; 12.10 may put `ruff` and `mypy` in the same run. **Accepted cost:** a
  locally skipped check has nothing to catch it.
  *Planning commits.* Phase 1 and the decisions taken before the split landed through one pull
  request from `plan/project-planning`. **Phase 2 and Phase 3 then part company, because they run
  on different clocks.** A unit's remaining Phase 2 items are settled on a short `plan/u<N>-gate`
  branch of its own. Its Phase 3 document is the **first commit on the unit's own branch**,
  followed by the step commits, so one pull request carries the plan and the implementation it
  produced, and a mid-flight replan (§2 Phase 4) lands in the same place. **No unit lacks a pull
  request; only commits inside units do.**

  *When a gate branch merges — writing and merging are separate acts, and this record conflated
  them until 2026-08-11.* The branch is **written** whenever a session is free, which is what
  makes parallel planning possible at all. It is **merged when its contract is first needed**:
  before the earliest unit that must know it, which is not necessarily the unit it is named after.
  *Why not "promptly", which this record said before:* prompt merging buys visibility between
  parallel sessions and nothing else, while planning runs ahead of building — so a gate could land
  on `main` up to five units before the unit it opens. `main` would stop reading as "decide, then
  build", in a history that is itself a graded deliverable a reviewer reads (R21, 14.5). Ordering
  merges by need restores that reading at no cost to parallelism: the work still happens whenever
  a session is free, and only the merge point is chosen rather than falling out of when a session
  happened to run.
  *The accepted cost:* a waiting gate branch is invisible to anyone who does not know to look for
  it. The merge point is therefore weighed at each unit rather than obeyed, and a session opening
  a unit whose gate is unmerged has to be told the branch exists — U1 §8 already had to say
  exactly that about `plan/u6-gate`.

  *The status table's `Total` cell is recounted at merge time and never carried from a branch.* It
  is computed against the merged file with `grep -c '\[decided\]'`, verified to equal the cell.
  Every gate branch increments that one cell, which makes it the only certain conflict in parallel
  work, and a count taken on a branch is stale by definition the moment another gate merges first.
  This has already produced one wrong count in the record.
  *Rejected:* **local `--no-ff` merges** — identical `main`, and the deviation §4 pre-emptively
  named. **A pull request per step** — forty to sixty. **A separate pull request for a unit's
  planning, before its implementation** — the closest reading of §2 Phase 4, and it buys no real
  evidence: with no self-review stage a merged pull request records that merge was pressed, not
  that a review happened. The ordering stays visible anyway, since the planning commit precedes
  the step commits on the branch. **CI as a required gate** — an external dependency for checks
  that already run before every commit.
  *Source:* `CLAUDE.md` §4. *Constrained by:* 14.2, 14.4. *Answers:* 2.8's CI deferral.

- **14.4 Unit-to-commit map.** `[decided]`
  *Decision:* **one commit per Phase 3 step; one branch and one pull request per unit.** The map
  is written in each unit's Phase 3 document — the step count is unknown until the unit is
  planned.
  *This resolves a contradiction.* §2 Phase 3 ("each step maps to exactly one commit"), §8.5
  ("committed on its own branch") and §4 ("one branch per plan **step** or feature") put the
  commit at step grain; Part 4 of `03-roadmap.md` ("one branch and one commit") puts it at unit
  grain. The outlier is the one in a planning file, which cannot amend the working agreement.
  *Why the branch is nevertheless per unit:* §4's "or feature" admits it, and a branch per step is
  forty to sixty branches.
  *Why not one commit per unit:* §8 gives every **step** a full Definition of Done. That describes
  a commit, not work in progress.
  *Two texts narrowed to match:* §8.5 to "on the unit's branch"; Part 4 to "one branch and one
  pull request, carrying one commit per plan step".
  *Source:* `CLAUDE.md` §2, §4, §8. *Constrains:* 14.2, 14.3, 14.7, every Phase 3 document.

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

- **14.6 `.gitignore` adequacy.** `[decided]`
  *Decision:* **adequate but for editor directories.** `.vscode/` and `.idea/` sit commented out
  in the GitHub template and §4 names editor files; both are uncommented, as a step in U1.
  *Verified with `git check-ignore` over eighteen paths, including ones that do not exist yet.*
  Three results other items rest on: `.env` ignored, `.env.example` not (10.3); 2.9's generated
  lock files tracked; `.claude/` matching 14.5 exactly.
  *Not trimmed:* 224 lines of GitHub template, mostly irrelevant — cutting it risks removing a
  line that was needed and buys nothing.
  *Source:* `CLAUDE.md` §4. *Constrained by:* 14.1. *Realised in:* U1.

- **14.7 What "main still runs" means in the early units.** `[decided]`
  *Decision:* **the strongest verification the system currently supports, as a command that exits
  zero.** Each unit that adds a level raises the bar permanently.

  | From | "runs" means |
  |---|---|
  | U1 | `ruff format --check .` · `ruff check .` · `mypy src tests` · `python -c "import pizza"` |
  | U2 | + `pytest tests/unit` |
  | U9 | + `docker compose up` reaches 11.3's PASS summary and the test service exits zero |
  | U11 | + the same with the full integration suite |

  `python -c "import pizza"` is not filler: 3.3 chose src-layout so an import resolves only
  through the install, so its failure means the package is not installed.
  *The `pytest` row moved from U4 to U2 on 2026-08-11.* U4 is the unit that fills
  `tests/unit/`, but U2 gets there first: 10.2's loader is pure logic with no infrastructure, so
  §5 admits its tests as free, and §8.2 requires every step's behaviour to be verified by a test
  that would fail if it broke. Recorded here rather than as a reading inside U2's plan, because a
  Phase 3 document may fill a silence this file left but may not amend one of its rows.
  Each Phase 3 document states its own list, and it applies **per step commit** — so `main`
  satisfies §8.6 after a merge by construction.
  *Rejected:* treating it as vacuous until U9 — §8.6 would be ceremony for eight units, and
  nobody starts believing it later.
  *Source:* `CLAUDE.md` §8. *Constrained by:* 14.4. *Constrains:* every Phase 3 document.


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
| **A14** † | `GET /orders` exists — light list, newest first, no cap and no paging | 6.6 |
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
| **A25** † | The local credentials are non-secret committed defaults for a disposable environment; a real deployment supplies its own | 10.5 |
| **A26** | Every configuration value comes from the environment, and `docker-compose.yml` is the only place a default is written | 10.1, 10.2 |

*Superseded:* A11 previously read "a list of typed objects — `name`, `quantity`, `toppings`".
It was narrowed on 2026-08-07 when 1.1's ceiling test was applied to it; the structure is now
FW11. A12 previously described the nested driver as produced by a `LEFT JOIN`, which
contradicted 6.5's decision to use two keyed reads. **6.5 is authoritative**; the register no
longer names a read mechanism at all. A15 was narrowed on 2026-08-09: it previously required
the broker to be reachable for `/health` to return `200`, which 7.6 made false. A14 dropped its
cap on 2026-08-10: the list previously returned the 50 most recent orders.
