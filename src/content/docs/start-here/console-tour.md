---
title: Tour the console
description: The console's agent column, its tabs and how to reach each one, how to open a flight and decide a gate, where help is, and how to quit.
sidebar:
  order: 5
---

The [console](/reference/glossary/#console) is the terminal application that opens when a person runs `gg` with no arguments. It shows what is waiting on a person, every [flight](/reference/glossary/#flight), the organisation's machines and more. Every action in it has a key. It also holds several AI agent sessions beside gg itself, and switches between them and gg without leaving the terminal. This page covers the keys needed to find the way around. [Console keys](/reference/console-keys/) lists all of them.

The console needs a signed-in machine. [Sign in](/start-here/sign-in/) covers signing in. If no one is signed in when the console opens, it offers to sign in. The console runs on macOS, Linux and Windows.

To open it, run:

```sh
gg
```

![The gg console on the queue tab, listing two nominations waiting to be opened and one flight awaiting a decision, with the tab bar along the bottom and the available keys on the last line.](/screenshots/console/queue.svg)

## gg includes tmux-like features

Like tmux, gg is a terminal multiplexer. It runs AI agent sessions in terminals of its own, keeps every one of them running, shows one at a time beside the console, and switches between them with a prefix key, `ctrl+g`. Several agents can work at once, and moving between them and gg needs no other terminal or window. [How gg works as a terminal multiplexer](/concepts/terminal-multiplexer/) explains the technical detail, and how it compares with tmux.

The column on the left is the agent column. It lists gg, then every agent session gg is holding, then **+ new agent**, then **history**. The console opens with the column in place, even before any agent is running.

![The console with three agents in the column on the left: the first waiting, the second working, and the third needing the person. Each row shows the agent's number, an activity mark, what the agent is working on and how long it has been running. The queue is on the right.](/screenshots/console/mux-column.svg)

Each agent runs in a terminal of its own inside gg and keeps running while gg, or another agent, is on screen. A row shows:

- **the agent's number**, which is also the key that switches to it;
- **what it is doing**: `»` while it works, `?` when it needs the person, such as to approve a command, and `·` while it waits for the next instruction;
- **what it is working on**, taken from the agent's own title;
- **how long it has been running**, and a `•` when its screen changed while it was hidden.

The activity marks come from the agent's own hooks. They appear for Claude Code sessions on this machine.

### Switching

Press `ctrl+g`, then:

| Key | Shows |
|---|---|
| `0` | gg |
| `1` to `9` | That agent |
| `+` | The new-agent menu |
| `h` | The history of earlier sessions |
| `esc` | Stays where it is |

Clicking a row in the column switches to it as well. While `ctrl+g` is waiting for the next key, the column's hint and the last line both list the choices:

![The console after ctrl+g: the column's hint reads "0 gg, 1-9, + new, H history", and the last line lists 0 gg, agents 1 to 3, + a new agent, h history and esc to stay.](/screenshots/console/mux-switch-agents.svg)

When an agent is on screen, gg keeps the top line, which names the agent and how to get back:

![An agent session on screen, with gg's bar on the top line reading "gg · Claude Code · ctrl-g then 0 for gg" and the agent column on the left.](/screenshots/console/mux-agent.svg)

### Starting an agent

`ctrl+g` then `+`, or **+ new agent** in the column, opens a menu. The arrow keys or `j` and `k` move, and `enter` picks:

![The new-agent menu, listing Claude Code here, Manage gg with an agent, Plan itinerary, Manage the airspace with an agent, Plan flight and Remote control.](/screenshots/console/mux-new-agent.svg)

| Choice | What it starts |
|---|---|
| Claude Code here | A plain Claude Code session in the folder gg was started from. |
| Manage gg with an agent | An agent that can read gates, the board, flights and runners freely, and asks the person before every action it takes. |
| Plan itinerary | An agent that drafts a plan of several flights. See [Plan with itineraries](/guides/plan-with-itineraries/). |
| Manage the airspace with an agent | An agent that drafts changes to the airspace. See [Change the airspace](/guides/change-the-airspace/). |
| Plan flight | An agent that helps write a new flight before it opens. |
| Remote control… | A session on another machine in the fleet. See [Driving an agent](/concepts/driving-an-agent/). |

gg holds at most nine agents at once. **history** lists the plans proposed from this machine and the agent sessions started from it, newest first. Opening a session resumes it in the folder where it ran.

Quitting gg ends every agent it holds. While any are running, `q` first names them and asks for `q` again.

[Driving an agent](/concepts/driving-an-agent/#the-agent-column) explains the column in more depth, including remote sessions.

## The tabs

The bar along the bottom lists every tab, each with the key that jumps to it. The last line lists the keys that work on the screen in view. `tab` moves to the next one.

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
| allowances | `v` | What every allowance in the fleet has left. The console shows it only to an administrator who has turned it on. |

A dot after a tab's name means the tab has not loaded anything yet. `g` refreshes what is on screen.

## Moving around

The arrow keys move through any list; `j` and `k` do the same. `enter` acts on the row under the cursor: on the flights tab it opens the flight, on the runners tab it opens the runner, and on the queue it lists what a person can do with the row.

`esc` closes any open window. To select and copy text, press `ctrl+f`. It freezes the screen and hands the mouse back to the terminal. Press it again to continue.

## The queue

The queue holds everything that is waiting on this person: flights stopped at a [gate](/reference/glossary/#gate), nominations waiting to be opened or declined, and failures that need attention. On a healthy day it can be empty. The flights tab still shows everything that has run.

Each row says what it is waiting for: a nomination asks whether to open it, and a flight stopped at a gate is awaiting a decision. `o` opens the selected row.

## Opening a flight

![The flights tab, listing recent flights with their number, state, stage, work kind, age and a description of the work.](/screenshots/console/flights.svg)

On the queue, `o` opens the selected flight. On the flights tab, `enter` does the same. The flight's window shows its history and its current state, and offers what a person can do with it, for example:

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

`n` starts a new flight. The console asks how to write it. `w` opens the editor to write the description by hand. Other keys compose it with an agent, or plan several flights with one. The console then asks which kind of work the flight is, and `enter` opens it.

## Help

`?` opens the help page. It lists every key that works at that moment, grouped by where it applies. The list matches what the keys actually do. `tab` turns to the second page, which shows the environment: every setting, and where its value came from. From the help page, `e` opens this machine's configuration file in the editor, and `o` takes any configuration the control plane is offering, as [Update gg](/guides/update-gg/#offered-configuration) describes.

## Quitting

`q` quits. `ctrl+c` quits from anywhere, including from an open window.

## When gg opens the editor

Some actions hand the terminal to the editor that `$EDITOR` names, such as writing a new flight's description. gg runs the editor inside a terminal of its own and keeps the top row, which reads:

```
 gg · editing — save and quit to come back
```

:::note[What gg sees while it hosts the editor]
Everything a person types into the editor, and everything it draws, passes through gg. gg stores none of it, writes none of it to disk, puts none of it in a diagnostics bundle, and sends none of it off the machine.
:::

When the editor exits, gg restores the terminal exactly as it was. Where gg cannot host the editor this way, such as behind a pipe, it opens the editor directly and says so.

## Next steps

- [Console keys](/reference/console-keys/): every key, in every window.
- [First flight](/start-here/first-flight/): open a flight and follow it to the end.
