---
title: Itineraries
description: How a plan of several flights is proposed, approved once and opened, how legs follow one another, how they are numbered, and what an itinerary does not do.
sidebar:
  order: 7
---

An **[itinerary](/reference/glossary/#itinerary)** is a plan made of several flights that pursue one goal together. Each flight in it is a **[leg](/reference/glossary/#leg)**. An itinerary exists for work that is too large or too varied for one flight: for example, investigating an item, then implementing it, then reviewing the result.

A plan is proposed as a whole, a person approves its shape once, and only then do its legs open. [Plan with itineraries](/guides/plan-with-itineraries/) gives the steps for writing, checking and proposing one.

## One flight, one loop; several flights, one itinerary

A [flight](/reference/glossary/#flight) runs one [loop](/reference/glossary/#loop), and one loop is one agent session. When a flight's work is not right yet, it runs again inside the same flight: a rejected decision sends it back for another [attempt](/reference/glossary/#attempt), with the same branch, the same pull request and the same gate. Rework does not need an itinerary.

An itinerary is for work that needs **different flights**, usually of different work kinds, each with its own result.

## What an itinerary is

An itinerary is a numbered record that groups the legs of one plan. Its number has the form `ITN-63`. Numbers only increase, and a number can be skipped, so a gap means nothing.

An itinerary holds no status of its own. What it shows, such as how many legs are still standing, is read from its legs each time it is displayed.

A leg is a **[nomination](/concepts/nominations-and-the-board/)**: a proposal that some work should become a flight. Each leg names its work kind, its subject (which piece of work it is) and a reason, and optionally a repository, an environment, a note for the agent that flies it, and the leg it follows. When the plan is approved, each leg opens as an ordinary flight, with its own number, rules and gates.

Legs are listed with their plan, by `gg itineraries` and `gg itinerary show`, rather than on the board.

## Two ways to propose a plan

### A planning flight

A **planning flight** is a flight whose work kind has a `flight` destination: instead of doing the work, its agent proposes the legs. The destination's `opens` list is the menu of work kinds a leg may use, and its `requires:` usually includes a human check, so that a person approves the plan before any leg opens.

```yaml
# An example destination for a planning work kind.
destinations:
  the-plan:
    kind: flight
    requires:
      - plan-reviewed
    opens:
      - investigate
      - implement
      - review
    cap-per-pass: 5
```

When the agent nominates legs with subjects, Good Grief creates an itinerary for that flight's plan. A later run of the same planning flight can revise the plan:

- a leg proposed again unchanged is the same leg;
- a leg proposed again with a change replaces the earlier version;
- a leg the revised plan no longer names is dropped, if it is still standing. A leg that has already opened is untouched.

### A person

A person can propose a plan directly, as a file with `gg itinerary propose`, or by drafting it with an agent through `gg itinerary tools`. The plan is checked against a planning work kind (`plan` unless the file names another) exactly as `gg itinerary check` would check it, and:

- **A plan with any refused leg is refused whole.** Only a plan the check would accept can be proposed.
- **The planner's destination must require at least one human check, and only human checks.** A person's plan has no agent run to produce the facts a machine check reads, so a machine check could never be satisfied.

A proposed plan is held by a flight of the planner's work kind that no runner ever takes. It exists only to carry the plan's gate.

The same draft proposed twice by the same person is one plan. A changed draft is a new plan, unless it replaces the earlier one: proposing a revised draft through the agent tools replaces the plan it was drafted from, as long as that plan is the same person's, has not already been replaced, and has not been approved. The replaced plan's flight ends `withdrawn` and its legs are declined. Two attempts to replace the same plan at once cannot both succeed.

## The gate

A plan's gate appears in `gg gates` like any other, and is answered with `gg decide`. [Gates and decisions](/concepts/gates-and-decisions/) explains gates in general.

| Decision | What happens |
|---|---|
| **Approved** | The legs open as flights, subject to the rules as they stand. The plan's own flight ends `landed`. |
| **Rejected** | Every leg that is still standing is declined, and the plan's flight ends `withdrawn`. A rejected plan is not sent back for another attempt. |

Each leg's flight belongs to the person who proposed the plan, or, for a planning flight, to the person who opened that flight. It does not belong to the person who approved it.

When the plan is approved, the legs are still judged one by one. A leg whose work kind is no longer on the menu, or whose rules no longer combine, ends `refused` with the reason.

### A plan larger than its cap

The planner's destination may set `cap-per-pass`, the most legs one plan may open. A plan with more legs is refused entirely: every leg ends `refused`. The plan is never opened in part. Separately, a plan file may hold at most 50 legs.

## Legs that follow other legs

By default, every leg of an approved plan can be taken as soon as a machine is free, in whatever order the queue offers them. A leg whose work depends on another leg's result says so with `after`:

```yaml
# An example: the fix waits for the investigation.
legs:
  - subject: find where sessions expire
    work-kind: investigate
    reason: The item does not say which service sets the timeout.
    repository: web-app
  - subject: fix the session expiry
    work-kind: implement
    reason: The change itself, once the cause is known.
    after: find where sessions expire
    repository: web-app
```

The rules for `after`:

- **It names one leg, by subject, in the same plan.** A leg cannot wait for two legs. A leg that needs two results follows the later of them, or is split.
- **It is enforced when a machine asks for work.** A leg is not offered to any runner until the leg it follows has **landed**. Nothing wakes the leg up: it is simply passed over until its predecessor lands.
- **A predecessor that does not land holds its followers for good.** If the leg it follows is grounded, fails or is withdrawn, the follower is never offered, because the premise it was written on is false. Nothing expires the hold. A person ends the held legs, for example with `gg ground`.
- **Only real dependencies should be ordered.** Ordering independent legs turns one plan into a queue of waits.

A held leg says why. `gg why`, `gg show` and the console name the leg it follows and what happened to it: that it has not landed yet, or that it ended some other way and the held leg will never be offered.

### Plans that cannot be ordered

A plan whose `after` lines cannot be satisfied is refused:

- A leg that follows itself is refused when it is nominated.
- An `after` that names no leg in the plan, or matches more than one leg, is refused.
- A ring of legs that follow each other, which would never start, is refused.

`gg itinerary check` reports these before anything is proposed. When a planning flight's plan cannot be ordered, every leg is refused.

## How legs are numbered and ordered

Legs that open are given flight numbers **in the order the plan lists them**, so the first leg written gets the lowest number. A leg that is refused gets no number.

The order of the list decides only the numbering. It does not decide when a leg runs: `after` does. Two legs with no `after` between them can run in either order, or at the same time.

Every leg needs a subject, and two legs of the same work kind need different subjects. The same subject under two different work kinds is allowed.

## What an itinerary does not do

An itinerary holds no process. Nothing polls it, wakes it or advances it. The `after` line is read in two places only: when a runner asks for work, and when a person asks why a leg has not started. Several things follow from that.

| An itinerary does not | What that means in practice |
|---|---|
| End by itself, or have an ending of its own | No command ends an itinerary. Ending its work means ending its legs, each with `gg ground`. |
| Expire a waiting leg | A leg held behind a predecessor that did not land waits until a person ends it. |
| Schedule by time | There is no "not before" and no deadline. A leg runs when its predecessor has landed and a machine is free. |
| Wait for more than one leg | Each leg follows at most one other. |
| Set priorities | Legs are offered in the order they became ready. |
| Re-plan when a leg fails | A refused or failed leg stays refused or failed. A new plan is proposed by a person or a new planning flight. |
| Report a leg's place in the queue | `gg why` says what a held leg follows; it does not say how many flights are ahead of a ready one. |
| Run legs on the same machine | Each leg is an ordinary flight, offered to any machine that meets its requirements. |

## Related

- [Plan with itineraries](/guides/plan-with-itineraries/): writing, checking, proposing and following a plan.
- [Nominations and the board](/concepts/nominations-and-the-board/): what a leg is before it opens.
- [Gates and decisions](/concepts/gates-and-decisions/): approving or rejecting the plan.
