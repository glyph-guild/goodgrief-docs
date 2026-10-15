---
title: Watches and sweeps
description: How a watch looks at a work-item query on a schedule, who performs each sweep, what bounds it, whose it is, and what a sweep may produce.
sidebar:
  order: 6
---

A [watch](/reference/glossary/#watch) is a standing instruction to look at something on a schedule and to propose work from what it finds. Each run of a watch is a **sweep**. A watch never opens a flight itself: everything a sweep proposes goes to the [board](/reference/glossary/#board) as a [nomination](/reference/glossary/#nomination), and the organisation's rules decide what happens next.

This page explains the model. [Set up a watch](/guides/set-up-a-watch/) gives the steps for writing, applying and checking one.

## A watch is an airspace document

A watch is one file in the [airspace](/reference/glossary/#airspace)'s `watches/` folder, named after the watch. Like every airspace document, it is versioned, it is checked when it is applied, and a change that loosens it waits for approval.

A watch says six things:

| What | Fields | In short |
|---|---|---|
| What to look at | `shape`, `host`, `filter` | Which tracker, and the query to ask it. `work-items` is the only shape. |
| How to reach it | `credential` | Where the credential for the tracker lives. The document holds only the reference; the runner resolves it. |
| How to read what comes back | `mapping` | Which field identifies an item (`subject`), which field says it changed (`version`), and which field names it outside Good Grief (`intent-key`). |
| How to decide what to propose | `repository`, `skill`, `ref` | The written procedure the sweep follows: a file in a registered repository, read at a ref. |
| How often, and who performs it | `trigger.every`, `pull-point` | The interval between sweeps, and what carries them out. |
| What it may propose, and how much | `nominates`, `bounds` | The work kinds its nominations may open, whether they open at once, and the limits on its spending. |

Two fields are optional: `bounds`, whose every member is optional and unlimited when left out, and `for`, which says whose watch it is.

When a watch is applied, Good Grief checks it and refuses it, naming the field, when any of these is true:

- A required field is blank.
- The filter is blank. A blank filter would read as every item in the tracker, so it is refused rather than taken to mean everything.
- `trigger.every` is not a positive duration.
- `nominates` is missing, or is not a `flight` [destination](/concepts/envelope/#destinations).
- A budget allows no flights, or its window cannot be read.
- `bounds.active-hours` is not written as `HH:MM-HH:MMZ`, in UTC.

The procedure itself never travels in the document. The watch names where the procedure is kept, and the runner reads it there.

```yaml
# watches/triage.yaml (an example)
shape: work-items
trigger:
  every: "1h"
host: "https://tracker.example.com/example-org/example-project"
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

## A sweep is one run of a watch

### When a sweep is due

The control plane decides when each watch is due, by its own clock:

- A watch that has never swept is due at once.
- After that, a watch is due when `trigger.every` has passed since its last sweep was decided.
- Outside `bounds.active-hours`, no sweep is decided. The schedule waits for the window to open.
- A sweep that no runner has answered holds the next one back for two intervals, so unanswered sweeps do not pile up.

### Who performs it

`pull-point` names what carries out the sweep. The document accepts three values, but only one is performed today:

| `pull-point` | Status |
|---|---|
| `resident-runner` | A [runner](/reference/glossary/#runner) performs the sweep. |
| `control-plane` | Accepted in the document, but nothing performs a sweep from there yet. |
| `forge-scheduler` | Accepted in the document, but nothing performs a sweep from there yet. |

A watch with a pull point that nothing performs is in force but never sweeps.

A runner takes a sweep the way it takes a flight: by asking. It lists the tracker addresses and credentials it holds, and it is offered sweeps for watches that use them. The control plane never reaches the tracker, and never holds the credential.

Runners perform sweeps by default. Setting `runner-sweeps` to off in the runner's configuration, or `GG_RUNNER_SWEEPS` in its environment, stops a machine from taking them.

### How the runner performs it

The runner reads the procedure (the `skill`) at the commit its `ref` points to when the sweep is decided, and starts an agent with it. The agent pages through the tracker query, decides which items deserve work, and proposes each one through a nomination tool. It is told to change nothing. Proposing is its whole output.

Because the ref can move between sweeps, the runner reports the commit and the content of the procedure it actually read. A sweep that does not say what it followed is not accepted.

`gg watches` names what performs a watch's sweeps as `instructions`, meaning an agent following the written procedure. That is the only way a sweep is performed.

## What a sweep may produce

A sweep ends with a report, in one of two outcomes:

- **`swept`**: it reached the tracker and reported what it saw. A sweep that found nothing worth proposing is still `swept`, with an empty list.
- **`unreachable`**: it could not do its job. The report carries the runner's explanation and no nominations.

What reaches the board depends on the outcome:

| What happened | What appears on the board |
|---|---|
| A swept report with nominations | One nomination per item, each opened, held for a person or refused by the rules. |
| An unreachable report | A gated entry carrying the runner's explanation, one per failed sweep, for a person to read and decline. |
| No report at all for two intervals | A gated entry saying the watch has gone quiet, one per quiet interval. |

A sweep produces nothing else. It does not comment on items, change them, or record findings, and a nomination carries no copy of an item's title, description or comments: only what identifies it, why it deserves work, and an optional note for the agent that takes it.

### One nomination per item and version

Each nomination is keyed on the item (qualified by its tracker) and its version. The first nomination for an item at a version is the only one: a later sweep that sees the same item unchanged is told it was nominated already, and nothing is sent again. When the item changes, its version changes, and it can be nominated again.

## Bounds

Every bound is optional, and a bound that is left out is unlimited. The control plane enforces them, not the runner.

| Bound | What it limits | What happens at the limit |
|---|---|---|
| `active-hours` | When a sweep may be decided at all. | Outside the window, no sweep is decided, and the watch is not counted as quiet. |
| `cap-per-pass` | How many nominations one sweep may stand. | The first ones stand. The rest are not refused; a later sweep can report them again. |
| `budget` | How many flights the watch's nominations may open (`flights`) within a window (`window`), counted across the whole watch. | Further nominations stand on the board as gated, with a reason, until a person opens them or the window moves on. |

A nomination can also be gated for reasons that have nothing to do with the budget: the `nominates` destination says `opens-as: gated`, or it requires a human check. [Nominations and the board](/concepts/nominations-and-the-board/) explains how a nomination opens.

## The organisation's watches and a person's own

A watch belongs either to the organisation or to one person, and never to anything in between. The `for` field says which: left out, it is the organisation's; set to a person, written as `<provider>:<subject>`, it is theirs.

`gg airspace name watch <name> --personal` declares a watch for the signed-in person and writes `for:` into the file. A personal watch differs from the organisation's in these ways:

- **Only its person may apply it.** Anyone else is refused, including the platform owner.
- **Only its person answers its gates and its nominations.** A loosening change to a personal watch waits for its person, and a nomination it makes stands on the organisation's board marked as theirs. Nobody else can open or decline it.
- **Its work runs only on its person's machines.** Its sweeps, and the flights its nominations open, are offered only to runners the person has claimed. For that reason, a personal watch must use `pull-point: resident-runner`.
- **Its flights are its person's.** A flight opened from a personal watch belongs to that person. A flight opened from the organisation's watch belongs to the person who wrote the version of the watch in force.
- **It never changes owner.** Changing `for` is refused. To move a watch, retire it and declare it again.

The person named in `for` must belong to the organisation, and a name declared for one person cannot be used for another.

## Changing a watch

A change that could make a watch propose more, or propose differently, loosens the rules and waits for approval. These changes loosen:

- Any change to the filter, even one that looks narrower, because whether a new query returns more items cannot be decided in advance.
- Any change to the repository, procedure, ref, tracker address, credential, shape, pull point or mapping.
- A shorter interval between sweeps.
- Removing the budget, or allowing more flights for each unit of time.
- Removing or raising `cap-per-pass`.
- Removing `active-hours`, or lengthening the window.
- Loosening the `nominates` destination.

Every other change, such as a longer interval or a smaller budget, tightens the watch and applies directly. For the organisation's watch, root's approver answers a loosening change; for a personal watch, its person does.

## Knowing a watch is alive

Nothing watches a sweep while it runs, so a watch that has stopped working is silent unless someone asks. `gg watches` lists every watch with its newest sweep:

```
triage                  instructions  swept        2026-10-14 15:00:12Z
  2 of 5 in 24h, 1 nominated
```

The first line gives the watch's name, what performs its sweeps, how its newest sweep ended, and when it last reported. The second gives its spending against its budget, or `unbounded` when it has none, and how many items the newest sweep nominated.

Two other states are worth recognising:

- **`never reported`**: the watch has not swept yet. A watch applied moments ago reads this way, and so does one whose pull point nothing performs.
- **`quiet since`**: at least two intervals have passed since the watch last reported, counting from when it was applied if it never has. Either no runner is taking its sweeps, or the runners that took them are not reporting. Only watches that runners perform are judged quiet, and only inside their active hours.

An unreachable sweep's explanation is printed beneath the watch. The console's board (`;`, then `v`) also shows when each watch's next sweep is due.

## Related

- [Set up a watch](/guides/set-up-a-watch/): writing, declaring, applying and checking a watch.
- [Nominations and the board](/concepts/nominations-and-the-board/): what happens to what a sweep proposes.
- [Use the board](/guides/use-the-board/): opening and declining nominations, including a watch's failures.
