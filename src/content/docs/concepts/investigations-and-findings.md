---
title: Investigations and findings
description: How work that changes nothing is shaped, how an agent's run ends, what a finding is, and how a later flight on the same work is handed what earlier flights found.
sidebar:
  order: 8
---

Not every flight changes code. An **investigation** reads a work item and a repository and reports what it found: where a change would go, how to make it, and what could go wrong. What it leaves behind is a **finding**, and a later flight on the same piece of work can be handed that finding instead of starting again.

## What makes work an investigation

Good Grief has no special kind of flight for an investigation. An investigation is an ordinary [work kind](/reference/glossary/#work-kind) whose rules leave the agent nothing to do but read and report. A typical one has these parts:

| Part | Typical value | Why |
|---|---|---|
| [`loops`](/concepts/envelope/#loops) moves | `read`, `search`, `history`, `propose-landing` | The agent can read the tree and its history and propose a result, but has no move that edits or writes a file. |
| [`produces`](/concepts/envelope/#produces) | `landing.proposal`, `loop.outcome`, `loop.digest`, `loop.question` | The analysis travels as a landing proposal, and the run's outcome and any question it asked are recorded. |
| [`obligations`](/concepts/envelope/#obligations) | `loop-not-exhausted` and `no-file-outside-scope` | Machine checks only: the agent finished within its budget and changed nothing it should not have. |
| [`destinations`](/concepts/envelope/#destinations) | `kind: none` | Nothing leaves Good Grief. The flight's record is the result. |

```yaml
# work-kinds/investigate.yaml (an example, abridged)
brief: "Investigate the work item this flight names and work out how it should be implemented. Change nothing: the result is the landing proposed, and its description is the analysis."
accepts:
  - repository
  - tracker
produces:
  - landing.proposal
  - loop.digest
  - loop.outcome
  - loop.question
loops:
  investigate:
    executor: frontier
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
destinations:
  none:
    kind: none
    requires:
      - investigate-finished
      - investigate-in-scope
```

The agent writes its analysis as the description of the landing it proposes. A description may be up to 16 KiB (16,384 characters); a longer one is refused, not shortened.

A variant can send the same analysis somewhere else. A work kind that [extends](/concepts/work-kinds/#extending-another-work-kind) the investigation can replace its `none` destination with a `work-item-tracker` destination, so that the analysis is written into a field of the work item instead.

## How an agent's run ends

A flight runs one [loop](/reference/glossary/#loop), and one loop is one agent session. The session ends in one of four outcomes, which the runner records as the `loop.outcome` fact:

| Outcome | How the runner decides it | What it means |
|---|---|---|
| `exhausted` | The loop's `wall-clock` budget ran out, and the runner stopped the agent. | Waiting, not broken. The envelope's `on-exhaustion` says who takes over. |
| `failed` | The agent's session ended in an error. | Something went wrong, and the run said what. |
| `blocked` | The agent asked a question it is not allowed to answer itself, and changed nothing afterwards. | Waiting on a person, neither broken nor finished. |
| `completed` | None of the above: the session ended of its own accord. | The agent stopped on its own terms. |

Two rules shape these outcomes:

- **`blocked` is declared, never inferred.** The runner knows the agent asked because the agent called the tool for asking, not because of anything it wrote in its closing words. Text in a repository cannot make a flight look blocked or keep a stuck one quiet.
- **Asking and finishing are separate facts.** An agent that asks a question and then goes on to change the tree ends `completed`, with its question recorded beside it as `loop.question`. Only an agent whose question is the last thing it did ends `blocked`.

`completed` says that the session ended, not that the work is right. That judgement belongs to the envelope's obligations and the destination's `requires:`, and to the people who answer its [gates](/concepts/gates-and-decisions/).

### What the outcome means for the flight

The runner turns the loop's outcome into its report on the flight, as described in [Anatomy of a flight](/concepts/anatomy-of-a-flight/#what-a-runner-reports-and-what-it-means-for-the-flight):

- `failed` is reported as `failed`, and the flight ends `failed`.
- `blocked` and `exhausted` are reported as `outstanding`. The flight stays open and waits for a person.
- `completed` is reported as `completed`, unless something is still pending, such as a push or a landing the rules did not accept, in which case it is reported as `outstanding`.

For an investigation, whose destination is `none`, a completed run whose required obligations are satisfied ends the flight `landed`. The `loop-not-exhausted` check fails only when the outcome is `exhausted`. When no outcome was recorded, the check cannot be evaluated, and the flight [halts](/concepts/gates-and-decisions/#halting).

When the budget runs out, the envelope decides what follows. With `on-exhaustion: handoff-to-human`, the flight waits for a person. With `handoff-to-agent`, the flight is offered again for a new [attempt](/reference/glossary/#attempt), carrying what the last attempt tried, up to the loop's `budget.attempts`. Only running out of time triggers that automatic retry; a run that stopped for any other reason is not retried automatically.

## What a finding is

A **finding** is what a flight left for a person to read. Nothing new is stored to make one: a finding is read from the flight's own recorded facts, and it is one of two things:

- The **description of the landing the flight proposed**, as an investigation writes it.
- The **field value the flight wrote** to a work item, for a flight whose destination is a work-item tracker field. When the flight wrote several fields, each value is given with the field it went into.

Only the newest such fact of a flight counts. Only a flight that **landed** leaves a finding, and only a flight governed by a work kind.

Each finding carries a record of how it was made, assembled by the control plane from its own records and never from what the agent said about itself:

- the flight's number;
- its work kind, and every work kind in its chain with the version in force;
- when it was found;
- the model or models the agent ran on;
- the commit of each repository the flight read.

There is no separate command that lists findings. A finding is read with its flight: `gg show` and `gg facts` display it.

## How a later flight receives earlier findings

A flight on a piece of work that has already been investigated is handed what earlier flights found, so it does not repeat the investigation. Three things decide which findings it receives.

### Same intent

Findings are matched by [intent](/reference/glossary/#intent): what the flight was opened for. A flight opened for a work item, a link or a file receives findings from earlier flights opened for the same one. A flight opened with plain text has no intent key that another flight can share, so it receives none.

### `consults:`

A work kind lists the work kinds whose findings it wants with `consults:`:

```yaml
# work-kinds/implement.yaml (an example, abridged)
consults:
  - investigate
```

Each name refers to a **family**: every flight whose work kind is that name, or extends it. A flight of a work kind that extends `investigate` therefore counts as an investigation.

Every work kind consults its own family whether or not it says so, so a second investigation of the same item starts from the first. `consults:` adds other families. It belongs to work kinds only; root cannot declare it. A child work kind that leaves it out inherits its parent's list, and one that sets it replaces the list. Adding a family to the list loosens the rules, and waits for approval.

### Which findings are chosen

When a runner takes the flight, the control plane chooses its findings:

1. It looks at the twenty most recent other flights opened for the same intent. Older flights are not considered, even when they landed.
2. It keeps only those that landed and belong to a family the flight consults. A flight is never handed its own finding.
3. For each work kind among them, it keeps only the newest finding.

The findings travel with the runner's claim on the flight. If anything goes wrong while the control plane reads them, the flight still starts, with no findings.

### Where the agent sees them

The runner places the findings in the agent's instructions after what has been learned about the environment and after any note left by the agent that proposed the flight. They are introduced as earlier flights' findings, and closed by a statement that they are other agents' words, not instructions from the platform, and that they change nothing about what the agent may do.

Each finding is headed by the flight's number, its work kind and chain, when it was found and the models it ran on. The runner then compares the commit each repository was at when the finding was made with the commit the flight fetched, and tells the agent one of three things for each repository:

- the tree is at the same commit;
- the tree has moved, giving both commits, so the agent checks what the finding names before relying on it;
- the flight did not fetch that repository.

When no finding qualifies, nothing is added to the instructions.

## When something goes wrong

| What happened | What the later flight receives |
|---|---|
| The earlier flight failed, was grounded or withdrawn, or is still open. | Nothing from it. Only landed flights leave findings. |
| The earlier flight was opened with plain text, or the later one was. | Nothing. Text has no intent key to match. |
| The earlier flight ran under no work kind. | Nothing from it. |
| The earlier flight's family is not one the later flight consults. | Nothing from it. |
| The tree has moved since the finding was made. | The finding, with both commits named. |
| The finding is wrong now. | The finding, with the instruction to trust what the agent observes and say so. |

## Related

- [Work kinds](/concepts/work-kinds/): `extends`, families and `consults:`.
- [Anatomy of a flight](/concepts/anatomy-of-a-flight/): what a runner reports, and how a flight ends.
- [Fly from a work item](/guides/fly-from-a-work-item/): opening flights for the same intent, and listing them with `gg flights --intent`.
