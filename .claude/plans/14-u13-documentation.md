# U13 — Documentation pass · Implementation Plan

**Phase 3 of the planning protocol in `CLAUDE.md` §2, for the thirteenth and last unit in Part 4 of
`03-roadmap.md`.** Decisions are in `02-decisions.md`; nothing here decides anything that belongs
there. Where executing a step needed a call Phase 2 had not made, it is recorded below under
*Readings* rather than left to implementation.

**Gate.** U13's *Decided by* column reads topic 13, and every item in it is `[decided]` — 13.1 to
13.4 and 13.7 closed on `plan/u13-gate`, merged in #26; 13.5 and 13.6 earlier. The status table
reads 112 decided and 0 open, the first point in the project at which planning is closed in full.

**One decided item was amended before this document was written, and it rides in the same commit.**
13.1 lists seven README sections and, separately, the headings its rule deleted. *Persistence* was
in neither, while 11.7 requires the compose file to point at a README section carrying the exact
lines that make the data survive — and `docker-compose.yml` names that section by title. The
amendment places those lines inside *Launch* and retargets the comment. **This is a return to
Phase 2, not a silence filled here** (`CLAUDE.md` §2), and the steps below are written against the
amended record. No item was added or closed: the total stays 112.

**`Depends on units: all`, and U11 is not merged.** Part 4's fourth rule says an implementation plan
is never written while a unit it depends on is unfinished. It is being written anyway, on the
developer's explicit instruction and under stated time pressure. §9 records exactly what U13 takes
from U11's unmerged branch and the closed list of checks that runs when it lands; the departure is
recorded here rather than glossed, because a rule this document is written in violation of is the
one thing a later reader must not have to infer.

---

## 1. What this unit delivers

Part 4 gives U13 the assembled README, the sequence diagram, the assumptions register and the
trade-off log. It is the unit that turns a built system into a delivered one: every earlier unit
documented its own change as it went (`CLAUDE.md` §7), and this is the assembly.

| File | What it becomes | Fixed by |
|---|---|---|
| `README.md` | **rewritten**, not extended — seven sections, in 13.1's order | 13.1, 13.2, 13.3, 13.4, 13.6 |
| `docs/how-this-was-built.md` | new — the reader's guide 14.5 requires, in the container 13.1 narrows it to | 12.10, 13.1, 14.2, 14.5, 14.7 |
| `docs/future-work.md` | new — nineteen entries in two tiers, derived from Part 5 | 13.7 |
| `docker-compose.yml` | one comment line retargeted from *Persistence* to *Launch* | 11.7, 13.1 as amended |

**The README on `main` is not the README 13.1 describes.** It carries *Running the system*, *Local
development*, *Configuration*, *Persistence* and *Tests*; 13.1 deletes three of those as headings
and folds their surviving content elsewhere. This unit writes the file again from the top. Treating
it as an edit would leave the deleted headings standing, which is the one failure mode the seven-row
table exists to prevent.

**Nothing under `src/` or `tests/` is touched, and no decision is taken.** Every sentence written
here summarises a record that already exists (1.4).

## 2. What this unit deliberately does not deliver

- **No item numbers and no `FW` codes in any delivered file.** 13.4 bars both from the README on the
  ground that they are internal; 13.7 extends the bar to `docs/future-work.md`. `.claude/plans/` and
  `docs/ai-log.md` name them freely and are unaffected.
- **No lint or type commands in the README.** 12.10's two `docker compose run --rm tests` commands
  go to `docs/how-this-was-built.md`, which is where 13.4 sent them and where that item's own
  argument lands. This is a decision, not an omission.
- **No second original.** `02-decisions.md` stays the only record of the trade-offs and Part 5 the
  only complete future-work list; both delivered documents are derived views (1.4).
- **No planned manual run of 1.2 end to end.** Whether that becomes a named act of this process is a
  new record beside 14.7 and a session of its own; it is not U13's and nothing here assumes it.
- **No `docs/` reshuffle.** 14.5 keeps the planning record in `.claude/plans/`.

## 3. Branch, commits, and the merge

- **Branch:** `docs/u13-documentation`, cut from `main` at `caa6457` (14.2), the merge of topic 13.
- **Commits:** one planning commit carrying the 13.1 amendment, then one commit per step
  (14.3, 14.4). Six in total.
- **Merge:** one pull request, squash-merged, `gh pr merge --squash` **without `--subject`**, so the
  number is appended to the title (14.2, 14.3). The branch is not deleted (14.2).

| # | Type | Title |
|---|---|---|
| P | planning | `docs: place 11.7's persistence lines in Launch, and plan U13` |
| 1 | step | `docs: add how-this-was-built — a reader's guide to the planning record` |
| 2 | step | `docs: add the future-work register — nineteen entries a reviewer can scan` |
| 3 | step | `docs: rewrite the README's operational half, and retarget the compose pointer` |
| 4 | step | `docs: add the sequence diagram — one path, five services` |
| 5 | step | `docs: close the README with the trade-offs, the assumptions, and the record it rests on` |

**P carries the Phase 2 amendment as well as this document**, because the amendment is what the
steps below are planned against and separating them would put a commit on the branch that plans
against a record it has already contradicted. 14.3 fixes the Phase 3 document as the first commit on
the unit's branch, and it is.

## 4. The Definition of Done that applies to every step

14.7's rows through U9 govern every step, and the U11 row joins them when U11 merges (§9). The five
commands are run from this worktree's virtual environment at the repository root:

```
ruff format --check .
ruff check .
mypy src tests
python -c "import pizza"
pytest tests/unit
```

**For the four Markdown-only steps the bar holds by construction, and this is a reading rather than
a licence** (R-e). 2.8 excludes Markdown from ruff's file scope, `mypy` reads `src` and `tests`, and
`pytest tests/unit` imports neither `README.md` nor `docs/`. No file any of the five commands reads
is changed by steps 1, 2, 4 or 5, so their results cannot differ from the commit before. **They are
executed in full at step 3**, the only step touching `docker-compose.yml`, and once more at the end
of the unit before the pull request opens.

**14.7's U9 row is checked at step 3** — from a clean state `docker compose up` brings every service
the file defines to the state 11.2's graph requires, and the stack stays up — because that is the
step that edits the compose file. `docker compose config -q` is not a substitute and is run beside
it, not instead.

A step is done when §8's six conditions hold.

## 5. Readings — where this plan filled a silence

Recorded here rather than resolved silently (`CLAUDE.md` §2). The boundary is U1 §5's: a Phase 3
document may fill a silence Phase 2 left; it may not settle an ambiguity inside a decided record.
**The one item that crossed that line is the persistence pointer, which went back to Phase 2 as the
13.1 amendment rather than being read here.**

- **R-a — of *Local development*, only the four pre-commit checks survive; the environment setup
  goes with the heading.** 13.1 gives the section one reason — *"no row fails without it"* — and
  then names exactly one thing that moves and one that does not: the checks go to
  `docs/how-this-was-built.md`, and the `uv pip compile` block is *"written for a contributor who
  does not exist"*. It is silent on the `uv venv` / activate / `pip install -e` block. The same
  sentence answers it: that block serves the same absent contributor, and the reason given for
  deleting the heading is a reason that covers everything under it not explicitly rescued. **What
  moves is what 13.1 names, and nothing else.**
  *Why this is a silence and not an ambiguity:* 13.1 does not describe the block at all, so nothing
  in the record is being reinterpreted.

- **R-b — the measured launch time enters *Launch* as one clause, and U11 supplies the number.**
  U11's plan hands it over as *"13.1 may want it stated"*, which decides nothing. It is stated:
  §7 writes the README for someone who has never seen the project, and a first `up` that spends
  minutes building looks like a hang to exactly that reader. The clause names the first launch and
  the later ones and asserts nothing else. **The number is read from U11's pull request** (its
  step 2 measures it from `up` to the `PASS` banner) and is never estimated here; until U11 merges,
  step 3 leaves the clause unwritten rather than guessing (§9).

- **R-c — the head is three lines: what the system is, what it is built from, and where to start.**
  13.1 says *"three lines — what the system is, and the stack"*, which names two of the three. The
  third is the pointer into *Launch*, because a reader who has never seen the project meets the head
  first and the DoD row grades whether they can run it.

- **R-d — the steps append sections in 13.1's reading order, so every intermediate README is a
  coherent document.** 13.1 fixes the order — head, *Launch*, *Using the CLI*, *How it works*,
  *Tests*, *Trade-offs*, *Assumptions*, closing line — but not the order in which they are written.
  Writing them in file order means step 3 leaves a README that is complete for launching, using and
  testing the system, step 4 inserts the diagram in its place, and step 5 closes it. **The rejected
  alternative is one commit for the whole file:** it is a single logical unit by §4's reading, and it
  is also a ~200-line rewrite that §2 asks to be verifiable in one sitting. Splitting by section
  boundary keeps both, since no intermediate state is a half-old file.

- **R-e — a Markdown-only step does not re-run the compose bar.** §4 states it; it is recorded here
  because it is a reading of 14.7's *"applies per step commit"* rather than something that item
  says. The claim is narrow: the five commands read no file these steps change, so their result is
  known without running them. It would stop being true the moment a step touched `src/`, `tests/`,
  `pyproject.toml` or the compose file — and step 3, which touches the last of those, runs them.

## 6. Steps

### Step 1 — The reader's guide to how the repository was built

**File added:** `docs/how-this-was-built.md`.

14.5 as 13.1 narrows it: the section that item required in the README becomes a file, linked once
from the README's last line. It carries a reader's guide to `CLAUDE.md` and `.claude/plans/`, 14.2's
sentence on where step grain survives a squash merge, the pre-commit checks of 14.7's U1 and U2
rows, and 12.10's two verification commands.

**This step is first because two later steps point at files that must already exist.** The README's
closing line names this file and the *Trade-offs* section names the next one; writing the pointers
before the targets would put a dead link on the branch.

**Definition of Done**

1. The file carries all four of: the guide to `CLAUDE.md` and `.claude/plans/`, 14.2's unit-branch
   sentence, the five pre-commit commands of §4, and 12.10's two
   `docker compose run --rm tests` commands.
2. **Every path it names resolves**, checked one by one against the working tree rather than read.
3. The five commands appear **verbatim** as 14.7 writes them, and the two verification commands
   verbatim as 12.10 writes them.
4. It claims nothing about lint or type checks running inside the launch — 12.10 decided they do
   not, and this file is where that fact is stated correctly or not at all.
5. Read from the diff: no `FW` code, nothing under `src/` or `tests/`, and no second copy of
   anything `CLAUDE.md` already says.

---

### Step 2 — The future-work register

**File added:** `docs/future-work.md`.

13.7's nineteen entries in two tiers. Tier 1 in its order — FW9, FW19, FW16, FW6, FW13, FW2, FW12,
FW4, FW17 — at two to three lines each; tier 2 — FW5, FW11, FW3, FW7, FW14, FW1, FW15, FW8, FW10,
FW18 — at one line each. Each entry is rewritten in its own words; the join back to Part 5 is the
title.

**Definition of Done**

1. **Nineteen entries, counted**, and each maps one-to-one onto a Part 5 entry with none invented
   and none dropped.
2. **`grep -o 'FW[0-9]*'` over the file returns nothing.** 13.7 bars the codes from the file a
   reviewer is handed.
3. **No sentence is carried across from Part 5**, checked by sampling tier 1 against the source. An
   entry quoted from Part 5 would arrive full of item numbers written for the developer.
4. The two tiers are visibly different in depth and equal in presence — every entry appears.
5. **FW17 is in tier 1 and its placement is stated in the file**, in the file's own words: it is the
   entry showing a timeout was traced rather than trusted. 13.7 requires the exception to be named,
   because a rule with a silent exception reads as a rule broken.
6. Each entry states a structural fact rather than a judgement of taste (13.7's mitigation against
   drift).
7. Read from the diff: no item numbers, and no link into `.claude/plans/`.

---

### Step 3 — The README's operational half ⚠ U11

**Files changed:** `README.md`, `docker-compose.yml`.

The rewrite begins. Head, *Launch*, *Using the CLI*, *Tests* — written from the top, with *Running
the system*, *Local development*, *Configuration* and *Persistence* gone as headings. The
persistence YAML moves into *Launch* under the teardown sentence, and the compose comment is
retargeted in the same commit.

*Launch* carries 11.10's v2.24 floor, `docker compose up` and what it prints (11.3), the API URL and
`/docs` (11.8), `--build` (11.9), the CI-style gate as 11.4 now writes it, teardown with
`docker compose down` (11.7), the persistence block, two lines on `.env.example` (10.3), and R-b's
launch-time clause. *Using the CLI* carries `docker compose run --rm cli` (9.3), the Git Bash
`winpty` note (9.6), and 1.2's thirteen steps including **both** outcomes of step 6. *Tests* carries
what runs at launch, 12.2's four scenario names one line each, re-running via `docker compose logs
tests` and `docker compose run --rm tests` (12.9), one sentence on the absent `--junit-xml=` beside
the decision it reverses (13.4), and 11.6's determinism boundary.

**Definition of Done**

1. **No heading named *Persistence*, and the exact YAML lines 11.7 requires are nonetheless in the
   file**, inside *Launch*. `docker-compose.yml` line 3 reads *Launch*, changed in this commit, so
   the pointer is never dangling at any commit on the branch.
2. **11.6's boundary is written with `down`, not `down -v`.** 11.6 quotes a sentence predating
   11.7's decision to use no named volumes; 1.2 already records that U13 writes `down`.
3. **The CI gate appears as two commands** — `docker compose up -d`, then
   `docker compose wait tests` — and **no flag commit A of U11 removed appears anywhere in the
   file.** ⚠ U11.
4. **12.10's two commands are absent**, being step 1's.
5. Both outcomes of 1.2's step 6 are stated, so a reviewer with a driver already registered reads
   an immediate assignment as correct rather than as a failure.
6. The five commands of §4 exit zero, and `pytest tests/unit` collects nineteen.
7. **14.7's U9 row holds:** from a clean state `docker compose up` brings every service the file
   defines to the state 11.2's graph requires and stays up; `docker compose config -q` passes
   beside it. Verified by polling `docker compose ps -a` — **no fixed sleep** (`CLAUDE.md` §5).
8. R-b's clause is present with U11's measured number, or absent (§9). It is never present with a
   number this unit estimated.
9. Read from the diff: no item numbers, no `FW` code, and no surviving sentence from a deleted
   heading that 13.1 did not place.

---

### Step 4 — The sequence diagram ⚠ U11

**File changed:** `README.md`.

*How it works*, inserted between *Using the CLI* and *Tests* where 13.1 puts it. One fenced
```mermaid block (13.2), five participants named after their Compose services — `cli`, `api`,
`postgres`, `rabbitmq`, `worker` — covering 1.2's steps 3 to 12 (13.3).

**Definition of Done**

1. **Exactly one `mermaid` fence**, in the README, with no separate file and no committed image
   (13.2).
2. **Exactly five participants**, named as the Compose services are, so a reviewer reading `worker`
   can type `docker compose logs worker` and get the same word.
3. The covered sequence is 1.2's steps 3 to 12 — no more, and nothing from steps 1, 2 or 13.
4. **The outbox insert is one message**, `UPDATE orders + INSERT outbox`, because 7.5's atomicity is
   what 13.4 explains in words and one line is what makes it visible.
5. **8.2's wait queue is a note over `rabbitmq`, not a sixth participant.**
6. **Neither `schema` nor `tests` appears** — 13.3 excludes both; R17 asks for the request path.
7. **The fence renders**, checked rather than assumed, and the source reads as an ordered list of
   messages when it does not (13.2's accepted cost).

---

### Step 5 — The trade-offs, the assumptions, and the record they rest on

**File changed:** `README.md`.

*Trade-offs* carries 13.4's nine entries in 13.4's order — the pair, the synchronous runtime,
DLX+TTL, publish-after-commit, migrations, CI, launching from empty, one worker, and no test
reaching around the thing it verifies — at three to six lines each: what was chosen, what was
rejected, what it costs. It closes with six lines naming what a reviewer would look for and not
find, one pointer to `docs/future-work.md`, and one pointer to `.claude/plans/02-decisions.md`.
*Assumptions* carries the fifteen lines 13.6 marks **†**, one line each. The closing line points at
`docs/how-this-was-built.md`.

**Definition of Done**

1. **Nine entries, counted, in 13.4's order**, which is foundational-first — a decision the rest of
   the system stands on before one answering a visible gap.
2. **Entry 2 rests on "taken once for the whole system" and names the cost of the side taken** —
   7.7's publisher lock, and a thread held across the publish window. **It does not argue from
   function colouring**, an argument 13.4 records as withdrawn because it applies to both sides.
3. **Entry 9 is one entry, not three**, merging 12.3, 12.6 and 12.8 into the single principle that
   no test reaches around the thing it claims to verify — and it names its cost, the port failure
   paths reached by hand.
4. **Entry 4 carries the one command the section allows** — `docker compose stop rabbitmq`, then a
   status update returning `200` with the order still `PENDING`.
5. **Entries 6 and 7 lead where 13.4 says they lead:** 6 with where a CI server belongs, 7 with the
   clean start rather than with the absent isolation.
6. **Fifteen assumption lines, checked against the † marks** — A2, A3, A4, A10, A11, A13, A14, A15,
   A17, A19, A20, A22, A23, A24, A25 — one line each, no line restating a decision.
7. **Exactly one link into `.claude/plans/`**, at the *Trade-offs* section's end (13.4, 14.5).
8. **No item number and no `FW` code anywhere in the README**, checked over the whole file now that
   it is complete.
9. Both files pointed at — `docs/future-work.md` and `docs/how-this-was-built.md` — exist and
   resolve.
10. **The README stands alone** (14.5's condition): no trade-off requires opening the planning record
    to be understood.

## 7. Ordering

**1 → 2 → 3 → 4 → 5, and only two of the four edges are forced.** Steps 1 and 2 must precede step 5,
which links to both; step 4 must follow step 3, which creates the sections it inserts between. Steps
1 and 2 are independent of each other and of U11, and are ordered by nothing stronger than reading
convenience.

**The two U11-exposed steps are as late as the file order allows.** Steps 1 and 2 can be written and
merged whatever U11 does; steps 3 and 4 name the gate command, the launch output and the measured
time, and are marked ⚠ throughout.

## 8. What U13 takes from U11's unmerged branch, and the check when it lands

U11 is unfinished: `test/u11-test-execution` is two commits ahead of `main` with its step 1
uncommitted, and `docker-compose.yml` on `main` has six services where 11.1 closes the list at
seven. Four facts below are read from that branch rather than from `main`, and every one is a fact
this unit writes into a delivered file.

| Taken from U11 | Used by |
|---|---|
| 11.4's gate is two commands, `docker compose up -d` then `docker compose wait tests` | step 3 |
| the launch runs the suite and prints a `PASS`/`FAIL` banner in that stream | steps 3, 4 |
| the stack stays up after the suite passes (11.5) | step 3 |
| the measured wall-clock time from `up` to the banner | step 3, R-b |

**When U11 merges, `main` is merged into this branch and seven things are checked. Nothing else.**

1. 11.4 — the two-command form survived the merge as U11's branch writes it.
2. 11.1 — seven services, and `tests` named in the service table.
3. 11.10 — the version floor is still v2.24.
4. 11.11 and 12.9 — both carry the new command's name, not the old flag.
5. **U11's own two README additions** — its step 2 edits *Running the system* and *Tests*, headings
   this unit deletes and rewrites. They must be **absorbed** into *Launch* and *Tests*, not
   overwritten. This is the check most likely to catch something.
6. R-b's number is read from U11's pull request and written into step 3's clause.
7. The status table's `Total` is **recounted with `grep -c '\[decided\]'`** and never carried
   (14.3).

**If any of the seven has moved, it is a return to Phase 2 or 3 and not a correction in place**
(`CLAUDE.md` §2). The list is closed so that the check is a check and not a re-reading.

## 9. After the merge

The repository is delivered. A reader who has never seen it opens `README.md`, learns what the
system is in three lines, brings it up with one command and watches it test itself, drives it from a
CLI through the thirteen steps that show every behaviour the brief names, sees the design as a
diagram on the page they are already reading, and finds the nine choices that would otherwise look
like mistakes answered before they ask. Two files beside it carry what was deliberately not built
and how the repository was built. The planning record is linked once, as depth they may decline.
