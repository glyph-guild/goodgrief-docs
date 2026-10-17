---
title: Work kinds
description: What a work kind is, how it combines with root, the fields that describe the work, how one work kind extends another, and how a flight's work kind is chosen.
sidebar:
  order: 3
---

A **[work kind](/reference/glossary/#work-kind)** is the rules for one kind of work, such as an investigation, a review or a change. It says how the agent works, what the work can yield, and where finished work lands. Every flight runs under at most one work kind, and the same work kind governs every flight of that kind.

This page explains what a work kind contributes and how it behaves. [Write a work kind](/guides/write-a-work-kind/) gives the steps for writing, checking and applying one.

## A work kind is one layer of the envelope

A flight's rules, its **[envelope](/concepts/envelope/)**, combine three layers:

> the rules for one flight = **root** + **work kind** + **narrowings**

[Root](/reference/glossary/#root) is the organisation's base rules, and decides where work may happen at all. The work kind decides what the work is. [Narrowings](/reference/glossary/#narrowing) add approvals a repository requires for itself.

The layers combine by these rules:

| Part | How it combines |
|---|---|
| `repositories`, `environments`, `models`, `context.constitution` | **Root only.** A work kind may leave them out or repeat root's value. The control plane refuses a different value. |
| The organisation's tool servers | **Root only.** The control plane refuses a work kind that declares them. |
| `loops`, `destinations`, `produces`, `accepts`, `brief`, `hosts`, `consults` | **Work kind only.** They come from the work kind as written. Root's loop and destination apply only to a flight that runs under no work kind. |
| `context.scope` | **The overlap** of root's scope and the work kind's. If neither contains the other, the control plane refuses the combination. |
| `obligations` | **Added together** from every layer. Two layers may not declare an obligation with the same name. |
| `instructions` | **Added together**, root's first, then the work kind's. |
| `learned` | **Added together** from root and the work kind. |

`gg envelope show <work-kind>` prints root combined with a work kind, and marks each rule with the document it came from.

## What a work kind says

### What the work may be about: `accepts`

`accepts` says what a flight of this kind may concern. Every work kind must declare it, and only a work kind may.

| Value | Meaning |
|---|---|
| `repository` | A tree to work in. |
| `tracker` | A backlog to read, with no tree. |
| `envelope` | An airspace document. |

An empty list means the work has no subject at all.

`accepts` decides two other things:

- **Which scope is allowed.** A work kind that accepts `repository` declares a path pattern as its `context.scope`. A work kind that does not must declare `scope: none`, because there is no tree to change.
- **Which facts the work can yield.** Facts that need a tree, such as the list of changed files (`change.manifest`), only a work kind that accepts `repository` can produce. The control plane marks obligations that read a fact the work kind can never produce not attached, instead of halting the flight.

Removing a value from `accepts` loosens the rules, and waits for approval.

The control plane reads `accepts` when a person proposes a plan: a leg whose work kind works in a repository must name one. It does not check `accepts` against the repositories `gg fly` names, so a flight opened directly can name a repository for a work kind that does not accept one, as long as root allows the repository.

### What the work yields: `produces`

`produces` lists the facts this kind of work can yield, such as `change.manifest`, `loop.outcome` or `landing.proposal`. Every work kind must declare it, even as an empty list. A work kind that does not accept `repository` cannot list a fact that needs a tree.

The list is a permission, not a promise. An obligation that depends on a fact the list leaves out never applies. For that reason, removing a fact from the list loosens the rules. [The envelope: produces](/concepts/envelope/#produces) explains the effect in detail.

### How the work is done: one loop

A work kind has exactly **one loop**: one agent session, with its executor, model, moves, budget and what happens when the budget runs out. The control plane refuses an envelope with a second loop. [The envelope: loops](/concepts/envelope/#loops) describes each setting.

### Where the work goes: one destination

A work kind has exactly **one destination**, which says where finished work lands and which obligations it requires. The control plane refuses an envelope with a second destination, and one with none, except for an abstract work kind (see [below](#abstract-work-kinds)). [The envelope: destinations](/concepts/envelope/#destinations) describes each kind of destination.

A work kind must also declare at least one obligation.

### What the agent is told: `brief`, `instructions` and `learned`

Three fields reach the agent, each in a different role.

| Field | What it is | Who writes it |
|---|---|---|
| `brief` | The job, in one sentence. The agent's task opens with it. | A person, in the work kind. Only a work kind may set it. |
| `instructions` | Standing guidance about how the work is done, passed word for word. | A person, in root and in the work kind. |
| `learned` | Advice about what a particular place is like: a repository, a commit, an image or an environment. | Usually an agent, in a flight that rehearses the work and hands the advice back for a person to approve. |

**`brief`** comes first in the agent's task: the task tells the agent what to work on, followed by the brief. A work kind with no brief tells the agent to make the code changes the work asks for. The brief is the place to say "change nothing" or "write a plan, not code".

**`instructions`** follow, introduced as the operator's standing instructions. Root's come first, then the work kind's, and the task marks each line with the document it came from.

**`learned`** comes later, fenced as reviewed advice that grants nothing. Each entry names what it was learned against, such as a repository and the commit it was true of, so that advice can be told to have gone stale. A flight receives only the entries that match its repository, image or environment. A flight whose destination proposes a change to the work kind's document normally adds advice, and a person approves that change like any other loosening change. A person can also write advice by hand. Any addition to `learned` loosens the rules and waits for approval.

```yaml
# An example of the three fields together.
brief: "Review the pull request this flight names. Change nothing: the result is the review."
instructions:
  - "Name only paths that were opened and read."
learned:
  - against:
      repository: "example-org/web-app"
      commit: "3a6de3c5cbe45e6bd23e6579d54c30db053a03f3"
    advice:
      - "The test suite needs the database container running; start it before running tests."
```

### Other fields

- **`description`**: one line for people choosing a work kind, such as in the console. It governs nothing, and no agent sees it.
- **`hosts`**: the environment the work's running application needs, when that differs from where the agent runs. The control plane checks it against the organisation's charted environments.
- **`variables`**: environment variables for what the flight runs, as names and literal values. They are never secrets. Names use only letters, digits and `_`, and do not start with a digit.
- **`consults`**: the other work kinds whose findings the control plane hands a flight of this kind. [Investigations and findings](/concepts/investigations-and-findings/#consults) explains it.

## Extending another work kind

A work kind can **extend** another and state only what it changes. The child names its parent with `extends:`, and inherits everything it leaves out:

```yaml
# work-kinds/investigate-instructions.yaml (an example)
extends: investigate
description: "Investigate a work item and write the implementation steps into it."
remove:
  destinations:
    - none
instructions:
  - "End the analysis with a numbered list of implementation steps."
destinations:
  instructions-field:
    kind: work-item-tracker
    requires:
      - investigate-finished
      - investigate-in-scope
    may-perform:
      - field
    may-write:
      - Custom.Instructions
```

The control plane resolves the chain first, applying each child over its parent, and then combines the result with root and narrowings as usual. The resolved work kind must be valid on its own.

### How a child changes what it inherits

| What | Rule |
|---|---|
| Single values and lists, such as `description`, `brief`, `hosts`, `accepts`, `produces` and `consults` | The child's value replaces the parent's whole. No list is merged item by item. |
| Loops, destinations and obligations | Matched by name. A child entry replaces the parent's entry of the same name whole; a new name is added. |
| `instructions` | The child's are added after the parent's. |
| `remove:` | Takes away the parent's loops, destinations or obligations by name, and instructions by their exact text. |

The control plane refuses a removal that matches nothing, naming it, so a parent reworded under its child fails at the child's next apply instead of being silently kept. Removing an obligation or a destination loosens the rules and needs approval like any other loosening change.

In the example, the child removes its parent's `none` destination before adding its own, because a work kind has one destination.

### What a child cannot do

- **Set root's fields or its own scope.** A child cannot set `context`, `environments`, `repositories`, `models` or the organisation's tool servers. It inherits its parent's.
- **Set `learned` or `variables`.** Both belong to complete documents.
- **Form a long chain.** A chain holds at most three work kinds, counting the top one. The top of the chain must be a complete work kind.
- **Change its parent.** A child's name is declared under its parent, and no one can change the parent once the name is declared. To move a child, retire it and declare it again.

### Abstract work kinds

A work kind that exists only to be extended is marked `abstract: true`. An abstract work kind:

- is never flown itself. The control plane refuses a flight that names it, and the message lists the work kinds that extend it;
- may leave out its destination, but may not declare more than one;
- is checked through each work kind that extends it.

Being abstract is not inherited: a child of an abstract work kind can be flown unless it is marked abstract too.

### A family of work kinds

A flight belongs to the **family** of every work kind in its chain. A flight of `investigate-instructions` in the example is also an `investigate` flight. Families decide which earlier findings the control plane hands a flight; see [Investigations and findings](/concepts/investigations-and-findings/#consults).

## How a flight's work kind is chosen

Every flight opens with at most one work kind, and keeps it:

- **`gg fly --work-kind <name>`** names it. The name must be a work kind the organisation has declared; the control plane refuses an unknown name, a name declared for something else, or an abstract work kind, and opens nothing.
- **With no work kind named**, the flight runs under the organisation's `implement` work kind. When the organisation has no `implement` work kind in force, the flight runs under root alone, and root's loop and destination govern it.
- **A nomination** names the work kind it would open. It must be on the `opens` list of the destination it stands under, or the control plane refuses it. This covers the legs of a plan, the flights a watch proposes, and the flights an agent proposes. See [Nominations and the board](/concepts/nominations-and-the-board/).
- **In the console**, starting a new flight offers the declared work kinds with their descriptions. Its first row sends no work kind, so the flight runs under `implement` as described above.

No one can change the work kind after the flight opens. A flight records every layer of its chain and the version of each that was in force, so a later change to a work kind does not change the rules of a flight already open.

## Related

- [Write a work kind](/guides/write-a-work-kind/): writing, checking, applying and extending a work kind.
- [The envelope](/concepts/envelope/): every field in full.
- [Change the airspace](/guides/change-the-airspace/): declaring names and applying documents.
