---
title: Set up a watch
description: Write a watch that looks at a work-item query on a schedule and nominates work from what it finds, apply it, and check that it is running.
sidebar:
  order: 8
---

A [watch](/reference/glossary/#watch) is a standing instruction to look at something on a schedule, such as a work-item query, and to nominate work from what it finds. Each run of a watch is a **sweep**. An agent that follows a written procedure (a skill kept in a repository) performs each sweep, and what it nominates goes to the [board](/guides/use-the-board/), where the organisation's rules decide whether it opens as a flight.

Use this guide to have Good Grief pick up work by itself: for example, to triage every work item carrying a particular tag, once an hour.

A watch belongs either to the organisation or to one person, never anything in between.

## Prerequisites

- A working copy of the airspace. [Change the airspace](/guides/change-the-airspace/) explains it.
- A registered repository that holds the skill the sweep follows, such as `.claude/skills/triage.md`.
- A [credential](/reference/glossary/#credential) the runner can use to read the tracker, registered with `gg credential add`.
- The work kind the watch will nominate, such as `review`, already in force.

## 1. Write the watch file

A watch is one file in `watches/`, named after the watch:

```yaml
# watches/triage.yaml (an example)
shape: work-items
trigger:
  every: "1h"
host: "https://dev.azure.com/example-org/example-project"
credential: "local:example-org/tracker"
filter: "SELECT [System.Id] FROM WorkItems WHERE [System.Tags] CONTAINS 'gg-triage'"
repository: web-app
skill: ".claude/skills/triage.md"
ref: "refs/heads/main"
mapping:
  subject: id
  version: rev
  intent-key: url
pull-point: resident-runner
nominates:
  triage-opens:
    kind: flight
    requires: []
    opens:
      - review
bounds:
  cap-per-pass: 1
  budget:
    flights: 5
    window: "24h"
```

Every field except `bounds` and `for` is required:

| Field | Meaning |
|---|---|
| `shape` | What a sweep looks at. `work-items`, a tracker query, is the only shape. |
| `trigger.every` | How often it sweeps, as a duration such as `15m` or `1h`. |
| `host` | Which tracker, by address. |
| `credential` | Where the credential to reach the tracker is, never the secret itself. The runner resolves it. |
| `filter` | What to ask the tracker for. Good Grief refuses a blank filter and never reads it as everything. |
| `repository` | The registered repository the skill is in. |
| `skill` | The path of the procedure the sweep's agent follows, inside that repository. |
| `ref` | The ref the skill is read at, so what runs is what was reviewed. |
| `mapping.subject` | Which field identifies each item the query returns. |
| `mapping.version` | Which field says the item changed. The watch nominates once per subject and version, so it can nominate a changed item again and does not nominate an unchanged one. |
| `mapping.intent-key` | Which field names the item outside Good Grief. The budget counts by it. |
| `pull-point` | Who performs the sweep: `resident-runner` (a runner), `control-plane` or `forge-scheduler`. |
| `nominates` | The `flight` destination the nominations stand under: which work kinds they may open (`opens`), and whether they open at once or wait for a person (`opens-as`). [Use the board](/guides/use-the-board/#auto-or-gated) explains `auto` and `gated`. |
| `bounds.active-hours` | When it may sweep at all, as `HH:MM-HH:MMZ` in UTC. Leave it out to sweep at any time. |
| `bounds.cap-per-pass` | The most items one sweep may report. |
| `bounds.budget` | How many flights its nominations may open (`flights`) within a window (`window`, such as `24h`). |
| `for` | Whose watch it is: the organisation, or one person. Leave it out for the organisation. |

Every bound is optional, and leaving a bound out makes it unlimited.

## 2. Declare the name

Declare a watch's name before applying its file:

```sh
gg airspace name watch triage
```

Declaring a name loosens the rules, so gg may report a flight that waits for approval, and no one can use the name until that gate opens. `gg airspace apply --declare-names` can declare it instead, as part of applying.

### A watch of one's own

To make a watch that belongs to one person, declare it with `--personal`:

```sh
gg airspace name watch my-queue --personal
```

gg declares the name bound to the signed-in person and writes their identity into the watch file's `for:` line, so no one has to type it. A personal watch differs from the organisation's in these ways:

- Only its person can apply, change or retire it, and only its person answers its gates, including a loosening change to it.
- Its sweeps and the flights it opens run only on runners its person has claimed, so its `pull-point` must be `resident-runner`. If none of them is running, `gg why` says so.
- Its nominations stand on the organisation's board marked with `for`, and only its person can open or decline them.
- A watch never changes whose it is. To move it, retire it and declare it again.

## 3. Apply it

```sh
gg airspace diff
gg airspace apply
```

A new watch, and any change that loosens its filter, bound or budget, opens a flight that waits for approval. For an organisation's watch, root's approver answers it; for a personal watch, its person does.

## 4. Check that it is running

Nothing watches a sweep while it runs, so asking is the only way to know a watch is alive:

```sh
gg watches
```

```
triage                  instructions  swept        2026-10-14 15:00:12Z
  2 of 5 in 24h, 1 nominated
```

Each watch gets two lines. The first gives its name, what performs its sweeps (`instructions`, meaning an agent following the skill), how its newest sweep ended, and when it last reported. The second gives what it has spent against its budget and how many items the newest sweep nominated. A watch with no budget shows its count followed by `unbounded`.

A sweep ends in one of two ways:

- **`swept`**: it reached the tracker and reported what it saw, even if that was nothing.
- **`unreachable`**: it could not do its job, and the next line says why.

Two other states are worth knowing:

- A watch that has `never reported` has not swept yet. A watch applied a minute ago reads this way.
- A watch marked `quiet since` has seen nothing it should have found. Either no runner is sweeping it, or the runners that took its sweeps are not reporting.

When no watch is in force, gg says so and suggests `gg airspace show` to list the declared names.

## The same steps in the console

Run `gg` with no arguments, then `;` to open the board, and `v` to switch from nominations to sweeps. When a watch's failure appears in the queue (`,`), `*` marks every failure so a person can decline them together.

## Related

- [Use the board](/guides/use-the-board/): what happens to the nominations a watch makes.
- [Change the airspace](/guides/change-the-airspace/): declaring, applying and retiring names.
- [Answer a gate](/guides/answer-a-gate/): approving a new watch.
