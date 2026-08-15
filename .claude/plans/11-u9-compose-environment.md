# U9 — Compose environment · Implementation Plan

**Phase 3 of the planning protocol in `CLAUDE.md` §2, for the ninth unit in Part 4 of
`03-roadmap.md`.** Decisions are in `02-decisions.md`; nothing here decides anything that
belongs there. Where executing a step needed a call Phase 2 had not made, it is recorded below
under *Readings* rather than left to implementation.

**Gate.** U9's *Decided by* column reads 3.7, 11.1, 11.2 and 11.7–11.11, and every one is
`[decided]` — topic 11 closed across pull requests #18, #19 and #20. *Depends on* reads U7 (#15)
and U8 (#16), both merged. **There was nothing to decide at this gate**, which is why this unit
begins at Phase 3.

Three groups of open items are touched and none is decided here: 12.4 and 12.5 own the suite's
waiting helpers and its fixture, and 12.8 its data strategy — all U10's; 9.1, 9.4 and 9.5 own what
the CLI does once it exists — U12's; 13.1 to 13.4 own the assembled README — U13's.

---

## 1. What this unit delivers

Part 4 gives U9 the Dockerfiles, the compose services, the healthchecks and readiness ordering,
the volumes, the ports and the restart policies. It is the unit that turns a package into a system
that starts: after U8 every port had an implementation and nothing could be run.

**It writes no Python.** Five files, none of them under `src/` or `tests/`:

| File | What it holds | Fixed by |
|---|---|---|
| `Dockerfile` | two stages, two installs, a non-root user | 11.9, given there as complete code |
| `.dockerignore` | a deny list of ten entries | 11.9 |
| `docker-compose.yml` | six services, three healthchecks, the graph, the ports, the policies | 11.1, 11.2, 11.8, 11.9, 11.10, 11.11, 10.1 |
| `.env.example` | one added line, `API_HOST_PORT` | 11.8, which moved 10.3's count from ten to eleven |
| `README.md` | two sections — how to run it, and why nothing persists | `CLAUDE.md` §7; 11.7 requires the second by name |

**Six services, not seven, and the split is 11.1's own.** `tests` is written by U11: 12.9 fixes
its command and carries *Realised in:* U11, 12.7 gives its `conftest.py` to U10, and
`pytest tests/integration` against the empty package exits `5`. 14.7's U9 row was rewritten on
2026-08-14 for exactly this reason, and the bar it now states — every service the file defines
reaching the state 11.2's graph requires, and the stack staying up — is the bar this unit is held
to. There is no suite here and no PASS banner.

## 2. What this unit deliberately does not deliver

Each line names the item that owns it, so nothing here is silence.

| Not built | Owner | Arrives in |
|---|---|---|
| The `tests` service, its `command`, and its two edges to `rabbitmq` and `api` | 11.1, 11.2, 12.9 | U11 |
| 11.3's PASS/FAIL banner and 11.4's `--exit-code-from tests` README line | 11.3, 11.4 | U11 |
| `tests/integration/conftest.py`, `waiting.py`, and the four scenarios | 12.2, 12.4, 12.5, 12.7 | U10 |
| `pizza/entrypoints/cli/main.py` — the module the `cli` service's `command` names | 9.1, 9.4, 9.5 | U12 |
| The README's CLI section and 9.6's TTY note | 9.3, 9.6 | U12 |
| The assembled README, the sequence diagram, the assumptions register, the trade-off log | 13.1–13.4 | U13 |
| Named volumes, and `docker compose down -v` as the reset | 11.7 | not built (FW13, then FW16) |
| A published `5432`, `5672`, or the management UI on `15672` | 11.8 | not built |
| A declared network | 11.1 — Compose's default already resolves a service by name | not built |
| `stop_grace_period` and `stop_signal`, on any service | 11.2 | not built |
| A healthcheck on `worker`, or any HTTP surface to probe | 11.2, 8.8 | not built |
| A restart policy on `schema` or `cli` | 11.11 — a one-shot that restarts never completes | not built |
| `ruff` and `mypy` inside the compose run, or an eighth `lint` service | 12.10, 11.1 | not built |
| A digest-pinned base image, or a pinned `setuptools` build backend | 11.9 | not built |
| A second compose file, an overlay, an entrypoint script, an in-app wait loop | 9.3, 9.6, 11.2, FW13 | not built |
| Alembic, a `versions/` directory, any migration | 4.6 | not built (FW16) |
| A CI workflow | 14.3 | not built |

## 3. Branch, commits, and the merge

- **Branch:** `feat/u9-compose-environment`, cut from `main` at `41d9035` (14.2). It already exists
  and is clean.
- **Commits:** one planning commit, one amendment, then one commit per step (14.3, 14.4). Six in
  total, plus any further correction a step's own Definition of Done turns up — U8's D was found
  that way and this plan expects the same to be possible rather than planning for it.
- **Merge:** one pull request, squash-merged, `gh pr merge --squash` **without `--subject`**, so the
  number is appended to the title (14.2, 14.3). The branch is not deleted (14.2).

| # | Type | Title |
|---|---|---|
| P | planning | `docs: plan the compose environment` |
| A | amendment | `docs: keep the build tree out of the image` |
| 1 | step | `build: one image for every service that runs our code` |
| B | amendment | `docs: give 11.2's pg_isready hazard its measured size` |
| 2 | step | `feat: bring up the database, the broker, and the schema they hold` |
| 3 | step | `feat: launch the api and the dispatch worker` |
| 4 | step | `feat: define the cli service, reachable but never started by up` |
| C | amendment | `fix: say when a repeated dispatch event changed nothing` |
| D | amendment | `fix: stop pika narrating a successful reconnect at INFO` |

## 4. The Definition of Done that applies to every step

14.7's U2 row governs steps 1 to 4, and **U9 raises the bar**. The five commands are run from the
activated virtual environment at the repository root, and each must exit zero **at every step
commit**:

```
ruff format --check .
ruff check .
mypy src tests
python -c "import pizza"
pytest tests/unit
```

**14.7's U9 row enters force at step 2 and not at step 1**, because before `docker-compose.yml`
exists there is no service for it to describe. From step 2 on, every step also satisfies it for the
services the file defines *at that step* — which is what makes the row checkable four times instead
of once at the merge.

**How the row is checked, since it names a command that does not return** (R-e): `docker compose up`
is run in the foreground with its stream captured, and `docker compose ps -a` is polled until every
service holds its required state or a timeout expires. **No fixed sleep** (`CLAUDE.md` §5). Each
step below names the states it expects.

**Three notes so no step improvises.** **No dependency is added and neither lock file changes** —
this unit adds no Python and imports nothing. **No file under `src/` or `tests/` is touched**, so
`pytest tests/unit` collects eighteen at every step; step 3 states why `.env.example` does not move
that number. **Every step runs against a clean state** — `docker compose down` before each `up`, so
11.7's guarantee is the one being observed rather than a leftover container.

A step is done when §8's six conditions hold.

## 5. Readings — where this plan filled a silence

Recorded here rather than resolved silently (`CLAUDE.md` §2). The boundary is U1 §5's, restated in
every unit since: a Phase 3 document may fill a silence Phase 2 left; it may not settle an ambiguity
inside a decided record. Nothing here is of the second kind.

- **R-a — the `schema` service is supplied all six `PIZZA_` service variables, though 10.1's
  *Read by* column never names it.** Read from `config.py` and `entrypoints/schema/main.py` rather
  than from the table: the one-shot calls `load_service_settings`, and `ServiceSettings` declares six
  **required** fields, so a service given `PIZZA_DATABASE_URL` alone exits `1` on the other five
  before it opens a connection. 10.1's table records who *reads* a variable; this fills who must be
  *supplied* one, which no record states. 10.1 already accepts the same cost at one value per process
  — "the api carries the retry delay and the worker carries the publish timeout" — and the schema
  service is that shape at five.
  *Rejected — a settings class of its own for the one-shot:* it amends 10.1 and 10.2 to spare a
  service that lives for a second five environment lines.
- **R-b — the `cli` service is supplied `PIZZA_API_BASE_URL` and nothing else**, which is the same
  mechanism read in the other direction. `ClientSettings` also sets `extra="forbid"`, and the loader
  collects *every* `PIZZA_`-prefixed variable out of the environment — so a `cli` that inherited the
  six would fail validation on all six and never reach its first prompt. 10.1 states the split as the
  reason there are two classes; this is the rule that follows for the compose file.
- **R-c — the three identical `environment:` blocks are written out per service, with no YAML
  anchor.** 11.1 rejected an anchor for the `build:` blocks on the ground that it puts one
  indirection between a reader and what a service actually is. The same reason applies here and is
  stronger: 10.1 calls `docker-compose.yml` a transcription of its table and not a second original,
  and the transcription a reviewer checks against that table is the one they can read beside the
  service.
  *Rejected — `x-service-env: &service-env` merged with `<<:` into `schema`, `api` and `worker`:*
  twelve lines shorter, and it turns the check into a lookup. **Named as the closer call of the
  Readings:** twelve duplicated lines is a real cost, and the reversal is local to one file.
- **R-d — `${VAR:-default}` on the four tunables and the five vendor variables; a literal on the two
  assembled URLs.** 10.1's *Value Compose supplies* column reads as constants, but 10.3 makes `.env`
  an override surface that works **only** through interpolation — so a literal `INFO` would make
  `PIZZA_LOG_LEVEL=DEBUG` in a reviewer's `.env` do nothing, which contradicts that item's table. The
  two URLs are assembled from the five vendor variables and are not interpolated at their own names,
  which is exactly what `.env.example`'s prose comment already tells a reader.
- **R-e — the Definition of Done runs the command 14.7 names, not a shorter one.** `docker compose up`
  in the foreground, readiness read by polling `docker compose ps -a`.
  *Rejected — `docker compose up -d --wait`:* one line instead of a poll, and it is not the command
  the row names; it also has to be told what to make of a one-shot that exits, so what would be
  verified is partly the flag's behaviour rather than the system's.
- **R-f — `stdin_open` and `tty` are not written on `cli`.** 9.3 and 9.6 both rest on
  `docker compose run` allocating a TTY by default, which it does. Those two keys affect services
  started by `up`, and `profiles: ["cli"]` means this one never is — so they would be configuration
  with no reader.
- **R-g — the `cli` service ships with a `command` naming a module that does not exist yet.** 11.1
  assigns six services to U9 and names `tests` as the sole exception; 11.9 fixes the command;
  `pizza.entrypoints.cli.main` arrives in U12.
  **What this costs, named rather than left as "the service does not run":** `docker compose run
  --rm cli` is the one way 9.3 documents to reach the CLI — *"the README documents this one way and
  no other"* — and it is broken from this merge until U12's, across U10 and U11. `profiles: ["cli"]`
  bounds the damage precisely: nothing starts it, so no red container reaches the stream 11.3 wants
  clean, and the README stays silent rather than promising a menu, which is why there is no
  half-true sentence to write and withdraw.
  **The reading 14.7's U9 row needs, because its wording is wider than what `up` can reach.** The row
  says *"every service the file defines"*, and `cli` is defined and never started — so read
  literally, no state it could reach would satisfy the row. What the row measures is
  `docker compose up`, and a profiled service is outside that command by construction (9.3): the bar
  is every service `up` starts. Written here so a later unit reading the row literally does not
  conclude that U9 left it unmet.
  It is **checked in step 4's Definition of Done rather than left to be discovered**.
  *Rejected — deferring the whole service to U12:* it reopens a split re-confirmed at this gate.
  *Rejected — a README line saying the CLI is not built yet:* documentation of an absence, which
  U12 would delete two merges later; §2's *not delivered* table above is where an absence belongs.
- **R-h — where each README section lands.** §7 and §8.4 put documentation in the step that changes
  what it describes. 11.7 requires the compose comment to point at a README section, so
  `## Persistence` lands in **step 2**, with the comment that points at it. `## Running the system`
  lands in **step 3**, the first step after which `docker compose up` delivers a system a reviewer
  can drive; written at step 2 it would describe a stack with no API. Neither section mentions the
  suite or the CLI — U11 and U12 write their own lines, and 13.1 assembles the whole in U13.

## 6. Steps

### Step 1 — One image for every service that runs our code

**Files created:** `Dockerfile`, `.dockerignore`.

11.9 gives the file as complete code, including the layer order, the position of `USER app`, and
the two purpose comments that are the only comments it carries. Nothing here restates it; what this
step does is write it and check that the image it produces is the one 3.7 and 11.9 describe.

`.dockerignore` is 11.9's deny list, in that item's order: `.git`, `.venv`, `__pycache__/`, `*.pyc`,
`.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`, `.env`, `.claude/`, `docs/`.

**Definition of Done**

1. Both files exist, with the content 11.9 fixes and the two comments it names.
2. The five commands of §4 exit zero. **14.7's U9 row is not yet in force** (§4).
3. `pytest tests/unit` still collects eighteen. **No test is added, and the reason is written rather
   than left as a gap:** nothing here is Python, and what would be asserted — that the image builds
   and runs as `app` — is asserted by the commands below against the real build.
4. `docker build --target runtime -t pizza-runtime .` and `docker build --target test -t pizza-test .`
   both exit zero.
5. `docker run --rm pizza-runtime python -c "import pizza"` exits zero — 3.3's src-layout means this
   proves the install, not the copy. `docker run --rm pizza-runtime id -un` prints `app`, and so does
   the same command against `pizza-test`: 11.9's `USER root` in the test stage is a build-time state
   that must not survive it.
6. `docker run --rm pizza-runtime pytest --version` **fails** and `docker run --rm pizza-test pytest
   --version` succeeds — 3.7's whole reason for two stages, checked rather than assumed.
   `docker run --rm pizza-runtime ls /app` shows no `tests`; the same against `pizza-test` shows it.
7. `docker run --rm pizza-runtime ls -a /app` lists no `.env` and no `.git` — 11.9 calls `.env` the
   entry in the deny list that matters beyond build speed, and 10.3 has that file reach no container
   ever. The build output's context-transfer size is read once, to confirm `.venv` is excluded.
8. Read from the diff: `git status --short` lists exactly these two files; the base tag is
   `python:3.12-slim` with no digest; `USER app` appears after both installs in `runtime`; no
   third stage.

---

### Step 2 — Bring up the database, the broker, and the schema they hold

**File created:** `docker-compose.yml`. **File changed:** `README.md`.

Three services — `postgres`, `rabbitmq`, `schema` — and the parts of 11.1, 11.2 and 11.11 that
belong to them: the two vendor tags, `attach: false`, the two healthchecks with 11.2's intervals,
`restart: on-failure` on the pair and **absent** on the one-shot, and the one edge each.

```
postgres ──healthy──> schema (exits 0)
rabbitmq
```

The file carries **no `version:` key** (11.10), no `volumes:` key and no declared network (11.7,
11.1), and one explanatory comment above `services:` stating that the absence of named volumes is
deliberate and pointing at the README section step 2 also writes (11.7 — a comment, not
commented-out YAML).

`README.md` gains `## Persistence`, appended: what the absence means, what `docker compose down`
therefore does, and the exact `volumes:` lines to add if persistence is wanted, with the note that
the reset then becomes `down -v`. It states the guarantee — every launch starts from empty — without
claiming anything about a suite that does not run yet (R-h).

**Definition of Done**

1. The file exists with the three services stated, and the README carries the section.
2. The five commands of §4 exit zero.
3. `pytest tests/unit` still collects eighteen. **No test:** the file is data read by Compose, and
   the assertions available are the ones in 5 and 6 below, made against a running stack.
4. `docker compose config` exits zero and prints **no** warning — in particular no `version` warning
   (11.10) and no unset-variable warning, which together are what 10.3's `${VAR:-default}` form buys.
5. From a clean state (`docker compose down` first), `docker compose up` brings `postgres` and
   `rabbitmq` to `healthy` and `schema` to `exited (0)`, and the stack stays up. Read from
   `docker compose ps -a`, polled (R-e). **This is 14.7's U9 row for the services this step
   defines.**
6. `docker compose exec postgres psql -U pizza -d pizza -c '\dt'` lists `orders`, `drivers` and
   `outbox` — the schema service did what 4.6 says it does. A second `docker compose up` after
   `down` reaches the same state, and a second `up` **without** `down` re-runs the one-shot to a
   no-op exit `0`, which is the behaviour 4.6 wrote so U5 would not choose.
7. `attach: false` is checked rather than assumed (11.1): neither vendor service writes into the
   `up` stream, while `docker compose logs postgres` returns its output.
8. **`pg_isready -h 127.0.0.1` is checked in both directions, because it is the one detail 11.2
   calls "the one that would have bitten".** The first `up` from cold — no container, no image
   layer cache for the database's initialisation — brings `schema` to exit `0` with **no connection
   error in its log**. Then, once, with `-h 127.0.0.1` removed: the check passes over the temporary
   server the postgres image runs during first initialisation, `schema` starts too early, and 4.6
   gives it nothing to retry with. The flag is restored before the commit. Observing the failure is
   what separates this from inheriting a claim.
9. Read from the diff: no `version:`, no `volumes:`, no `networks:`; `restart: on-failure` on the
   two vendor services and no `restart` key on `schema` (11.11 — a one-shot that restarts never
   satisfies `service_completed_successfully`); the credentials appear only as `${…:-pizza}` and
   nowhere as a literal; `schema` carries all six `PIZZA_` service variables (R-a).

---

### Step 3 — Launch the api and the dispatch worker

**Files changed:** `docker-compose.yml`, `.env.example`, `README.md`.

Two services, and with them the rest of 11.2's graph that U9 owns:

```
postgres ──healthy──> schema ──completed 0──> api
                                        └───> worker
rabbitmq ──healthy───────────────────────────> worker
```

`api` carries 11.2's `python -c` healthcheck with its 5/5/12/10 intervals, 11.8's single published
port `${API_HOST_PORT:-8000}:8000`, `restart: on-failure`, and 11.9's `uvicorn` command. `worker`
carries 11.9's module command, `restart: on-failure`, no healthcheck and no port. Both carry all six
`PIZZA_` service variables and **not** `PIZZA_API_BASE_URL` (R-b).

`.env.example` gains one line, `API_HOST_PORT=8000`, with a comment saying Compose alone reads it —
11.8's Compose-only variable, which is why it carries no `PIZZA_` prefix and sits outside 10.3's
drift test. This is the eleventh active line 10.3 already records.

`README.md` gains `## Running the system`, inserted after the title: the Compose v2.24 prerequisite
(11.10), `docker compose up` and what it starts, where the API is published and how `API_HOST_PORT`
is overridden through `.env` rather than through a shell prefix (A21, 9.6), `--build` after a source
change (11.9), and `docker compose down`.

**Definition of Done**

1. The three files are as stated.
2. The five commands of §4 exit zero. `pytest tests/unit` still collects eighteen — `.env.example`
   gains a line with no `PIZZA_` prefix, which `test_env_example.py` ignores by construction, and
   this is **checked by running it** rather than reasoned from the regex.
3. From a clean state, `docker compose up` reaches: `postgres` and `rabbitmq` `healthy`, `schema`
   `exited (0)`, `api` `healthy`, `worker` `running` — and the stack stays up. **This is 14.7's U9
   row nearly whole**, and it is the row's first satisfaction against every service `up` starts.
4. The worker's **restart count is `0`** and `event=worker_ready` appears once. 8.8 handed 11.2 the
   prediction that without the broker edge a reviewer meets a wall of `pika` errors and a mounting
   restart count on the first `up`; 11.2 took the edge to prevent it, and this is where that is
   observed rather than argued.
5. The image is built **once**, not three times — 11.1's stated reason for the shared `image:` tag,
   read from the build output.
6. From the host: `GET http://localhost:8000/health` answers `200`, and `/docs` renders the OpenAPI
   document — 2.3's claim, which 11.8 published the port to keep true. With `API_HOST_PORT=8080` in
   a temporary `.env`, the API answers on `8080` and not on `8000`; the file is deleted afterwards
   and `git status --short` is clean (10.3 — `.env` is ignored).
7. **The system is driven end to end by hand, once**, over HTTP: place an order, advance it to
   `BAKING`, and watch the worker log `event=no_driver_available … attempt=1`; register a driver, and
   within one retry cycle watch `event=dispatch_notification` name it; re-read the order and see the
   nested driver and `ASSIGNED`. **This is a check, not a test** — 12.3 gives every assertion on this
   path to U10, and this step only establishes that the path exists at all before a suite is written
   against it.
8. Read from the diff: `api` and `worker` each carry the six service variables and no
   `PIZZA_API_BASE_URL`; one `ports:` entry in the whole file and it is the api's (11.8); no
   healthcheck on `worker` (11.2, 8.8); `api` has no edge to `rabbitmq` — the asymmetry 7.1 and 7.6
   made deliberate; both commands are list form (11.9).

---

### Step 4 — Define the cli service, reachable but never started by `up`

**File changed:** `docker-compose.yml`.

The sixth and last service U9 writes: `profiles: ["cli"]` (9.3), `depends_on` on the api's health
(11.2), 11.9's module command, `PIZZA_API_BASE_URL` alone (R-b), no `restart` key (11.11), no `tty`
or `stdin_open` (R-f). The module it names arrives in U12, and R-g states why the service is written
here regardless.

**No README change.** The command that would document it does not work yet, and a README that
promised a menu would be false until U12 (R-h).

**Definition of Done**

1. The service is as stated, and `docker-compose.yml` now defines six services.
2. The five commands of §4 exit zero.
3. `docker compose up` reaches step 3's state unchanged and creates **no** `cli` container —
   `docker compose ps -a` has no row for it. 9.3's whole reason for `profiles` is that a service
   started at `up` with no terminal reads EOF and prints a failed container into the stream; this is
   where that is checked. **14.7's U9 row holds for every service `up` starts**, which is the bar
   this unit is merged on and the reading R-g writes down.
4. `docker compose config` omits `cli`; `docker compose --profile cli config` includes it.
5. `docker compose run --rm cli python -c "import os; print(os.environ['PIZZA_API_BASE_URL'])"`
   prints `http://api:8000` — the service builds, joins the network, and carries the one variable
   `ClientSettings` accepts.
6. `docker compose run --rm cli` fails with `No module named pizza.entrypoints.cli.main`. **This is
   the expected state until U12** (R-g), and it is written into the Definition of Done so that the
   gap is a checked fact rather than something a later session discovers.
7. Read from the diff: `profiles: ["cli"]`; no `restart`, no `tty`, no `stdin_open`, no `ports`; the
   `environment:` block holds one variable; `depends_on` names `api` with `condition:
   service_healthy` and nothing else.

## 7. Ordering, and where it is free

One edge is forced and the rest is the graph's own shape.

- **1 → 2, 3, 4:** every service that runs our code names `build: target:` and an image tag, so no
  compose service can start before the `Dockerfile` exists.
- **2 → 3:** `api` and `worker` both wait on `schema`, which waits on `postgres`. A step 3 written
  first would define services whose `depends_on` names nothing.
- **3 → 4:** `cli` waits on the api's health.

Steps 2, 3 and 4 could in principle be one commit — the file is one artifact — and they are three
because each adds a level of 11.2's graph that can be observed on its own, which is what makes
14.7's U9 row checkable four times instead of once. **No step depends on a step after it.**

## 8. What U9 hands to the units after it

- **U10 (12.3, 12.5):** an environment the suite can drive. The API answers at `http://api:8000`
  from inside the network — the default `PIZZA_API_BASE_URL` already carries — and 11.7's clean start
  is now a property of the delivered file rather than a promise.
- **U11 (11.1, 11.2, 12.9):** one service to add into a file that already defines six, with
  `build: target: test` and `image: pizza-test` — a stage this unit already built and checked — plus
  its two edges, `rabbitmq: service_healthy` and `api: service_healthy`, and no `restart` key.
  Everything about them is stated in 11.2; U11 transcribes.
- **U11 (14.7):** the U9 row is satisfied on `main`. The U11 row adds the suite, the PASS summary and
  a zero exit.
- **U12 (9.3, 9.6):** the `cli` service exists, builds, joins the network and is given its one
  variable; it fails on the missing module alone. **U12 writes Python and touches no YAML** — and
  the README's CLI section, including 9.6's TTY note for Git Bash, is U12's first documentation.
- **U13 (13.1, 13.4):** two README sections to fold into the assembled document, and three trade-offs
  now demonstrable rather than argued — 11.7's disposability, 4.6's `create_all` in place of
  migrations, and 12.10's two on-demand check commands.

## 9. After the merge

`main` satisfies 14.7's **U9** row: the five commands of §4 exit zero on a clean clone with eighteen
unit tests, and `docker compose up` brings every service the file defines to the state 11.2's graph
requires and stays up. The bar rises once more, at U11.

The system runs. Two processes, a database, a broker and a schema come up in one command, an order
placed over HTTP reaches a worker through the broker and comes back with a driver, and nothing under
`src/` changed to make it happen — which is what 3.1's dependency rule was for. What is still
missing is a suite that proves it without a person watching, and a menu to drive it from.
