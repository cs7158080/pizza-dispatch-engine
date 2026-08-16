# How this repository was built

This project was built with an AI coding agent, under a written working agreement that was fixed
before any code existed. The agreement, the plan it produced, and the record of where the agent was
overruled are all committed. This file is a guide to them.

Reading it is optional. The [README](../README.md) stands on its own.

## The agreement

[`CLAUDE.md`](../CLAUDE.md) is the process, and it is the first file to read. Two of its rules
shaped everything else: nothing is written without approval of that specific change, and no
implementation begins before planning is complete and approved. Planning runs in four ordered
phases — an inventory of what must be decided, the decisions, a numbered implementation plan, then
an approval gate.

The agreement was written first and edited since only by explicit decision. It is not a description
of what happened; it is what the work was held to.

## The plan

[`.claude/plans/`](../.claude/plans/) holds the output of those phases.

| File | Phase | What it holds |
|---|---|---|
| [`01-inventory.md`](../.claude/plans/01-inventory.md) | 1 | the questions, never the answers — plus the assignment restated as numbered requirements, the ambiguities found in it, and a map of cross-cutting failure modes |
| [`02-decisions.md`](../.claude/plans/02-decisions.md) | 2 | every question resolved: the decision, why, and what was rejected and why. It is the only original — the README's trade-offs are a summary of it |
| [`03-roadmap.md`](../.claude/plans/03-roadmap.md) | — | the build order in thirteen units, and the future-work list every out-of-scope candidate was sent to |

Phase 3 adds one implementation plan per unit, named for the unit it belongs to. Each states what
the unit delivers, what it deliberately does not, one commit per step, and a Definition of Done per
step that says how it was verified. Where executing a step needed a judgement the decisions had not
made, the plan records it as a named reading rather than leaving it to whoever typed the code.

Items are numbered and cross-referenced throughout — a record names what constrains it and what it
constrains, so a change can be traced to everything it touches.

## Where the agent was overruled

[`docs/ai-log.md`](ai-log.md) records what the agent proposed and did not get. A row is written when
a proposal was rejected or materially changed, when review caught an error, or when something was
accepted without full verification — and only when it would otherwise leave no trace once the
session ended. Routine accepted output is not logged; the file is a record of correction, not of
activity.

[`.claude/settings.json`](../.claude/settings.json) is the permission boundary the agent ran inside.
Its deny list is the substantive half: force-push, hard reset, `git clean -fd` and
`docker system prune` are refused outright.

[`.claude/commands/plan-project.md`](../.claude/commands/plan-project.md) is the command that starts
the protocol, and it exists so that Phase 1 cannot quietly become Phase 3.

## Reading the history

`main` carries one commit per unit. Each was squash-merged from its own branch through a pull
request, so the commit list reads as thirteen units rather than as fifty steps.

**Step grain is not lost — it is on the branches, which are not deleted.** To see the individual
steps of a unit, with the Definition of Done each was committed against:

```
git branch -a
git log main..feat/u7-api-service
```

The squashed commit body on `main` also carries the step messages.

## The checks that ran before every commit

Run from a local virtual environment at the repository root. Every one had to exit zero before a
step was committed:

```
ruff format --check .
ruff check .
mypy src tests
python -c "import pizza"
pytest tests/unit
```

`python -c "import pizza"` is not filler. The package uses a src layout, so an import resolves only
through the install — its failure means the package is not installed rather than that the code is
broken.

## Verifying those checks yourself

The linter and the type checker are in the test image already, so the claim above can be checked
against the delivered environment rather than taken on trust. With the stack up:

```
docker compose run --rm tests ruff check .
docker compose run --rm tests mypy src tests
```

**Neither runs as part of `docker compose up`, by decision.** Chaining them into the launch would
let a style rule turn a working system red and suppress the test suite's own result; the checks are
a condition of every commit instead, verifiable on demand by the two commands above.
