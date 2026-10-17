---
title: The envelope
description: The rules that govern a flight, field by field. What each one decides, when it is checked, what happens when it does not match, and how the layers combine.
sidebar:
  order: 2
---

The **envelope** is the set of rules that governs a [flight](/reference/glossary/#flight). It decides which repositories a flight may concern, where it may run, how the agent works, which files it may change, what must be approved, and where finished work goes.

Good Grief determines every flight's envelope once, when the flight opens. It then checks each field at a particular [stage](/concepts/anatomy-of-a-flight/#six-stages) of the flight, so when a flight stops or is rejected, the stage points to the field responsible.

## Where the rules come from

An envelope combines three layers:

> the rules for one flight = **root** + **work kind** + **narrowings**

| Layer | What it is | What it contributes |
|---|---|---|
| **Root** | The organisation's base rules. | `repositories:` and `environments:`, which only root may set. Its share of `context.scope:` and its obligations. |
| **[Work kind](/reference/glossary/#work-kind)** | The rules for one kind of work, such as an investigation, a review or a change. | `loops:`, `produces:` and `destinations:`, which replace root's entirely. Its share of `context.scope:` and its obligations. |
| **Narrowings** | Rules a repository declares for itself. | Additional obligations only, each of which the destination also requires. |

A work kind may repeat a value only root may set, but Good Grief rejects a different one. `context.scope:` is the overlap of root's scope and the work kind's. Obligations add up across all three layers.

| Field | Checked at | Set by | In short |
|---|---|---|---|
| [`repositories:`](#repositories) | Created | Root | Which repositories a flight may concern. |
| [`environments:`](#environments) | Created, then Ready → Leased | Root | Where the work may run, and so which machines may take it. |
| [`loops:`](#loops) | Leased → Worked | Work kind | Which agent runs, what it may do, and for how long. |
| [`context.scope:`](#contextscope) | Evaluated | Root and work kind together | Which files the agent may change. |
| [`obligations:`](#obligations) | Evaluated | Every layer | What must be true, and what a person must approve. |
| [`produces:`](#produces) | Evaluated | Work kind | What the work yields, which decides which obligations can apply. |
| [`destinations:`](#destinations) | Evaluated → Ended | Work kind | Where finished work goes, and what it requires first. |

The examples below come from a real organisation's envelope, with repository names changed.

## `repositories:`

**What it decides.** The repositories a flight may concern. Root declares one name or a list. Leaving the field out places no limit on repositories.

**When it is checked.** When the flight is created. Every repository the flight names must be on the list. A flight that names no repository inherits the list's only entry when the list has exactly one.

**What happens when it does not match.** The request to open the flight fails, and Good Grief creates no flight. The message names the repository the request named and the repositories the envelope allows.

```yaml
repositories:
  - "example-org/web-app"
  - "example-org/api"
```

Only root may set this field. A work kind may repeat root's value, but Good Grief rejects a different one.

## `environments:`

**What it decides.** Where the work may run, such as a general development machine (`dev`) or one that can run a browser (`ui`). Root declares one name or a list, chosen from the environments the organisation has charted.

**When it is checked.** Twice:

1. **When the flight is created**, its environment must be on the list. As with repositories, a flight that names none inherits the list's only entry when there is exactly one.
2. **When the flight is ready**, its environment becomes a requirement on the machine. The control plane offers the flight only to a runner that advertises the environment, as the label `environment=<name>`.

**What happens when it does not match.** Good Grief rejects an environment that is not on the list the same way: the request to open the flight fails. An environment that no runner advertises is not an error: the flight waits in Ready until a matching machine appears. `gg runner labels` shows what each runner advertises.

```yaml
environments:
  - dev
  - ui
```

Only root may set this field.

## `loops:`

**What it decides.** How the work is done. Each envelope has exactly one loop, and the loop says:

- **`executor`**: who does the work. `frontier` means an AI agent; `human` means a person.
- **`model`**: which model the agent runs on. Leaving it out uses the account's default.
- **`moves`**: what the agent is allowed to do, such as `read`, `search`, `edit`, `run-tests` and `write`. Moves that open something for review include `propose` and `propose-landing`. The single move `anything` removes the list entirely and must appear on its own.
- **`budget`**: how long the agent has (`wall-clock`, such as `20m`) and, optionally, how many times the work may run again automatically when that time runs out (`attempts`). The limit applies when `on-exhaustion` is `handoff-to-agent`; once the flight reaches it, the flight waits for a person instead. Leaving out `attempts` sets no limit.
- **`on-exhaustion`**: who takes over when the budget runs out: `handoff-to-human` or `handoff-to-agent`.
- **`discharges`**: which of the envelope's checks this loop is responsible for satisfying.
- **`mcp`**: optionally, which tools from the organisation's MCP servers the agent may call.

**When it is checked.** When a runner claims the flight, the loop's settings travel with it. The runner then enforces them while the agent works: it blocks a tool call outside the allowed moves when the agent attempts it.

**What happens when the budget runs out.** The loop ends `exhausted`, and the work is handed over as `on-exhaustion` says. The flight stays open.

```yaml
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
```

This investigation can read, search and look through history, and can propose a result for a person to accept. It cannot edit files. It has twenty minutes, and when those run out, a person takes over.

The work kind's loop replaces root's entirely. Root's loop applies only to flights with no work kind.

## `context.scope:`

**What it decides.** Which files the agent may change. The scope is a path pattern: `**` means anywhere in the repository, and `.goodgrief/**` means only files under `.goodgrief/`. Work that has no repository, such as a change to the rules themselves, uses the word `none`.

**When it is checked.** At Evaluated. The check covers every file the flight changed at any point during its work, not only the files in the final result, so a change the agent made and later undid still counts.

**What happens when it does not match.** The envelope's scope check (the `no-file-outside-scope` rule) fails. gg lists the files outside the scope and the scope that was allowed. A person's approval cannot excuse this; the only way to allow those files is to change the scope in the envelope, and someone reviews that change in turn. If the flight cannot report which files changed, Good Grief cannot evaluate the check and the flight halts.

```yaml
context:
  scope: ".goodgrief/**"
```

Root and the work kind each declare a scope, and the flight receives the **overlap** of the two. For example, root's `**` and a work kind's `.goodgrief/**` give `.goodgrief/**`. If neither scope contains the other, Good Grief rejects the combination.

## `obligations:`

**What it decides.** What must be true about the work, and what a person must approve. Each obligation is one of two kinds:

- A **machine check** (`check: machine`) is a rule Good Grief evaluates itself. The available rules are `no-file-outside-scope` (the agent stayed within `context.scope`) and `loop-not-exhausted` (the agent finished within its budget).
- A **human check** (`check: human`) is a decision a person makes, with an `approver` who may make it. A human check that applies to a flight opens a **[gate](/reference/glossary/#gate)**.

An obligation can carry a condition (`when:`) that decides whether it applies to a flight at all:

| Condition | Applies when |
|---|---|
| `change.manifest touches <pattern>` | The flight changed a file matching the pattern. |
| `envelope widens` | The flight proposes loosening the rules. |
| `moves used include <move>` | The agent used a particular move. |
| `loop asked for a decision` | The agent stopped to ask a question. |
| `loop changed nothing` | The agent finished without changing anything. |

An obligation with no condition applies to every flight. An obligation can also require `evidence`, such as the list of changed files, for Good Grief to attach for the approver.

**When it is checked.** At Evaluated. Every obligation ends up in one of these states:

- **Satisfied**: the rule passed, or a person approved.
- **Violated**: the rule failed, or a person rejected.
- **Awaiting**: a gate is open and waiting on its approver.
- **Not attached**: its condition did not apply to this flight.
- **Unevaluable**: Good Grief could not tell. This halts the flight.

**What happens when it is not met.** That depends on the destination, described [below](#destinations). A destination lists the obligations it requires, and only those obligations block it. An obligation awaiting a decision is not a failure: nothing is missing, and a person simply has not answered yet.

```yaml
obligations:
  in-scope:
    check: machine
    rule: no-file-outside-scope
  widen-root:
    check: human
    when: "envelope widens"
    approver: platform-owner
```

The first obligation checks that the agent stayed within scope. The second means that any change loosening the organisation's rules waits for a platform owner's approval.

Obligations **add up** across layers: a flight carries root's obligations, the work kind's, and any the repository's narrowings declare. Two layers may not declare an obligation with the same name.

## `produces:`

**What it decides.** What this kind of work yields, as a list of named facts. Examples include `change.manifest` (the list of files changed), `loop.outcome` (how the agent's run ended), `loop.digest` (a summary of the run) and `preview.url` (a link to a running preview).

**When it is checked.** At Evaluated. Good Grief marks an obligation that depends on a fact this kind of work never produces **not attached**, instead of halting the flight. A review that changes no files, for example, does not produce `change.manifest`, so a scope check cannot apply to it.

**What happens when it is wrong.** Nothing fails while the flight runs. Leaving a fact out of `produces:` quietly switches off the obligations that depend on it. For that reason, removing a fact from the list counts as loosening the rules, and needs approval.

```yaml
produces:
  - loop.digest
  - loop.outcome
  - loop.question
```

Every work kind must declare `produces:`, even when the list is empty. Root does not declare it.

## `destinations:`

**What it decides.** Where finished work goes. Each work kind has one destination, and its `kind` is one of the following:

| Kind | Where the work lands |
|---|---|
| `pull-request` | A branch and a pull request in the repository. |
| `work-item-tracker` | Changes to work items, such as creating one or setting a field. |
| `flight` | New flights. Used by planning work, which proposes the flights that follow it. |
| `envelope-change` | A change to the organisation's rules. |
| `airspace-registration` | A newly registered name, such as a repository. |
| `check-run` | A check result on a commit. |
| `none` | Nowhere. The flight's record is the result, as with an investigation. |

Every destination lists the obligations it **requires**. Other settings depend on the kind:

- A `pull-request` can name the `branch` (it must include `{flight}`, and it is `gg/<flight>` by default). Setting `preserve-unadmitted: true` keeps work that Good Grief did not accept, by pushing it to a separate branch for a person to look at.
- A `work-item-tracker` lists what it may do (`may-perform`, such as `create`, `update` or `field`) and which fields it may write (`may-write`).
- A `flight` lists which kinds of flight it may open (`opens`), whether they open straight away or wait for approval (`opens-as: auto` or `gated`), and how many it may open at once (`cap-per-pass`).

**When it is checked.** As the flight is evaluated and ended. Good Grief checks the obligations the destination requires. When all of them are satisfied, it accepts the work and the flight ends **landed**. When one is still awaiting a decision, the flight waits at that gate. When one is violated, it does not accept the work.

**Permission is not the same as ability.** The envelope grants permission to land the work, but the runner performs the landing with the organisation's own credential. A pull request needs a credential with write access to the repository. If the credential is read-only, the landing fails at the credential, and gg names it.

```yaml
destinations:
  pull-request:
    kind: pull-request
    requires:
      - in-scope
      - loop-finished
    preserve-unadmitted: true
    branch: "refs/heads/feature/{flight}-{ticket}"
```

The destination comes entirely from the work kind. The only additions come from repository narrowings: Good Grief adds each obligation a narrowing declares to the destination's `requires:` list automatically.

## Changing the rules

Rules live in documents (root, work kinds and narrowings), and those documents are versioned. Good Grief compares each new version with the version in force:

- A change that **tightens** the rules, such as removing a move or shortening a budget, applies directly.
- A change that **loosens** them, such as adding a repository, adding a move, removing an obligation or lengthening a budget, does not apply straight away. It opens a flight that waits for the approver named by root's `envelope widens` obligation. If root declares no such obligation, Good Grief rejects loosening changes.

Good Grief always rejects unknown fields and values, with a message naming them, so it never silently ignores a misspelt rule.
