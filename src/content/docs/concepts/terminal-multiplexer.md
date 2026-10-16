---
title: How gg works as a terminal multiplexer
description: How the console holds several agent sessions beside itself, much as tmux holds windows, and the processes, terminals, keys and screen drawing behind it.
sidebar:
  order: 14
---

The gg console is also a terminal multiplexer. Like tmux, it runs several programs in terminals of its own, keeps all of them running, shows one at a time, and switches between them with a prefix key. The programs it holds are AI agent sessions, such as Claude Code, and the console itself is always one of the things it can show.

[Tour the console](/start-here/console-tour/#gg-includes-tmux-like-features) covers how to use it. This page explains how it works.

## Compared with tmux

| | tmux | gg |
|---|---|---|
| Prefix key | `ctrl+b`, then a key | `ctrl+g`, then a key |
| What it holds | Shells and any program | Agent sessions, plus gg's own console |
| Choosing what is shown | Window numbers, a status line | Numbers `0` to `9`, a column down the left side |
| Activity | Optional activity and bell flags | What each agent is doing (working, needs the person, waiting), and whether its screen changed while hidden |
| Splits | Panes, side by side | One session on screen at a time |
| Server | A separate server process | None: everything runs inside the one gg process |
| Detach and reattach | Yes | Not for sessions on this machine: quitting gg ends them. Sessions on another machine can be left running and reattached. |
| Scrollback | Copy mode | None of its own; the mouse wheel becomes arrow keys for a program that does not use the mouse |
| Platforms | Any Unix | macOS and Linux |

The rest of this page explains each part.

## One process, one terminal per agent

When an agent starts, gg starts it as a child process with a pseudo-terminal of its own, using the Porta.Pty library. The child is told its terminal is the size of the screen minus the column on the left and the bar on the top line, so it lays itself out in the space it will actually have. Its environment sets `TERM=xterm-256color`, and it runs in the folder the session was started for.

```
gg (one process)
├── the console (Terminal.Gui)
├── agent 1 ── pseudo-terminal ── reader thread ── terminal emulator (its screen)
├── agent 2 ── pseudo-terminal ── reader thread ── terminal emulator (its screen)
└── agent 3 ── pseudo-terminal ── reader thread ── terminal emulator (its screen)
```

Each agent has a reader thread that takes everything the agent writes and feeds it into a terminal emulator kept for that agent alone (XTerm.NET). The emulator is the agent's screen, held in memory. It is updated whether or not the agent is on screen, so a hidden agent's screen is always current, and switching to it shows exactly what it would have shown.

There is no server. The agents, their emulators and their reader threads all belong to the gg process, and they live outside the console's user interface, so they keep running while the console is being drawn, torn down or rebuilt.

## Drawing the screen

Only one thing is on screen at a time: either the console or one agent. The column on the left is drawn in both cases, from the same list of rows and in the same colours, so it never moves when the screen switches.

**When the console is on screen,** Terminal.Gui draws it, and the column is part of its window. The column is refreshed four times a second, so an agent's activity and age stay current while a person works in the console.

**When an agent is on screen,** Terminal.Gui is not running at all. gg takes the terminal itself:

1. It switches the real terminal to its alternate screen and puts it in raw mode.
2. It paints the column, then gg's bar on the top line (for example `gg · Claude Code · ctrl-g then 0 for gg`), then the agent's screen from its emulator, offset past the column and below the bar.
3. It repaints whenever the agent writes, whenever the terminal is resized, and four times a second when nothing else happens, so the column's ages and marks keep moving.

Each repaint draws the whole frame from the emulator, with colours in 256-colour or true colour as the agent used them. Because the agent was told its terminal is one line shorter, it never draws over gg's bar.

**Switching back to the console** restores the terminal's modes, leaves the alternate screen and builds the console again from its saved state. The console's state, such as the tab, the selected row and what it has loaded, survives every switch; its windows are rebuilt each time.

**Resizing** the terminal resizes the agent on screen: gg resizes both its pseudo-terminal and its emulator. An agent that is hidden keeps its old size until it is next shown.

## Keys and the mouse

`ctrl+g` is the prefix. It was chosen because readline and vim rarely use it.

Beside an agent, gg reads the keyboard itself, straight from the terminal, and decides where each key goes:

- `ctrl+g` arms the switch, and the next key chooses: `0` for gg, `1` to `9` for an agent, `+` for a new agent, `h` for history.
- If the key after `ctrl+g` is not one of those, gg passes the `ctrl+g` and the key on to the agent, so a program that uses `ctrl+g` itself still receives it. Claude Code sessions are the exception: gg always keeps `ctrl+g` for itself beside them.
- Every other key goes to the agent untouched. A key gg acts on never reaches the agent.

Typing fast can deliver `ctrl+g` and the next key together, so gg splits what it reads at the prefix. It keeps escape sequences whole, so arrow keys and pasted text arrive intact.

While an agent is on screen, gg turns on mouse reporting:

- A click on a row in the column switches to it. A click on the column's empty space folds the column to a single cell.
- Other clicks are shifted to account for the column and passed to the agent, but only if the agent asked for the mouse.
- For an agent that did not ask for the mouse, the scroll wheel becomes the up and down arrow keys, as a terminal would send on its alternate screen.

In the console itself, `ctrl+g` arms the same switch, and pressing `ctrl+g` twice covers the screen with the gg mark.

## What each row knows

**What the agent is doing.** When gg starts Claude Code, it adds hook settings to that session's command line. It never changes the person's own Claude Code settings. The hooks call back into gg:

| Claude Code event | gg records |
|---|---|
| A prompt is submitted, or a tool is about to be used | working (`»`) |
| The agent stops | waiting (`·`) |
| A notification asks for permission | needs the person (`?`) |

Each hook runs `gg mux mark`, which writes one small file for that session in gg's state folder and always succeeds, so a hook can never break the agent. The file is deleted when the session ends. Sessions that are not Claude Code show no activity mark.

**What it is working on.** For a plain Claude Code session, the row shows the title the agent sets for its terminal window, as its emulator reads it. Until the agent sets one, the row shows the session's kind.

**Whether it changed.** When an agent writes while hidden, its row gains a `•`. Showing the agent clears it.

**How long it has run,** in seconds, minutes or hours.

## History and resuming

Every session gg starts on this machine is recorded in a history file in gg's state folder, one line each: an identifier, its label, the folder it ran in, when it started and, for a session on another machine, which machine. The file holds no transcript; what was said in a session stays with the agent.

gg gives each Claude Code session its identifier when it starts it, so it can ask Claude Code to resume exactly that session later. Opening a session in **history** starts Claude Code again with that session resumed, in the folder where it ran.

## Ending sessions

When an agent exits, its row disappears. If it was on screen, gg shows the agent on the row above it, or the console if there is none.

Quitting gg ends every session on this machine that it holds, because they are its own child processes. While any are running, the first `q` names them and asks for a second `q`.

Sessions on another machine behave differently. Leaving one lets go of it without ending it, much as detaching does in tmux, and it keeps running on that machine. [Driving an agent](/concepts/driving-an-agent/) explains remote sessions.

## Limits

- gg holds at most nine agents. Every way of starting another says so instead.
- One agent is on screen at a time. There are no split panes.
- gg has no scrollback or copy mode of its own.
- The multiplexer needs a terminal gg can take over. It runs on macOS, Linux and Windows (release 0.88.45 or later), and not when gg's output is piped.
- Every repaint draws the whole screen.
- The terminal libraries gg uses ship beside the gg binary. [Install gg](/start-here/install/) covers installing them.

## Related

- [Tour the console](/start-here/console-tour/#gg-includes-tmux-like-features): using the agent column.
- [Driving an agent](/concepts/driving-an-agent/): attended flights, the agent column and remote sessions.
- [What leaves the machine](/concepts/what-leaves-the-machine/): what gg can see while it hosts a program's terminal.
