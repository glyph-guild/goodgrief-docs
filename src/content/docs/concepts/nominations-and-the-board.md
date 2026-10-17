---
title: Nominations and the board
description: What a nomination is, where nominations come from, how one opens or waits on the board, and every way a nomination can end.
sidebar:
  order: 5
---

A **[nomination](/reference/glossary/#nomination)** is a proposal that some work should become a flight. It names the kind of work it needs and says why. Nominations are how work enters Good Grief from anywhere other than a person typing `gg fly`: a watch that found an item, a planning flight that broke work into pieces, a pull request that wants a review.

A nomination is not a flight. It has no flight number, no runner takes it, and nothing has been done yet. It either opens as a flight, waits for a person on the **[board](/reference/glossary/#board)**, or the rules turn it down.

[Use the board](/guides/use-the-board/) gives the steps for reading the board and answering nominations.

## What a nomination holds

| Part | Meaning |
|---|---|
| **Nominator** | What proposed it: a flight, a plan, a watch, or a repository's pull requests. |
| **Subject** | Which piece of work it is about, such as a work item or a pull request. |
| **Version** | Which state of that work it saw, such as a work item's revision or a pull request's head commit. |
| **Work kind** | The [work kind](/concepts/work-kinds/) the flight would run under. |
| **Reason** | Why the work deserves a flight, in the nominator's words. |
| **Note** | Optional advice for the agent that will do the work. gg shows it to that agent as advice, and it grants nothing. |
| **Repository and environment** | Optional: where the work would happen. |
| **For** | The person it belongs to, when it came from a person's own watch. |

A nomination also records the rules the board judged it against, so a person reading the board sees the same rules the board applied.

## Where nominations come from

| Source | What it nominates |
|---|---|
| **A flight** | An agent whose work kind has a `flight` destination proposes flights through a nomination tool. A planning flight uses this to propose the legs of a plan. |
| **A plan a person proposes** | Each leg of the plan is a nomination, made when the person proposes the plan. See [Itineraries](/concepts/itineraries/). |
| **A [watch](/concepts/watches-and-sweeps/)** | Each sweep nominates the items its procedure decides deserve work. A watch's failures also stand on the board, as entries for a person to read. |
| **A pull request** | Opening or updating a pull request in a registered repository can nominate a flight, such as a review. The subject is the pull request and the version is its head commit. |
| **`gg fly`** | A flight opened directly also passes through the board, as a nomination that a person opened by hand. It never waits there. |

Whatever the source, a `flight` [destination](/concepts/envelope/#destinations) bounds every nominator: for a flight, its work kind's destination; for a watch, its `nominates` destination. The destination's `opens` list is the menu of work kinds a nomination may name. The board refuses a nomination outside the menu.

## One nomination per piece of work

Its nominator, subject and version identify a nomination. The same nominator proposing the same subject at the same version twice makes one nomination, not two. When the work changes, its version changes, and the nominator can nominate it again.

For nominations made by a flight or a plan, a newer nomination of the same subject from the same nominator replaces the older one: the last one wins, and the older one ends `superseded`. No newer nomination replaces a watch or pull-request nomination this way; each version stands on its own.

## Auto or gated

The destination's `opens-as` decides how a nomination opens:

- **`auto`** (the default): the nomination opens as a flight straight away, if the rules allow it. No one needs to answer it.
- **`gated`**: the nomination waits on the board until a person opens or declines it.

Even an `auto` nomination waits for what its destination requires:

- A flight's nominations open only once the flight's own destination accepts its work. A planning work kind's destination typically requires a person to approve the plan, so its legs open when a person approves that gate.
- A watch has no flight of its own to carry a gate, so when its `nominates` destination requires a human check, each of its nominations waits on the board for a person instead.

An `auto` nomination can become gated when its nominator has spent its budget:

- A watch's `bounds.budget` limits how many flights its nominations may open in a window.
- A repository's budget limits how many flights its pull requests may open.

Once a budget is spent, further nominations stand on the board as gated, and the board says why. Changing `auto` to `gated` tightens the rules; changing `gated` to `auto` loosens them, and waits for approval.

### How many at once

A destination's `cap-per-pass` limits how many nominations one run may make:

- For a **plan**, the cap applies to the plan as a whole. The board refuses a plan with more legs than the cap entirely: every leg ends `refused`, rather than some opening and others not.
- For a **watch**, the first nominations up to the cap stand, and the watch leaves the rest for a later sweep to report again.

A destination that leaves out the cap has no limit.

## The board

The board lists every nomination that is still **standing**: it has not ended, and something can still happen to it. `gg board` lists them, and `gg board --all` includes the ones that have ended. `gg itineraries` lists the legs of a plan with their plan, rather than on the board.

### Opening and declining

A person answers a standing nomination in one of two ways:

- **Open it** with `gg board open <id> <why>`. The board does not simply open the flight: it applies the rules again, as they stand now. The work kind must still be on the menu, the rules must still combine, and anything else the nominator's destination requires must still hold. If they do not, the nomination ends `refused`, with the reason.
- **Decline it** with `gg board decline <id> <why>`. It ends `declined` at once, with the person's sentence.

A reason is required either way. It is the only record of why a person opened work no one explicitly asked for, or turned down work that something proposed.

The first answer stands. Once one person has answered a nomination, the board refuses a second answer.

Only that person can answer a nomination marked `for` a person, from that person's own watch. The board refuses anyone else.

### Whose flight it becomes

The flight a nomination opens belongs to whoever the work is for, not to the person who opened it:

- A flight nominated by an agent belongs to the person who opened the flight that nominated it.
- A leg of a plan belongs to the person who proposed the plan.
- A flight nominated by a personal watch belongs to that watch's person.

Opening a nomination is a decision about whether the work happens, not a claim to it.

## How a nomination ends

Every nomination ends exactly once, and the first ending stands.

| Ending | What ended it |
|---|---|
| `opened` | It became a flight. `gg board --all` shows which. |
| `declined` | A person said no. |
| `refused` | The rules said no, and the reason names the rule. This happens when a nomination names a work kind not on the menu, when a plan exceeds its cap or its legs cannot be ordered, or when the rules no longer allow it at the moment someone opens it. |
| `superseded` | A newer nomination of the same subject from the same flight or plan replaced it. |
| `dropped` | A planning flight revised its plan, and the new version no longer names this leg. The revision drops only legs still standing; a leg that already opened is untouched. |
| `lapsed` | No one opened it in time. See below. |

Only `opened` and `declined` record a person's decision. The others belong to the rules, the nominator and the clock.

### A nomination no one answers

What happens to a nomination no one answers depends on how it stands:

- **An `auto` nomination lapses** if it has not opened an hour after the nominator made it, as long as no gate is open on the flight or plan that nominated it. An `auto` nomination is meant to open at once, so one that has not opened within the hour ends `lapsed` rather than standing indefinitely. While a gate on the nominating flight or plan is open, the board keeps its nominations.
- **A `gated` nomination never lapses.** It stands on the board until a person opens or declines it.

Gated nominations therefore accumulate when no one reads the board. In the console, the queue (`,`) lists them alongside the gates waiting on a person.

## Related

- [Use the board](/guides/use-the-board/): reading the board and answering nominations.
- [Watches and sweeps](/concepts/watches-and-sweeps/): the most common source of nominations.
- [Itineraries](/concepts/itineraries/): plans, whose legs are nominations.
- [Gates and decisions](/concepts/gates-and-decisions/): what a flight waits for after it opens.
