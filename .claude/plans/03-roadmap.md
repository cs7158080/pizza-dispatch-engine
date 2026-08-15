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
one branch and one pull request, carrying one commit per plan step (`CLAUDE.md` §4; the grain
is fixed by 14.4).

**The rule for each unit, in order:**

1. Every topic listed under *Decided by* must be `[decided]` before the unit is planned.
2. The unit gets its own Phase 3 plan document in `.claude/plans/`.
3. The unit is implemented, verified against its Definition of Done, and merged.
4. Only then is the next unit's **Phase 3 plan** written. An implementation plan is never written
   while a unit it depends on is unfinished — that is what makes the dependency real rather than
   nominal. **Phase 2 is not bound by it:** a unit's decisions are system-level contracts rather
   than an ordering of steps, so they may be settled at any time, and in parallel with other
   units.

## Unit table

| Unit | Content | Decided by (topics) | Depends on units | Depended on by |
|---|---|---|---|---|
| **U1** Foundation | Repository skeleton, package layout, dependency management, formatter/linter/type-checker config, `.gitignore` verification, `docs/ai-log.md` | 1, 2.8–2.10, 3.1, 3.3, 13.5, 14 | — | all |
| **U2** Configuration | Typed settings object, `.env.example`, config validation at startup | 10 | U1 | U5, U6, U7, U8, U9 |
| **U3** Business core | Order and Driver entities, status transition rules, driver-selection and assignment rules, the port interfaces, the `ORDER_READY` event type. Framework-free, no infrastructure | 3.2, 3.4, 3.5, 4.1–4.4, 4.7–4.9, 5, 7.2 | U1 | U4, U5, U6, U7, U8 |
| **U4** Core unit tests *(nothing left to realise — see below)* | Unit tests for the rules identified as infrastructure-free | 5.7, 12.6, 12.7 | U3 | — |
| **U5** Persistence | Schema creation (4.6), repository implementations, the `outbox` table and its insert/mark-published operations (7.5) with the event serialization it stores (7.3), integrity constraints, concurrency-safe driver claiming | 2.2, 2.5, 4.5, 4.6, 7.3, 7.5, 8.9 | U2, U3 | U6, U7, U8 |
| **U6** Broker adapter | Topology declaration, publisher implementation, connection lifecycle | 2.1, 2.7, 7.1, 7.3–7.7 | U2, U3, U5 *(7.3's module only)* | U7, U8 |
| **U7** API service | Routes, edge validation, error format, status-update endpoint including the publish trigger, wiring of core + repositories + publisher | 2.3, 2.4, 3.9, 6, 7.5, 7.6, 8.7 | U3, U5, U6 | U9, U12 |
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
- **U4** was placed here because it can be written immediately after U3 and blocks nothing.
  **It has nothing left to implement.** §8.2 makes each unit verify its own steps as it goes,
  so U3 wrote every free candidate 5.7 names, and 12.6 opened nothing beyond them; 12.7, the
  unit's other item, is realised in U10 and U11. The number is kept and nothing is renumbered
  — what is not expected under it is a branch, a Phase 3 document, or a commit.
- **U6** runs after U5 for one file only: 7.3's serialization module, which U5 writes because the
  outbox row needs it and U5 does not depend on U6. Everything else in U6 depends on U2 and U3
  alone, and the edge changes no build order — U5 is already ahead of U6 on the spine, and U6 is
  needed first by U7.
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
  *What it would repair — recorded when 4.9 accepted the cost.* Today `DELIVERED` is a claim typed at
  the CLI and nothing verifies it: an order whose dispatch gave up can be moved there by hand — the
  customer collected it, or the wrong order was advanced — and the system cannot tell which. 4.9
  therefore preserves `assignment_state = FAILED` across that transition, because the last thing the
  system actually observed is that no driver was ever dispatched. **The accepted cost is that one real
  story records two ways:** with no driver available, a customer collecting before the retry budget
  expires leaves `COMPLETED`, one collecting after leaves `FAILED` — separated by a timer rather than
  by anything that happened. FW1 removes it at the source: the terminal state would be produced by an
  arrival event rather than asserted by a keystroke, so `DELIVERED` becomes evidence instead of a
  claim, and a self-collected order needs a path of its own.

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

- **FW4 — Order filtering and paging.** `GET /orders` **is built** (6.6): a light list, newest
  first, with no cap. What is not built is filtering by status and paging. 6.6 rejected a cap
  without paging as the worse half of both and left paging to this entry; under 11.7's disposable
  environment, the volume that would justify it never arrives.
  *Corrected on 2026-08-11:* this entry previously read "`GET /orders` with status filters and
  paging", which claimed an endpoint that ships. 6.6 had already written the correct scope —
  "paging is FW4 if volume ever becomes real".

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
  and every use case is coloured with it; the unit set needs an async pytest plugin, losing
  the "free" status `CLAUDE.md` §5 admits it under; and SQLAlchemy's async support pulls in
  `greenlet`. `domain/` is the one layer that does not change — the entities are values and
  reach for nothing.
  *One thing it would simplify:* the publisher thread-safety obligation 2.4 hands to 7.7
  disappears. A single event loop serialises channel access by construction, so no lock is
  needed.

- **FW13 — Isolated end-to-end test environment.** A compose overlay
  (`docker-compose.test.yml`) that brings the whole system up a second time — its own
  PostgreSQL, RabbitMQ, API and worker — alongside the test runner, so the suite never shares a
  database or a broker with the environment a reviewer drives by hand. **The Dockerfiles are not
  duplicated:** the API and the worker run the same images as the demo environment, and the
  difference is confined to compose configuration and storage.

  ```
  docker compose up                                                    # demo, stays up
  docker compose -f docker-compose.yml -f docker-compose.test.yml up   # isolated E2E
  ```

  *Why it is not in scope:* R15 requires `docker compose up` **itself** to execute the suite. An
  overlay reached by a second command does not satisfy it, and promoting the overlay to the
  primary launch would leave the default `up` with no tests at all. What it buys over 11.6 is
  also narrower than it looks: 11.7 already guarantees a clean start, so the only failure it
  removes is re-running `up` after driving the system by hand — which one documented
  `docker compose down` already covers. Under 1.1's ceiling test, no named DoD row fails without
  it.
  *The lighter version was considered and fails the same test:* keeping `up` exactly as 11.3
  defines it and documenting the overlay beside it, the way 11.4 documents its CI gate. R15
  would survive, but the overlay would still be structure no DoD row requires.

  *What it would unlock — the two real reasons to want it, neither obtainable while the
  environments are shared:*
  1. **Test-only configuration.** A short retry TTL and a low attempt cap would make an
     exhaustion scenario (F7) cost seconds instead of the ~60 s that 1.2's human-paced floor
     imposes. There is one `TTL × cap` product, the wait queue's TTL is a queue-level property
     (8.2) rather than a per-consumer one, and the demo and the suite pull that single number in
     opposite directions. 10.4 holds the shipped pair — 8 s × 8 redeliveries, a 64 s budget — and
     names this entry as the only condition under which the cap could drop.
     *The cost is not small:* the suite would stop exercising the
     configuration that ships, so a wrong retry budget in the delivered environment would pass
     green.
  2. **Named volumes for the demo environment.** 11.7's sole justification is the shared driver
     pool, so isolation removes it and A19 reopens. Nothing asks for persistence, and it turns
     `docker compose down` into `down -v`. **This is also the only door to FW16**, which needs
     data that survives a launch before a migration tool has anything to migrate.

  *What it would touch, if ever taken:* 11.6 rewritten; 11.3, 11.4, 11.5 and 11.7 materially
  affected; A8 and A19; steps 1 and 2 of 1.2's demo path; 12.3's reopen condition and 12.5's
  data strategy.
  *One thing it does not break:* an overlay merged with `-f` is not a second independent compose
  file, so R14's "one `docker-compose.yml`" survives. 9.3 rejected a second compose file for the
  CLI on that same reading, and the distinction would have to be written there.

- **FW14 — Standard AMQP properties on the message.** Filling `message_id`, `type` and
  `timestamp` with values the payload already carries, so the management UI and any tracing tool
  can list and group messages without decoding the body.
  *Why it is not in scope:* it puts the same fact in two places that nothing keeps in step, for a
  display the management UI already gives from the body itself. 7.2 keeps one source of truth.
  *What would trigger it:* a monitoring or tracing tool that reads message metadata.
  *Cost when taken:* one keyword argument on `basic_publish`, and no change to the consumer —
  nothing reads properties, so it breaks no contract and needs no coordinated deploy.

- **FW15 — Event-carried state transfer for `ORDER_READY`.** The event carries a snapshot of the
  order — customer name, items, destination — instead of identifiers alone.
  *What would trigger it:* the worker no longer sharing a database with the API (3.8), or a
  driver-selection rule needing a fact the order row does not hold.
  *Why it is not in scope:* while the row is reachable and current, a snapshot is a second source
  of truth that goes stale, and 5.5 forbids relying on it — the consumer must read the row
  regardless, so the fields would be present and unusable. `items` would also be carried in the
  unstructured form FW11 exists to replace.
  *Recorded because the developer proposed it as groundwork for driver types:* that feature's rule
  belongs in `domain/` beside 5.4, and the dispatch use case already holds the order it loaded, so
  the groundwork is the database read rather than the message.

- **FW16 — Schema migrations.** Alembic in place of 4.6's `create_all`: the schema becomes an
  ordered chain of revisions, and changing it stops meaning recreating it.
  *Why it is not in scope, stated as a missing object rather than as a saved dependency:* a
  migration tool is the ability to change a schema **that holds data which must survive the
  change**, and 11.7 leaves no such data — with no named volumes the schema is built from empty on
  every launch, so there is never a second version. `versions/` would hold one revision describing
  a capability nothing exercises.
  *Its preconditions are a chain, and this is the entry's real content — recorded because the
  developer traced it:* migrations need persistence, persistence needs A19 reopened, and A19
  reopens only through **FW13's second point**, since 11.7 rests entirely on the shared driver pool
  that an isolated test environment removes. Nothing shorter than that chain makes Alembic worth
  its own file. The one route that bypasses it is deployment to an environment we do not recreate
  from empty, which this assignment does not have.
  *Cost when taken, and it is small by construction:* `Base.metadata` is already the single source
  of the schema (2.5, 4.6), so `alembic revision --autogenerate` writes the first revision from it,
  and the one-shot Compose service 4.6 defines changes its command and nothing else — the topology,
  the ordering conditions and the image stay as they are.
  *What it does not buy:* nothing about container startup order. 4.6 records that either choice
  needs the same one-shot service in the same place.

- **FW17 — A bounded wait for the publisher confirm.** 7.7 feeds three `pika` parameters from
  10.4's single timeout, and between them they bound every phase of a publish but the last. Once
  the connection is established and the message is on the wire, the wait for the broker's confirm
  is bounded only by the heartbeat mechanism. `pika`'s checker runs on the connection's I/O loop,
  which **is** being serviced during that wait, and it aborts the stream after one check interval
  with no bytes received — `heartbeat + 5` seconds, so about 65 s against RabbitMQ's default
  60 s heartbeat, against the five seconds 10.4 configures. Read from `pika/heartbeat.py` in 1.4.4
  rather than estimated.
  *Why it cannot be repaired in place:* the calling thread is inside `pika` for the whole wait, so
  no code of ours runs to check a clock; and a blocking socket call cannot be interrupted from
  another thread without closing the socket underneath it, which 7.7 already records. The bound has
  to come from somewhere the caller can wait **interruptibly**.
  *Two routes, and they are not the same size.*
  1. **A dedicated publisher thread with an internal queue** — `pika`'s own recommendation, already
     rejected by 7.7 as machinery this scale does not justify. The request thread would wait on the
     queue with a timeout instead of on the socket, and so be released on schedule. **It frees the
     caller, not the resource:** the publisher thread stays stuck in the same call.
  2. **FW12's asynchronous runtime** — the wait becomes an awaitable the event loop abandons at a
     deadline, with nothing left behind. This closes it completely, and it is the second thing
     FW12 buys the publisher after removing 7.7's lock.
  *Why it is not in scope:* the failure it covers is a broker that accepts a connection and then
  goes silent, which is distinct from the two 7.5 names — an unreachable broker and a stale
  connection — and both of those the three parameters do bound. `Connection.Blocked`, the broker
  announcing that it is stalled, is bounded too. What is left is silence without announcement.
  Under 1.1's ceiling test no named DoD row degrades.
  *What would trigger it:* taking FW12, which closes it as a side effect; or a broker that stops
  being a container on the same Compose host, at which point a connection that establishes and then
  stops answering is no longer exotic.

- **FW18 — A single `advance` action in the CLI.** The fourth menu action (9.2) becomes one
  keystroke that moves the selected order to the next status, instead of a choice among the five
  values.
  *Why it is not in scope, and the reason is a fork rather than a cost:* the action needs somebody
  to know which status follows which, and there are exactly two places that knowledge can come from.
  **The client computes it** — 3.6 rejects this by name, because 5.1's sequence would then execute
  inside an adapter and the rule would exist in two components. **The API publishes it** — a
  `next_status` field on `OrderResponse`, which is a change to 6.1's nine keys with topic 6 closed.
  Neither is available to U12's gate; the second is the one worth taking.
  *What it would still not remove:* the five values stay selectable under either route, because
  5.2's `409` has to be reachable from the interface a reviewer is handed (1.2, step 11). `advance`
  is therefore an **additional** action rather than a replacement — it buys one keystroke on the
  legal path and does not make the menu smaller.
  *What 9.2 shipped instead:* the chain drawn with the current position marked. It carries the same
  information to the reader, it is display rather than a decision, and it needs no change to a
  closed contract.
  *Cost when taken:* by the second route, one field derived from the table 5.1 already owns plus the
  CLI reading it, and the rule stays in one place. By the first, one expression — and the rule in
  two.
