# Planning — Inventory

**Phase 1 of the planning protocol in `CLAUDE.md` §2: what must be decided, stated as
questions.** This file records the questions, never the answers. Answers live in
`02-decisions.md`; the build order lives in `03-roadmap.md`.

- **Part 0** restates the assignment as numbered requirements (`R1`…). Every item cites them.
- **Part 1** is the inventory of items still to be decided.
- **Part 2** lists the ambiguities in the assignment (`Q1`…`Q21`) — readings that differ, each
  resolved with the developer and recorded as an explicit assumption.
- **Part 3** maps cross-cutting failure modes (`F1`…`F14`) to the items that define them.

**Append-only.** An item's text is never rewritten or deleted. Items discovered mid-planning
are appended with a note of when. Because the question is preserved as it was asked, an item
here may describe a state of the world that has since changed — that is the point, not a
defect.

**Items carry no status marker.** Which items are decided is the table at the top of
`02-decisions.md`, and only there. A marker here would be the same fact in two files, and
would be wrong the first time one was updated without the other.

**An item may narrow its own question; it may never answer it.** Where a resolved item
constrains one still open, the open item points at the decision by number rather than
restating it — a fact stated in two places is a fact that will eventually disagree with
itself.

**31 items were resolved before this inventory was separated from the decision record, and
their question form was not preserved.** They are not reconstructed here — writing a question
after knowing its answer would be fiction. Their records are in `02-decisions.md`.

---

# Part 0 — Requirements, restated

## API service
- **R1.** `POST /orders` creates an order from `customer_name`, `address`, `items`; initial status `RECEIVED`.
- **R2.** `PATCH /orders/{id}/status` moves an order through `RECEIVED → PREPARING → BAKING → READY → DELIVERED`.
- **R3.** `POST /drivers` registers a driver with status `AVAILABLE` or `BUSY`.
- **R4.** `GET /orders/{id}` returns order details, status, and the assigned driver.
- **R5.** A status update to `BAKING` **or** `READY` must publish an `ORDER_READY` event to the broker.

## Worker service
- **R6.** Consumes `ORDER_READY` events.
- **R7.** Queries the database for an `AVAILABLE` driver.
- **R8.** On success: marks the driver `BUSY`, assigns them to the order, logs a mock dispatch notification.
- **R9.** On no driver available: logs a warning and requeues/retries the message.
- **R10.** Acknowledges messages after processing and does not crash on the retry path.

## CLI
- **R11.** An interactive Python console client to place orders, register drivers, and check order status against the running system.

## Infrastructure
- **R12.** Python 3.10+.
- **R13.** Broker: RabbitMQ or Kafka. Database: PostgreSQL or MongoDB.
- **R14.** One `docker-compose.yml` launching API, worker, broker, and database.
- **R15.** `docker compose up` must also execute the automated test suite automatically.
- **R16.** Configuration supplied through an `.env` file.

## Graded deliverables
- **R17.** End-to-end sequence diagram covering order creation, driver registration, status updates, broker publish, worker consume, driver lookup, state updates, and the missing-driver path.
- **R18.** 3–4 automated tests, each documented with scenario, goal, and rationale for its assertions.
- **R19.** `README.md` covering launch, CLI usage, test instructions, and design trade-offs.
- **R20.** Clean architecture separating routes, domain logic, worker, and console tool.
- **R21.** Public git repository whose history reads as a coherent narrative (`CLAUDE.md` §4).

## Storage
- **R22.** The database stores **orders, drivers, and assignment states**.

## Process
- **R23.** Design decisions and implementation details must be defensible verbally in the
  interview.

*R22 and R23 were appended on 2026-08-07. Both are stated in the assignment and were omitted
from the original restatement: R13 dropped the second half of "use PostgreSQL or MongoDB **to
store orders, drivers, and assignment states**", which left item 4.2's successor 4.4 as the
only decision in the record citing the brief directly for want of a requirement to cite; and
"be ready to explain your design decisions during the interview" is the requirement that item
1.3 exists to serve. Item 1.1's ceiling test is only as good as this list, which is how both
gaps surfaced.*


---

# Part 1 — Planning inventory

## Topic 1 — Scope and time

- **1.1 Scope ceiling for the 4-day budget.**
  *Decide:* what is explicitly excluded and written down as out of scope.
  *Why now:* `CLAUDE.md` §3 treats over-engineering as a defect and §7 requires exclusions to be stated; without a ceiling every later item drifts upward.
  *Source:* assignment time estimate; `CLAUDE.md` §3, §7.

- **1.2 The demo path.**
  *Decide:* the exact sequence a reviewer runs to see the system work end to end.
  *Why now:* it drives the CLI menu, the README, the sequence diagram, and the test scenarios; decided late, those four disagree with each other.
  *Source:* R11, R17, R19.

- **1.3 Decisions we must be able to defend verbally.**
  *Decide:* which design choices are expected interview questions and therefore need recorded rationale rather than silent resolution.
  *Why now:* determines how much justification Phase 2 must capture per item.
  *Source:* assignment AI guidelines.

- **1.4 Where Phase 2 decisions are recorded.**
  *Decide:* inline in this file, in a separate document, or in the README trade-offs section.
  *Why now:* the recording format must exist before the first decision is made, or the first decisions are recorded inconsistently.
  *Source:* `CLAUDE.md` §2 Phase 2, §7.

- **1.5 Per-unit time budget.**
  *Decide:* whether each atomic unit in Part 4 carries an estimate, and what total the plan must fit inside.
  *Why now:* nothing else in this inventory forces the plan to fit 4 days; a correct but undeliverable plan is a failure.
  *Source:* assignment time estimate.


## Topic 2 — Stack and tooling

- **2.4 Sync or async runtime.**
  *Decide:* sync or async for the API and for the worker, and whether both must match.
  *Why now:* constrains every other library — database driver, broker client, HTTP client in tests. Changing it later rewrites all adapters.
  *Source:* `CLAUDE.md` §3.

- **2.5 Database access approach.**
  *Decide:* ORM, query builder, or driver-level access, and whether API and worker use the same one.
  *Why now:* defines the repository interface the core depends on (3.4).
  *Source:* R20, `CLAUDE.md` §3.

- **2.6 Test framework and clients.**
  *Decide:* test runner, HTTP client, and any broker client used by tests.
  *Why now:* tests are a graded deliverable executed at container startup; the choice shapes the test image and the result output.
  *Source:* R18, DoD "Test Automation".

- **2.7 Broker client library and retry mechanism.**
  *Decide:* which client, and whether retry/backoff is hand-written or provided by the broker.
  *Why now:* `CLAUDE.md` §6 requires approval before adding a dependency; retry semantics cannot be improvised mid-implementation.
  *Source:* R9, R10, `CLAUDE.md` §6.

- **2.8 Formatter, linter, type checker.**
  *Decide:* which tools, which settings, and where they run.
  *Why now:* `CLAUDE.md` §8.3 makes them part of the Definition of Done for **every** step, including the first.
  *Source:* `CLAUDE.md` §8.

- **2.9 Dependency management and pinning.**
  *Decide:* requirements files or a project file, lockfile or not, one dependency set or one per service.
  *Why now:* determines Dockerfile layout and build caching, and must exist before the first buildable step.
  *Source:* R14, R20.

- **2.10 Full dependency list for approval.**
  *Decide:* every third-party library, each with a justification, presented as one list.
  **Two libraries have no other owner and are decided here:** the ASGI server 2.3's framework
  requires, and the HTTP client the CLI speaks through — 2.6 covers the test client only, and
  3.6 fixed the CLI as an adapter without naming a library. Both surfaced from assembling the
  list rather than from reading the items.
  *Why now:* `CLAUDE.md` §6 — "Ask before adding any dependency."
  *Source:* `CLAUDE.md` §6.


## Topic 3 — Architecture and layering

- **3.1 Layer definition.**
  *Decide:* the concrete names, directories, and responsibilities of each layer, and the direction of the dependency arrow.
  *Why now:* `CLAUDE.md` §3; retrofitting a layering rule is a rewrite, not a refactor.
  *Source:* R20, `CLAUDE.md` §3.

- **3.2 What lives in the framework-free core.**
  *Decide:* specifically where the status-transition rule, the publish-trigger rule, and the driver-selection/assignment rule live.
  *Why now:* if the transition rule is enforced in the route and the assignment rule in the worker, business rules exist in two places — a direct §3 violation.
  *Source:* `CLAUDE.md` §3.

- **3.3 Code sharing between API and worker.**
  *Decide:* one shared installable package, duplicated modules, or two independent services sharing only a wire contract.
  *Why now:* determines repository layout, Dockerfiles, and whether a rule change touches one place or two.
  *Source:* R20, `CLAUDE.md` §3. *Constrained by 7.5* — FW2 adds a **second** long-running
  non-HTTP process (the outbox relay) alongside the worker. Whether the layout makes a second
  such process cheap — a module plus a compose entry — or forces the worker's plumbing to be
  duplicated, is settled here. **The tension is explicit:** `CLAUDE.md` §3 forbids structure
  the current scope does not require, and the scope requires exactly one background process.
  The outbox table is built (7.5); the relay is not.

- **3.4 The interfaces the core exposes to adapters.**
  *Decide:* order repository, driver repository, event publisher, clock, id generator — names and exact typed signatures.
  *Why now:* Phase 3 steps must be implementable without judgement calls; these interfaces are the contract those steps are written against.
  *Source:* `CLAUDE.md` §3 ("explicit typed boundaries"), §2 Phase 3. *Constrained by 7.5* —
  the event-publisher signature carries no AMQP terms (no exchange, routing key or channel),
  so a non-broker implementation can satisfy it.

- **3.5 Transaction ownership.**
  *Decide:* which layer opens and commits a transaction, and whether the core may know transactions exist.
  *Why now:* determines whether "assign driver + mark BUSY" can be atomic (F2).
  *Source:* R8, `CLAUDE.md` §3. *Constrained by 7.5* — the transaction is owned by the use
  case, and the publish call is one identified line relative to the commit.

- **3.6 Where the CLI sits.**
  *Decide:* a pure HTTP adapter over the API, or a component with logic of its own.
  *Why now:* §3 requires additional interfaces to be thin adapters that never re-implement logic.
  *Source:* R11, `CLAUDE.md` §3.

- **3.7 Number of Docker images.**
  *Decide:* one shared image with different commands, or separate images per service (api / worker / cli / tests).
  *Why now:* shapes the build steps and the compose file, both of which appear early in the plan.
  *Source:* R14, R15. *Constrained by 7.5, via 3.3* — the relay FW2 adds should not require an
  image beyond what the worker already establishes.

- **3.8 Whether the worker uses the same core as the API.**
  *Decide:* worker writes through the shared core and repositories, or has its own data path.
  *Why now:* §3 — "every entry point uses the same core"; deciding later means duplicated write logic.
  *Source:* `CLAUDE.md` §3, R20.


## Topic 4 — Data model

- **4.1 Order entity fields.**
  *Decide:* identifier, `customer_name`, `address`, `items`, `status`, driver reference, timestamps.
  *Why now:* it is simultaneously the contract for the API, the database schema, the event payload, and the tests.
  *Source:* R1, R4.

- **4.5 Uniqueness and integrity constraints.**
  *Decide:* one active assignment per driver, one driver per order, enum storage, foreign keys, indexes.
  *Why now:* these are the last line of defence for the concurrency race (F2) and must be in the schema from the first migration.
  *Source:* R8, DoD "Broker & Consumer". *Constrained by 4.4* — "one active assignment per
  driver" is already expressible in the schema; what remains open is the rest of the
  constraint set. *Recommendation from 7.3* — the outbox `payload` column as `jsonb` rather than
  `text`: the table is only ever asked which orders lost their dispatch, and byte-exactness has
  no consumer.

- **4.6 Schema creation strategy.**
  *Decide:* migration tool, framework auto-create at startup, or init script — and how it behaves when a container starts before the database is ready.
  *Why now:* every service startup and the test container depend on the schema existing.
  *Source:* R14, R15.

- **4.7 Identifier scheme.**
  *Decide:* UUID or sequential integer, generated by the database, the application, or the core.
  *Why now:* appears in URLs, event payloads, CLI input ergonomics, and test fixtures.
  *Source:* R1, R4, R11.

- **4.9 Entity shape and operations.** *Appended 2026-08-10, mid-Phase 2.*
  *Decide:* whether the entities are frozen or mutable; which construction paths exist and what each
  one enforces; the complete operation set on `Order` and `Driver`, including the two 3.2 left
  unnamed; and the concrete form of the two status enums.
  *Why now:* 4.1 asks for a field list, and every field it names is already fixed by a closed item.
  What remains open is the shape those fields sit in — which 2.5 and 3.2 both presuppose without
  deciding, and which U3 cannot be planned without.
  *Source:* R1, R4, `CLAUDE.md` §2 Phase 3. *Constrained by:* 2.5, 3.2, 4.4.


## Topic 5 — Business rules

- **5.4 Driver selection rule.**
  *Decide:* which `AVAILABLE` driver is chosen when several exist, and whether the rule must be deterministic.
  *Why now:* tests assert on outcomes; a non-deterministic rule forces weaker assertions.
  *Source:* R7, `CLAUDE.md` §5.

- **5.7 Which rules are unit-testable without infrastructure.**
  *Decide:* the subset of 5.1–5.6 provable against the core alone.
  *Why now:* `CLAUDE.md` §5 permits unit tests only where they are free; the subset determines whether any exist at all.
  *Source:* `CLAUDE.md` §5.


## Topic 6 — API contract

- **6.1 Request and response schemas.**
  *Decide:* field-by-field schemas for all four endpoints.
  *Why now:* the CLI, the tests, and the README are all written against them.
  *Source:* R1–R4, R11, R18.

- **6.2 Status codes.**
  *Decide:* success and failure codes for unknown order, illegal transition, validation failure, unknown driver.
  *Why now:* tests assert on them.
  *Source:* R1–R4, R18.

- **6.3 Error response body format.**
  *Decide:* one consistent shape, or acceptance of the framework default.
  *Why now:* repository-wide consistency (§6) and CLI error rendering depend on it.
  *Source:* `CLAUDE.md` §6, R11.

- **6.7 Path prefix and versioning.**
  *Decide:* no prefix, or `/api/v1`.
  *Why now:* baked into the CLI, the tests, the README, and the diagram.
  *Source:* R19.

- **6.9 Concurrent `PATCH` behaviour.**
  *Decide:* what happens when two status updates hit the same order simultaneously.
  *Why now:* determines whether optimistic locking or a database constraint is needed in the schema (4.5).
  *Source:* R2, `CLAUDE.md` §5.


## Topic 7 — Broker contract

- **7.1 Topology.**
  *Decide:* exchange/queue/routing-key names (RabbitMQ) or topic/partition/consumer-group names (Kafka), and which service declares them.
  *Why now:* publisher and consumer must agree before either is written; declaration ownership affects startup order.
  *Source:* R5, R6, R14.

- **7.2 `ORDER_READY` payload schema.**
  *Decide:* fields, event id, event type, timestamp, and whether the event carries an order snapshot or only an identifier.
  *Why now:* it is a typed cross-service boundary (§3) and appears in the sequence diagram.
  *Source:* R5, R6, R17, `CLAUDE.md` §3. *Constrained by 7.5* — the event carries an
  `event_id` generated once at creation; it is also the outbox row's key.

- **7.3 Serialization and version marker.**
  *Decide:* encoding, and whether a schema version field exists.
  *Why now:* part of the same contract as 7.2.
  *Source:* R5, R6. *Constrained by 7.5* — the wire bytes are produced by a function on the
  event, not inline at the publish site, so exactly one component defines the format.

- **7.4 Durability.**
  *Decide:* persistent messages, durable queues, and what happens to in-flight events across a broker restart.
  *Why now:* it is set at topology-declaration time; adding it later requires redeclaring topology.
  *Source:* DoD "Broker & Consumer".

- **7.5 Publish versus commit ordering.**
  *Decide:* publish before commit, after commit, or via an outbox — and which failure window is accepted.
  *Why now:* the central reliability trade-off of the design, balanced against the §3 simplicity requirement; it must be a decision, not an accident.
  *Source:* R5, `CLAUDE.md` §3, §7.

- **7.6 Behaviour when the broker is unreachable during a status update.**
  *Decide:* the `PATCH` fails, or succeeds with the event lost.
  *Why now:* determines the API error contract (6.2) and is a candidate test scenario.
  *Source:* R5, `CLAUDE.md` §5.

- **7.7 Connection lifecycle.**
  *Decide:* connection/channel per request or long-lived, and reconnection behaviour on both sides.
  *Why now:* affects the publisher interface signature (3.4) and worker resilience (R10).
  *Source:* R5, R10. *Constrained by 7.5* — the publisher's reconnect-once behaviour is fixed
  there; connection lifetime and the consumer side remain open.


## Topic 8 — Worker

- **8.4 Poison message handling.**
  *Decide:* what happens to a malformed message, and whether it can block the queue.
  *Why now:* an unhandled parse error in a nack-requeue loop stops all dispatch — a silent total failure.
  *Source:* R10, DoD. *Constrained by 7.3 and 7.7* — `deserialize` raises rather than returning a
  partial event, and 3.1 forbids `entrypoints/worker/consumer.py` from importing either it or its
  error type, so the `try`/`except` must sit on the infrastructure side of the seam.

- **8.7 Logging format and levels.**
  *Decide:* structured or plain, and correlation by order id across services.
  *Why now:* the log is the reviewer's main window into the asynchronous path; consistency is a §6 requirement.
  *Source:* R8, R9, DoD.

- **8.8 Startup and shutdown behaviour.**
  *Decide:* what the worker does when the broker or database is not yet available, and how it shuts down without losing an in-flight message.
  *Why now:* compose starts everything at once; this is the first thing a reviewer encounters.
  *Source:* R14, R10. *Constrained by 7.7* — it fixes that the worker reconnects and that every
  connection re-declares the topology before subscribing; the startup wait, the retry cadence and
  the shutdown path are left here.


## Topic 9 — CLI

- **9.1 Interaction style.**
  *Decide:* numbered menu loop, prompt-driven shell, or sub-commands with an interactive fallback.
  *Why now:* the DoD grades "easy to use"; it is also the reviewer's first impression of the system.
  *Source:* R11, DoD "Interactive CLI".

- **9.3 How the CLI is run.**
  *Decide:* `docker compose run`/`exec` into a container, or on the host against a published port; and how it receives the API base URL.
  *Why now:* determines whether it needs its own image and compose service, and what the README instructs.
  *Source:* R11, R14, R16.

- **9.4 Validation and error presentation.**
  *Decide:* what the CLI validates locally versus what it lets the API reject, and how API errors are displayed.
  *Why now:* §3 places validation at the edge and forbids adapters from re-implementing logic; the split must be explicit.
  *Source:* R11, `CLAUDE.md` §3.

- **9.5 Client-side state.**
  *Decide:* whether the CLI remembers anything between actions (e.g. the last created order id).
  *Why now:* affects usability and the "thin adapter" rule in 3.6.
  *Source:* R11, `CLAUDE.md` §3.


## Topic 10 — Configuration

- **10.1 The complete environment variable list.**
  *Decide:* names, types, defaults, which are required, and which service reads which.
  *Why now:* §3 forbids hardcoded hosts, ports, and credentials; every service's first line of code reads configuration.
  *Source:* R16, `CLAUDE.md` §3, DoD "Code Quality".

- **10.2 Configuration loading mechanism.**
  *Decide:* a typed settings object or raw environment reads, and where configuration itself is validated.
  *Why now:* it is a typed boundary (§3) shared by all entry points.
  *Source:* `CLAUDE.md` §3.

- **10.3 `.env` versus `.env.example`.**
  *Decide:* what is committed, what is ignored, and how compose consumes each.
  *Why now:* §4 forbids committing local environment files and requires an example; `.gitignore` must be correct before the first commit that adds configuration.
  *Source:* R16, `CLAUDE.md` §3, §4.

- **10.4 Which values are tunable.**
  *Decide:* retry delay, retry cap, prefetch, ports, log level — tunable or fixed.
  *Why now:* tests may need to tune them (e.g. a short retry delay) to stay fast and deterministic.
  *Source:* R16, `CLAUDE.md` §5. *Constrained by 7.5* — one publish-attempt timeout, default
  5 s; with the single reconnect a `PATCH` blocks for at most roughly twice that.

- **10.5 Local credentials.**
  *Decide:* default database and broker credentials, and how they are supplied without being hardcoded.
  *Why now:* §4 forbids committed secrets, but a reviewer must still run `docker compose up` with zero setup.
  *Source:* `CLAUDE.md` §4, DoD "Docker Deployment".


## Topic 11 — Docker Compose

- **11.1 Service inventory.**
  *Decide:* api, worker, broker, database, tests, cli, and any init/migration service.
  *Why now:* R15 only works if the dependency graph is designed up front.
  *Source:* R14, R15.

- **11.2 Readiness and ordering.**
  *Decide:* healthchecks with `depends_on: condition: service_healthy`, in-app retry loops, or both.
  *Why now:* `CLAUDE.md` §5 forbids fixed sleeps; this must be a condition-based design from the start.
  *Source:* R14, R15, `CLAUDE.md` §5. *Constrained by 6.6* — a readiness probe for the API
  already exists; what remains open is how ordering is composed around it.

- **11.8 Published host ports.**
  *Decide:* which services are exposed, on which ports, and how conflicts are avoided.
  *Why now:* README instructions and host-side CLI use (9.3) depend on it.
  *Source:* R14, R19.

- **11.9 Image build strategy.**
  *Decide:* base images, layer caching, build context, and whether a separate build step is required before `up`.
  *Why now:* the DoD requires a seamless launch; first-run build time is part of that.
  *Source:* R14, DoD "Docker Deployment".

- **11.10 Compose command form.**
  *Decide:* `docker compose` v2 or `docker-compose` v1, documented as a prerequisite.
  *Why now:* the deliverable is a file a stranger runs on an unknown machine.
  *Source:* R14, R19.

- **11.11 Restart policies.**
  *Decide:* restart behaviour for api, worker, and broker-dependent services.
  *Why now:* the difference between a crash-looping stack and a self-healing one on the reviewer's first run.
  *Source:* R14, R10.


## Topic 12 — Testing

- **12.1 Risk ranking.**
  *Decide:* enumerate the failure modes that would break silently, rank them, and take the top 3–4.
  *Why now:* `CLAUDE.md` §5 mandates selection by risk, and the assignment fixes the count as a ceiling.
  *Candidate already identified:* the **ghost driver** — see 4.3. It breaks silently by
  construction, which is exactly the selection criterion.
  *Source:* R18, `CLAUDE.md` §5.

- **12.2 The chosen scenarios.**
  *Decide:* each with scenario description, goal, assertions, and the rationale for those assertions.
  *Why now:* the written rationale is itself a graded deliverable, not a by-product.
  *Source:* R18, DoD "Test Automation". *Blocked by:* Q16.

- **12.3 Interface each test drives.**
  *Decide:* HTTP plus database inspection, HTTP only, or direct broker publication.
  *Why now:* §5 requires testing behaviour and contracts, not internals; reading the database directly is a boundary decision.
  *Source:* `CLAUDE.md` §5.

- **12.4 Waiting for the asynchronous assignment.**
  *Decide:* the condition-polling primitive and its timeout.
  *Why now:* fixed sleeps are explicitly forbidden by §5; the helper must exist before the first asynchronous test is written.
  *Source:* `CLAUDE.md` §5, R18.

- **12.5 Test data strategy and isolation.**
  *Decide:* unique data per test, truncation between tests, or a fresh database; and how order-independence is guaranteed.
  *Why now:* §5 requires determinism and independence.
  *Source:* `CLAUDE.md` §5.

- **12.6 Scope of the unit test set.**
  *Partially settled* — that unit tests exist and how they are counted is resolved; see Q16
  and its record in `02-decisions.md`.
  *Still open:* **how far they may go**, and which pure-core rules from 5.7 they cover. Left
  deliberately unfixed, because time may remain after the four integration scenarios for a
  more substantial unit set.
  *What this collides with:* `CLAUDE.md` §5 currently reads *"Unit — an addition, permitted
  only when free: pure logic, no infrastructure, written in minutes."* A larger unit suite is
  not merely undecided under that wording — it contradicts it. Expanding beyond "free"
  therefore requires **amending §5**, not just resolving this item. Flagged now so the choice
  is made deliberately rather than discovered mid-implementation.
  *Source:* `CLAUDE.md` §5. *Partly answered by:* Q16.

- **12.7 Directory layout and separate run commands.**
  *Decide:* where each category lives and how each is run independently.
  *Why now:* explicitly required by §5.
  *Source:* `CLAUDE.md` §5.

- **12.8 Deterministic testing of the retry path.**
  *Decide:* the mechanism that makes the no-driver retry observable without sleeps — a config-tuned delay, controlled driver registration timing, or another approach.
  *Why now:* the highest-risk behaviour in the assignment and the hardest to assert deterministically.
  *Source:* R9, `CLAUDE.md` §5.

- **12.9 Where results are surfaced.**
  *Decide:* console output only, or a report file.
  *Why now:* 11.3 and 11.4 depend on it.
  *Source:* R15.

- **12.10 Whether lint and type checks run inside the compose test run.**
  *Decide:* gate in the delivered environment, or local-only.
  *Why now:* §8.3 requires them per step; whether they also gate the delivered environment is a separate call.
  *Source:* `CLAUDE.md` §8.


## Topic 13 — Documentation and deliverables

- **13.1 README structure.**
  *Decide:* sections for launch, CLI usage, test instructions, named test scenarios, trade-offs, assumptions, and out-of-scope.
  *Why now:* §5 requires the scenarios to be findable from the README; §7 requires assumptions and exclusions listed.
  *Source:* R19, `CLAUDE.md` §5, §7.

- **13.2 Sequence diagram format and location.**
  *Decide:* Mermaid in the README, a separate document, or an image.
  *Why now:* a separately graded deliverable that must stay in sync with topics 5, 7, and 8.
  *Source:* R17, DoD "System Design".

- **13.3 Diagram scope and count.**
  *Decide:* one diagram covering both the happy path and the missing-driver path, or two diagrams.
  *Why now:* R17 lists both paths as required content; one overloaded diagram risks failing the "clear" criterion.
  *Source:* R17.

- **13.4 Trade-off log content.**
  *Decide:* which rejected alternatives are written down — broker, database, publish-versus-outbox, retry strategy.
  *Why now:* documentation is updated in the same commit as the change (§7), so the list must exist before those commits happen.
  *Source:* R19, `CLAUDE.md` §7.

- **13.6 Assumptions register.**
  *Decide:* where the Part 2 assumptions live once resolved, and how they are kept current.
  *Why now:* §7 requires assumptions to be explicit and up to date.
  *Source:* `CLAUDE.md` §7.


## Topic 14 — Git and process

- **14.1 Public remote.**
  *Decide:* where the public repository lives and when it is created.
  *Why now:* R21 asks for a public link; §4 forbids rewriting pushed history, so the remote must exist before history becomes meaningful.
  *Source:* R21.

- **14.2 Branch convention and merge style.**
  *Decide:* branch naming, and merge commit / squash / rebase.
  *Why now:* §4 requires one branch per unit merged via pull request; the merge style determines whether the history reads as intended.
  *Source:* `CLAUDE.md` §4.

- **14.3 How much of the branch-per-unit workflow is actually executed.**
  *Decide:* full pull-request flow, or a documented simplification for a solo 4-day assignment.
  *Why now:* it multiplies the operations in every unit; `CLAUDE.md` currently makes no allowance for it.
  *Source:* `CLAUDE.md` §4, assignment time estimate.

- **14.4 Unit-to-commit map.**
  *Decide:* the explicit mapping from Part 4 units to commits, produced during Phase 3.
  *Why now:* §4 requires one commit per logical unit and treats a bulk commit as a process failure.
  *Source:* `CLAUDE.md` §4, §2.

- **14.5 Whether `CLAUDE.md`, `.claude/`, and the plans directory are committed.**
  *Decide:* included in the delivered public repository, or deliberately excluded.
  *Why now:* `CLAUDE.md` is currently untracked and `.claude/` may be ignored; the planning history is either part of the delivered narrative or not.
  *Source:* R21, `CLAUDE.md` §4.

- **14.6 `.gitignore` adequacy.**
  *Decide:* verify coverage for Python caches, virtual environments, `.env`, Docker artifacts, and editor files — and whether it currently ignores `.claude/`.
  *Why now:* the file already exists and is committed; it must be correct before the first source commit, not after.
  *Source:* `CLAUDE.md` §4.

- **14.7 What "main still runs" means in the early units.**
  *Decide:* the criterion for a commit that precedes any runnable system.
  *Why now:* §8.6 applies from the first commit; without a definition the criterion is unmeetable.
  *Source:* `CLAUDE.md` §8.


---

# Part 2 — Open questions

Each of these can be read more than one way. Per `CLAUDE.md` §2, none is resolved silently.
They are answered one at a time with the developer; each answer is recorded in
`02-decisions.md` — in the item it unblocks, and as an explicit assumption where it fills a
gap the assignment left. **Phase 2 does not end while any row is open.**

| # | Question | Blocks | Status |
|---|---|---|---|
| **Q1** | `ORDER_READY` is published on **two** statuses. The event name says "ready" but it also fires at `BAKING`, and the business context says matching happens "when they reach the baking stage". Is the second event expected to be a no-op, or a genuine re-dispatch? | 5.3, 5.5, F3, F8 | **answered → A2** |
| **Q2** | Is `RECEIVED → PREPARING → BAKING → READY → DELIVERED` a strict linear rule, or just the happy path with skips and rollbacks tolerated? Nothing states what an illegal transition returns. | 5.1, 5.2, 6.2, F9 | **answered → A3** |
| **Q3** | The storage requirement names "assignment states" as a third stored thing, but no endpoint or event exposes an assignment lifecycle. Is an assignment an entity, or a field on the order? | 4.4 | **answered → A6** |
| **Q4** | Nothing says a driver is ever released. `DELIVERED` exists and `BUSY` is set by the worker, but no requirement returns a driver to `AVAILABLE`, and no endpoint changes driver status after registration. Do drivers get released? | 5.6, F12 | **answered → A4** |
| **Q5** | "Register a driver with status AVAILABLE or BUSY" — does the client choose the initial status, or does the field simply have two legal values while registration is always `AVAILABLE`? | 6.4, F11 | **answered → A10** |
| **Q6** | "Requeues/retries" covers several different mechanisms — immediate nack-requeue, delayed retry, dead-letter with a retry loop, in-process retry — and nothing says whether attempts are bounded. Which is intended? | 8.2, 8.3, F7 | **answered → A7** |
| **Q7** | "Logs a mock dispatch notification" is undefined. A log line, a fake HTTP call, or a stored notification record all satisfy the wording. Which, and must it be assertable? | 8.6 | **answered → A16** |
| **Q8** | "Execute the test suite automatically upon startup" does not say whether a failing suite must fail the launch, whether the stack stays up afterwards, or whether tests run against the same instance the user then interacts with. | 11.3, 11.4, 11.5, 11.6 | **answered → A8** |
| **Q9** | The `items` field has no schema, no validation rules, and no quantity or price concept. What is it? | 4.2, F13 | **answered → A11** |
| **Q10** | `GET /orders/{id}` "assigned driver" — full object, identifier only, or `null` when unassigned? | 6.5 | **answered → A12** |
| **Q11** | No listing endpoints are specified, but the CLI must let a user "check order statuses" (plural). Does the user always supply an id, or is a list endpoint needed — which conflicts with §6's ban on unrequested features? | 6.6, 9.2 | **answered → A14** |
| **Q12** | No health endpoint is specified, but compose readiness and the test suite typically need one. Same tension as Q11. | 6.6, 11.2 | **answered → A15** |
| **Q13** | Ordering and concurrency guarantees are unstated. One worker or several? Must events for one order be processed in order? | 8.5, 8.9, F2 | **answered → A5** |
| **Q14** | Idempotency of `PATCH` is unstated — setting a status to its current value: no-op, error, or re-publish? | 5.1, F3 | **answered → A3** |
| **Q15** | Authentication and multi-tenancy are not mentioned at all. Presumed absent — confirm so it can be recorded. | 6.8 | **answered → A20** |
| **Q16** | Does "3–4 automated tests" mean 3–4 scenarios or 3–4 test functions, and do permitted unit tests count against the ceiling? | 12.2, 12.6 | **answered → A17** |
| **Q17** | Data persistence across runs is unstated — should a reviewer's second `docker compose up` see the previous run's data? | 11.7 | **answered → A19** |
| **Q18** | The broker and database choices interact: transactional claiming is easier in one database, delayed retry is easier in one broker. They must be chosen as a pair, not independently. | 2.1, 2.2, 8.2, 8.9 | **answered → A1** |
| **Q19** | The diagram shows "Interactive CLI / REST client" as alternatives. Must the CLI cover **all** operations, including status updates that the demo needs, or only the three named ones? | 9.2 | **answered → A18** |
| **Q20** | The development host is Windows; the delivery target is Docker on an unknown host. The assignment does not address line endings, entrypoint scripts, or CLI TTY behaviour. | 9.6, 11.9 | **answered → A21** |
| **Q21** | R5 requires a publish on a status change, but the status change and the publish are writes to **two systems that cannot be committed atomically**. One must happen first, and if the second fails the system is left inconsistent. Which failure is accepted — a **phantom event** (published, then the commit failed: the worker sees an order the database never advanced) or a **lost event** (committed, then the publish failed: the order is `BAKING` forever and no driver is ever dispatched, silently)? The assignment says the event *must* be published and says nothing about what happens when it cannot be. | 7.5, 7.6, 6.6, F4 | **answered → A22, A23** |

*Q21 was appended on 2026-08-07. It is not a new ambiguity — it was always in R5 — but no
question had been written for it, so item 7.5 sat open with nothing scheduled to resolve it.
It is the assignment's central reliability trade-off and the most likely interview question
about the design.*

**Answering order.** All 21 are answered; the order taken was
Q18 → Q1 → Q2 → Q4 → Q13 → Q6 → Q8 → Q3 → Q5 → Q9 → Q10 → Q14 → Q11 → Q12 → Q7 → Q16 → Q19 → Q17 → Q15 → Q20 → Q21.
**Q21 was answered last, on 2026-08-09, with 7.5, 7.6 and 6.6 decided as one unit** — 6.6
could not resolve its own open coupling before 7.6, and 7.6 could not be resolved before 7.5.
That unblocks units U6 and U7 in the roadmap.

---

# Part 3 — Cross-cutting failure modes

Each needs a defined behaviour before implementation. `CLAUDE.md` §5 requires failure paths
to be tested, and §2 Phase 3 requires a plan with no judgement calls left in it.

| # | Failure mode | Defined by |
|---|---|---|
| **F1** | `PATCH` on a non-existent order id | 6.2 |
| **F2** | Two `ORDER_READY` events race for the last `AVAILABLE` driver | 8.9, 4.5, 3.5 |
| **F3** | Duplicate `ORDER_READY` for one order — `BAKING` then `READY`, plus broker redelivery | 5.5 |
| **F4** | Broker down when the API tries to publish — and the dual-write window either side of it | 7.5, 7.6 |
| **F5** | Database down when the worker tries to assign; the message must not be lost | 8.1, 8.8 |
| **F6** | Worker crashes after marking the driver `BUSY` but before the ack — redelivery into a partially applied state | 8.1, 5.5 |
| **F7** | No drivers exist at all, indefinitely — retry behaviour over a long horizon | 8.2, 8.3 |
| **F8** | Order reaches `READY` when it already has a driver — no-op, error, or reassignment | 5.5 |
| **F9** | Illegal or out-of-order status transition requested | 5.1, 5.2 |
| **F10** | Malformed or unparseable message on the queue | 8.4 |
| **F11** | ~~Driver registered directly as `BUSY` with no order~~ | eliminated — see 6.4 |
| **F12** | Order reaches `DELIVERED` with no driver ever assigned | 5.6 |
| **F13** | Validation failures on order creation — empty items, empty address, oversized payload | 4.2, 6.2 |
| **F14** | Concurrent `PATCH` requests on the same order | 6.9 |
