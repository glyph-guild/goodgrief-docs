---
title: Anatomy of a flight
description: The stages a flight moves through, the ways it can leave early, how it ends, and when Good Grief checks each rule.
sidebar:
  order: 1
---

A [flight](/reference/glossary/#flight) is one piece of requested work. This page follows a flight from the moment it opens to the moment it ends. Along the way it covers where Good Grief checks the organisation's rules, and what each status means.

## Which rules apply

When a flight opens, Good Grief determines its rules once, by combining three layers:

> the rules for one flight = **root** + **work kind** + **narrowings**

- **Root** is the organisation's base rules. It alone decides which repositories and environments flights may use.
- The **[work kind](/reference/glossary/#work-kind)** describes one kind of work, such as an investigation, a review or a change. It decides how that work is done and where it lands.
- **Narrowings** are additional approvals a repository requires for itself.

The combined result is the flight's **[envelope](/reference/glossary/#envelope)**. [The envelope](/concepts/envelope/) describes what each layer contributes, field by field.

## Six stages

```
Created → Ready → Leased → Worked → Evaluated → Ended
```

| Stage | What happens |
|---|---|
| **Created** | Someone has opened the flight, and Good Grief has determined its rules. |
| **Ready** | Everything the flight needs before it can start is in place. It is waiting for a machine. |
| **Leased** | A [runner](/reference/glossary/#runner) has claimed the flight, and no other machine can take it. |
| **Worked** | The agent has run. |
| **Evaluated** | Good Grief has checked the agent's work against the rules, including which files changed and what requires approval. |
| **Ended** | The flight has its final outcome. |

These are **stages, not statuses**. A flight can remain in a stage for some time, waiting for a machine or a person, without anything being wrong.

## Three ways to leave early

Not every flight passes through all six stages:

- **Rejected when opened.** The request to open the flight fails, and Good Grief creates no flight. This happens when a request names an environment that does not exist or a repository that no one registered, or when the rules contradict each other. gg states which.
- **Halted.** Good Grief found a rule it cannot evaluate as yes or no. It stops and reports the rule rather than guessing. **The flight is still open**: once someone fixes the rule, it can continue.
- **Sent back.** The work gets another attempt, because a reviewer rejected it or it ran out of time. Each retry is a new attempt. When retries happen automatically after the time runs out, the envelope's attempt limit decides when to stop and wait for a person.

## Waiting is not the same as finished

A flight can stop because no machine is free, because a person has not answered yet, because time ran out, or because Good Grief could not check a rule. **None of these ends the flight.** Until something ends it, the flight stays `open`, and a runner can pick it up again later.

A flight ends in exactly one of four ways:

| Ending | Meaning |
|---|---|
| `landed` | Somewhere accepted the work. |
| `grounded` | A person stopped it. |
| `withdrawn` | The question stopped mattering. |
| `failed` | The work finished, but nowhere accepted it. |

Two other words can appear, and neither is an ending:

- `open`: nothing has ended the flight yet, and something still can.
- `unknown`: Good Grief cannot account for the flight's state. Run `gg bundle` and send the result to the Good Grief team.

## What a runner reports, and what it means for the flight

A runner never decides how a flight ended. It reports only what happened to **its own turn** at the work, and Good Grief decides what that means for the flight. A machine therefore never declares its own work accepted.

| Runner reports | Meaning | The flight | Offered to another machine? |
|---|---|---|---|
| `completed` | The runner finished, and somewhere accepted the work. | **landed** | No. It is done. |
| `failed` | The runner finished, and nowhere accepted the work. | **failed** | No. It is done. |
| `outstanding` | The runner has stopped for now. Nowhere accepted the work, and a person needs to answer something. | stays open | No. It is waiting on a person. |
| `abandoned` | The runner gave up, but the work remains available. | stays open | Yes. |
| `expired` | Good Grief reports it, not the runner: the machine stopped checking in while it held the flight. | stays open | Yes. |

Only two of these end the flight. The other three leave it open, and one question separates them: **should another machine pick it up?**

A runner cannot report `grounded` or `withdrawn`. Those endings belong to people, and only people record them.

### Why `outstanding` exists

Consider an agent that stops to ask a question. Without `outstanding`, the runner would have had two options, and neither would be accurate:

- `completed` would record the work as accepted, which it was not.
- `abandoned` would return the flight to the queue. The next machine would run the same agent into the same question and ask it again.

`outstanding` states what actually happened. The work is waiting on a person, and should not go to another machine.

### One word, two meanings

`completed` means different things at two levels:

- When the **agent's run** ends `completed`, the agent stopped of its own accord.
- When the **runner** reports `completed`, somewhere accepted the work.

An agent's run can therefore finish while the flight is still waiting on a person:

```
the agent's run ended  blocked
  → the runner reports  outstanding
    → the flight is  open
```


## When each rule is checked

Good Grief does not check the envelope all at once at the end. It checks each field at a particular stage. When a flight stops or Good Grief rejects it, the stage points to the field responsible.

| Field | Checked at | Set by | In short |
|---|---|---|---|
| [`repositories:`](/concepts/envelope/#repositories) | Created | Root | Which repositories a flight may concern. |
| [`environments:`](/concepts/envelope/#environments) | Created, then Ready → Leased | Root | Where the work may run, and so which machines may take it. |
| [`loops:`](/concepts/envelope/#loops) | Leased → Worked | Work kind | Which agent runs, what it may do, and for how long. |
| [`context.scope:`](/concepts/envelope/#contextscope) | Evaluated | Root and work kind together | Which files the agent may change. |
| [`obligations:`](/concepts/envelope/#obligations) | Evaluated | Every layer | What must be true, and what a person must approve. |
| [`produces:`](/concepts/envelope/#produces) | Evaluated | Work kind | What the work yields, which decides which obligations can apply. |
| [`destinations:`](/concepts/envelope/#destinations) | Evaluated → Ended | Work kind | Where finished work goes, and what it requires first. |

[The envelope](/concepts/envelope/) describes each field in detail, with examples.

### A gate does not stop everything

While a flight waits at a [gate](/reference/glossary/#gate), the runner still pushes the branch, so there is real code to review. It does not open the pull request until a person answers the gate. For example, a work kind that requires a person to approve a running preview before its pull request opens lists that approval in the destination's `requires:`. The branch exists for review, and the pull request follows the approval.
