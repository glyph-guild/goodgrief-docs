---
title: Write a work kind
description: Write the rules for one kind of work, check them, apply them, and make a variant of an existing work kind without copying it.
sidebar:
  order: 7
---

A [work kind](/reference/glossary/#work-kind) is the rules for one kind of work, such as an investigation, a review or a change. It supplies how the agent works, what the work produces and where it lands. Choose one for a flight with `gg fly --work-kind`. A flight opened without one runs under the organisation's `implement` work kind, or under root alone when there is none. Use this guide to write a new work kind, or to make a variant of an existing one.

[The envelope](/concepts/envelope/) describes each field in full. This page shows how the fields fit together in one file.

## Prerequisites

- A working copy of the airspace, pulled with `gg airspace pull`. [Change the airspace](/guides/change-the-airspace/) explains the cycle.
- Permission to apply airspace documents. A new work kind loosens the rules, so its approver also needs to be available.

## 1. Write the file

A work kind is one file in `work-kinds/`, named after the work kind. This example is an investigation that reads a work item and its repository and proposes an analysis without changing any file:

```yaml
# work-kinds/investigate.yaml (an example)

# For people choosing a work kind. No agent sees it.
description: "Analyse a work item for implementation. Changes no code."

# The job, in one sentence. It opens the agent's task.
brief: "Investigate the work item this flight names and work out how it should be implemented. Change nothing."

# Which files the agent may change, and the rules version root uses.
context:
  scope: "**"
  constitution: "1.0.0"

# What a flight of this kind may be about.
accepts:
  - repository
  - tracker

# What the work can yield. Obligations that need a fact not listed here never apply.
produces:
  - landing.proposal
  - loop.digest
  - loop.outcome
  - loop.question

# Standing guidance, passed to the agent word for word after root's.
instructions:
  - "Name only paths that were opened and read, not paths expected to exist."
  - "When the item is too unclear to analyse, return the question instead of a guess."

# What must be true before the work is accepted.
obligations:
  investigate-finished:
    check: machine
    rule: loop-not-exhausted
  investigate-in-scope:
    check: machine
    rule: no-file-outside-scope

# How the work is done: exactly one loop.
loops:
  investigate:
    executor: frontier
    model: claude-opus-5-5
    discharges:
      - investigate-finished
      - investigate-in-scope
    moves:
      - history
      - propose-landing
      - read
      - search
    budget:
      wall-clock: "20m"
    on-exhaustion: handoff-to-human

# Where finished work goes, and what it requires first.
destinations:
  none:
    kind: none
    requires:
      - investigate-finished
      - investigate-in-scope
```

What each field does, with a link to its full description:

| Field | Required | What it does |
|---|---|---|
| `description` | No | One line for people choosing a work kind, such as in the console. It governs nothing, and no agent sees it. |
| `brief` | No | The job a flight of this kind is to do, in one sentence. It is the first thing the agent's task says, so it is the place to say "change nothing" or "write a score, not code". |
| [`context.scope`](/concepts/envelope/#contextscope) | Yes | The files the agent may change. The flight receives the overlap of this and root's scope. `constitution` repeats root's value. |
| `accepts` | Yes | What a flight of this kind may be about: `repository` (a tree to work in), `tracker` (a backlog to read, with no tree), or `envelope` (an airspace document). An empty list means no subject. |
| [`produces`](/concepts/envelope/#produces) | Yes | The facts this work can yield. Leaving a fact out switches off the obligations that depend on it, so removing one counts as loosening the rules. |
| `instructions` | No | Standing guidance, passed to the agent word for word. Root's instructions come first, then the work kind's. |
| [`obligations`](/concepts/envelope/#obligations) | Yes | Machine checks and human checks. A human check opens a gate for its `approver`. |
| [`loops`](/concepts/envelope/#loops) | Yes | Who does the work, on which model, with which moves, for how long, and who takes over when time runs out. |
| [`destinations`](/concepts/envelope/#destinations) | Yes | Where finished work lands, and which obligations it requires. |

A work kind may also set `hosts` (the environment the work's running application needs, when that differs from where the agent runs) and `variables` (environment variables for what the flight runs; never a secret). Repositories, environments, the models a person may choose and the organisation's tool servers belong to root. The control plane refuses a work kind that sets a different value.

## 2. Check it

Check the file's shape before sending it anywhere:

```sh
gg envelope validate work-kinds/investigate.yaml
```

gg prints `This is a valid envelope.` and the form the control plane will store it in, or `This is not an envelope.` with the reason. It contacts nothing.

Then see what applying it would do:

```sh
gg airspace diff
```

A new work kind shows as `widening`. gg lists a file that does not read as a document with the reason.

## 3. Declare and apply it

Declare a new work kind's name before applying its file:

```sh
gg airspace apply --declare-names
```

Both the declaration and the new document loosen the rules, so gg reports the flights they opened and who each one awaits. Once someone answers those gates, the work kind is in force, and `gg fly --work-kind investigate` uses it.

To read the rules a flight of this kind would run under, run `gg envelope show investigate`. It prints root combined with the work kind, and marks each rule with the document it came from.

## Make a variant without copying

A work kind can extend another and state only what it changes. The child names its parent with `extends:`, and inherits everything it leaves out:

```yaml
# work-kinds/investigate-instructions.yaml (an example)
extends: investigate
description: "Investigate a work item and write the implementation instructions into it."
remove:
  destinations:
    - none
  instructions:
    - "When the item is too unclear to analyse, return the question instead of a guess."
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

Good Grief applies the child over its parent with these rules:

- **Single values**, such as `description`, `brief` or a loop's `model`, take the child's value when it gives one.
- **Lists**, such as `accepts`, `produces` and `hosts`, take the child's list whole. Good Grief merges no list item by item.
- **Loops, destinations and obligations** match by name. A child entry replaces the parent's entry of the same name whole, and a new name adds an entry.
- **Instructions** from the child follow the parent's.
- **`remove:`** takes things away from the parent: `loops`, `destinations` and `obligations` by name, and `instructions` by their exact text. Good Grief refuses a removal that matches nothing, and names it. If the parent is reworded, the child's next apply fails and says which removal no longer matches. Removing an obligation or a destination loosens the rules and needs approval like any other loosening change.

In the example, the child removes the parent's `none` destination and adds its own, because a work kind has one destination.

A chain holds at most three work kinds, counting the top one. A child cannot set root's fields or `context`. It inherits them.

Mark a base that exists only to be extended with `abstract: true`. No flight ever runs under it directly. It need not declare a destination, and Good Grief checks it through each work kind that extends it. A child does not inherit being abstract.

Declare a child's name under its parent. `gg airspace apply --declare-names` does this from the `extends:` line. Once the name is declared, its parent cannot change. `gg airspace show investigate-instructions` prints the child as written and then the result of applying it over its parent.

## Related

- [The envelope](/concepts/envelope/): every field in full, and how the layers combine.
- [Change the airspace](/guides/change-the-airspace/): pulling, applying and declaring names.
- [Fly from a work item](/guides/fly-from-a-work-item/): choosing a work kind for a flight.
