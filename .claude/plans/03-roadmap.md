# Planning — Roadmap

**The build order, and what is deliberately not built.** Decisions are in `02-decisions.md`;
the questions behind them are in `01-inventory.md`.

- **Part 4** is the execution order: atomic units of work, what must be decided before each is
  planned, and which units must precede which.
- **Part 5** is the future-work list: everything on the far side of the scope ceiling (1.1),
  kept as a record of what was considered and consciously not built.

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
| **U5** Persistence | Schema and migrations, repository implementations, the `outbox` table and its insert/mark-published operations (7.5), integrity constraints, concurrency-safe driver claiming | 2.2, 2.5, 4.5, 4.6, 7.5, 8.9 | U2, U3 | U7, U8 |
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
  *Half of it is already built:* 7.5 writes every event into an `outbox` table transactionally.
  What FW2 adds is the **relay** — the loop that publishes rows with `published_at IS NULL` and
  marks them — plus its compose service.

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
  claiming race is safe under real contention, rather than by design argument plus a constraint.
  8.9 already makes the claim safe in code, so this buys evidence rather than safety; what it
  revisits is 8.5's choice of one replica, taken for test determinism.
  *What does not change with it, and this is the entry that makes the reason visible:*
  `prefetch` stays at 1. RabbitMQ dispatches round-robin without regard to how busy a consumer
  is, so a wide window lets one consumer hold messages it has not started while another sits
  idle — and messages already handed to a client buffer cannot be taken back. Prefetch 1 is
  what makes several consumers share work at all: its cost profile inverts the moment there is
  more than one of them, from mildly useful to actively harmful. 8.5 records the two conditions
  under which a wider window would be worth revisiting, and "more replicas" is neither of them.

- **FW8 — Persisted dispatch notifications.** Storing dispatch records instead of only logging
  them (8.6), which would make the notification history queryable rather than grep-able.

- **FW9 — Authentication and authorisation.** Excluded per 6.8; there is no user or tenant
  concept anywhere in the assignment.

- **FW10 — Delivery estimates and driver location.** Assignment by proximity or load rather
  than "any available driver" (5.4). This is the interesting version of the problem, and the
  one the assignment explicitly did not ask for.

- **FW11 — Structured order items.** `items` as typed objects — `name`, `quantity`,
  `toppings` — instead of strings. It would let the CLI render `2 × Margherita (olives)`
  rather than echoing input, and it is the precondition for anything that ever reads an
  order's contents: pricing, a kitchen display, per-item preparation times. Excluded under
  1.1 because nothing in the delivered system reads `items`, so no DoD row degrades without
  it. Note that this is a **widening** change to the API contract, not a breaking one.

- **FW12 — Asynchronous runtime.** Moving the system to `async` — `async def` handlers, an async
  database driver, `aio-pika`, an async suite — so that a request waiting on the broker or the
  database releases its thread instead of holding it. 2.4 chose synchronous and named the
  condition that would turn the trade over; this is the record of what happens when it does.
  *Why it is not in scope:* the concurrency it optimises does not exist. 8.5 runs one worker
  replica at prefetch 1, and the API serves one interactive CLI user plus four sequential test
  scenarios.
  *What would trigger it:* raising prefetch above 1, running worker replicas (FW7), or genuinely
  concurrent API traffic — most visibly across 7.5's publish window, where a `PATCH` against an
  unreachable broker occupies a thread-pool thread for up to twice the configured timeout.
  *What it touches, and why it is not a small change:* unlike FW11 this is not additive. 3.5's
  `UnitOfWork` becomes `__aenter__` / `__aexit__` / `async def commit`; every repository method
  and every use case is coloured with it; U4's unit tests need an async pytest plugin, losing
  the "free" status `CLAUDE.md` §5 admits them under; and SQLAlchemy's async support pulls in
  `greenlet`. `domain/` is the one layer that does not change — the entities are values and
  reach for nothing.
  *One thing it would simplify:* the publisher thread-safety obligation 2.4 hands to 7.7
  disappears. A single event loop serialises channel access by construction, so no lock is
  needed.
