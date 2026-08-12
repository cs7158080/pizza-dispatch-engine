# U5 — Persistence · Implementation Plan

**Phase 3 of the planning protocol in `CLAUDE.md` §2, for the fifth unit in Part 4 of
`03-roadmap.md`.** Decisions are in `02-decisions.md`; nothing here decides anything that
belongs there. Where executing a step needed a call Phase 2 had not made, it is recorded below
under *Readings* rather than left to implementation.

**Gate.** U5's *Decided by* column reads 2.2, 2.5, 4.5, 4.6, 7.3, 7.5 and 8.9. All are
`[decided]`. 4.5 and 4.6 reached `main` as pull request #9, merged where U5 first needs them per
14.3, and 7.3 was added to the column by commit A below — the module it places was filed under a
unit this one does not depend on, which is the same shape as the 7.2 finding at U3's gate. U2 and
U3 are merged, so both dependencies are real rather than nominal. Two open items are touched and
neither is decided here: 12.7 owns how the test directories are invoked, and this unit only adds
files to `tests/unit/`; 8.7 owns logging, and this unit logs nothing.

---

## 1. What this unit delivers

Part 4 gives U5 six things: schema creation (4.6), the repository implementations, the `outbox`
table with its insert and mark-published operations (7.5) together with the event serialization it
stores (7.3), the integrity constraints (4.5), and concurrency-safe driver claiming (8.9).

That is **every port U3 declared, implemented** — `Clock`, `OrderRepository`, `DriverRepository`,
`OutboxStore` and `UnitOfWork` — plus the schema those adapters write into and the one-shot service
that creates it. After U5 the repository holds the whole of layer 3's driven side: the core can be
given something real to run against, and still nothing runs it. There is no API, no worker and no
publisher, so no process wires an adapter to a use case yet.

`infrastructure/` is also the first code able to break 3.1's dependency rule, since it is the first
code allowed to import a third-party library at all. Step 1 turns that rule into a lint rule before
any of it is written.

## 2. What this unit deliberately does not deliver

Each line names the item that owns it, so nothing here is silence.

| Not built | Owner | Arrives in |
|---|---|---|
| The api and worker composition roots — the `Engine`, the `sessionmaker`, and 2.5's two session settings | 2.5 places them in `entrypoints/{api,worker}/main.py`; 10.2 owns the loader call | U7, U8 |
| The topology, the publisher, the connection lifecycle | 7.1, 7.7 — this unit writes only 7.3's module, which they import | U6 |
| The Compose service that runs `entrypoints/schema/main.py`, and its two ordering conditions | 4.6 fixes the contract; 11.1 wires it and 11.2 owns the healthcheck it waits on | U9 |
| Any test that reaches the database | 12.3 — the suite speaks HTTP and holds no database client | U10 |
| A relay over unpublished rows | A23, FW2 | not built |
| Migrations, and a `versions/` directory | 4.6 chose `create_all`; FW16 holds the entry and its preconditions | not built |
| Any index beyond the primary keys and 4.5's partial unique | 4.5 weighed four and rejected all four under 11.7 | not built |
| `[tool.pytest.ini_options]`, and how the two test directories are invoked separately | 12.7 — open | U4 |

## 3. Branch, commits, and the merge

- **Branch:** `feat/u5-persistence`, cut from `main` at `570a802` (14.2).
- **Commits:** one amendment commit, one planning commit, then one commit per step (14.3, 14.4),
  and one further amendment where step 4 found a decided expression that the chosen stack does not
  support. Eleven in total.
- **Merge:** one pull request, squash-merged, its title ending in `(#10)` (14.2, 14.3). The branch
  is not deleted (14.2).

| # | Type | Title |
|---|---|---|
| A | amendment | `docs: file 7.3's module under the unit that writes it` |
| B | planning | `docs: plan the persistence layer` |
| C | amendment | `docs: write the outbox payload as the structure the column stores` |
| 1 | step | `chore: let the linter hold the dependency rule` |
| 2 | step | `feat: turn the event into bytes, and back` |
| 3 | step | `feat: give the core a clock it can read` |
| 4 | step | `feat: describe the schema the database enforces` |
| 5 | step | `feat: create the schema once, from a service that exits` |
| 6 | step | `feat: read and write orders, and claim a driver exactly once` |
| 7 | step | `feat: record the event beside the change that caused it` |
| 8 | step | `feat: hold one transaction, and open a second when asked` |

**A is not a plan step.** It amends records rather than filling a silence — the boundary U2 §5
drew and 14.7 stated first — and it rides on this branch rather than on a gate branch of its own,
by the same ruling that placed U2's commit A and U3's commits A to C: it was found while opening
the unit, and it is a handful of cells and lines. **A precedes B** because B cites it, and a plan
cannot cite a record the history does not yet contain.

*What A changed:* three records gave `infrastructure/broker/serialization.py` to U6 while two
others had U5 calling it, and U5 depends on U2 and U3 alone. The module is now U5's, `broker/` is
still where it lives, and the `db/ → broker/` edge that follows is stated in 7.3 rather than left
to be discovered.

**C is not a plan step either, and it came from inside step 4.** 7.3 had the adapter write
`serialize(event).decode("utf-8")` into a `jsonb` column, and SQLAlchemy's `JSONB` runs
`json.dumps` over what it is handed — so an already-serialized string is encoded twice and the row
keeps a JSON string instead of an object, silently. That is a decided record contradicted by the
library 2.5 chose, not a silence this plan may fill, so implementation stopped and the record was
corrected first. Step 7 below is written against the corrected expression.

## 4. The Definition of Done that applies to every step

14.7's U2 row still governs; **U5 raises no bar**, and the next raise is U9's. The five commands
are run from the activated virtual environment at the repository root, and each must exit zero
**at every step commit**:

```
ruff format --check .
ruff check .
mypy src tests
python -c "import pizza"
pytest tests/unit
```

**What changes is what `ruff check .` now enforces.** U3 §4 carried 3.1's import rule as a `grep`
that belonged to its branch and stopped running when that branch merged. Step 1 replaces it with a
lint rule that travels, and from step 1 onward the second command above *is* the layering check.
No step reintroduces the `grep`.

Each step below adds its own checks on top of these. A step is done when §8's six conditions hold.

*Two mechanical notes so no step improvises:* `sqlalchemy` and `psycopg[binary]` are already in
`pyproject.toml` and in both lock files — 2.10 approved the whole list at U1 and only the two
conditional lines were left open, both since closed by declining. **No dependency is added by this
unit, and neither lock file changes.** And U1's editable install is a `.pth` file naming `src`, so
a new subpackage is importable the moment its `__init__.py` exists.

## 5. Readings — where this plan filled a silence

Recorded here rather than resolved silently (`CLAUDE.md` §2). The boundary is U1 §5's, restated in
U2 §5 and U3 §5: a Phase 3 document may fill a silence Phase 2 left; it may not settle an ambiguity
inside a decided record. Anything of the second kind became commit A before this document existed.

- **R-a — the lint rule lands first, before the directories its ignores name.** U3 §8 deferred it
  because per-file ignores naming directories that do not exist are configuration written ahead of
  its subject. Inside this unit that objection expires: the directories arrive two steps later, and
  a rule added after the imports it governs would leave this unit's own steps as the only code the
  rule never guarded. Ruff accepts a pattern that matches nothing today.
- **R-b — each adapter names its `Protocol` as a base class.** Structural typing is checked where a
  value is assigned to the port type, which happens at U7's and U8's composition roots — so without
  this, nothing in this unit compares an adapter to the interface it claims to implement, and U3's
  step 3 promised the second half of that check here. PEP 544 allows explicit subclassing of a
  `Protocol` and it makes `mypy` verify every signature at the class definition. 3.4's "`Protocol`s
  rather than base classes" governs how the ports are *declared* and which way the import points;
  both stand, and any other adapter still satisfies them by shape.
- **R-c — a database exception is translated only where a caller catches it by name.**
  `mark_published` raises `OutboxWriteFailed`, because `AdvanceOrderStatus` catches exactly that
  and continues. Nothing catches a failed `add`, `save`, `get` or claim: those abort the
  transaction and the request, and reach the edge as U7's `500`. Translating them anyway would
  invent a vocabulary with no reader — and the port declares none.
- **R-d — `mark_published` over zero rows raises `OutboxWriteFailed`.** The row was inserted in a
  transaction that has committed, so its absence is a broken invariant rather than a race. The
  caller's handling — log, keep the successful publish — is already the right response to "the mark
  did not happen", and it is the only response the port allows.
- **R-e — the outbox row's `created_at` is `event.occurred_at`.** The port hands the adapter no
  clock, 4.5 forbids a `server_default` because it would be a second clock no test can control, and
  4.8 allows one `Clock.now()` read per operation. `occurred_at` is that read, taken by the use
  case before the transaction opened.
- **R-f — the schema service loads `ServiceSettings`, not a settings model of its own.** It needs
  one variable, `database_url`, and a fourth settings class to hold it would widen 10.1's surface
  for a process that lives for one command. The cost is stated rather than hidden: by U2's R-f the
  container is then given the same variable set as the api and the worker, which §8 hands to U9.
- **R-g — the row↔entity mappers are private functions in `repositories.py`.** 2.5 assigns the
  conversion to the repository, and `models.py` stays what 4.6 needs it to be: `Base.metadata` and
  nothing that imports `domain/`.
- **R-h — the enum `CHECK` constraints are written from the Python enums.** 4.5 fixes `text` plus a
  `CHECK` listing the legal values; generating that list with a comprehension over `OrderStatus`,
  `AssignmentState` and `DriverStatus` is what stops the schema and the core from drifting apart
  silently. It is the same rule in one place, written once.
- **R-i — `list_all` orders by `created_at DESC, id`.** 6.6 fixes newest first and stops there. Two
  orders placed inside the same clock tick would otherwise come back in an order the database is
  free to change between calls, which is a flaky assertion waiting for U10 rather than a behaviour
  anyone chose.
- **R-j — the unit of work takes a `sessionmaker`, not a `Session`.** It must be re-enterable
  (3.5, and U3's step 5 re-enters it after the commit), so `__enter__` opens a fresh `Session` from
  the factory and `__exit__` closes it. The repositories are built inside `__enter__` bound to that
  session, because they cannot outlive it. The factory is built once per process at the composition
  root, which is 2.5's sample and U7's and U8's work.
- **R-k — PostgreSQL column types are named directly.** `UUID(as_uuid=True)`, `ARRAY(Text)`,
  `JSONB` and `TIMESTAMP(timezone=True)` from `sqlalchemy.dialects.postgresql`. 2.2 fixed the
  database and 4.5 fixed `text[]`, `jsonb` and `timestamptz`; a portable spelling would describe a
  portability nothing asks for and would not produce the schema 4.5 decided.

## 6. Steps

### Step 1 — Let the linter hold the dependency rule

**File changed:** `pyproject.toml`.

`[tool.ruff.lint]` gains **`TID251` by its exact code** to `select` — not the `TID` family, which
would also bring `TID252` and `TID253`, rules nobody chose. That is 2.8's own lesson, recorded in
`docs/ai-log.md` after a wider default enforced `UP047` on U2. Two new tables follow:

```toml
[tool.ruff.lint.flake8-tidy-imports.banned-api]
"sqlalchemy".msg = "infrastructure only — 3.1"
"pika".msg      = "infrastructure only — 3.1"
"fastapi".msg   = "infrastructure only — 3.1"
"pydantic".msg  = "config.py and entrypoints only — 3.1"

[tool.ruff.lint.per-file-ignores]
"src/pizza/infrastructure/*" = ["TID251"]
"src/pizza/entrypoints/*"    = ["TID251"]
"src/pizza/config.py"        = ["TID251"]
"tests/*"                    = ["TID251"]
```

This is the rule U3 §8 handed forward, in the form 3.1 asked for — one that a diff can be checked
against. The four ignore paths are 3.1's own: `infrastructure/` implements the ports, the two
`main.py` files wire them, `config.py` is the boundary 10.2 built on `pydantic`, and `tests/`
arranges whatever it needs. The globs were checked against a copy of this tree before the step was
written: a single `*` crosses directory separators in ruff's matcher, so
`src/pizza/infrastructure/*` covers `db/models.py` two levels down.

**Definition of Done**

1. `ruff check .` exits zero on the tree as it stands.
2. The rule is verified by breaking it: adding `import sqlalchemy` to `src/pizza/domain/order.py`
   makes `ruff check .` report `TID251` on that line, and adding the same import to
   `src/pizza/config.py` does not. Both edits are reverted before the commit — the check is the
   rule itself, and §8.2 is answered by the rule firing rather than by a test asserting a
   configuration file contains a key.
3. The other four commands of §4 exit zero, and `pytest tests/unit` still collects eleven tests.

---

### Step 2 — Turn the event into bytes, and back

**Files created:** `src/pizza/infrastructure/__init__.py` (empty),
`src/pizza/infrastructure/broker/__init__.py` (empty),
`src/pizza/infrastructure/broker/serialization.py`.

7.3 transcribed: `SerializationError`, `serialize(event: OrderReadyEvent) -> bytes` and
`deserialize(raw: bytes) -> OrderReadyEvent`. JSON encoded UTF-8; `UUID` as the canonical
hyphenated string and `datetime` as ISO 8601 with an explicit offset (4.7, 4.8). The reader is
tolerant — unknown fields are ignored, and a required field that is missing, or that fails to
parse, raises `SerializationError` with the original exception chained. The module imports the
standard library and `pizza.application.events`, and nothing else; `pika` never appears in it,
which is what lets step 7 import it from `db/`.

**File created:** `tests/unit/test_serialization.py`, three tests. Each is chosen by the failure it
would catch (`CLAUDE.md` §5) and carries that reason as its docstring. They are free by 5.7's
standard — pure logic, no infrastructure, no double.

| Test | What it asserts | Why it earns its place |
|---|---|---|
| `test_an_event_survives_the_round_trip` | `deserialize(serialize(event))` equals the event, `UUID`s and the UTC-aware `datetime` included | The same bytes are the wire message and the outbox `payload` (7.3, 7.5). A `datetime` that lost its offset, or a `UUID` that came back a `str`, would reach the worker as a valid-looking message and fail at the use case instead |
| `test_a_message_with_an_unknown_field_still_parses` | an extra key is ignored | The tolerant reader is the half of 7.3 that replaces a version marker. If it broke, the field addition 7.3 calls safe without coordination would stop being safe, and nothing else would say so |
| `test_malformed_input_raises_one_kind_of_error` | invalid UTF-8, invalid JSON, a missing field and an unparseable `UUID` each raise `SerializationError` | 8.4's poison-message path catches one family, which is why both signatures take `bytes` (7.3). A `UnicodeDecodeError` or a `KeyError` escaping here would arrive at the consumer as an unhandled exception |

**Definition of Done**

1. The three files exist, with the content stated.
2. The five commands of §4 exit zero.
3. `pytest tests/unit` collects fourteen tests — the eleven from U2 and U3, and these three.
4. `python -c "import pizza.infrastructure.broker.serialization"` succeeds with only the package
   installed, proving 7.3's stdlib-only claim rather than asserting it.

---

### Step 3 — Give the core a clock it can read

**File created:** `src/pizza/infrastructure/clock.py` — `SystemClock`, implementing the `Clock`
port per R-b, returning `datetime.now(UTC)`.

**File created:** `tests/unit/test_clock.py`, one test —
`test_the_clock_reads_utc_with_an_offset`: `now()` is timezone-aware and its offset is zero. It
earns its place because 4.8 fixes every timestamp as UTC-aware and a naive `datetime.now()` is the
one-character mistake that satisfies the type checker: the value reaches `timestamptz` columns and
the API unchanged in appearance, and only its comparisons and its rendering are wrong.

**Definition of Done**

1. Both files exist, with the content stated.
2. The five commands of §4 exit zero.
3. `pytest tests/unit` collects fifteen tests.
4. `clock.py` imports the standard library only — the `Clock` port is the one port with no third
   party behind it.

---

### Step 4 — Describe the schema the database enforces

**Files created:** `src/pizza/infrastructure/db/__init__.py` (empty),
`src/pizza/infrastructure/db/models.py`.

`Base(DeclarativeBase)` and three models — `OrderModel`, `DriverModel`, `OutboxModel` — carrying
4.5's tables column for column, with the types of R-k and no `server_default` anywhere. The two
constraints 4.5 named are declared in `__table_args__`: the partial unique index on `driver_id`
where `assignment_state = 'ASSIGNED'` through `postgresql_where`, and the one-directional `CHECK`
on the assignment triple. The three enum `CHECK`s are generated from the domain enums per R-h, and
that import is the only thing `models.py` takes from `domain/`.

**Definition of Done**

1. Both files exist, with the content stated.
2. The five commands of §4 exit zero.
3. `pytest tests/unit` still collects fifteen — **this step adds none, and the reason is 12.3's.**
   A model class asserts nothing until a database applies it; what the constraints do is exercised
   by U10's race scenario and by the suite's `409` path, over HTTP. A test that read
   `Base.metadata` back would assert that a declaration declares, which U3's step 3 already
   refused.
4. Every column named in 4.5's three tables is present, with its nullability, and no column is
   present that 4.5 did not name — checked against the record by reading, since the schema is not
   applied until step 5.

---

### Step 5 — Create the schema once, from a service that exits

**Files created:** `src/pizza/infrastructure/db/schema.py`,
`src/pizza/entrypoints/__init__.py` (empty), `src/pizza/entrypoints/schema/__init__.py` (empty),
`src/pizza/entrypoints/schema/main.py`.

`schema.py` holds `create_schema(engine: Engine) -> None`, one call to
`Base.metadata.create_all(engine)`. `main.py` is 4.6's one-shot: load `ServiceSettings` from the
environment per R-f, build an `Engine` on `database_url`, call `create_schema`, dispose the engine,
exit. A `ConfigurationError` is written to standard error and exits non-zero, which is the contract
U2 §8 fixed for every composition root; any other failure exits non-zero by propagating, and 4.6
requires exactly that — nothing downstream starts.

It is an entry point by 3.1's composition-root rule rather than by being a driving adapter, which
4.6 states in those words; it drives no use case and imports no `application/` module.

**Definition of Done**

1. The four files exist, with the content stated.
2. The five commands of §4 exit zero.
3. `pytest tests/unit` still collects fifteen. Whether `create_all` produces 4.5's schema is a
   statement about PostgreSQL, and the environment that could answer it is U9's; U10 exercises it
   on every run, since nothing else starts unless this service exits zero.
4. `python -m pizza.entrypoints.schema.main` with no environment set exits non-zero and prints the
   configuration message — the failure path, checked by hand at the step, because it is the one
   behaviour here that needs no database.

---

### Step 6 — Read and write orders, and claim a driver exactly once

**File created:** `src/pizza/infrastructure/db/repositories.py`.

`SqlAlchemyOrderRepository` and `SqlAlchemyDriverRepository`, each naming its port as a base class
(R-b) and taking a `Session`. The private mappers of R-g convert both ways. `save()` is 2.5's
sample: `session.get(Model, entity.id)` — which resolves from the identity map on every write path
here, because the use case loaded the entity through the same unit of work — then field assignment,
with `.value` written for every enum column as 4.9 fixed.

`list_all()` is R-i's ordering. `claim_next_available_driver()` is 8.9, exactly:

```python
select(DriverModel)
    .where(DriverModel.status == DriverStatus.AVAILABLE.value)
    .order_by(DriverModel.created_at)
    .limit(1)
    .with_for_update(skip_locked=True)
```

It returns the entity or `None`, and **does not mark it busy** — the marking and the assignment are
the use case's, in the same transaction, which is what `ports.py` states and what makes the lock
mean anything.

**Definition of Done**

1. The file exists, with the content stated.
2. The five commands of §4 exit zero. `mypy` passing is the substantive check here: with R-b the
   two classes are compared to `OrderRepository` and `DriverRepository` signature by signature,
   which is the half of U3 step 3's verification that this unit owes.
3. `pytest tests/unit` still collects fifteen — every method needs a database, so 12.3 puts the
   assertions in U10. The claim is one of its named scenarios (F2, the race for the last driver).
4. `claim_next_available_driver` contains no `UPDATE` and no call to `mark_busy`, and the generated
   SQL ends in `FOR UPDATE SKIP LOCKED` — read from `print(query)` at the step, since no test can
   see it before U10.

---

### Step 7 — Record the event beside the change that caused it

**File created:** `src/pizza/infrastructure/db/outbox.py`.

`SqlAlchemyOutboxStore`, naming `OutboxStore` as its base (R-b) and taking a `Session`. `add(event)`
writes one row: `event_id`, `event_type` from the class constant `OrderReadyEvent.EVENT_TYPE` (7.2),
`payload` as `json.loads(serialize(event).decode("utf-8"))` (7.3, as commit C corrected it — the
column stores the structure, and the bytes it is parsed from come from the one producer),
`created_at` per R-e, `published_at` null. It does not commit; 7.5 requires the row and
the status change to be one transaction, and the commit is the use case's.

`mark_published(event_id, now)` reads the row and sets `published_at`, translates
`SQLAlchemyError` to `OutboxWriteFailed` per R-c, and raises the same error when the row is not
there, per R-d. **The `UPDATE` itself leaves with the transaction rather than being flushed here**,
which is the developer's call and is recorded in `docs/ai-log.md`: a write that fails at the commit
raises out of `commit()`, where the caller catches nothing, so that window returns a `500` for a
request whose status change and publish both succeeded. It stays open because closing it here buys
one narrow case and starts a pattern — the next step is translating `commit()`, then `__exit__` —
and the whole question of what `commit()` may raise belongs to U7's gate.

This is the step that imports `broker/serialization.py` from `db/` — the edge commit A wrote into
7.3.

**Definition of Done**

1. The file exists, with the content stated.
2. The five commands of §4 exit zero, including `ruff check .` — which now permits the `sqlalchemy`
   import here and would not have permitted it two directories up.
3. `pytest tests/unit` still collects fifteen. 12.3 records that the outbox is the one thing HTTP
   cannot observe and that nothing inside the system reads it, so this row's absence is the
   lowest-consequence failure in the design; the assertion it would need is a database client the
   suite deliberately does not have.
4. `add` contains no `commit()`, and `mark_published` raises on both paths R-c and R-d name —
   read from the diff, and the reason each is right is stated above rather than in the source.

---

### Step 8 — Hold one transaction, and open a second when asked

**File created:** `src/pizza/infrastructure/db/unit_of_work.py`.

`SqlAlchemyUnitOfWork`, naming `UnitOfWork` as its base (R-b) and taking a `sessionmaker` per R-j.
`__enter__` opens a fresh `Session`, builds the three adapters bound to it, assigns `orders`,
`drivers` and `outbox`, and returns `self`. `__exit__` rolls back if `commit()` was not called and
closes the session in every case. `commit()` commits.

Re-enterability is the point, not a property: U3's step 5 leaves the `with` block, publishes, and
re-enters the same instance to mark the row (7.5). A unit of work that kept one session would put
that second write in a transaction the first `__exit__` had already ended.

**Definition of Done**

1. The file exists, with the content stated.
2. The five commands of §4 exit zero. `mypy` now compares the whole port set to its adapters,
   which completes what U3's step 3 deferred: every `Protocol` in `ports.py` has an implementation
   the checker has verified.
3. `pytest tests/unit` still collects fifteen — the transaction boundary is what U10's scenarios
   ride on, and 12.3 gives them HTTP to see it through.
4. Entering the same instance twice yields two different `Session` objects, and leaving without
   `commit()` rolls back — read from the code at the step; both become observable in U10, where a
   failed request must leave no row behind.

## 7. Ordering, and where it is free

Four edges are forced, and the rest is chosen:

- **1 before everything.** The rule must exist before the first `import sqlalchemy`, or the code it
  governs is the code it never checked (R-a).
- **2 before 7.** The outbox row's `payload` is `serialize(event)`.
- **4 before 5, 6 and 7.** All three name the models, and 5 needs `Base.metadata` to have something
  in it.
- **6 and 7 before 8.** The unit of work constructs all three adapters.

Everything else is free, and is ordered for a reader rather than by dependency. **3 sits early**
because it is the one adapter with no database behind it, so the two stdlib-only steps stay
together and the rest of the unit is uniformly about PostgreSQL. **5 before 6** so that the schema
is complete — described and applied — before anything queries it, though nothing runs at either
point.

No step depends on a step after it, and no step needs a file a later step creates.

## 8. What U5 hands to the units after it

- **U6 (7.3):** `pizza.infrastructure.broker.serialization` exists, with `serialize`,
  `deserialize` and `SerializationError`. U6 imports it and writes none of it. `broker/__init__.py`
  is already there, and the module takes no `pika` import — if one ever arrives, `db/` starts
  depending on the broker client, which is the thing 7.3's stdlib-only rule exists to prevent.
- **U7 and U8 (2.5, 3.5):** the composition root builds
  `create_engine(settings.database_url, pool_pre_ping=True)` and
  `sessionmaker(engine, autoflush=False, expire_on_commit=False)` — both settings are 2.5's and
  both matter to this unit's behaviour rather than to the root's: `autoflush=False` is what keeps an
  `UPDATE` out of step 6's lock window, and `expire_on_commit=False` is what makes `save()`'s
  identity-map claim hold. The root then builds `SqlAlchemyUnitOfWork(factory)` and `SystemClock()`
  and passes them to the use cases. **The adapters take a factory and a session, never a URL** — no
  module in `infrastructure/db/` reads configuration.
- **U8 additionally (8.9):** `claim_next_available_driver` returns a driver that is locked and not
  marked. The consumer does not need to know that; `DispatchOrder` already marks and saves it in
  the same transaction, and this is the sentence that says the adapter did not do it twice.
- **U9 (4.6, 11.1):** the schema service runs the `runtime` image with
  `python -m pizza.entrypoints.schema.main`, after `postgres` is `service_healthy` and before api,
  worker and tests, which wait on `service_completed_successfully`. **It receives the same
  variables as the api and the worker** — R-f loads `ServiceSettings`, and by U2's R-f a container
  given a subset fails at startup rather than ignoring what it does not use.
- **U10 (12.3):** this unit is the largest one whose behaviour no test in it asserts, and the
  reason is 12.3's own — the suite holds no database client. What lands here as "read from the
  diff" becomes observable in U10 through HTTP: the race for the last driver exercises step 6's
  lock, the `409` path exercises step 4's `CHECK`s indirectly, and a failed request leaving no row
  exercises step 8's rollback. The one thing that stays unobservable is the outbox row, which 12.3
  already records and accepts.
- **U12:** nothing directly.

## 9. After the merge

`main` satisfies 14.7's U2 row unchanged — `ruff format --check .`, `ruff check .`, `mypy src
tests`, `python -c "import pizza"` and `pytest tests/unit` all exit zero on a clean clone, with
fifteen unit tests. The bar rises at U9. Three of 3.1's four directories now exist, `domain/` and
`application/` still import nothing but the standard library and each other, and from this merge
onward that is enforced by `ruff check .` rather than by a plan.
