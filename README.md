# pizza-dispatch-engine
Event-driven pizza order and delivery dispatch system built with REST API, message broker, worker service, and database.

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
