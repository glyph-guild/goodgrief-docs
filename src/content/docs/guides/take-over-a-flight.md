---
title: Take over a flight
description: Take a flight from its runner, continue the work by hand, and hand it back with an outcome, or stop it altogether.
sidebar:
  order: 3
---

Use this guide when a flight needs a person rather than another attempt by the agent: the agent ran out of time and handed the work over, it is stuck on something a person can resolve quickly, or the work is easier to finish by hand. To [take over](/reference/glossary/#take-over) a flight is to hold it exclusively, continue the work, and then hand it back with an outcome. The guide also covers stopping a flight that should not continue at all.

## Prerequisites

- gg is signed in to the organisation's control plane. The control plane records a takeover against the signed-in person, so no one can take over a flight with a machine's own credentials.
- The flight's number, such as `GG-42`. `gg flights` and `gg gates` list them.

## 1. Take the flight

Run `gg take` with the flight:

```sh
gg take GG-42
```

gg first claims the flight for the signed-in person, then prints what the flight tried and ruled out so far, so the work can continue from where it stopped. After that, gg adds three notes:

- the time the hold lasts until, in UTC;
- how soon before that to renew it, or the control plane releases the flight and someone else may take it;
- the exact command for handing it back, with the list of outcomes.

Exactly one person holds a flight at a time, which stops two people working on the same thing. If someone else already holds it, gg refuses and names who holds it, since when and until when. Ask that person, or try again after the hold ends. A refused takeover changes nothing.

`gg take` fetches no code. It grants the hold and prints the record of the flight so far.

## 2. Keep the hold

To renew the hold, run `gg take GG-42` again before it lapses. Taking a flight again while holding it continues the same hold. Only its end time moves.

A hold expires on the clock, whether or not the work is still going on. When a hold lapses, the flight returns and another person may take it.

## 3. Hand it back

When the work is done, or when stopping, hand the flight back with `--return` and one of three outcomes:

| Outcome | Meaning |
|---|---|
| `completed` | The person finished the work. |
| `abandoned` | The person stopped, and the work stands where they left it. |
| `handing-back` | The person wants the agent to carry on. |

Add `--note` to say something about it for whoever reads the flight next:

```sh
gg take GG-42 --return completed --note "Fixed the expiry check and added a test for it."
```

gg records the outcome and prints the flight's log, where the handback appears as an entry naming the person. The entry can take a moment to appear. Run `gg log GG-42` again if it is not there yet.

If the hold moved on to someone else before the handback, gg refuses and records nothing, because a decision recorded against another person's hold would attribute their work to the wrong person. gg refuses an outcome other than the three above, and names it.

## Stop a flight instead

When the flight should not continue at all, ground it. A [grounded](/reference/glossary/#grounded) flight is one a person stopped while it could still have been done:

```sh
gg ground GG-42 "The fleet cannot serve this environment yet."
```

The reason is required. It tells a later reader why work that could have been done was not. gg prints the flight in its ending.

Grounding is not withdrawing. A flight is [withdrawn](/reference/glossary/#withdrawn) when the question it was answering stopped mattering, such as a work item someone closed. gg has no command that withdraws a flight. When a flight will not move and the question still matters, ground it.

## The same steps in the console

Run `gg` with no arguments, then:

- The console does not yet offer taking over or handing back. Use `gg take` in a terminal.
- On an open flight, `x` grounds it. The console asks first: `y` grounds it, and `esc` leaves it flying.
- `y` on the main screen flies a new flight by hand. The work happens on this machine, under the same rules as any other flight.

## Related

- [Answer a gate](/guides/answer-a-gate/): approving or rejecting the work instead of taking it over.
- [Anatomy of a flight](/concepts/anatomy-of-a-flight/): how a flight ends, and which endings belong to people.
- [The envelope: loops](/concepts/envelope/#loops): `on-exhaustion`, which decides who takes over when the agent's time runs out.
