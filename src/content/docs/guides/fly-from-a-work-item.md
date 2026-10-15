---
title: Fly from a work item
description: Open a flight from a sentence, a link, a work item or a file in a repository, choose the rules and machine it runs under, and find every flight opened for the same work.
sidebar:
  order: 1
---

Use this guide to open a [flight](/reference/glossary/#flight) from something that already describes the work, such as a work item in a tracker or a plan file in a repository, and to control where and how that flight runs. It also covers finding every flight opened for the same piece of work, and moving a flight that is already running to a different model.

## Prerequisites

- gg is signed in to the organisation's control plane. `gg doctor` confirms it.
- At least one [runner](/reference/glossary/#runner) is available. `gg runners` lists them.
- The repository the work concerns is registered. `gg airspace show` lists the registered names, and [Change the airspace](/guides/change-the-airspace/) explains how to register one.

## 1. Say what the flight is for

What a flight is opened for is its [intent](/reference/glossary/#intent). `gg fly` takes exactly one intent, in one of four forms:

| Form | Example | Use it for |
|---|---|---|
| Text | `gg fly "Why does login time out after an hour?"` | A question or request that exists nowhere else. |
| A link | `gg fly --uri https://example.com/incidents/77` | Work described at an address. |
| A work item | `gg fly --ticket ado#1234` | An item in a work-item tracker, as `<provider>#<id>`. |
| A file | `gg fly --file web-app:docs/plans/session-timeout.md@main` | A document in a registered repository, as `<repository>:<path>[@ref]`. |

A few rules apply to each form:

- **A work item needs both halves.** `--ticket 1234` is refused, because the id alone does not say which tracker the item is in.
- **A file is read by the runner, not by gg.** The repository is its registered name, the path is inside that repository, and the ref is optional. Without a ref, the runner reads the repository's default branch. The runner records the commit it read, so the agent works from exactly the words that were named.
- **Only one form at a time.** A command that gives text and `--ticket` together is refused, and nothing is opened.

gg replies with the flight's number:

```
Opened GG-42.
```

If the control plane has not assigned the number yet, gg prints the flight's id instead and says that the number is assigned as the flight starts.

## 2. Name the repository

A work item or a link does not say which repository the work concerns, so name it with `--repo`, using its registered name:

```sh
gg fly --ticket ado#1234 --repo web-app
```

`--repo` can be repeated when the work spans two repositories, such as a procedure kept in one and the code it describes in another. The runner clones them and lists them to the agent in the order given, so name the repository the work is mainly about first. Naming the same repository twice is refused.

A flight that names no repository inherits one only when the organisation's [root](/reference/glossary/#root) rules list exactly one. The [envelope](/concepts/envelope/#repositories) explains the rule.

## 3. Choose the rules, the place and the model

Each of these options narrows a choice the organisation's rules already allow. None of them can grant something the rules withhold.

- **`--work-kind <name>`** chooses the [work kind](/reference/glossary/#work-kind) whose rules govern the flight, such as `investigate` or `review`. `gg airspace show` lists the work kinds the organisation has declared. A name the organisation has not declared is refused, and so is a work kind marked as abstract, which exists only for other work kinds to extend.
- **`--environment <name>`** chooses the [environment](/reference/glossary/#environment) the flight runs in, such as `dev` or `ui`. It must be one of the environments root lists; `gg environments` lists every charted one. A flight that names none inherits the only entry when root lists exactly one.
- **`--model <name>`** chooses the model the agent runs on. It must be one of the models root lists under `models:`. When root lists none, no person may choose a model, and the work kind's loop decides.

```sh
gg fly --ticket ado#1234 --repo web-app --work-kind investigate --environment dev --model claude-sonnet-5-5
```

A root that allows people to choose between two models declares them like this (an example):

```yaml
models:
  - claude-opus-5-5
  - claude-sonnet-5-5
```

Adding a model to that list loosens the rules, so it waits for approval like any other loosening change.

## 4. Choose the machine (optional)

By default, any runner that meets the flight's requirements may take it. Two options change that:

- **`--runner <id|name>`** opens the flight for one machine. `gg runners` lists the machines and their names.
- **`--attended`** says that a person will watch the flight from wherever they are. The runner opens a channel for watching, and an agent still does the work. It requires `--runner`, because there must be a named machine to watch.

```sh
gg fly --ticket ado#1234 --repo web-app --runner build-01 --attended
```

## 5. Find every flight for the same work

`gg flights --intent` lists the flights opened for one intent. Add `--all` to include flights that have ended:

```sh
gg flights --all --intent ado#1234
```

```
GG-42       2026-10-14 14:31:59Z  landed     ado#1234
GG-57       2026-10-15 09:02:11Z  open       ado#1234
```

The intent can be a work item (`<provider>#<id>`), an absolute link, or a file. A file is given as the control plane records it: the repository's forge path, then the file's path, then `@ref` when one was pinned, for example `example-org/web-app:docs/plans/session-timeout.md@main`.

When there are more flights than fit on one page, gg ends the list with the command for the next page, in the form `More: gg flights --after <cursor>`. `--limit <rows>` sets the page size.

## 6. Move a running flight to another model

`gg model` moves a flight that is still in the air to another model from root's `models:` list:

```sh
gg model GG-42 claude-opus-5-5
```

gg prints the flight as it now stands. Its `model` line shows the model now in force. The model must be one root lists; any other name is refused.

## The same steps in the console

Run `gg` with no arguments, then:

- `n` starts a new flight and asks how to compose it: `w` writes it in an editor, `m` composes it with an agent, `l` plans several legs with an agent, and `s` starts a Claude Code agent.
- When the console asks which work kind a flight is for, `enter` flies it as the selected kind, and `tab` switches between the work kinds and the repositories.
- `[` opens the intents tab, which lists work items from the organisation's trackers. `f` flies the selected item, `l` plans from it, `v` moves to the next source, and `/` narrows the list.
- On an open flight, `m` moves it to another model.

## Related

- [First flight](/start-here/first-flight/): a flight from start to finish.
- [The envelope](/concepts/envelope/): the rules each option above is checked against.
- [Plan with itineraries](/guides/plan-with-itineraries/): work too large for one flight.
- [Answer a gate](/guides/answer-a-gate/): what to do when a flight waits for a person.
