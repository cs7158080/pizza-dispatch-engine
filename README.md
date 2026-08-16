# pizza-dispatch-engine
Event-driven pizza order and delivery dispatch system built with REST API, message broker, worker service, and database.

## Running the system

Requires Docker with the Compose v2 plugin, version 2.24 or later — check with
`docker compose version`.

```
docker compose up
```

That builds the image on the first run, then starts PostgreSQL, RabbitMQ, a one-shot
service that creates the database schema, the API, and the dispatch worker. It needs no
setup and no `.env` file: every value has a working default.

The database and the broker are deliberately kept out of this stream, so what you see is
the API and the worker. Their logs are still collected — `docker compose logs postgres`.

The API is published on the host at **http://localhost:8000**:

- `GET /health` — `200` while the database is reachable, `503` otherwise
- `/docs` — the generated OpenAPI document, which is the contract in full

If port 8000 is already taken, copy `.env.example` to `.env` and set `API_HOST_PORT` to
something else. Nothing inside the environment changes; only the host side moves.

After changing source, rebuild with `docker compose up --build`. To stop and reset,
`docker compose down` — see *Persistence* below for what that discards.

## Local development

The system runs under Docker Compose; this section is only for working on the source.
Requires Python 3.12.

```
uv venv --python 3.12
.venv\Scripts\Activate.ps1          # PowerShell; source .venv/bin/activate elsewhere
uv pip install -e ".[dev]"
python -c "import pizza"
```

The package is installed rather than imported from the working directory, so `import pizza`
failing means the install did not happen.

Before every commit:

```
ruff format .
ruff check .
mypy src tests
pytest tests/unit
```

`requirements.txt` and `requirements-dev.txt` are generated from `pyproject.toml` and are
never edited by hand. After changing `dependencies` or the `dev` extra, regenerate both in
the same commit:

```
uv pip compile pyproject.toml --universal --python-version 3.12 -o requirements.txt
uv pip compile pyproject.toml --universal --python-version 3.12 --extra dev -o requirements-dev.txt
```

## Tests

Two sets, in two directories, run separately.

**`tests/unit`** — pure logic, no running system. `pytest tests/unit`, and it needs nothing
started.

**`tests/integration`** — five test functions covering four scenarios, driven entirely over
HTTP against a running stack. With the system up, from another terminal:

```
PIZZA_API_BASE_URL=http://localhost:8000 pytest tests/integration
```

| Scenario | What it covers |
|---|---|
| A complete order lifecycle | one order from `RECEIVED` to `DELIVERED`, assigned at `BAKING`, unchanged by the second event at `READY`, and its driver released at the end |
| Recovery when a driver registers | an order that reaches `BAKING` with no driver available waits, and is dispatched once one registers — with nothing asked of the system again |
| One driver, two orders | only one of the two is assigned, and the other is picked up when the first is delivered |
| API rule enforcement | a skipped or repeated status change is refused with `409`, and malformed input with `422` |

The suite registers its own drivers and leaves none behind, so it can be run repeatedly.
Running it against a stack you have been driving by hand may observe drivers you registered
yourself; `docker compose down` resets it.

## Configuration

Every value the services read comes from the environment, and `docker-compose.yml` supplies
each one with a working default — so `docker compose up` needs no setup and no `.env` file.

`.env.example` lists the whole surface. To change a value, copy it and edit:

```
cp .env.example .env
```

`.env` is not committed. Two variables in the example, `PIZZA_DATABASE_URL` and
`PIZZA_BROKER_URL`, are assembled by `docker-compose.yml` from the credentials above them, so
they are documented there rather than set there.

The credentials are local development defaults for an environment that `docker compose down`
destroys. They are not secrets, and a real deployment would supply its own from the
environment.

## Persistence

There are no named volumes. PostgreSQL and RabbitMQ write to their own container
filesystems, so `docker compose down` deletes the data along with the containers and the
next `docker compose up` starts from empty. Stopping with `Ctrl-C` keeps everything: the
containers still exist, and only `down` removes them.

That is deliberate. Every launch starts from a known state — no orders, no drivers — which
is what makes a run reproducible, and `docker compose down` is the whole reset.

To keep the data instead, add to `docker-compose.yml`:

```yaml
services:
  postgres:
    volumes:
      - postgres-data:/var/lib/postgresql/data
  rabbitmq:
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq

volumes:
  postgres-data:
  rabbitmq-data:
```

The reset then becomes `docker compose down -v`, because data in a named volume outlives
the containers.
