# Future work

What was deliberately not built, and what taking it would need.

Everything here was considered and consciously left out — nothing on this list was discovered
afterwards. The scope was fixed by one test: delete the thing, and does any graded requirement fail?
Where the answer was no, the candidate was recorded here instead of built.

The list is ordered by a different question: **would a competent engineer expect a production
service to have this, independent of this brief?** That asks about professional norms rather than
about this project, so the first section holds what a reviewer is most likely to go looking for. The
second section is a scan rather than a read — those entries are shorter because they are less
expected, not because they matter less. Every candidate appears in one section or the other.

---

## Most expected

### Authentication and authorisation

Every endpoint is open, and nothing identifies a caller. No notion of a user, a tenant or a role
appears anywhere in the brief, which also means there is nothing in the domain for a permission to
attach to. Adopting it starts with an identity model, and only then with deciding what each of the
five operations should demand.

### Continuous integration

No commit triggers anything. Every check such a pipeline would perform is already defined and
already performed — formatting, linting, type checking and the unit suite gate each commit, and the
integration scenarios execute during the launch. **What is absent is the automation, not the
verification.** Where it would live is also outside this repository: build servers get provisioned
once and shared between projects, so adopting this means pointing an installation that already
exists at the published remote, with the job description versioned alongside the source it builds.

### Schema migrations

The schema is generated from the model at every launch, so altering it means generating it again.
Migration tooling earns its place once a schema has to evolve underneath data that must be
preserved, and no such data exists here — storage is discarded with the containers, the schema is
built from nothing each time, and a second version never arises. Persistence is therefore the
precondition, and persistence arrives only with the isolated test environment below.

### Metrics and tracing

No correlation identifier follows a request from the API through the broker to the worker, and
nothing tallies assignments, retries or messages that exhausted their attempts. Logs answer what
became of a particular order; they stop being enough when the question shifts from that to how
frequently a thing occurs.

### An isolated end-to-end test environment

The suite exercises the same stack a reviewer drives by hand, rather than a duplicate with a private
database and broker. It is absent because the brief requires the launch itself to run the tests, and
anything invoked as a separate command is a separate command. Isolation would buy configuration
meant only for testing — a compressed retry budget turns an exhaustion scenario from a minute into
seconds — and it is also the sole route to durable storage, and through that to migrations.

### A relay for the outbox

Half of this already ships: each event is recorded in an outbox table within the very transaction
that changes the status, so no event is ever missing from the record. Absent is the process that
sweeps unsent rows, publishes them and stamps them as delivered. That is what stops an event from
being dropped when the broker happens to be unavailable.

### An asynchronous runtime

Everything blocks, so a request sitting on the database or the broker keeps its thread instead of
yielding it. The parallelism this would buy is not present — a single worker takes one message at a
time, one person uses the client, and the scenarios execute one after another. Nor is the change
additive: the transaction protocol, all repositories, all use cases and both composition roots
convert together, leaving only the domain layer as it stands.

### Order filtering and paging

Listing orders already works, newest first and uncapped. Narrowing by status and walking through
pages do not. Capping without paging was turned down as the worst of both, since it conceals rows
while offering no route to them; and in an environment emptied at every launch, the quantity that
would make paging necessary never builds up.

### A bounded wait for the publisher's confirmation

Three client timeouts derive from a single configured value, and between them they cover every stage
of publishing except the final one. Once the bytes are away, the delay before the broker
acknowledges is capped only by heartbeat detection — roughly 65 seconds where five were configured,
a figure taken from the client library's source rather than assumed. No local repair exists: the
publishing thread sits inside library code throughout, so nothing of ours is scheduled to observe a
deadline, and cancelling a blocking read from elsewhere means tearing down the socket beneath it.
Closing it takes either a thread dedicated to publishing, or the asynchronous runtime above.

*This entry sits here by exception.* Nobody carries a standing expectation about how long a
publisher waits to be acknowledged, so the ordering question above would place it in the section
below. It is kept here because it is the one entry demonstrating that a timeout was **measured
rather than assumed**, and that is worth more than its rank.

---

## Also considered

- **Dead-letter inspection and replay** — a way for an operator to view messages that have been
  parked and return them to circulation, without going through the broker's own management surface.
- **Structured order items** — items as typed objects, carrying a name, a quantity and toppings,
  in place of free-form strings. Nothing reads an order's contents today; whatever first needs to
  will need this first.
- **Driver endpoints beyond registration** — reading the roster, amending availability after
  sign-up, and exposing the orders a driver has already handled, which the database records
  and only a query is missing for.
- **Verified multi-consumer operation** — running more than one worker and showing under genuine
  contention that two cannot take the same driver, instead of resting on a uniqueness constraint
  plus an argument.
- **Standard message properties** — populating the broker's own identifier, type and timestamp
  fields from values the payload carries anyway, so tooling can group messages without decoding
  bodies.
- **Automated delivery completion** — an arrival raising an event of its own, so that the final
  status becomes something observed rather than something asserted at a keyboard.
- **Event-carried state transfer** — the dispatch event carrying a copy of the order rather than
  identifiers alone, worth taking only once the worker no longer shares a database with the API.
- **Persisted dispatch notifications** — writing dispatch records to the database rather than only
  emitting a log line, so the history can be queried instead of scrolled.
- **Delivery estimates and driver location** — choosing by distance or current load instead of
  taking whoever happens to be free. This is the genuinely hard form of the problem, and the brief
  deliberately steered around it.
- **A single advance action in the client** — one keystroke moving an order onward. It needs the API
  to publish which status comes next, so that the sequence stays defined in exactly one place.
