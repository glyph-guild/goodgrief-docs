---
title: Tour the console
description: The console's tabs and how to reach each one, how to open a flight and decide a gate, where help is, and how to quit.
sidebar:
  order: 5
---

The [console](/reference/glossary/#console) is the terminal application that opens when `gg` is run with no arguments. It shows what is waiting on a person, every [flight](/reference/glossary/#flight), the organisation's machines and more, and every action in it has a key. This page covers the keys needed to find the way around. [Console keys](/reference/console-keys/) lists all of them.

The console needs a signed-in machine; [Sign in](/start-here/sign-in/) covers that. If nobody is signed in when the console opens, it offers to sign in. The console is not available on Windows, where gg is a command-line tool only.

To open it, run:

```sh
gg
```

![The gg console on the queue tab, listing two nominations waiting to be opened and one flight awaiting a decision, with the tab bar along the bottom and the available keys on the last line.](/screenshots/console/queue.svg)

## The tabs

The bar along the bottom lists every tab, each with the key that jumps to it, and the last line lists the keys that work on the screen in view. `tab` moves to the next one.

| Tab | Key | What it shows |
|---|---|---|
| queue | `,` | Everything waiting on this person. The console opens here. |
| itineraries | `'` | Plans made of several flights, and the flights (legs) each plan is made of. See [itinerary](/reference/glossary/#itinerary). |
| board | `;` | Every [nomination](/reference/glossary/#nomination), including those already answered, and the [watches](/reference/glossary/#watch) that make them. `v` switches between the two lists. |
| flights | `.` | Every recent flight, whether or not it needs anyone. |
| runners | `u` | The organisation's machines, with this machine's runner first. |
| intents | `[` | Work items from the organisation's trackers, ready to become flights. `f` flies the selected item. |
| credentials | `r` | Every credential, what it is for, and how it rests on this machine. |
| airspace | `e` | The rules in force and the documents in the [airspace](/reference/glossary/#airspace). |
| allowances | `v` | What every allowance in the fleet has left. Shown only to an administrator who has turned it on. |

A dot after a tab's name means the tab has not loaded anything yet. `g` refreshes what is on screen.

## Moving around

The arrow keys move through any list; `j` and `k` do the same. `enter` acts on the row under the cursor: on the flights tab it opens the flight, on the runners tab it opens the runner, and on the queue it lists what can be done with the row.

`esc` closes any open window. `ctrl+f` freezes the screen and hands the mouse back to the terminal, so text can be selected and copied; press it again to continue.

## The queue

The queue holds everything that is waiting on this person: flights stopped at a [gate](/reference/glossary/#gate), nominations waiting to be opened or declined, and failures that need attention. On a healthy day it can be empty, and the flights tab still shows everything that has run.

Each row says what it is waiting for: a nomination asks whether to open it, and a flight stopped at a gate is awaiting a decision. `o` opens the selected row.

## Opening a flight

![The flights tab, listing recent flights with their number, state, stage, work kind, age and a description of the work.](/screenshots/console/flights.svg)

On the queue, `o` opens the selected flight. On the flights tab, `enter` does the same. The flight's window shows its history and its current state, and offers what can be done with it, for example:

- `a` approves and `r` rejects, when a gate is waiting on the flight;
- `m` moves the flight to another model;
- `f` flies it again;
- `x` stops the flight (grounds it), after asking to confirm;
- `c` copies what is shown;
- `esc` closes the window.

`a` on the main screen opens a short list of actions for the flight under the cursor.

![A flight's window for GG-48, showing its intent, id, stage, state, when it opened, the envelope version and the number of attempts.](/screenshots/console/flight-detail.svg)

## Deciding a gate

When a flight is stopped at a gate, select it and press `d`. The window that opens states the question and who may answer it (the approver). Press `a` to approve or `r` to reject. This records the same [decision](/reference/glossary/#decision) as `gg decide` on the command line.

![The gate window for GG-48: the code-review obligation, its approver, the commit and branch, the condition that applied, why it applied, and how long it has waited. The last line offers a to approve, r to reject and esc to close.](/screenshots/console/gate-decision.svg)

## Starting a flight

`n` starts a new flight. The console asks how to write it: `w` opens the editor to write the description by hand, and other keys compose it, or plan several flights, with an agent. It then asks which kind of work the flight is, and `enter` opens it.

## Help

`?` opens the help page. It lists every key that works at that moment, grouped by where it applies, and the list matches what the keys actually do. `tab` turns to the second page, which shows the environment: every setting, and where its value came from. From the help page, `e` opens this machine's configuration file in the editor, and `o` takes any configuration the control plane is offering, as described in [Update gg](/guides/update-gg/#offered-configuration).

## Quitting

`q` quits. `ctrl+c` quits from anywhere, including from an open window.

## When gg opens the editor

Some actions hand the terminal to the editor named by `$EDITOR`, such as writing a new flight's description. gg runs the editor inside a terminal of its own and keeps the top row, which reads:

```
 gg · editing — save and quit to come back
```

This means everything typed into the editor, and everything it draws, passes through gg. gg stores none of it, writes none of it to disk, puts none of it in a diagnostics bundle, and sends none of it off the machine. When the editor exits, gg restores the terminal exactly as it was. Where gg cannot host the editor this way, such as behind a pipe or on Windows, it opens the editor directly and says so.

## Next steps

- [Console keys](/reference/console-keys/): every key, in every window.
- [First flight](/start-here/first-flight/): open a flight and follow it to the end.
