# U2 — Configuration · Implementation Plan

**Phase 3 of the planning protocol in `CLAUDE.md` §2, for the second unit in Part 4 of
`03-roadmap.md`.** Decisions are in `02-decisions.md`; nothing here decides anything that
belongs there. The plan is written to be tight enough that executing it contains no judgement
calls — where a call was needed and Phase 2 had not made it, it is recorded below under
*Readings*, not left to implementation.

**Gate.** U2's *Decided by* column reads topic 10 alone. All five items — 10.1 to 10.5 — are
`[decided]` in the status table of `02-decisions.md`, settled on `plan/u2-gate` and merged as
pull request #5 before this document was written, which is the split 14.3 draws between a
unit's Phase 2 and its Phase 3. U1 is merged, so the dependency is real rather than nominal.
No open item is touched: 8.7 owns the log's *format* and this unit supplies only its level;
7.1 owns who declares the broker topology and this unit supplies only the delay it needs;
11.10 owns the Compose version floor and this unit writes no Compose file.

---

## 1. What this unit delivers

Part 4 gives U2 three things: a typed settings object, `.env.example`, and configuration
validation at startup. After U2 the repository holds one module that turns a mapping of
environment strings into two frozen, typed objects — and refuses to produce either from an
environment that is incomplete, mistyped, or carries a variable nobody declared. Beside it
sits the committed catalogue of that surface, and a test that keeps the catalogue and the code
from disagreeing.

The unit still runs nothing. There is no entrypoint to load the settings, so the third item —
"validation at startup" — is delivered as **the mechanism and the contract, not the moment it
fires**: `ConfigurationError`, its message, and the rule that loading is a call made once by a
composition root. The call sites arrive with the entrypoints in U7, U8 and U12.

## 2. What this unit deliberately does not deliver

Each line names the item that owns it, so nothing here is silence.

| Not built | Owner | Arrives in |
|---|---|---|
| `docker-compose.yml`, and the `environment:` blocks that supply every value in 10.1 | topic 11; 10.3 fixes the mechanism as `${VAR:-value}` | U9 |
| The call itself — `load_service_settings(os.environ)` in a composition root, and turning a `ConfigurationError` into a non-zero exit | 10.2 places it at the composition root; §8 below states the contract both services owe | U7, U8, U12 |
| Logging configuration — handler, format, and where the level is applied | 8.7 — open | U7, U8 |
| Any *use* of a setting: the engine, the publisher, the HTTP client | 2.5, 7.7, 3.6 | U5, U6, U12 |
| `.env` itself | 10.3 — ignored by git, and never committed | never |
| `[tool.pytest.ini_options]`, and how the two test directories are invoked separately | 12.7 — open | U4 |
| A mypy per-module override for `pika` | 2.8 — nothing imports `pika` yet | U6 |
| README beyond a *Configuration* section | 13.1 | U13 |

## 3. Branch, commits, and the merge

- **Branch:** `feat/u2-configuration`, cut from `main` at `68d6353` (14.2).
- **Commits:** one gate commit, one planning commit, then one commit per step (14.3, 14.4).
  Four in total.
- **Merge:** one pull request, squash-merged, its title ending in `(#N)` (14.2, 14.3).
  The branch is not deleted (14.2).

| # | Type | Title |
|---|---|---|
| A | gate | `docs: merge a Phase 2 gate when its contract is needed, not promptly` |
| B | planning | `docs: plan the configuration unit` |
| 1 | step | `feat: turn the environment into a typed, validated settings boundary` |
| 2 | step | `chore: catalogue the configuration surface in .env.example` |

**Neither A nor B is a plan step**, and the distinction has a consequence here that it did not
have in U1: 14.4 defines a step as a commit carrying §8's Definition of Done, and §4 below now
includes `pytest tests/unit`. At A and B no test exists, and `pytest` exits 5 — "no tests
collected" — rather than 0. The fifth command therefore joins at step 1, the commit that creates
the first test.

*Why A is here at all.* It belongs to neither topic 10 nor U2: it amends 14.3, and it was found
while reviewing this document. It rides on this branch by the developer's ruling — the same
ruling and the same reason that put D on U1's branch — rather than on a gate branch of its own,
and the squash message will name it so the merge does not swallow the fact that it was an
incidental find. **It precedes B** because B cites it, and a plan cannot cite a decision the
history does not yet contain; that is U1's ordering rule, applied again.

*What A changes, in one line, because it governs this branch's own merge:* a gate branch is now
merged when its contract is first needed rather than promptly. **And it carries a live
consequence:** the amendment reaches `main` only when U2 merges, while `plan/u6-gate` and
`plan/u7-gate` are open in parallel worktrees right now and will choose their merge points under
the old rule unless they are told. U1 §8 had to record exactly this kind of hand-off, and it is
recorded here for the same reason.

**U2's own Phase 2 amendments are not here.** Topic 10, 2.10's dropped conditional and 14.7's
moved row travelled on `plan/u2-gate` and reached `main` as #5, before this document was
written. That is what 14.3's split is for, and U2 is the first unit to use it as designed.

## 4. The Definition of Done that applies to every step

14.7 fixes five commands for U2, the fifth having moved here from U4 in #5. They are run from
the activated virtual environment at the repository root, and each must exit zero **at every
step commit**:

```
ruff format --check .
ruff check .
mypy src tests
python -c "import pizza"
pytest tests/unit
```

`python -c "import pizza"` is not filler, for two reasons now. 3.3 chose src-layout so that an
import resolves only through the install; and 10.2 forbids loading settings at import time, so
an `import pizza` that succeeds with an empty environment is also the proof of that rule.

Each step below adds its own checks on top of these five. A step is done when §8's six
conditions hold.

## 5. Readings — where this plan filled a silence

Recorded here rather than resolved silently (`CLAUDE.md` §2). **The boundary this section
respects,** inherited from U1 §5: a Phase 3 document may fill a silence Phase 2 left; it may
not settle an ambiguity inside a decided record. Anything of the second kind went back to the
gate branch before this document existed.

- **R-a — `ConfigurationError`, a plain `Exception` subclass in `config.py`.** 10.2 fixed that
  `ValidationError` is wrapped so the message names the environment variable rather than the
  field, and left the type unnamed. It is **not** a domain error: 5.2's typed errors live in
  `domain/errors.py` and describe business outcomes, while this describes a process that cannot
  start. Its message is one line per fault, each `PIZZA_<NAME>: <reason>`, under a single
  `invalid configuration:` header — so a reader of `docker compose up` sees every fault at once
  and can fix them in one pass.
- **R-b — the loader takes the mapping and has no default argument.** `load_service_settings(env)`
  rather than `load_service_settings(env=os.environ)`. With a default, any module could load
  settings by calling with no arguments, which is the module-level instantiation 10.2 forbids,
  arriving by a different door. The composition root passes `os.environ` explicitly.
- **R-c — one generic private loader, not two.** `_load(model, env)` carries the collect-and-wrap
  logic once and the two public functions are one line each. Two copies of six lines would put
  the same rule in two places, which `CLAUDE.md` §3 forbids for exactly this reason.
- **R-d — the `api_base_url` normaliser is a `field_validator`.** 10.1 fixed the behaviour —
  an `http(s)` scheme required, a trailing slash stripped — and not the mechanism. A
  `field_validator` keeps the rule inside the declaration, where 2.3's argument puts validation.
- **R-e — the drift test locates `.env.example` by path, not by fixture.**
  `Path(__file__).parents[2] / ".env.example"`, since 3.3 puts `tests/` at the repository root.
  No environment variable, no `conftest.py`, no packaging trick.
- **R-f — a container receives exactly the variables its class declares.** This follows from
  `extra="forbid"` (10.2) plus 10.1's *Read by* column, and is stated because it is a real
  constraint on U9 rather than a note: an api container that also carried `PIZZA_API_BASE_URL`
  would **fail to start**, because `ServiceSettings` does not declare it. The two variable sets
  are disjoint by design, which is what turns *Read by* from documentation into a contract. If
  a later unit needs a variable in a process that does not declare it — 12.4 sizing a timeout
  from the retry delay is the live candidate — the field is added to that class, in the open,
  rather than the variable being sprinkled into a service.

## 6. Steps

### Step 1 — Turn the environment into a typed, validated settings boundary

**File created:** `src/pizza/config.py`, with exactly this content:

```python
"""The configuration boundary: environment strings turned into typed settings.

10.1 registers the variables; 10.2 fixes this module's shape and placement. No module
under domain/ or application/ imports it, and nothing here reads the environment at
import time — loading is a call, made once by a composition root.
"""

from collections.abc import Mapping
from typing import Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

_PREFIX = "PIZZA_"

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class ConfigurationError(Exception):
    """The environment does not describe a usable configuration."""


class ServiceSettings(BaseModel):
    """Read by the api and the worker (10.1)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    database_url: str = Field(min_length=1)
    broker_url: str = Field(min_length=1)
    log_level: LogLevel
    broker_publish_timeout_seconds: float = Field(gt=0)
    dispatch_retry_delay_seconds: int = Field(gt=0)
    dispatch_max_retries: int = Field(ge=1)


class ClientSettings(BaseModel):
    """Read by the CLI and the integration suite (10.1)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    api_base_url: str

    @field_validator("api_base_url")
    @classmethod
    def _without_trailing_slash(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            raise ValueError("must start with http:// or https://")
        return value.rstrip("/")


_Settings = TypeVar("_Settings", bound=BaseModel)


def _load(model: type[_Settings], env: Mapping[str, str]) -> _Settings:
    declared = {
        key.removeprefix(_PREFIX).lower(): value
        for key, value in env.items()
        if key.startswith(_PREFIX)
    }
    try:
        return model.model_validate(declared)
    except ValidationError as error:
        raise ConfigurationError(_describe(error)) from error


def _describe(error: ValidationError) -> str:
    faults = [
        f"{_PREFIX}{'_'.join(str(part) for part in item['loc']).upper()}: {item['msg']}"
        for item in error.errors()
    ]
    return "invalid configuration:\n" + "\n".join(faults)


def load_service_settings(env: Mapping[str, str]) -> ServiceSettings:
    return _load(ServiceSettings, env)


def load_client_settings(env: Mapping[str, str]) -> ClientSettings:
    return _load(ClientSettings, env)
```

Every element is transcribed: the field list and its bounds are 10.1's table, `extra="forbid"`
and `frozen=True` and the prefix collector are 10.2, and the five log levels are 10.4. **No
field carries a default value** — that is 10.1's rule that Compose is the only place a default
is written, made checkable in this file.

**File created:** `tests/unit/test_config.py`, four tests. Each is chosen by the failure it
would catch, per `CLAUDE.md` §5, and each carries that reason as its docstring.

| Test | What it asserts | Why it earns its place |
|---|---|---|
| `test_complete_environment_loads` | both classes load from a mapping that also holds unrelated variables (`PATH`); `dispatch_max_retries` is `8` as an `int`; `api_base_url` given with a trailing slash comes back without one | the two silent transformations. Coercion failing would surface as a type error deep in U6 or U8; a surviving trailing slash as a double slash in a URL built in U10 or U12 |
| `test_missing_variable_names_it` | a mapping without `PIZZA_DATABASE_URL` raises `ConfigurationError` whose message contains `PIZZA_DATABASE_URL` | this *is* "validation at startup". A failure that names the field rather than the variable sends the reader to the wrong file, and one that names nothing sends them to the source |
| `test_unknown_prefixed_variable_is_rejected` | `PIZZA_LOG_LEVL=DEBUG` alongside a complete environment raises | 10.2 rejected `pydantic-settings` **on this behaviour**. If it does not hold, that decision's justification is void and the record must be reopened, so the test guards a rejection as much as a feature |
| `test_out_of_range_values_are_rejected` | `PIZZA_DISPATCH_MAX_RETRIES=0`, and `PIZZA_LOG_LEVEL=verbose`, each raise | 10.4's per-field bounds. A cap of zero would mark an order `FAILED` on the first rejection with no retry at all, which no interface would report as a configuration fault |

Each test passes a literal `dict`; none touches `os.environ`, so order and process state cannot
affect them (`CLAUDE.md` §5).

**Definition of Done**

1. The two files exist, with the content stated.
2. The five commands of §4 exit zero.
3. `python -c "import pizza.config"` succeeds **with no `PIZZA_` variable set** — the executable
   proof of 10.2's rule that nothing loads at import time.
4. `src/pizza/config.py` contains no host name, port, credential, or field default. This is
   A26 and `CLAUDE.md` §3 checked in the file where they could be broken.

---

### Step 2 — Catalogue the configuration surface in `.env.example`

**File created:** `.env.example`, with exactly this content:

```
# Configuration example. Every value below is already applied as a default by
# docker-compose.yml, so `docker compose up` needs no .env at all. Copy this file
# to .env to override any of them; .env is never committed.
#
# PIZZA_DATABASE_URL and PIZZA_BROKER_URL are read by the api and the worker, but
# docker-compose.yml assembles them from the five values below — setting them here
# has no effect.

# Read by the postgres image, and by Compose to assemble PIZZA_DATABASE_URL
POSTGRES_USER=pizza
POSTGRES_PASSWORD=pizza
POSTGRES_DB=pizza

# Read by the rabbitmq image, and by Compose to assemble PIZZA_BROKER_URL
RABBITMQ_DEFAULT_USER=pizza
RABBITMQ_DEFAULT_PASS=pizza

# Read by the api and the worker
PIZZA_LOG_LEVEL=INFO
PIZZA_BROKER_PUBLISH_TIMEOUT_SECONDS=5
PIZZA_DISPATCH_RETRY_DELAY_SECONDS=8
PIZZA_DISPATCH_MAX_RETRIES=8

# Read by the CLI and the test suite
PIZZA_API_BASE_URL=http://api:8000
```

Ten active lines and no commented assignment, per 10.3: the two assembled URLs are named in
prose because a `# NAME=value` line in an env file reads as an invitation to uncomment, and
uncommenting these would change nothing. The values are 10.5's credentials and 10.4's
tunables, unchanged.

**File created:** `tests/unit/test_env_example.py`, one test.

It scans every `PIZZA_[A-Z_]+` token in `.env.example` — comment lines included — and asserts
that set equals `{_PREFIX + name.upper() for name in ServiceSettings.model_fields} |
{... ClientSettings ...}`. It covers the drift 13.6 warns about, in both directions: a field
renamed in `config.py` and not in the file, a variable documented that nothing reads, and a new
field added without an example. The vendor variables carry no `PIZZA_` prefix and are outside
the comparison by construction.

**README**, a new section appended:

````markdown
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
````

**Definition of Done**

1. Both files exist, with the content stated, and the README carries the section.
2. The five commands of §4 exit zero, and `pytest tests/unit` now collects five tests.
3. **The drift test is proved live**, in the session scratchpad so that no file enters the
   repository in a broken state: a copy of `.env.example` with `PIZZA_DISPATCH_MAX_RETRIES`
   deleted, and a second copy with `PIZZA_DISPATCH_MAX_RETRY` in its place, must each make the
   test fail. Without this the step asserts only that the test ran, which it did before it too.
4. `git status --short` lists exactly the two new files and the README change — `.env.example`
   is tracked, which 14.6 already verified and this step re-asserts by fact.

---

## 7. Ordering, and why it is the only one available

- **1 before 2.** Step 2's drift test derives its expected set from `ServiceSettings` and
  `ClientSettings`, so the classes must exist. Step 1 depends on nothing but U1.
- **Nothing follows 2.** The unit has no third step: Part 4's third item, validation at
  startup, has no call site until U7, and §2 records that rather than inventing one here.

No step depends on a step after it, and no step needs a file a later step creates.

## 8. What U2 hands to the units after it

- **U5 (2.5, 4.6):** `settings.database_url` is a `str`, so 2.5's
  `create_engine(settings.database_url, pool_pre_ping=True)` stands with no conversion. If 4.6
  chooses Alembic, it reads that same variable rather than one of its own (10.1).
- **U6 (7.1, 8.2):** `settings.broker_url` is a `str` for `pika.URLParameters`, and
  `dispatch_retry_delay_seconds` is in **seconds** — the wait queue's `x-message-ttl` is in
  milliseconds, so the declaration multiplies by 1000. Which process declares the topology, and
  therefore reads the delay, is still 7.1.
- **U7 and U8 — one contract both owe, so the two services cannot diverge:** the composition
  root calls the loader as its first action, and on `ConfigurationError` writes the message to
  standard error and exits non-zero. Nothing catches it further in; a process without a usable
  configuration must not reach the point of serving or consuming. U8 additionally owns the
  cap's arithmetic, whose meaning 10.4 fixed: `dispatch_max_retries` counts redeliveries after
  the first attempt.
- **U9 (10.1, 10.3):** `.env.example` is the transcription source for the `environment:` blocks,
  and each service receives **exactly** the variables its settings class declares — R-f explains
  why an extra one is a startup failure rather than a harmless surplus. A step in U9 checks the
  Compose file against 10.1's table.
- **U10 and U12 (9.3, 12.4):** `api_base_url` is guaranteed to carry a scheme and no trailing
  slash, so `f"{base}/orders"` is safe. If 12.4 sizes its polling timeout from the retry delay,
  the field is added to `ClientSettings` and the variable to the tests service together.
- **U4 (12.7):** `tests/unit/` now holds five real tests, so `pytest tests/unit` is part of the
  Definition of Done from here on. How the two directories are invoked separately is still open.

## 9. After the merge

`main` satisfies 14.7's U2 row: `ruff format --check .`, `ruff check .`, `mypy src tests`,
`python -c "import pizza"` and `pytest tests/unit` all exit zero on a clean clone once the
environment of U1's §6 step 1 is built. The bar rises again at U9.
