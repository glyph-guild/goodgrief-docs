---
title: Gates and decisions
description: How obligations are checked, when a flight stops at a gate, who may answer it, what each decision does, and why a flight halts instead of guessing.
sidebar:
  order: 4
---

Every flight is checked against the conditions its [envelope](/reference/glossary/#envelope) sets. Some of those conditions Good Grief checks itself. Others need a person, and the flight waits for that person at a **[gate](/reference/glossary/#gate)**. This page explains how conditions are checked, when a gate opens, what a person's answer (a **[decision](/reference/glossary/#decision)**) does, and what happens when a condition cannot be checked at all.

[Answer a gate](/guides/answer-a-gate/) gives the steps for finding a gate and recording a decision.

## Obligations

An **[obligation](/reference/glossary/#obligation)** is one condition a flight must meet. Each is one of two kinds:

| Kind | Declared as | Who answers it |
|---|---|---|
| **Machine check** | `check: machine` with a `rule` | Good Grief, from the facts the runner reported. |
| **Human check** | `check: human` with an `approver` | A person, at a gate. |

A machine check must name a rule and a human check must name an approver; a human check cannot also name a rule. Two rules exist:

- **`no-file-outside-scope`**: every file the flight changed is within the envelope's `context.scope`.
- **`loop-not-exhausted`**: the agent finished within its budget.

Obligations come from every layer of the envelope, and an obligation can carry a `when:` condition that decides whether it applies to a flight at all. [The envelope: obligations](/concepts/envelope/#obligations) lists the conditions.

```yaml
# An example: one check of each kind.
obligations:
  in-scope:
    check: machine
    rule: no-file-outside-scope
  code-review:
    check: human
    approver: platform-owner
```

### Two questions per obligation

Good Grief asks two separate questions about each obligation, and `gg why` shows both.

**Does it apply?** The answer is one of:

- `attached`: it applies to this flight.
- `not-attached`: its condition was checked and does not hold, or this kind of work can never produce what the rule depends on.
- `unevaluable`: the condition could not be answered.

Machine checks are not attached to flights that change no repository, such as a flight that proposes a document or a flight with no repository.

**What is the verdict?** For an obligation that applies:

- `satisfied`: the rule passed, or a person approved.
- `violated`: the rule failed, or a person rejected.
- No verdict yet: a human check is waiting at its gate. Waiting is not a failure: nothing is missing, and a person has not answered yet.

## When a gate opens

A gate opens when a human check applies to a flight. Good Grief decides this when it evaluates the flight's facts: after the agent has worked and the runner has reported what happened.

Two things can hold a gate back until there is something real to decide:

- **A pull request destination waits for the push.** For a flight whose work lands as a pull request, the gate opens only once the runner has pushed the branch, so the approver has real code to look at. The pull request itself opens after the decision. Flights that propose something rather than change a repository, such as a plan or a question the agent asked, are not held back this way.
- **Evidence must be assembled first.** When the obligation asks for evidence, Good Grief assembles it before the gate opens. See [Evidence](#evidence) below.

There is one gate per flight and obligation. It is not replaced on each attempt. When the work changes, the same gate opens again, and any earlier answer no longer counts. When the obligation stops applying, for example because a later change no longer touches the files its condition names, the gate is withdrawn.

While any gate on a flight is open, no runner is offered the flight.

## Who may decide a gate

The obligation's `approver` is written in one of two ways, and the control plane treats them differently:

- **A named person**, written as `<provider>:<subject>`, the form `gg whoami` prints. Only that person can decide the gate. Anyone else is refused, and nothing is recorded.
- **A role**, written as a bare word such as `platform-owner`. A role says who the organisation expects to decide. The control plane does not check the role itself: any person who is allowed to decide gates in the organisation can decide a gate that names a role.

To make sure only one person can answer a gate, name that person.

Some gates are routed to a particular person regardless of how they are written:

- A gate on a change that loosens a person's own [watch](/concepts/watches-and-sweeps/#the-organisations-watches-and-a-persons-own) belongs to that person.
- A human check on a flight running on a machine that a person has claimed belongs to that machine's owner.

Nothing prevents the person who requested a flight from deciding its gate.

## Evidence

An obligation can list `evidence:` to be assembled for its approver:

| Item | What it is |
|---|---|
| `change-manifest` | The files the flight changed. |
| `migration-list` | The database migrations among them. |
| `agent-account` | The agent's own account of what it did. |

```yaml
# An example.
obligations:
  migration-review:
    check: human
    approver: platform-owner
    when: "change.manifest touches db/migrations/**"
    evidence:
      - change-manifest
      - migration-list
```

An obligation may ask for at most five items. Good Grief assembles them before the gate opens, from the facts the runner reported. **If an item cannot be assembled, because the facts it needs are missing, the flight [halts](#halting)** with a message naming the item, and no gate opens. A gate never opens with its evidence silently missing.

## Decisions

A decision is one of two outcomes:

| Outcome | What it does |
|---|---|
| `approved` | The obligation is **satisfied**. The flight is evaluated again, and if nothing else its destination requires is outstanding, the work is accepted. |
| `rejected` | The obligation is **violated**. The flight is sent back for another [attempt](/reference/glossary/#attempt), and the reason travels to the agent with the next attempt. |

A reason is optional when approving and required when rejecting, because a rejection reason is what the next attempt works from. A reason may be up to 4,000 characters; a longer one is refused, not shortened.

There are no other outcomes. An obligation cannot be waived. To stop the work instead of sending it back, ground the flight with `gg ground`.

### Limits on sending work back

A rejection starts a new attempt only while the loop's `budget.attempts` allows it. Once that limit is reached, the flight waits for a person instead of running again.

If the work is unchanged after a rejection and the agent has run again, the gate opens again with an explanation, so the approver knows they are looking at the same work.

### Rejecting a plan

Rejecting the gate of a plan a person proposed does not send it back. Every leg that is still waiting is declined, and the plan's flight ends `withdrawn`. [Itineraries](/concepts/itineraries/#the-gate) explains plans.

### A decision is about one version of the work

A decision applies to the work as it was when the gate opened. Good Grief identifies that work by the content of the files it changed, not by a commit. If the work changes before the decision arrives, the decision is refused, with a message saying the work changed, and nothing is recorded. If the work changes after a decision, the gate opens again and the earlier decision no longer counts.

The first answer stands. A second, different answer to the same gate is refused. Sending the same answer again is accepted and changes nothing.

Decisions belong to one flight. An approval on one flight does not satisfy a gate on another.

## Decisions and the destination

Every [destination](/concepts/envelope/#destinations) lists the obligations it **requires**. The work is accepted at the destination only when every required obligation that applies is satisfied:

- A required obligation that is **waiting** at a gate holds the work until it is answered.
- A required obligation that is **violated** means the work is not accepted.
- A required obligation that is **not attached** is passed over.

An obligation the destination does not require cannot stop the work from being accepted. Its gate still opens if it is a human check, however, and an open gate keeps the flight from being offered to a runner until someone answers it.

```yaml
# An example destination.
destinations:
  pull-request:
    kind: pull-request
    requires:
      - in-scope
      - code-review
```

Here the pull request opens only once the scope check has passed and a person has approved `code-review`.

## Halting

Good Grief never guesses. When it cannot tell whether an obligation applies or whether it is met, it **halts** the flight instead of choosing an answer. A flight halts when:

- an obligation's condition or rule is `unevaluable`, for example because a fact it reads was never reported or holds a value Good Grief does not recognise;
- the flight's envelope cannot be determined;
- evidence an obligation asks for cannot be assembled.

A halted flight records no verdicts and opens no gates. It is **still open**: halting is not an ending. `gg why` prints `HALTED:` followed by the reason, and `gg log` shows the halt.

When a halt was caused by missing or unreadable facts, it stops counting as soon as new facts arrive, and the flight is evaluated again. When it was caused by the envelope or by evidence that cannot be assembled, it stands until the cause is fixed, such as by changing the envelope, or until a person ends the flight.

## Related

- [Answer a gate](/guides/answer-a-gate/): listing gates, reading `gg why`, and recording a decision.
- [The envelope](/concepts/envelope/): how obligations, conditions and destinations are declared.
- [Anatomy of a flight](/concepts/anatomy-of-a-flight/): where evaluation sits among a flight's stages.
