---
title: Use the board
description: Read the work someone has proposed but no one has started, and open it as a flight or decline it, with a reason either way.
sidebar:
  order: 4
---

The [board](/reference/glossary/#board) lists work that someone has proposed but that has not become a flight yet. Each entry is a [nomination](/reference/glossary/#nomination): a proposal that some work should become a flight, together with the kind of work it needs and why. Use this guide to see what someone has proposed, to decide which proposals become flights, and to find out why a proposal never became one.

A gate is a flight that has stopped and is waiting on a person. A nomination is one step earlier: work that has not started.

## Where nominations come from

Nominations arrive from several places:

- **[Watches](/reference/glossary/#watch).** A watch looks at something on a schedule, such as a work-item query, and nominates work from what it finds. [Set up a watch](/guides/set-up-a-watch/) covers them.
- **Plans.** A planning flight, or a plan a person proposes, nominates each of its legs. `gg itineraries` lists legs with their plan; the board does not. [Plan with itineraries](/guides/plan-with-itineraries/) covers plans.
- **Pull requests.** A pull request opened or updated in a registered repository can nominate a flight, such as a review.
- **Flights opened directly.** A flight opened with `gg fly` also passes through the board, as a nomination that opens at once. It never waits there.

## Auto or gated

A `flight` [destination](/concepts/envelope/#destinations) bounds every nominator, and its `opens-as` setting decides how a nomination opens:

- **`auto`** (the default): the nomination opens as a flight straight away, if the rules allow it. No one needs to answer it.
- **`gated`**: the nomination waits on the board until a person opens or declines it.

An `auto` nomination can still wait. When a nominator has spent its budget, such as five flights in a day, its nominations become gated, and the board says why.

```yaml
# An example destination for a planning work kind.
destinations:
  the-plan:
    kind: flight
    requires:
      - plan-reviewed
    opens:
      - implement
      - review
    opens-as: gated
    cap-per-pass: 5
```

Changing `auto` to `gated` tightens the rules. Changing `gated` to `auto` loosens them, so it waits for approval.

## 1. Read the board

Run `gg board`:

```sh
gg board
```

```
1 nomination(s) standing. Ended ones are not shown - gg board --all.

01a0792a-5c4e-4b1f-9d3e-2f6a8c1b7e44 - review
  nominated by: watch:triage
  about:        https://dev.azure.com/example-org/example-project/_workitems/edit/1234
  standing:     gated - waiting for a person to answer it
  nominated:    2026-10-14 15:02:41Z
```

Each nomination shows:

| Line | Meaning |
|---|---|
| The first line | The nomination's id, then the work kind it would open. A nomination has no flight number, because it is not a flight yet. |
| `nominated by` | What proposed it, such as a watch or a plan. |
| `for` | The person it belongs to, when it came from a person's own watch. Only that person may answer it. |
| `about` | The piece of work, such as a work item's address. Free-text work says so. |
| `standing` | `gated` when it is waiting for a person to answer it, or `auto` when no one needs to. |
| `because` | Why a gated nomination is gated, when the gate came from a spent budget. |
| `nominated` | When the nominator proposed it. |

`gg board --all` includes nominations that have ended, each with an `ended` line, a `because` line and, when it opened, the `flight` it became. A nomination ends in one of six ways:

| Ending | Who ended it |
|---|---|
| `opened` | It became a flight. |
| `declined` | A person said no. |
| `refused` | The rules said no, and the reason names the rule. |
| `superseded` | A newer version of the same work arrived. |
| `lapsed` | No one opened it in time. |
| `dropped` | The plan that named it no longer does. |

Only `opened` and `declined` are a person's decision; the others belong to the board, the clock and the rules.

## 2. Open or decline a nomination

Use the full id that `gg board` prints, and a reason. The reason is required either way, because it is the only record of why a person opened work no one asked for, or declined work someone did:

```sh
gg board open 01a0792a-5c4e-4b1f-9d3e-2f6a8c1b7e44 "This item blocks the release."
gg board decline 01a0792a-5c4e-4b1f-9d3e-2f6a8c1b7e44 "Already fixed in the current sprint."
```

Opening a nomination asks the board to open it. The board still applies the rules, and may refuse. gg therefore reports what the board recorded, not what the person asked for:

```
01a0792a-5c4e-4b1f-9d3e-2f6a8c1b7e44 - review
  about:        https://dev.azure.com/example-org/example-project/_workitems/edit/1234
  ended:        opened
  because:      This item blocks the release.
  flight:       GG-61

  looked:   2 time(s) over 0.6s of a 30s bound
```

If the board has not settled when gg stops watching, gg says the board recorded the decision and the outcome is not known yet. Run `gg board --all` to see it. An opened nomination can briefly show `opened, and its number is not minted yet` before its flight number appears.

The flight a nomination opens belongs to whoever the work is for, not to the person who opened it.

## The same steps in the console

Run `gg` with no arguments, then:

- `;` opens the board. `*` shows everyone's rows, `v` switches between nominations and the sweeps of watches, and `enter` opens the selected row.
- In an open row, `o` opens the nomination, `d` declines it, and `f` goes to the flight it became.
- Nominations waiting on a person also appear in the queue (`,`). There, `enter` opens or declines one, `space` marks it, `o` opens it, and `d` declines every marked row.

![The board tab: two gated nominations from the triage watch waiting to be opened, one already opened, and below them the triage watch's last sweep.](/screenshots/console/board.svg)

## Related

- [Set up a watch](/guides/set-up-a-watch/): the most common source of nominations.
- [Plan with itineraries](/guides/plan-with-itineraries/): plans, whose legs are nominations.
- [The envelope: destinations](/concepts/envelope/#destinations): `opens`, `opens-as` and `cap-per-pass`.
