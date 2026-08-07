# Planning — Decisions

**Phase 2 of the planning protocol in `CLAUDE.md` §2: every inventory item resolved.** Each
record states the decision, why it was chosen, and what was rejected and why. The questions
these answer are in `01-inventory.md`; the build order is in `03-roadmap.md`.

Item numbering is inherited from the inventory and is stable. Depth follows item 1.3: a full
record where a reviewer would ask "why this?", a single line where no genuine alternative was
weighed.

---

## Status

**Authoritative.** The `[open]` markers in `01-inventory.md` record each item's state when it
was written and are not maintained; this table is.

| Topic | Decided | Open |
|---|---|---|
| 1 — Scope and time | 1.1, 1.3, 1.5 | 1.2, 1.4 |
| 2 — Stack and tooling | 2.1, 2.2, 2.3 | 2.4–2.10 |
| 3 — Architecture and layering | — | 3.1–3.8 |
| 4 — Data model | 4.2, 4.3, 4.4, 4.8 | 4.1, 4.5, 4.6, 4.7 |
| 5 — Business rules | 5.1, 5.2, 5.3, 5.5, 5.6, 5.8 | 5.4, 5.7 |
| 6 — API contract | 6.4, 6.5, 6.6, 6.8 | 6.1, 6.2, 6.3, 6.7, 6.9 |
| 7 — Broker contract | — | 7.1–7.7 |
| 8 — Worker | 8.1, 8.2, 8.3, 8.5, 8.6, 8.9 | 8.4, 8.7, 8.8 |
| 9 — CLI | 9.2, 9.6 | 9.1, 9.3, 9.4, 9.5 |
| 10 — Configuration | — | 10.1–10.5 |
| 11 — Docker Compose | 11.3–11.7 | 11.1, 11.2, 11.8–11.11 |
| 12 — Testing | — | 12.1–12.10 *(12.6 partial)* |
| 13 — Documentation | 13.5 | 13.1–13.4, 13.6 |
| 14 — Git and process | 14.5 | 14.1–14.4, 14.6, 14.7 |
| **Total** | **35** | **74** |

Phase 3 does not begin while any item is open (`CLAUDE.md` §2).

---

# Part 1 — Decision records

## Topic 1 — Scope and time

- **1.1 Scope ceiling.** `[decided]`
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
  **`GET /health`.** It returns `200` when the application can reach the database and the
  broker, `503` otherwise — no metrics, no version, no uptime, no per-dependency detail.
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
  health condition. **Revisit with 7.5 and 7.6 — the three are one decision.**
  *Source:* R11, R14, `CLAUDE.md` §6, 1.1. *Answers:* Q11, Q12.

- **6.8 Authentication.** `[decided]`
  *Decision:* **none.** Every endpoint is open. Recorded in the README under assumptions:
  *"There is no authentication. The API targets an internal network and a demonstration
  environment; public exposure would require an auth layer, which is out of scope."*
  *Why:* the assignment mentions no users, tenants, roles, or tokens anywhere. Adding auth
  would be an unrequested feature (`CLAUDE.md` §6); leaving it unmentioned would be an
  unstated assumption (§7). Stating the absence satisfies both.
  *Source:* `CLAUDE.md` §7. *Answers:* Q15. *Deferred to:* FW9.


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
| **A15** † | `GET /health` exists — `200` when the database and broker are reachable, `503` otherwise | 6.6 |
| **A16** | The mock dispatch notification is one structured `INFO` log line, and not a test assertion target | 8.6 |
| **A17** † | "3–4 automated tests" means four integration scenarios; unit tests are separate and uncounted | 12.6 *(partial)* |
| **A18** | The CLI covers status updates as well as the three operations R11 names | 9.2 |
| **A19** † | The environment is disposable — no named volumes, `docker compose down` is the reset | 11.7 |
| **A20** † | No authentication or authorisation | 6.8, FW9 |
| **A21** | Windows-to-Linux friction is handled by configuration and documentation, not code | 9.6 |

*Superseded:* A11 previously read "a list of typed objects — `name`, `quantity`, `toppings`".
It was narrowed on 2026-08-07 when 1.1's ceiling test was applied to it; the structure is now
FW11. A12 previously described the nested driver as produced by a `LEFT JOIN`, which
contradicted 6.5's decision to use two keyed reads. **6.5 is authoritative**; the register no
