---
title: Answer a gate
description: Find the flights waiting for a decision, read why each one is waiting, and approve or reject it from the terminal or the console.
sidebar:
  order: 2
---

A [gate](/reference/glossary/#gate) is a point where a flight waits for a person to approve or reject something, such as a pull request or a running preview. Use this guide when a flight is waiting on a decision: to find it, to understand exactly what the gate asks, and to record an answer. Nothing behind a gate proceeds until someone answers it. Waiting at a gate does not end the flight.

## Prerequisites

- gg is signed in to the organisation's control plane.
- The person answering is the gate's [approver](/reference/glossary/#approver), or may otherwise decide it. [Who may decide a gate](#who-may-decide-a-gate) explains the rules.

## 1. List what is waiting

Run `gg gates`:

```sh
gg gates
```

```
1 decision(s) waiting.

GG-42 - code-review
  approver: platform-owner
  commit:   3f2c1e9 on refs/heads/gg/GG-42
  when:     always (this obligation declares no condition)
  because:  <why the gate opened>
  since:    2026-10-14 14:38:03Z
```

Each entry names the flight and the **[obligation](/reference/glossary/#obligation)**, which is the thing awaiting a decision. The lines below it say:

| Line | Meaning |
|---|---|
| `approver` | Who the rules say may decide it: a role, such as `platform-owner`, or a named person. |
| `commit` | The commit and branch the decision is about. A decision that does not concern a repository says `none - this decision is not about a repository`. |
| `when` | The condition that made this obligation apply. `always` means the obligation has no condition. |
| `because` | Why the gate opened. When the agent stopped to ask a question, the question is the end of this sentence. |
| `since` | When the gate opened. |

When an agent proposed a flight, the entry adds a block that begins `an agent proposed this flight, in its own words`, followed by the kind of work, the environment and repository it asked for, its reason, and any note it left for the next agent. 

:::caution[An agent's own words]
Those are the agent's words, not the organisation's rules. Answering the gate is the only review they get before they reach the next agent.
:::

When nothing is waiting, gg says `Nothing is waiting on a decision.`

## 2. Read why the flight is stopped

`gg why` explains every obligation on a flight: whether it applied, why, and what was decided.

```sh
gg why GG-42
```

```
GG-42 — governed by envelope v20

code-review: attached
  when:     always (this obligation declares no condition)
  history:  attached 14:38

in-scope: attached
  when:     always (this obligation declares no condition)
  verdict:  satisfied
```

To read one obligation only, name it: `gg why GG-42 code-review`.

The first line names the version of the rules (the [envelope](/reference/glossary/#envelope)) that governs the flight. After it, gg may print two kinds of notice before the obligations:

- **`HALTED:`** followed by a reason. Good Grief found a rule it could not evaluate, so the flight stopped instead of guessing. The flight is still open.
- **A held leg.** When the flight is a [leg](/reference/glossary/#leg) of a plan that is waiting for another leg, a sentence names the leg it follows and how that leg ended.

Each obligation then appears as `<obligation>: <whether it applied>`, where the second part is one of:

- **`attached`**: the obligation applies to this flight.
- **`not-attached`**: Good Grief checked its condition, and it did not hold.
- **`unevaluable`**: Good Grief could not answer its condition.

The indented lines under it say more:

| Line | Meaning |
|---|---|
| `never` | This kind of work can never produce what the rule depends on, so the rule can never apply. This differs from a rule that Good Grief checked and that did not apply this time. |
| `when` | The obligation's condition. |
| `history` | Each change in whether it applied, with the time, such as `attached 14:38 -> not-attached 14:51`. |
| `because` | Why it applied or did not. |
| `verdict` | The result: `satisfied`, `violated` or `unevaluable`. An obligation with no verdict has not been decided yet. |
| `detail` | More about the result, such as the files outside the allowed scope. |

When gg prints `Nothing has been judged against this flight.`, either the envelope declares no obligation or Good Grief has evaluated nothing yet. A flight that has not reached its first gate reads this way. Run `gg show` to see its stage.

## 3. Record a decision

Run `gg decide` with the flight, the obligation and the outcome, `approved` or `rejected`, followed by a reason:

```sh
gg decide GG-42 code-review approved "Correct, and the test covers the expiry path."
```

A reason is optional when approving and required when rejecting. A reason may be up to 4,000 characters. Good Grief refuses a longer one rather than shortening it.

gg records the decision, then watches the gate until the decision is visible, and reports what it saw:

```
decided: the obligation is now satisfied
  looked:   2 time(s) over 1.5s of a 30s bound
  decided:  approved
  by:       Ada Lovelace
  at:       2026-10-14 14:52:10Z
  landing:  not yet - something else this destination requires is outstanding
```

- The first line is one of three: **`decided:`** with what the obligation became, **`refused:`** with the reason the control plane gave, or **`not yet visible:`**. The last is not a failure. gg sent the decision, and stopped watching before it appeared. Run `gg gates` to check before sending it again.
- **`looked`** says how many times gg checked and for how long.
- **`landing`** says whether its [destination](/reference/glossary/#destination) may now accept the work. `not yet` means another requirement of the destination is still outstanding. Otherwise the line names the destination and why it now accepts the work.

A decision applies to the gate as it was when gg looked it up, for that exact version of the work. When no gate is open for that obligation, because someone has already answered it or a new attempt replaced it, gg says that nothing is waiting on a decision about it and suggests `gg gates`.

## What rejecting does

Rejecting sends the work back. The agent makes another [attempt](/reference/glossary/#attempt), with the reason attached. Give a reason that says what to change. `gg show` numbers the attempts `#1`, `#2` and so on.

Rejecting the gate of a plan a person proposed works differently. The control plane declines every leg of that plan that is still waiting, and the plan's flight ends `withdrawn`. [Plan with itineraries](/guides/plan-with-itineraries/) covers plans.

## Who may decide a gate

The `approver` line says who the rules expect to decide. An approver takes one of two forms:

- **A role**, such as `platform-owner`, written as a bare word.
- **A named person**, written as `<provider>:<subject>`, the form `gg whoami` prints.

When the approver is a role, anyone in the organisation who may decide gates can answer it. The control plane does not check the role. To limit a gate to one person, name that person as the approver.

When the approver is a named person, only that person can decide the gate. The control plane refuses anyone else, including an administrator, and says whose gate it is. Gates that belong to a person's own [watch](/reference/glossary/#watch) work the same way: only that person can answer them. [Set up a watch](/guides/set-up-a-watch/) explains personal watches.

## The same steps in the console

Run `gg` with no arguments, then:

- `,` opens the queue, which lists what is waiting on a person.
- `d` starts deciding the selected flight's gate. In the window that opens, `a` approves, `r` rejects and `esc` closes without deciding.
- On an open flight, `a` approves and `r` rejects when a gate is waiting.
- When a gate is a runner asking for its agent to be signed in, `s` signs the agent in instead.

![The gate window for GG-48: the code-review obligation, its approver, the commit and branch, the condition that applied, why it applied, and how long it has waited.](/screenshots/console/gate-decision.svg)

## Related

- [The envelope: obligations](/concepts/envelope/#obligations): how an envelope declares obligations, conditions and approvers.
- [Anatomy of a flight](/concepts/anatomy-of-a-flight/): why a gate does not end a flight.
- [Take over a flight](/guides/take-over-a-flight/): continuing the work by hand instead of sending it back.
