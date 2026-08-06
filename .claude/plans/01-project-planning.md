# Plan 01 — Project Planning: Pizza Order & Dispatch Engine

This file is the working artifact for **Phase 1 and Phase 2** of the planning protocol
defined in `CLAUDE.md` §2. It contains no implementation plan and no code.

- **Part 0** restates the requirements as numbered items (`R1`…`R21`). Every planning item
  cites them.
- **Part 1** is the planning inventory: 14 topics, each split into items that must be
  decided before implementation begins. Items are open questions, not answers.
- **Part 2** lists the open questions (`Q1`…`Q20`) — ambiguities in the assignment that can
  be read more than one way. These are resolved one at a time in a question-and-answer pass
  with the developer, and each becomes an explicit written assumption.
- **Part 3** maps cross-cutting failure modes (`F1`…`F14`) to the topics that must define
  their behaviour.
- **Part 4** is the execution order: the atomic units of work, what must be decided before
  each is planned, and which units must run before which.
- **Part 5** is the future-work list: things deliberately excluded from delivery, kept as a
  record of what was considered and consciously not built.

## How this file is worked through

1. Open questions in Part 2 are answered by the developer, one at a time, in the order given
   at the end of Part 2 (most-blocking first).
2. Each answer is written back into this file — into the inventory item it unblocks, and as
   an explicit assumption. **No question may remain open when Phase 2 ends.**
3. Each inventory item in Part 1 is then resolved and recorded per `CLAUDE.md` §2 Phase 2:
   the decision, why it was chosen, what was rejected and why.
4. Item status markers: `[open]` → `[decided]`. No item moves to Phase 3 while `[open]`.
5. Only when every item is `[decided]` does Phase 3 begin. Phase 3 is written **per atomic
   unit** from Part 4, not for the whole system at once: a unit is planned in full, executed,
   and only then is the next unit planned.

## Where plans live

Planning documents live in `.claude/plans/`, numbered in creation order:
`NN-<subject>.md`. This file is `01`. Phase 3 implementation plans are separate documents in
the same directory, one per atomic unit from Part 4.

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

---

# Part 1 — Planning inventory

## Topic 1 — Scope and time

- **1.1 Scope ceiling for the 4-day budget.** `[open]`
  *Decide:* what is explicitly excluded and written down as out of scope.
  *Why now:* `CLAUDE.md` §3 treats over-engineering as a defect and §7 requires exclusions to be stated; without a ceiling every later item drifts upward.
  *Source:* assignment time estimate; `CLAUDE.md` §3, §7.

- **1.2 The demo path.** `[open]`
  *Decide:* the exact sequence a reviewer runs to see the system work end to end.
  *Why now:* it drives the CLI menu, the README, the sequence diagram, and the test scenarios; decided late, those four disagree with each other.
  *Source:* R11, R17, R19.

- **1.3 Decisions we must be able to defend verbally.** `[open]`
  *Decide:* which design choices are expected interview questions and therefore need recorded rationale rather than silent resolution.
  *Why now:* determines how much justification Phase 2 must capture per item.
  *Source:* assignment AI guidelines.

- **1.4 Where Phase 2 decisions are recorded.** `[open]`
  *Decide:* inline in this file, in a separate document, or in the README trade-offs section.
  *Why now:* the recording format must exist before the first decision is made, or the first decisions are recorded inconsistently.
  *Source:* `CLAUDE.md` §2 Phase 2, §7.

- **1.5 Per-unit time budget.** `[open]`
  *Decide:* whether each atomic unit in Part 4 carries an estimate, and what total the plan must fit inside.
  *Why now:* nothing else in this inventory forces the plan to fit 4 days; a correct but undeliverable plan is a failure.
  *Source:* assignment time estimate.

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

- **2.3 API framework.** `[open]`
  *Decide:* which web framework.
  *Why now:* fixes the edge-validation style, request/response typing, and the runtime model shared with the worker.
  *Source:* R12, `CLAUDE.md` §3 ("external input is validated at the edge").

- **2.4 Sync or async runtime.** `[open]`
  *Decide:* sync or async for the API and for the worker, and whether both must match.
  *Why now:* constrains every other library — database driver, broker client, HTTP client in tests. Changing it later rewrites all adapters.
  *Source:* `CLAUDE.md` §3.

- **2.5 Database access approach.** `[open]`
  *Decide:* ORM, query builder, or driver-level access, and whether API and worker use the same one.
  *Why now:* defines the repository interface the core depends on (3.4).
  *Source:* R20, `CLAUDE.md` §3.

- **2.6 Test framework and clients.** `[open]`
  *Decide:* test runner, HTTP client, and any broker client used by tests.
  *Why now:* tests are a graded deliverable executed at container startup; the choice shapes the test image and the result output.
  *Source:* R18, DoD "Test Automation".

- **2.7 Broker client library and retry mechanism.** `[open]`
  *Decide:* which client, and whether retry/backoff is hand-written or provided by the broker.
  *Why now:* `CLAUDE.md` §6 requires approval before adding a dependency; retry semantics cannot be improvised mid-implementation.
  *Source:* R9, R10, `CLAUDE.md` §6.

- **2.8 Formatter, linter, type checker.** `[open]`
  *Decide:* which tools, which settings, and where they run.
  *Why now:* `CLAUDE.md` §8.3 makes them part of the Definition of Done for **every** step, including the first.
  *Source:* `CLAUDE.md` §8.

- **2.9 Dependency management and pinning.** `[open]`
  *Decide:* requirements files or a project file, lockfile or not, one dependency set or one per service.
  *Why now:* determines Dockerfile layout and build caching, and must exist before the first buildable step.
  *Source:* R14, R20.

- **2.10 Full dependency list for approval.** `[open]`
  *Decide:* every third-party library, each with a justification, presented as one list.
  *Why now:* `CLAUDE.md` §6 — "Ask before adding any dependency."
  *Source:* `CLAUDE.md` §6.

## Topic 3 — Architecture and layering

- **3.1 Layer definition.** `[open]`
  *Decide:* the concrete names, directories, and responsibilities of each layer, and the direction of the dependency arrow.
  *Why now:* `CLAUDE.md` §3; retrofitting a layering rule is a rewrite, not a refactor.
  *Source:* R20, `CLAUDE.md` §3.

- **3.2 What lives in the framework-free core.** `[open]`
  *Decide:* specifically where the status-transition rule, the publish-trigger rule, and the driver-selection/assignment rule live.
  *Why now:* if the transition rule is enforced in the route and the assignment rule in the worker, business rules exist in two places — a direct §3 violation.
  *Source:* `CLAUDE.md` §3.

- **3.3 Code sharing between API and worker.** `[open]`
  *Decide:* one shared installable package, duplicated modules, or two independent services sharing only a wire contract.
  *Why now:* determines repository layout, Dockerfiles, and whether a rule change touches one place or two.
  *Source:* R20, `CLAUDE.md` §3.

- **3.4 The interfaces the core exposes to adapters.** `[open]`
  *Decide:* order repository, driver repository, event publisher, clock, id generator — names and exact typed signatures.
  *Why now:* Phase 3 steps must be implementable without judgement calls; these interfaces are the contract those steps are written against.
  *Source:* `CLAUDE.md` §3 ("explicit typed boundaries"), §2 Phase 3.

- **3.5 Transaction ownership.** `[open]`
  *Decide:* which layer opens and commits a transaction, and whether the core may know transactions exist.
  *Why now:* determines whether "assign driver + mark BUSY" can be atomic (F2).
  *Source:* R8, `CLAUDE.md` §3.

- **3.6 Where the CLI sits.** `[open]`
  *Decide:* a pure HTTP adapter over the API, or a component with logic of its own.
  *Why now:* §3 requires additional interfaces to be thin adapters that never re-implement logic.
  *Source:* R11, `CLAUDE.md` §3.

- **3.7 Number of Docker images.** `[open]`
  *Decide:* one shared image with different commands, or separate images per service (api / worker / cli / tests).
  *Why now:* shapes the build steps and the compose file, both of which appear early in the plan.
  *Source:* R14, R15.

- **3.8 Whether the worker uses the same core as the API.** `[open]`
  *Decide:* worker writes through the shared core and repositories, or has its own data path.
  *Why now:* §3 — "every entry point uses the same core"; deciding later means duplicated write logic.
  *Source:* `CLAUDE.md` §3, R20.

## Topic 4 — Data model

- **4.1 Order entity fields.** `[open]`
  *Decide:* identifier, `customer_name`, `address`, `items`, `status`, driver reference, timestamps.
  *Why now:* it is simultaneously the contract for the API, the database schema, the event payload, and the tests.
  *Source:* R1, R4.

- **4.2 Shape and validation of `items`.** `[decided]`
  *Decision:* `items` is a list of **typed objects**:

  ```json
  { "name": "Margherita", "quantity": 2, "toppings": ["olives", "extra cheese"] }
  ```

  Validation at the edge, before the core sees anything:
  - `items` — a list, 1 to 20 entries
  - `name` — non-empty after trimming, at most 100 characters
  - `quantity` — an integer, 1 to 20
  - `toppings` — a free list of strings, **optional, defaulting to empty**; at most 10 entries,
    each non-empty and at most 50 characters
  - unknown fields are **rejected**, not stored
  - `customer_name` — non-empty, at most 100 characters
  - `address` — non-empty, at most 200 characters
  - any violation returns `422`
  *Why typed rather than a free dictionary:* `CLAUDE.md` §3 requires data crossing a layer
  boundary to be a defined type and external input to be validated at the edge — an
  unvalidated object is precisely the untyped dictionary that rule forbids. It also costs
  nothing: declaring the fields *is* the validation. Leaving `quantity` unconstrained would
  push real decisions into implementation time — what the CLI prints when it is absent,
  whether `0` or `-3` is storable — which §2 Phase 3 forbids. PostgreSQL will hold this as
  JSONB and check nothing, so the edge is the only place it can be checked at all.
  *Why structured rather than plain strings:* nothing in the system reads `items`, so a list of
  strings would have been sufficient — but the CLI is a graded deliverable and renders
  `2 × Margherita (olives, extra cheese)` far better from fields than from prose.
  *Deliberately excluded:* `size`. Adding it forces a choice between an enum, which is a menu
  model nothing consumes, and free text, which carries no meaning. `toppings` avoids that trap
  by being explicitly a free list — no vocabulary to define, no rule to enforce.
  *The numeric limits are arbitrary* and recorded as an assumption; their purpose is that no
  field is unbounded, not that 20, 100, 10 and 50 are meaningful.
  *Source:* R1, `CLAUDE.md` §3. *Answers:* Q9. *Defines:* F13.

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

- **4.5 Uniqueness and integrity constraints.** `[open]`
  *Decide:* one active assignment per driver, one driver per order, enum storage, foreign keys, indexes.
  *Why now:* these are the last line of defence for the concurrency race (F2) and must be in the schema from the first migration.
  *Source:* R8, DoD "Broker & Consumer". *Constrained by A6:* "one active assignment per driver" is expressible as a partial unique index on `orders(driver_id) WHERE assignment_state = 'ASSIGNED'`; what remains open is the rest of the constraint set.

- **4.6 Schema creation strategy.** `[open]`
  *Decide:* migration tool, framework auto-create at startup, or init script — and how it behaves when a container starts before the database is ready.
  *Why now:* every service startup and the test container depend on the schema existing.
  *Source:* R14, R15.

- **4.7 Identifier scheme.** `[open]`
  *Decide:* UUID or sequential integer, generated by the database, the application, or the core.
  *Why now:* appears in URLs, event payloads, CLI input ergonomics, and test fixtures.
  *Source:* R1, R4, R11.

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

- **5.4 Driver selection rule.** `[open]`
  *Decide:* which `AVAILABLE` driver is chosen when several exist, and whether the rule must be deterministic.
  *Why now:* tests assert on outcomes; a non-deterministic rule forces weaker assertions.
  *Source:* R7, `CLAUDE.md` §5.

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

- **5.7 Which rules are unit-testable without infrastructure.** `[open]`
  *Decide:* the subset of 5.1–5.6 provable against the core alone.
  *Why now:* `CLAUDE.md` §5 permits unit tests only where they are free; the subset determines whether any exist at all.
  *Source:* `CLAUDE.md` §5.

## Topic 6 — API contract

- **6.1 Request and response schemas.** `[open]`
  *Decide:* field-by-field schemas for all four endpoints.
  *Why now:* the CLI, the tests, and the README are all written against them.
  *Source:* R1–R4, R11, R18.

- **6.2 Status codes.** `[open]`
  *Decide:* success and failure codes for unknown order, illegal transition, validation failure, unknown driver.
  *Why now:* tests assert on them.
  *Source:* R1–R4, R18.

- **6.3 Error response body format.** `[open]`
  *Decide:* one consistent shape, or acceptance of the framework default.
  *Why now:* repository-wide consistency (§6) and CLI error rendering depend on it.
  *Source:* `CLAUDE.md` §6, R11.

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
  *Decide:* whether list-orders, list-drivers, or a health endpoint exist.
  *Why now:* §6 forbids unrequested features, but compose readiness and the CLI may need them; the boundary must be drawn deliberately, not discovered.
  *Source:* R11, R14, `CLAUDE.md` §6. *Answers:* Q11, Q12.
  *Settled (A9):* there is **no** driver-history endpoint, and no driver listing.
  *Settled (A14):* **`GET /orders` exists.** It returns a light representation —
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
  *Settled (A15):* **`GET /health` exists.** It returns `200` when the application can reach
  the database and the broker, `503` otherwise — no metrics, no version, no uptime, no
  per-dependency detail.
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
  *Open coupling:* whether `/health` treats the broker as a health dependency follows 7.6. If a
  `PATCH` fails when the broker is unreachable, an API without a broker genuinely cannot serve
  and must report `503`; if the `PATCH` succeeds and the event is lost, the broker is not a
  health condition. **Revisit both items together when 7.6 is decided.**

- **6.7 Path prefix and versioning.** `[open]`
  *Decide:* no prefix, or `/api/v1`.
  *Why now:* baked into the CLI, the tests, the README, and the diagram.
  *Source:* R19.

- **6.8 Authentication.** `[decided]`
  *Decision:* **none.** Every endpoint is open. Recorded in the README under assumptions:
  *"There is no authentication. The API targets an internal network and a demonstration
  environment; public exposure would require an auth layer, which is out of scope."*
  *Why:* the assignment mentions no users, tenants, roles, or tokens anywhere. Adding auth
  would be an unrequested feature (`CLAUDE.md` §6); leaving it unmentioned would be an
  unstated assumption (§7). Stating the absence satisfies both.
  *Source:* `CLAUDE.md` §7. *Answers:* Q15. *Deferred to:* FW9.

- **6.9 Concurrent `PATCH` behaviour.** `[open]`
  *Decide:* what happens when two status updates hit the same order simultaneously.
  *Why now:* determines whether optimistic locking or a database constraint is needed in the schema (4.5).
  *Source:* R2, `CLAUDE.md` §5.

## Topic 7 — Broker contract

- **7.1 Topology.** `[open]`
  *Decide:* exchange/queue/routing-key names (RabbitMQ) or topic/partition/consumer-group names (Kafka), and which service declares them.
  *Why now:* publisher and consumer must agree before either is written; declaration ownership affects startup order.
  *Source:* R5, R6, R14.

- **7.2 `ORDER_READY` payload schema.** `[open]`
  *Decide:* fields, event id, event type, timestamp, and whether the event carries an order snapshot or only an identifier.
  *Why now:* it is a typed cross-service boundary (§3) and appears in the sequence diagram.
  *Source:* R5, R6, R17, `CLAUDE.md` §3.

- **7.3 Serialization and version marker.** `[open]`
  *Decide:* encoding, and whether a schema version field exists.
  *Why now:* part of the same contract as 7.2.
  *Source:* R5, R6.

- **7.4 Durability.** `[open]`
  *Decide:* persistent messages, durable queues, and what happens to in-flight events across a broker restart.
  *Why now:* it is set at topology-declaration time; adding it later requires redeclaring topology.
  *Source:* DoD "Broker & Consumer".

- **7.5 Publish versus commit ordering.** `[open]`
  *Decide:* publish before commit, after commit, or via an outbox — and which failure window is accepted.
  *Why now:* the central reliability trade-off of the design, balanced against the §3 simplicity requirement; it must be a decision, not an accident.
  *Source:* R5, `CLAUDE.md` §3, §7.

- **7.6 Behaviour when the broker is unreachable during a status update.** `[open]`
  *Decide:* the `PATCH` fails, or succeeds with the event lost.
  *Why now:* determines the API error contract (6.2) and is a candidate test scenario.
  *Source:* R5, `CLAUDE.md` §5.

- **7.7 Connection lifecycle.** `[open]`
  *Decide:* connection/channel per request or long-lived, and reconnection behaviour on both sides.
  *Why now:* affects the publisher interface signature (3.4) and worker resilience (R10).
  *Source:* R5, R10.

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

- **8.4 Poison message handling.** `[open]`
  *Decide:* what happens to a malformed message, and whether it can block the queue.
  *Why now:* an unhandled parse error in a nack-requeue loop stops all dispatch — a silent total failure.
  *Source:* R10, DoD.

- **8.5 Consumer concurrency.** `[decided]`
  *Decision:* **one worker replica in compose, prefetch 1.** This is a deployment choice, not
  a correctness mechanism — correctness comes from 8.9. The README states that scaling to N
  replicas requires no code change.
  *Why:* a single consumer keeps the integration tests deterministic (`CLAUDE.md` §5) and
  keeps message order per queue trivially preserved. Ordering is not load-bearing anyway,
  since every rule in 5.5 and 5.6 is idempotent.
  *Rejected:* multiple replicas by default — weakens test determinism to demonstrate a scale
  the assignment never asks for.
  *Source:* R14, DoD. *Answers:* Q13.

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

- **8.7 Logging format and levels.** `[open]`
  *Decide:* structured or plain, and correlation by order id across services.
  *Why now:* the log is the reviewer's main window into the asynchronous path; consistency is a §6 requirement.
  *Source:* R8, R9, DoD.

- **8.8 Startup and shutdown behaviour.** `[open]`
  *Decide:* what the worker does when the broker or database is not yet available, and how it shuts down without losing an in-flight message.
  *Why now:* compose starts everything at once; this is the first thing a reviewer encounters.
  *Source:* R14, R10.

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

- **9.1 Interaction style.** `[open]`
  *Decide:* numbered menu loop, prompt-driven shell, or sub-commands with an interactive fallback.
  *Why now:* the DoD grades "easy to use"; it is also the reviewer's first impression of the system.
  *Source:* R11, DoD "Interactive CLI".

- **9.2 Menu actions.** `[decided]`
  *Decision:* five actions —
  1. place an order
  2. register a driver
  3. list orders and select one (by customer name, via `GET /orders` — A14)
  4. advance the selected order's status
  5. quit
  *Why status update is included:* the entire behaviour of the system is dispatch triggered by
  `BAKING`. Without it the CLI demonstrates half a product — create an order, register a
  driver, then reach for `curl` to make anything happen. The DoD asks for a client that
  "allows manual interaction with the running API services", not for the three calls named in
  R11, and the demo path (1.2) does not run without it.
  *Consequence of A3 worth naming:* because transitions are strictly linear, every order has
  exactly **one** legal next status. The CLI therefore offers a single `Advance to BAKING`
  action rather than a menu of five statuses of which four would return `409`. A tighter
  business rule produced a simpler interface — worth a line in the README.
  *Source:* R11, R19. *Answers:* Q19.

- **9.3 How the CLI is run.** `[open]`
  *Decide:* `docker compose run`/`exec` into a container, or on the host against a published port; and how it receives the API base URL.
  *Why now:* determines whether it needs its own image and compose service, and what the README instructs.
  *Source:* R11, R14, R16.

- **9.4 Validation and error presentation.** `[open]`
  *Decide:* what the CLI validates locally versus what it lets the API reject, and how API errors are displayed.
  *Why now:* §3 places validation at the edge and forbids adapters from re-implementing logic; the split must be explicit.
  *Source:* R11, `CLAUDE.md` §3.

- **9.5 Client-side state.** `[open]`
  *Decide:* whether the CLI remembers anything between actions (e.g. the last created order id).
  *Why now:* affects usability and the "thin adapter" rule in 3.6.
  *Source:* R11, `CLAUDE.md` §3.

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

- **10.1 The complete environment variable list.** `[open]`
  *Decide:* names, types, defaults, which are required, and which service reads which.
  *Why now:* §3 forbids hardcoded hosts, ports, and credentials; every service's first line of code reads configuration.
  *Source:* R16, `CLAUDE.md` §3, DoD "Code Quality".

- **10.2 Configuration loading mechanism.** `[open]`
  *Decide:* a typed settings object or raw environment reads, and where configuration itself is validated.
  *Why now:* it is a typed boundary (§3) shared by all entry points.
  *Source:* `CLAUDE.md` §3.

- **10.3 `.env` versus `.env.example`.** `[open]`
  *Decide:* what is committed, what is ignored, and how compose consumes each.
  *Why now:* §4 forbids committing local environment files and requires an example; `.gitignore` must be correct before the first commit that adds configuration.
  *Source:* R16, `CLAUDE.md` §3, §4.

- **10.4 Which values are tunable.** `[open]`
  *Decide:* retry delay, retry cap, prefetch, ports, log level — tunable or fixed.
  *Why now:* tests may need to tune them (e.g. a short retry delay) to stay fast and deterministic.
  *Source:* R16, `CLAUDE.md` §5.

- **10.5 Local credentials.** `[open]`
  *Decide:* default database and broker credentials, and how they are supplied without being hardcoded.
  *Why now:* §4 forbids committed secrets, but a reviewer must still run `docker compose up` with zero setup.
  *Source:* `CLAUDE.md` §4, DoD "Docker Deployment".

## Topic 11 — Docker Compose

- **11.1 Service inventory.** `[open]`
  *Decide:* api, worker, broker, database, tests, cli, and any init/migration service.
  *Why now:* R15 only works if the dependency graph is designed up front.
  *Source:* R14, R15.

- **11.2 Readiness and ordering.** `[open]`
  *Decide:* healthchecks with `depends_on: condition: service_healthy`, in-app retry loops, or both.
  *Why now:* `CLAUDE.md` §5 forbids fixed sleeps; this must be a condition-based design from the start.
  *Source:* R14, R15, `CLAUDE.md` §5. *Constrained by A15:* the API's readiness probe is
  `GET /health`; PostgreSQL and RabbitMQ use their built-in checks.

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

- **11.8 Published host ports.** `[open]`
  *Decide:* which services are exposed, on which ports, and how conflicts are avoided.
  *Why now:* README instructions and host-side CLI use (9.3) depend on it.
  *Source:* R14, R19.

- **11.9 Image build strategy.** `[open]`
  *Decide:* base images, layer caching, build context, and whether a separate build step is required before `up`.
  *Why now:* the DoD requires a seamless launch; first-run build time is part of that.
  *Source:* R14, DoD "Docker Deployment".

- **11.10 Compose command form.** `[open]`
  *Decide:* `docker compose` v2 or `docker-compose` v1, documented as a prerequisite.
  *Why now:* the deliverable is a file a stranger runs on an unknown machine.
  *Source:* R14, R19.

- **11.11 Restart policies.** `[open]`
  *Decide:* restart behaviour for api, worker, and broker-dependent services.
  *Why now:* the difference between a crash-looping stack and a self-healing one on the reviewer's first run.
  *Source:* R14, R10.

## Topic 12 — Testing

- **12.1 Risk ranking.** `[open]`
  *Decide:* enumerate the failure modes that would break silently, rank them, and take the top 3–4.
  *Why now:* `CLAUDE.md` §5 mandates selection by risk, and the assignment fixes the count as a ceiling.
  *Candidate already identified:* the **ghost driver** from 4.3 — `drivers.status` left `BUSY`
  after the order completes, removing a driver from the pool with no error anywhere. It breaks
  silently by construction, which is exactly the selection criterion.
  *Source:* R18, `CLAUDE.md` §5.

- **12.2 The chosen scenarios.** `[open]`
  *Decide:* each with scenario description, goal, assertions, and the rationale for those assertions.
  *Why now:* the written rationale is itself a graded deliverable, not a by-product.
  *Source:* R18, DoD "Test Automation". *Blocked by:* Q16.

- **12.3 Interface each test drives.** `[open]`
  *Decide:* HTTP plus database inspection, HTTP only, or direct broker publication.
  *Why now:* §5 requires testing behaviour and contracts, not internals; reading the database directly is a boundary decision.
  *Source:* `CLAUDE.md` §5.

- **12.4 Waiting for the asynchronous assignment.** `[open]`
  *Decide:* the condition-polling primitive and its timeout.
  *Why now:* fixed sleeps are explicitly forbidden by §5; the helper must exist before the first asynchronous test is written.
  *Source:* `CLAUDE.md` §5, R18.

- **12.5 Test data strategy and isolation.** `[open]`
  *Decide:* unique data per test, truncation between tests, or a fresh database; and how order-independence is guaranteed.
  *Why now:* §5 requires determinism and independence.
  *Source:* `CLAUDE.md` §5.

- **12.6 Scope of the unit test set.** `[open]`
  *Settled by A17:* unit tests exist, live in their own directory with their own run command,
  and do **not** count against the 3–4 ceiling, provided the README frames them as an addition
  rather than part of the required suite.
  *Still open:* **how far they may go.** The developer has deliberately not fixed this yet,
  because time may remain after the four integration scenarios for a more substantial unit set.
  *What this collides with:* `CLAUDE.md` §5 currently reads *"Unit — an addition, permitted
  only when free: pure logic, no infrastructure, written in minutes."* A larger or more
  elaborate unit suite is not merely undecided under that wording — it contradicts it.
  Expanding beyond "free" therefore requires **amending §5**, not just resolving this item.
  Flagged now so the choice is made deliberately rather than discovered mid-implementation.
  *Decide, when decided:* which pure-core rules from 5.7 are covered, and whether §5 is
  amended.
  *Source:* `CLAUDE.md` §5. *Answers (partially):* Q16.

- **12.7 Directory layout and separate run commands.** `[open]`
  *Decide:* where each category lives and how each is run independently.
  *Why now:* explicitly required by §5.
  *Source:* `CLAUDE.md` §5.

- **12.8 Deterministic testing of the retry path.** `[open]`
  *Decide:* the mechanism that makes the no-driver retry observable without sleeps — a config-tuned delay, controlled driver registration timing, or another approach.
  *Why now:* the highest-risk behaviour in the assignment and the hardest to assert deterministically.
  *Source:* R9, `CLAUDE.md` §5.

- **12.9 Where results are surfaced.** `[open]`
  *Decide:* console output only, or a report file.
  *Why now:* 11.3 and 11.4 depend on it.
  *Source:* R15.

- **12.10 Whether lint and type checks run inside the compose test run.** `[open]`
  *Decide:* gate in the delivered environment, or local-only.
  *Why now:* §8.3 requires them per step; whether they also gate the delivered environment is a separate call.
  *Source:* `CLAUDE.md` §8.

## Topic 13 — Documentation and deliverables

- **13.1 README structure.** `[open]`
  *Decide:* sections for launch, CLI usage, test instructions, named test scenarios, trade-offs, assumptions, and out-of-scope.
  *Why now:* §5 requires the scenarios to be findable from the README; §7 requires assumptions and exclusions listed.
  *Source:* R19, `CLAUDE.md` §5, §7.

- **13.2 Sequence diagram format and location.** `[open]`
  *Decide:* Mermaid in the README, a separate document, or an image.
  *Why now:* a separately graded deliverable that must stay in sync with topics 5, 7, and 8.
  *Source:* R17, DoD "System Design".

- **13.3 Diagram scope and count.** `[open]`
  *Decide:* one diagram covering both the happy path and the missing-driver path, or two diagrams.
  *Why now:* R17 lists both paths as required content; one overloaded diagram risks failing the "clear" criterion.
  *Source:* R17.

- **13.4 Trade-off log content.** `[open]`
  *Decide:* which rejected alternatives are written down — broker, database, publish-versus-outbox, retry strategy.
  *Why now:* documentation is updated in the same commit as the change (§7), so the list must exist before those commits happen.
  *Source:* R19, `CLAUDE.md` §7.

- **13.5 `docs/ai-log.md`.** `[open]`
  *Decide:* its columns, and what counts as a loggable event on this project.
  *Why now:* §6 requires the row to be written as part of the same change; the format must exist before the first rejection. One rejection has already occurred during planning and is a candidate first row.
  *Source:* `CLAUDE.md` §6.

- **13.6 Assumptions register.** `[open]`
  *Decide:* where the Part 2 assumptions live once resolved, and how they are kept current.
  *Why now:* §7 requires assumptions to be explicit and up to date.
  *Source:* `CLAUDE.md` §7.

## Topic 14 — Git and process

- **14.1 Public remote.** `[open]`
  *Decide:* where the public repository lives and when it is created.
  *Why now:* R21 asks for a public link; §4 forbids rewriting pushed history, so the remote must exist before history becomes meaningful.
  *Source:* R21.

- **14.2 Branch convention and merge style.** `[open]`
  *Decide:* branch naming, and merge commit / squash / rebase.
  *Why now:* §4 requires one branch per unit merged via pull request; the merge style determines whether the history reads as intended.
  *Source:* `CLAUDE.md` §4.

- **14.3 How much of the branch-per-unit workflow is actually executed.** `[open]`
  *Decide:* full pull-request flow, or a documented simplification for a solo 4-day assignment.
  *Why now:* it multiplies the operations in every unit; `CLAUDE.md` currently makes no allowance for it.
  *Source:* `CLAUDE.md` §4, assignment time estimate.

- **14.4 Unit-to-commit map.** `[open]`
  *Decide:* the explicit mapping from Part 4 units to commits, produced during Phase 3.
  *Why now:* §4 requires one commit per logical unit and treats a bulk commit as a process failure.
  *Source:* `CLAUDE.md` §4, §2.

- **14.5 Whether `CLAUDE.md`, `.claude/`, and the plans directory are committed.** `[open]`
  *Decide:* included in the delivered public repository, or deliberately excluded.
  *Why now:* `CLAUDE.md` is currently untracked and `.claude/` may be ignored; the planning history is either part of the delivered narrative or not.
  *Source:* R21, `CLAUDE.md` §4.

- **14.6 `.gitignore` adequacy.** `[open]`
  *Decide:* verify coverage for Python caches, virtual environments, `.env`, Docker artifacts, and editor files — and whether it currently ignores `.claude/`.
  *Why now:* the file already exists and is committed; it must be correct before the first source commit, not after.
  *Source:* `CLAUDE.md` §4.

- **14.7 What "main still runs" means in the early units.** `[open]`
  *Decide:* the criterion for a commit that precedes any runnable system.
  *Why now:* §8.6 applies from the first commit; without a definition the criterion is unmeetable.
  *Source:* `CLAUDE.md` §8.

---

# Part 2 — Open questions

Each of these can be read more than one way. Per `CLAUDE.md` §2, none is resolved silently.
They are answered one at a time with the developer; each answer is written into the inventory
item it unblocks and recorded as an assumption. **Phase 2 does not end while any row is open.**

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
| **Q16** | Does "3–4 automated tests" mean 3–4 scenarios or 3–4 test functions, and do permitted unit tests count against the ceiling? | 12.2, 12.6 | **answered → A17** (unit-test scope deliberately left open in 12.6) |
| **Q17** | Data persistence across runs is unstated — should a reviewer's second `docker compose up` see the previous run's data? | 11.7 | **answered → A19** |
| **Q18** | The broker and database choices interact: transactional claiming is easier in one database, delayed retry is easier in one broker. They must be chosen as a pair, not independently. | 2.1, 2.2, 8.2, 8.9 | **answered → A1** |
| **Q19** | The diagram shows "Interactive CLI / REST client" as alternatives. Must the CLI cover **all** operations, including status updates that the demo needs, or only the three named ones? | 9.2 | **answered → A18** |
| **Q20** | The development host is Windows; the delivery target is Docker on an unknown host. The assignment does not address line endings, entrypoint scripts, or CLI TTY behaviour. | 9.6, 11.9 | **answered → A21** |

**Answering order** (most-blocking first):
Q18 → Q1 → Q2 → Q4 → Q13 → Q6 → Q8 → Q3 → Q5 → Q9 → Q10 → Q14 → Q11 → Q12 → Q7 → Q16 → Q19 → Q17 → Q15 → Q20.

## Resolved answers and assumptions

Recorded here until item 1.4 fixes the permanent location. Each entry is the answer as given
by the developer, stated as an assumption the rest of the plan may rely on.

- **A1** *(answers Q18)* — **The stack pair is RabbitMQ + PostgreSQL.** The broker is chosen
  for native per-message requeue and TTL-based delayed retry; the database is chosen for
  transactional, lock-based driver claiming. Consequences: retry design in 8.2/8.3 is
  expressed as a dead-letter exchange with TTL rather than retry topics, and driver claiming
  in 8.9 is expressed as `SELECT … FOR UPDATE SKIP LOCKED` inside the same transaction that
  writes the assignment. Recorded in 2.1 and 2.2.

- **A2** *(answers Q1)* — **`ORDER_READY` is published on both `BAKING` and `READY`, and
  assignment is idempotent per order.** Two events per order on the normal path is expected,
  not a defect. The second one finds the order already assigned, changes nothing, and is
  acknowledged. The same rule is the system's answer to duplicate delivery generally.
  Recorded in 5.3 and 5.5; defines F3, F6, F8.

- **A3** *(answers Q2 and Q14)* — **The status lifecycle is a strictly linear, single-step,
  forward-only chain, with `DELIVERED` terminal.** Skips, rollbacks, and same-status updates
  are all illegal transitions and are rejected identically (`409`); an unrecognised status
  string is a validation failure at the edge (`422`). Consequence: the API can never publish
  a duplicate `ORDER_READY` for the same order, so 5.5 exists solely to absorb broker-level
  redelivery. Recorded in 5.1 and 5.2; defines F9.

- **A4** *(answers Q4)* — **Drivers are released. The transition into `DELIVERED` returns the
  assigned driver to `AVAILABLE`.** This is an assumption, not a stated requirement, and is
  documented as such. Its consequence is a second clause in the worker's assignment guard: a
  driver is assigned only to an order that is both unassigned **and** not delivered, otherwise
  a driver assigned after the release point would stay `BUSY` forever. Recorded in 5.5 and
  5.6; defines F12. Automating the `DELIVERED` transition itself is deliberately out of scope
  — see FW1 in Part 5.

- **A5** *(answers Q13)* — **One worker replica with prefetch 1, but claiming is safe in code,
  not by deployment.** The claim is a `SELECT … FOR UPDATE SKIP LOCKED` inside the assignment
  transaction, backed by a uniqueness constraint. Message ordering is preserved by having a
  single consumer but is not load-bearing, since the assignment rules are idempotent. Scaling
  to N workers is a compose change, not a code change, and this is stated in the README.
  Recorded in 8.5 and 8.9; defines F2.

- **A6** *(answers Q3)* — **"Assignment states" is a second axis on the order, not a separate
  entity.** The order carries `assignment_state` (`PENDING → ASSIGNED → COMPLETED`, plus
  `FAILED`), `driver_id`, and `assigned_at`, alongside the untouched five-value `status` from
  R2. `driver_id` is never cleared, so "which orders did this driver take" is a single query
  and driver history is preserved without an extra table. `COMPLETED` is set by the same
  transition to `DELIVERED` that releases the driver, which is what keeps the uniqueness
  constraint conditioned on `assignment_state` alone. Recorded in 4.4; constrains 4.5.

- **A7** *(answers Q6)* — **Fixed-delay retry through a dead-letter exchange and a TTL wait
  queue, with a capped number of attempts.** On exhaustion the order is marked
  `assignment_state = FAILED`, the failure is logged at error level, and the message is
  acked — there is no parked queue, because the failure belongs where the domain can show it.
  Delay and cap are both env-tunable. Accepted cost: an exhausted order is not picked up if a
  driver appears later. Recorded in 8.1, 8.2 and 8.3; defines F7.

- **A8** *(answers Q8)* — **A one-shot test service runs the suite at startup against the live
  stack, and the stack stays up afterwards.** Plain `docker compose up` reports pass or fail
  in its output without tearing anything down; `--abort-on-container-exit --exit-code-from
  tests` is documented as the gating variant for CI. Isolation is by unique per-test data plus
  a clean start rather than a duplicated environment. Accepted cost: determinism is
  conditional on a clean start, and that condition is stated in the README instead of being
  assumed away. Recorded in 11.3–11.6.

- **A9** *(developer decision, narrows Q11)* — **No driver-history endpoint.** The data to
  answer "which orders did this driver take" exists from day one because `driver_id` is never
  cleared (A6), but exposing it is an unrequested feature and is not built. Recorded in 6.6
  and FW3.

- **A10** *(answers Q5)* — **Drivers are always registered `AVAILABLE`; the registration
  request has no status field.** `status` remains part of the driver resource with exactly the
  two values R3 names, but only the core's assignment and release rules ever write it. This
  eliminates F11 outright: a `BUSY` driver with no order is no longer a state the system can
  hold, rather than a state it has to cope with. Recorded in 6.4; constrains 4.3.

- **A11** *(answers Q9)* — **`items` is a list of typed objects: `name`, `quantity`, and a free
  `toppings` list.** Validated at the edge with explicit bounds, unknown fields rejected, and
  `size` deliberately omitted. Nothing in the system reads `items`, so the structure exists for
  the CLI's benefit; the typing exists because `CLAUDE.md` §3 does not permit an untyped
  dictionary to cross into the core. Recorded in 4.2; defines F13.

- **A12** *(answers Q10)* — **`GET /orders/{id}` returns a nested driver object, or `null`.**
  Storage stays normalised (`orders.driver_id` → `drivers.id`); the nesting is produced by a
  `LEFT JOIN` at read time and belongs to the adapter, not the core. Driven by A9: with no
  driver endpoint, an id alone would be unresolvable anywhere in the system. The response also
  exposes `assignment_state`, without which 8.3's failure record would be invisible. Recorded
  in 6.5; timestamps settled in 4.8.

- **A13** *(developer-raised, no prior question)* — **One active order per driver.** This had
  been assumed by every decision since 4.3 without being stated. Now recorded as item 5.8,
  together with the seven things that would change if capacity were greater than one.

- **A14** *(answers Q11)* — **`GET /orders` exists**, returning a light list without the nested
  driver, newest first, capped at 50. The CLI uses it to let the user pick an order by customer
  name instead of retyping a UUID. Justified by the DoD's "easy-to-use console client" rather
  than by the endpoint list in the brief, and recorded as such. Recorded in 6.6; affects 9.2.

- **A15** *(answers Q12)* — **`GET /health` exists**, returning `200` when the database and
  broker are reachable and `503` otherwise. It is required infrastructure, not a feature:
  without something to ask "are you ready", condition-based startup ordering is impossible and
  the only alternative is the fixed sleep `CLAUDE.md` §5 forbids. Whether the broker counts as
  a health dependency is coupled to 7.6 and must be settled with it. Recorded in 6.6;
  constrains 11.2.

- **A16** *(answers Q7)* — **The mock dispatch notification is a single structured `INFO` log
  line** with a fixed field set, written after the assignment commits. It is for the human
  watching `docker compose up`, and is **not** something a test asserts on: tests assert the
  state change (driver `BUSY`, order `ASSIGNED`, driver visible on the order), because
  `CLAUDE.md` §5 forbids testing implementation details, and a log string is one. Recorded in
  8.6.

- **A17** *(answers Q16)* — **"3–4 automated tests" means 3–4 integration scenarios, one test
  function each**, and the full allowance of four is used, since risk ranking will produce more
  than three worthwhile candidates. **Unit tests are a separate category and are not counted**,
  on condition that the README says so explicitly — a reviewer counting functions must not read
  4 + N as having ignored the limit. Unit tests earn their place as the *evidence* for R20 and
  `CLAUDE.md` §3: a core that can be tested with no database, no broker and no Docker is a core
  that is genuinely detached from infrastructure, demonstrated rather than claimed.
  **Deliberately left open:** how large the unit set may grow — see 12.6, including the §5
  amendment it would require.

- **A18** *(answers Q19)* — **The CLI covers status updates as well as the three operations
  R11 names.** Without it the client cannot trigger dispatch, which is the system's entire
  behaviour, and the demo path does not run. Because A3 makes transitions strictly linear, the
  CLI offers a single "advance" action rather than a status menu — one legal target always.
  Recorded in 9.2.

- **A19** *(answers Q17)* — **The environment is disposable: no named volumes, and
  `docker compose down` is the reset.** The compose file explains the absence in a comment and
  the README gives the lines to add for persistence. Persistence was considered and reversed:
  it conflicts with running the suite on every launch, because the "no available driver"
  scenario depends on global state a reviewer's own session would have changed. Recorded in
  11.7; this is the condition A8 depends on.

- **A20** *(answers Q15)* — **No authentication or authorisation.** Not a gap: the assignment
  names no user, tenant, role or token anywhere. Stated in the README so the absence is a
  recorded decision rather than an oversight, and parked as FW9. Recorded in 6.8.

- **A21** *(answers Q20)* — **Windows-to-Linux friction is handled by configuration and
  documentation, not code.** `.gitattributes` already forces LF; no entrypoint scripts will be
  written, since healthchecks cover readiness; and the Git Bash TTY caveat for the CLI is a
  README note. Recorded in 9.6, pending 9.3's decision on where the CLI runs.

---

# Part 3 — Cross-cutting failure modes

Each needs a defined behaviour before implementation. `CLAUDE.md` §5 requires failure paths
to be tested, and §2 Phase 3 requires a plan with no judgement calls left in it.

| # | Failure mode | Defined by |
|---|---|---|
| **F1** | `PATCH` on a non-existent order id | 6.2 |
| **F2** | Two `ORDER_READY` events race for the last `AVAILABLE` driver | 8.9, 4.5, 3.5 |
| **F3** | Duplicate `ORDER_READY` for one order — `BAKING` then `READY`, plus broker redelivery | 5.5 |
| **F4** | Broker down when the API tries to publish | 7.6 |
| **F5** | Database down when the worker tries to assign; the message must not be lost | 8.1, 8.8 |
| **F6** | Worker crashes after marking the driver `BUSY` but before the ack — redelivery into a partially applied state | 8.1, 5.5 |
| **F7** | No drivers exist at all, indefinitely — retry behaviour over a long horizon | 8.2, 8.3 |
| **F8** | Order reaches `READY` when it already has a driver — no-op, error, or reassignment | 5.5 |
| **F9** | Illegal or out-of-order status transition requested | 5.1, 5.2 |
| **F10** | Malformed or unparseable message on the queue | 8.4 |
| **F11** | ~~Driver registered directly as `BUSY` with no order~~ — **cannot occur.** A10 removes the status field from the registration request, so the state is unreachable rather than handled | eliminated by 6.4 |
| **F12** | Order reaches `DELIVERED` with no driver ever assigned | 5.6 |
| **F13** | Validation failures on order creation — empty items, empty address, oversized payload | 4.2, 6.2 |
| **F14** | Concurrent `PATCH` requests on the same order | 6.9 |

---

# Part 4 — Execution order

The work is split into **atomic units**. A unit is a set of changes that only makes sense
together: it is planned as a whole, implemented as a whole, verified as a whole, and lands as
one branch and one commit (`CLAUDE.md` §4).

**The rule for each unit, in order:**

1. Every topic listed under *Decided by* must be `[decided]` before the unit is planned.
2. The unit gets its own Phase 3 plan document in `.claude/plans/`.
3. The unit is implemented, verified against its Definition of Done, and merged.
4. Only then is the next unit planned. A unit is never planned while a unit it depends on is
   unfinished — that is what makes the dependency real rather than nominal.

## Unit table

| Unit | Content | Decided by (topics) | Depends on units | Depended on by |
|---|---|---|---|---|
| **U1** Foundation | Repository skeleton, package layout, dependency management, formatter/linter/type-checker config, `.gitignore` verification, `docs/ai-log.md` | 1, 2.8–2.10, 3.1, 3.3, 13.5, 14 | — | all |
| **U2** Configuration | Typed settings object, `.env.example`, config validation at startup | 10 | U1 | U5, U6, U7, U8, U9 |
| **U3** Business core | Order and Driver entities, status transition rules, driver-selection and assignment rules, the port interfaces. Framework-free, no infrastructure | 3.2, 3.4, 3.5, 4.1–4.4, 4.7, 4.8, 5 | U1 | U4, U5, U6, U7, U8 |
| **U4** Core unit tests | Unit tests for the rules identified as infrastructure-free | 5.7, 12.6, 12.7 | U3 | — |
| **U5** Persistence | Schema and migrations, repository implementations, integrity constraints, concurrency-safe driver claiming | 2.2, 2.5, 4.5, 4.6, 8.9 | U2, U3 | U7, U8 |
| **U6** Broker adapter | Topology declaration, event payload type, publisher implementation, connection lifecycle | 2.1, 2.7, 7 | U2, U3 | U7, U8 |
| **U7** API service | Routes, edge validation, error format, status-update endpoint including the publish trigger, wiring of core + repositories + publisher | 2.3, 2.4, 6, 7.5, 7.6 | U3, U5, U6 | U9, U12 |
| **U8** Dispatch worker | Consumer loop, ack/nack policy, retry and dead-letter handling, poison-message handling, dispatch logging, startup/shutdown | 8 | U3, U5, U6 | U9 |
| **U9** Compose environment | Dockerfiles, compose services, healthchecks and readiness ordering, volumes, ports, restart policies | 3.7, 11.1, 11.2, 11.7–11.11 | U7, U8 | U10, U11 |
| **U10** Integration test suite | The 3–4 risk-ranked scenarios, condition-based waiting, data isolation | 12.1–12.5, 12.8 | U9 | U11 |
| **U11** Automatic test execution | Test service wired into compose startup, failure behaviour, result output | 11.3–11.6, 12.9, 12.10 | U10 | — |
| **U12** Interactive CLI | Menu loop, actions, API client, error presentation, how it is launched | 3.6, 9 | U7 | — |
| **U13** Documentation pass | README assembled, sequence diagram, assumptions register, trade-off log | 13 | all | — |

## Ordering and parallelism

Sequential spine: **U1 → U3 → U5 → U7 → U8 → U9 → U10 → U11**.

Off the spine:
- **U2** runs after U1 and before U5; it is small and blocks everything that touches infrastructure.
- **U4** can be written immediately after U3 and blocks nothing. It is the only work possible
  before any infrastructure exists.
- **U6** runs in parallel with U5 — both depend only on U2 and U3, not on each other.
- **U12 (CLI) depends only on U7 and nothing depends on it.** Once the API contract is frozen
  it can be built at any point, including last. There is no reason to build it early.
- **U13** is last by necessity: the sequence diagram reflects decisions realised in U6, U7,
  and U8, and documents a system that must already exist. Per `CLAUDE.md` §7, each earlier
  unit still updates documentation in its own commit; U13 is the assembly and the diagram,
  not the first time documentation is written.

## Freeze points

Two contracts, once frozen, unlock everything downstream in parallel:

- **The API contract (topic 6)** — unblocks U7, U10, and U12 simultaneously.
- **The event contract (topic 7)** — unblocks U6, and therefore U7 and U8 in parallel.

Everything before these two is sequential; everything after is parallelisable.

---

# Part 5 — Future work

Nothing in this part is required by the assignment, and nothing here is built unless the
required scope is complete, verified, and documented first. The list exists for two reasons:
`CLAUDE.md` §7 requires deliberate exclusions to be stated, and an interview is likely to ask
what we would do next. Items move out of this list only by an explicit decision, never by
drift (`CLAUDE.md` §6).

Item 1.1 (scope ceiling) draws the line; this is where everything on the far side of it is
recorded.

- **FW1 — Automated delivery completion.** Today the transition to `DELIVERED` is a manual
  `PATCH`, and it is what releases the driver (5.6). Instead, the arrival of the delivery
  would emit its own event — the driver, or a simulator standing in for one, signals arrival;
  a consumer moves the order to its terminal state and releases the driver automatically.
  This is the natural continuation of the event-driven design: right now the *start* of
  dispatch is event-driven and the *end* of it is a human pressing a key.
  *Possible shape:* an `ORDER_ARRIVED` (or `DELIVERY_COMPLETED`) event, and an `ARRIVED`
  status ahead of the terminal state.
  *Why it is not in scope:* R2 fixes the lifecycle at five statuses and stops at `DELIVERED`.
  Adding a sixth status changes a stated requirement rather than extending it, and a reviewer
  comparing the implementation to the brief would see a mismatch. If built, it must be
  additive: the five required statuses keep behaving exactly as specified.

- **FW2 — Transactional outbox for publishing.** Removes the dual-write window left open by
  whatever 7.5 decides: the event and the status change become atomic, and a publish is never
  lost because the broker was briefly unreachable. Out of scope because it adds a table, a
  relay process, and its own failure modes for a reliability level the assignment does not ask
  for.

- **FW3 — Driver endpoints beyond registration.** Listing drivers, changing availability after
  registration, and **driver order history** (`GET /drivers/{id}/orders`). The history is
  already stored — `driver_id` on the order is never cleared (A6) — so this is a read endpoint
  over existing data, not a data-model change. Excluded by A9 and `CLAUDE.md` §6: the
  assignment names exactly one driver endpoint.

- **FW4 — Order listing and filtering.** `GET /orders` with status filters and paging. Related
  to Q11, which decides only the minimum the CLI needs.

- **FW5 — Dead-letter inspection and replay.** An operator-facing way to see parked messages
  and requeue them, rather than reading broker internals.

- **FW6 — Metrics and tracing.** A correlation id carried from API through broker to worker,
  plus counters for assignments, retries, and exhausted messages. Currently logging alone
  covers the reviewer's need to see what happened.

- **FW7 — Verified multi-consumer operation.** Running several worker replicas and proving the
  claiming race is safe under real contention, rather than by design argument plus a
  constraint. Depends on what 8.5 and 8.9 decide.

- **FW8 — Persisted dispatch notifications.** Storing dispatch records instead of only logging
  them (8.6), which would make the notification history queryable rather than grep-able.

- **FW9 — Authentication and authorisation.** Excluded per 6.8; there is no user or tenant
  concept anywhere in the assignment.

- **FW10 — Delivery estimates and driver location.** Assignment by proximity or load rather
  than "any available driver" (5.4). This is the interesting version of the problem, and the
  one the assignment explicitly did not ask for.
