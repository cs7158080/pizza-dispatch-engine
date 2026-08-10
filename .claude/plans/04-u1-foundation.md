# U1 — Foundation · Implementation Plan

**Phase 3 of the planning protocol in `CLAUDE.md` §2, for the first unit in Part 4 of
`03-roadmap.md`.** Decisions are in `02-decisions.md`; nothing here decides anything that
belongs there. The plan is written to be tight enough that executing it contains no
judgement calls — where a call was needed and Phase 2 had not made it, it is recorded below
under *Readings*, not left to implementation.

**Gate.** U1's *Decided by* column reads topics 1, 2.8–2.10, 3.1, 3.3, 13.5 and 14. All are
`[decided]` in the status table of `02-decisions.md`. No open item is touched by this unit.

---

## 1. What this unit delivers

Part 4 gives U1 six things: repository skeleton, package layout, dependency management,
formatter/linter/type-checker configuration, `.gitignore` verification, and `docs/ai-log.md`.
After U1 the repository is an installable Python package that a checker can be pointed at.
It runs nothing yet — there is nothing to run.

`docs/ai-log.md` needs no work: 13.5 decided that the file already exists and defines itself,
and that rows are added when an event warrants one, not on a schedule.

## 2. What this unit deliberately does not deliver

Each line names the item that owns it, so nothing here is silence.

| Not built | Owner | Arrives in |
|---|---|---|
| `domain/`, `application/`, `infrastructure/`, `entrypoints/` under `src/pizza/` | 3.1 draws them; 3.2 established that the tree is a destination map, not a creation list, when it refused to create `domain/rules.py` empty | U3 onward |
| `[tool.pytest.ini_options]`, any pytest configuration | 12.7 — open | U4 |
| A mypy per-module override for `pika` | 2.8 — the list is confirmed on the first run, not guessed; nothing imports `pika` yet | U6 |
| `.env.example`, any settings object | 10.3, 10.2 | U2 |
| `Dockerfile`, `docker-compose.yml`, `.dockerignore` | 3.7, topic 11 | U9 |
| CI | 14.3 — decided against | — |
| README beyond a *Local development* section | 13.1 | U13 |

## 3. Branch, commits, and the merge

- **Branch:** `chore/u1-foundation`, cut from `main` (14.2).
- **Commits:** three ahead of the steps, then one commit per step (14.3, 14.4). Eight in total.
- **Merge:** one pull request, squash-merged, its title ending in `(#N)` (14.2, 14.3).
  The branch is not deleted (14.2).

| # | Type | Title |
|---|---|---|
| A | gate | `docs: settle 2.8 on ruff's default rule set plus import order` |
| B | gate | `docs: decide 2.9's upper version bound instead of borrowing it` |
| C | planning | `docs: plan the foundation unit, and hand pika's type gap to U6` |
| D | record | `docs: narrow FW4 to filters and paging, since GET /orders ships` |
| 1 | step | `build: declare the project and add the package skeleton` |
| 2 | step | `chore: turn on ruff's import rules and mypy strict` |
| 3 | step | `build: pin the dependency set in generated lock files` |
| 4 | step | `chore: ignore editor directories and re-verify the ignore rules` |

**None of A–D is a plan step.** 14.4 defines a step as a commit carrying §8's Definition of
Done, and 14.3 places a unit's planning ahead of the steps. That distinction is what makes
these commits possible at all: before step 1 there is no `src/` for `mypy` to check.

*Why A and B precede C, when 14.3 puts the Phase 3 document first.* They are Phase 2
amendments to U1's own gate topics, and C transcribes them — a plan cannot cite a decision the
history does not yet contain. 14.3's ordering separates **planning from implementation**, and
that separation is intact: nothing executable precedes C. Under the split 14.3 now draws, A and
B would normally travel on a `plan/u1-gate` branch and merge promptly; they ride here because
U1's gate had already closed when the ambiguities surfaced, and because a pull request per
four-line amendment costs more than it buys.

*Why D is here at all.* FW4 has nothing to do with U1 — it was found while reviewing this plan.
It rides on this branch by the developer's ruling, for the same reason, and the squash message
names it so that the merge does not swallow the fact that it was an incidental find.

## 4. The Definition of Done that applies to every step

14.7 fixes four commands for U1. They are run from the activated virtual environment at the
repository root, and each must exit zero **at every step commit**:

```
ruff format --check .
ruff check .
mypy src tests
python -c "import pizza"
```

The fourth is not filler. 3.3 chose src-layout so that the directory holding the package is
not itself importable; an `import pizza` that resolves proves the install happened.

Each step below adds its own checks on top of these four. A step is done when §8's six
conditions hold — with §8.2 read as the step's own verification section, since U1 introduces
no behaviour a test could name.

## 5. Readings — where this plan filled a silence

Recorded here rather than resolved silently (`CLAUDE.md` §2). **The boundary this section
respects:** a Phase 3 document may fill a silence Phase 2 left; it may not settle an ambiguity
inside a decided record. The form of ruff's rule set was the second kind — it turned on how
2.8's own words were read — so it went back to Phase 2 rather than being decided here, and 2.8
now fixes it. What remains below is only the first kind.

- **R-a — `[project] name = "pizza"`.** 3.3 rejected `src/` as the package partly because it
  "breaks the correspondence between distribution name and import name". 14.1 names the
  repository `pizza-dispatch-engine`. The import name wins, because that is the correspondence
  3.3's argument rests on. `version = "0.1.0"`.
- **R-b — `tests/unit/__init__.py` and `tests/integration/__init__.py`, empty.** 14.7 makes
  `mypy src tests` a Definition-of-Done command, and mypy fails on a directory holding no `.py`
  file; git tracks no empty directory either. The marker chosen is `__init__.py` rather than
  `.gitkeep` because it also keeps identically-named modules in the two directories from
  colliding once tests exist. 3.3 fixed the two directories; 12.7 owns only how they are run.
- **R-c — editable install.** The local environment is built with `uv pip install -e ".[dev]"`.
  A non-editable install would have to be repeated after every source edit, which is unusable
  from U3 onward. src-layout's guarantee survives it: `pizza` is still reached through the
  install, never through the working directory.

## 6. Steps

### Step 1 — Declare the project and add the package skeleton

**Files created**

- `pyproject.toml`, with exactly this content:

  ```toml
  [project]
  name = "pizza"
  version = "0.1.0"
  requires-python = ">=3.12"
  dependencies = [
      "fastapi",
      "pydantic>=2",
      "uvicorn",
      "sqlalchemy>=2.0",
      "psycopg[binary]",
      "pika",
      "httpx",
  ]

  [project.optional-dependencies]
  dev = [
      "pytest",
      "ruff",
      "mypy",
  ]

  [build-system]
  requires = ["setuptools>=68"]
  build-backend = "setuptools.build_meta"
  ```

  The seven runtime entries and the three dev entries are 2.10's approved list, unchanged and
  unextended. The bounds are 2.10's: `pydantic>=2` and `sqlalchemy>=2.0` carry semantics the
  decisions depend on; the rest are unbounded because nothing depends on a version. No
  `[tool.setuptools]` section — 2.9 recorded that setuptools detects src-layout unaided.
  The two conditional lines 2.10 names, `pydantic-settings` and `alembic`, are **not** added:
  they enter with the decision that requires them (10.2 in U2, 4.6 in U5).

- `src/pizza/__init__.py` — empty.
- `tests/unit/__init__.py` — empty.
- `tests/integration/__init__.py` — empty.

**Environment, built once and never committed**

```
uv venv --python 3.12
.venv\Scripts\Activate.ps1          # PowerShell; source .venv/bin/activate elsewhere
uv pip install -e ".[dev]"
```

`--python 3.12` is required: the interpreter on `PATH` is 3.11, and 2.9 fixed one version for
the local environment and the base image alike.

**README**, a new section appended:

````markdown
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
````

**Definition of Done**

1. The four files above exist, with the content stated.
2. The four commands of §4 exit zero.
3. `uv pip show pizza` reports `Name: pizza` and `Version: 0.1.0`.
4. `uv pip list` contains all seven runtime distributions and all three dev distributions
   (`psycopg[binary]` appears as `psycopg` and `psycopg-binary`).
5. `git status --short` lists exactly the four new files and the README change — proving
   `.venv/` and `*.egg-info/` are already ignored.

**Contingency, pre-decided so it is not improvised.** If `mypy src tests` reports
`Duplicate module named "pizza"`, the cause is the editable install exposing a second copy of
the package to mypy. The remedy is `mypy_path = "src"` and `explicit_package_bases = true`
added to the `[tool.mypy]` section in step 2 — and nothing else. In particular, dropping `src`
from the command is not permitted; 14.7 fixes the command.

---

### Step 2 — Turn on ruff's import rules and mypy strict

**File edited:** `pyproject.toml`, appended:

```toml
[tool.ruff.lint]
extend-select = ["I"]

[tool.mypy]
strict = true
```

Both lines are transcribed from 2.8, which fixes the `extend-select` form and records why
`select = ["E", "F", "I"]` is rejected: it enables `E501`, which `ruff format` cannot fix, so
two of §4's four commands would disagree about the same file. Everything else stays at its
default, so line length, target version and formatter settings are not written. `strict`
covers `src/pizza/` and `tests/` alike because §4's command names both paths.

**README**, appended to *Local development*:

````markdown
Before every commit:

```
ruff format .
ruff check .
mypy src tests
```
````

**Definition of Done**

1. `pyproject.toml` carries the two sections above.
2. The four commands of §4 exit zero.
3. **The configuration is proved live by two deliberate violations**, written to the session
   scratchpad so that no file enters the repository:
   - a file containing `import sys` then `import os` — `ruff check --config pyproject.toml <file>`
     must report `I001` (un-sorted imports) and `F401` (unused import);
   - a file containing `def f(x):` returning `x` — `mypy --config-file pyproject.toml <file>`
     must report `no-untyped-def`.

   Without this the step would assert only that the tools ran, which they did before it too.

---

### Step 3 — Pin the dependency set in generated lock files

**Commands, exactly as 2.9 wrote them:**

```
uv pip compile pyproject.toml --universal --python-version 3.12 -o requirements.txt
uv pip compile pyproject.toml --universal --python-version 3.12 --extra dev -o requirements-dev.txt
```

**Files created:** `requirements.txt`, `requirements-dev.txt`. Both are generated artifacts
that are committed and never hand-edited; 14.6 already verified that `.gitignore` tracks them.
Neither contains the project itself — 2.9's Dockerfile installs the dependencies from the
file and the package separately.

**README**, appended to *Local development*:

````markdown
`requirements.txt` and `requirements-dev.txt` are generated from `pyproject.toml` and are
never edited by hand. After changing `dependencies` or the `dev` extra, regenerate both in
the same commit:

```
uv pip compile pyproject.toml --universal --python-version 3.12 -o requirements.txt
uv pip compile pyproject.toml --universal --python-version 3.12 --extra dev -o requirements-dev.txt
```
````

**Definition of Done**

1. Both files exist and are tracked by git.
2. Each carries `uv pip compile`'s generated header naming the command that produced it, and
   the `--universal` resolution shows environment markers where a distribution is
   platform-specific.
3. All seven runtime distributions of 2.10 appear in `requirements.txt`; `pytest`, `ruff` and
   `mypy` appear in `requirements-dev.txt` and **not** in `requirements.txt`.
4. Running both commands a second time leaves `git status --short` clean — the files are
   derived, so a regeneration that changes them means the previous one was not.
5. The four commands of §4 exit zero.

---

### Step 4 — Ignore editor directories, and verify the ignore rules

**File edited:** `.gitignore`, two lines uncommented, per 14.6:

- `# .idea/` → `.idea/`
- `# .vscode/` → `.vscode/`

The surrounding template comments are left as they are: 14.6 decided the 224-line template is
not trimmed, because cutting it risks removing a line that was needed and buys nothing.

**Definition of Done**

1. `git check-ignore -v .idea/workspace.xml` and `git check-ignore -v .vscode/settings.json`
   both report `.gitignore` and the newly uncommented line.
2. The four results other decisions rest on are re-asserted, since Part 4 lists `.gitignore`
   *verification* as U1 content:

   | Path | Expected | Rests on |
   |---|---|---|
   | `.env` | ignored | 10.3 |
   | `.env.example` | **not** ignored | 10.3 |
   | `requirements.txt`, `requirements-dev.txt` | **not** ignored | 2.9 |
   | `.claude/settings.local.json` | ignored | 14.5 |
   | `.claude/settings.json`, `.claude/plans/` | **not** ignored | 14.5 |

3. The four commands of §4 exit zero.

---

## 7. Ordering, and why it is the only one available

- **1 before 2.** Configuring a checker requires the checker to be installed and a package for
  it to point at. Both arrive in step 1.
- **2 before 3.** Independent in fact — the lock is generated from `[project]` alone, which
  step 2 does not touch. Placed second so that steps 3 and 4 are verified at full strictness
  rather than at ruff's defaults.
- **4 last.** Depends on nothing. It closes 14.6 and carries the unit's verification duty, so
  it belongs at the end rather than in the middle of the build-up.

No step depends on a step after it, and no step needs a file a later step creates.

## 8. What U1 hands to the units after it

- **U2 (10.x):** `pyproject.toml` gains `pydantic-settings` if 10.2 chooses a typed settings
  object, and both lock files are regenerated in that same commit (2.9, 2.10).
- **U5 (4.6):** the same, for `alembic`.
- **U6 (2.7, 2.8):** the first `import pika` fails `mypy src tests`; the remedy is a per-module
  `ignore_missing_imports`, and this plan deliberately did not write it early. The obligation is
  recorded in 2.7, which is inside U6's planning gate. **It travels on this branch**, so it
  reaches `main` only when U1 merges — a session opening `plan/u6-gate` before then has to be
  told it exists.
- **U4 (12.7):** `tests/unit/` and `tests/integration/` exist as packages; how they are invoked
  separately is still open.
- **U9 (3.7, 11.9):** `requirements.txt` is the source-independent file 2.9 created for the
  cached dependency layer, and 2.10's note stands — `psycopg[binary]` has no musl wheel, so the
  base image is a `python:3.12` family and not Alpine.

## 9. After the merge

`main` satisfies 14.7's U1 row: `ruff format --check .`, `ruff check .`, `mypy src tests` and
`python -c "import pizza"` all exit zero on a clean clone once the environment of §6 step 1 is
built. The bar rises again at U4.
