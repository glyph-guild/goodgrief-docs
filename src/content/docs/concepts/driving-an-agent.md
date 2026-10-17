---
title: Driving an agent
description: The ways a person can work alongside an agent rather than leave it to run alone, from flying a flight by hand to driving an agent on another machine.
sidebar:
  order: 12
---

Most [flights](/reference/glossary/#flight) run with no one watching: a [runner](/reference/glossary/#runner) takes the flight, runs the [agent](/reference/glossary/#agent) on its own, and reports what happened. Sometimes a person wants to be closer to the work. gg offers several ways to do that. They differ in two respects: whether there is a flight, and whether the person can type to the agent or only watch.

| Way | A flight? | Where the agent runs | The person can |
|---|---|---|---|
| [Fly a flight by hand](#flying-a-flight-by-hand) | Yes | This machine, in the person's own terminal | Type to it |
| [Watch a runner](#watching-a-runner) | Whatever it is flying | Another machine | Watch only |
| [Open a flight for one machine and watch it](#an-attended-flight) | Yes | One named machine | Watch only |
| [Hold an agent beside gg](#the-agent-column) | No | This machine | Type to it |
| [Drive an agent on another machine](#driving-an-agent-on-another-machine) | No | Another machine | Type to it |

To take a flight away from its runner and finish the work by hand, see [Take over a flight](/guides/take-over-a-flight/).

## Flying a flight by hand

`y` on the console's main screen opens a new flight and flies it on this machine, with the person at the keyboard. gg starts a runner for that one flight, and that runner gives the person's own terminal to the agent, running interactively in the flight's working copy of the repository. Its [envelope](/reference/glossary/#envelope) governs the flight like any other. The same rules decide what it may concern and where its work may land, and the person answers any [gate](/reference/glossary/#gate) it reaches from the same session.

Because a person holds the terminal, the runner cannot measure the agent's run the way it measures a flight that runs alone. Instead of recording how the agent's run ended, it records that a person flew the session by hand: which agent binary and version ran, how long the person held it, and what it could not measure as a result.

## Watching a runner

To follow what a runner is doing, run:

```sh
gg runner watch <id|name>
```

In the console, `w` in a runner's window does the same while the runner is checking in, and `w` in a flight's window watches the flight. gg shows the agent's output as it arrives, from the flight the machine is running now, and then whatever it flies next. Watching is read-only: nothing typed reaches the agent.

The output comes from the runner directly, over an encrypted [channel](#how-the-console-reaches-a-machine) between the two machines. The control plane does not store it.

## An attended flight

A person can open a flight for one particular machine, in order to watch it:

```sh
gg fly "why does login time out after an hour?" --runner <id|name> --attended
```

The rules for this are stricter than for an ordinary flight sent to a machine with `--runner`:

- **A machine must be named.** Without `--runner`, the control plane refuses the request, because any machine that matches could otherwise take the flight.
- **Only the person who registered the machine may do this.** Anyone in the organisation may send work to a machine, but watching it means reading what it is doing.
- **The machine must be free.** If it is already flying, the control plane refuses the request rather than queuing it.
- **The machine must take the flight promptly.** If it does not claim the flight within the time it is expected to check in, the flight ends `grounded`, with no person named as the one who stopped it.

Once the machine takes the flight, watch it as described [above](#watching-a-runner).

## The agent column

![The console with three agents in the column on the left: the first waiting, the second working, and the third needing the person.](/screenshots/console/mux-column.svg)

The console can hold agents beside gg itself, each running in a terminal of its own inside gg, and switch between them. Agents keep running while another one, or gg, is on screen. A column on the left lists gg, then each agent, then **+ new agent**, then the history of earlier sessions. The console holds at most nine agents at once.

| Keys | What they do |
|---|---|
| `ctrl+g`, then `0` | Show gg. |
| `ctrl+g`, then `1` to `9` | Show that agent. |
| `ctrl+g`, then `+` | Start a new agent. |
| `ctrl+g`, then `H` | Show the history, from which the person can resume an earlier session. |

A new agent can be a Claude Code session in a chosen directory, or an agent started for a purpose, such as managing gg (its gates, board, flights and runners), managing the [airspace](/reference/glossary/#airspace), or planning a flight or an [itinerary](/reference/glossary/#itinerary). The menu ends with **Remote control…**, described [below](#driving-an-agent-on-another-machine).

Each local agent's entry in the column shows what it is doing: `»` while it works, `?` when it needs the person, and `·` while it waits. A `•` means its screen changed while it was hidden. gg learns this from the agent's own hooks, which run `gg mux mark`. That command is for the hooks, not for people.

Quitting gg with agents running asks first, and names the local agents that will stop.

## Driving an agent on another machine

A person can start an agent on another machine in the fleet and drive it from their own console, with no flight involved. This suits work that does not fit a flight, such as exploring a problem on a machine that has the right tools.

From the agent column, choose **+ new agent**, then **Remote control…**. gg lists the machines that will accept a session. Choosing one opens that machine's window on its sessions, where:

| Key | What it does |
|---|---|
| `n` | Start a session on the machine. |
| `enter` | Attach to a running session, or resume one that ended. |
| `d` | Forget a session that ended. |
| `D` | Forget every session that ended. |

The session then appears in the agent column like a local one. Its entry says it is being reached until the machine answers, the next time it checks in.

### What runs on the machine

The machine runs the agent's own interactive program in a terminal it owns, in an empty directory of its own for that session. The person sees the agent's screen and types to it as if it were local.

- **The latest person to attach drives.** Anyone attached earlier can still see the session but can no longer type to it.
- **A session outlives the console.** Quitting gg leaves remote sessions running, and attaching again replays the most recent part of the screen.
- **A machine holds at most three sessions**, and ends a session that has been idle for four hours.
- **A machine that is flying refuses new sessions.** A session already running keeps running.
- Remote entries in the agent column show no activity marks, because the agent's hooks run on the other machine.

### Who may drive a machine

A session starts only when both of these hold:

1. **The machine allows it.** Its own configuration file must say `"accept-agent-sessions": true`. gg reads this setting only from that file. No environment variable can set it, and the control plane cannot offer it. To turn it on, edit the file on that machine. A machine without it refuses the session and names the setting.
2. **The person may reach the machine.** A machine someone has claimed admits only its owner. Any other machine admits the person who registered it, or an administrator of the organisation.

[Add machines to the fleet](/guides/enrol-machines/#whose-a-machine-is) explains claiming.

### What is recorded

The control plane records who reached which machine, and when. Each machine also reports its sessions: who last attached and how long each ran. It records nothing of what the person typed or the session showed. The agent keeps its own record of the conversation, on that machine.

## How the console reaches a machine

Watching a runner, driving an agent on another machine, sending a credential and signing a runner's agent in all use a **channel**: a direct, encrypted connection between the console and the runner. The [control plane](/reference/glossary/#control-plane) arranges each channel but cannot read it.

1. **The console asks the control plane for an introduction** to a runner, stating what it is for. The control plane checks that the person may make that request of that machine, and the introduction is valid for one minute.
2. **Both sides seal the connection details.** The console seals its offer to the runner's registered key, and the runner seals its answer to a single-use key of the console's. The control plane passes both along, and the runner picks up the offer when it next checks in. Neither the control plane nor anything else carrying them can read the details, and the encryption detects any alteration.
3. **The two machines connect** with WebRTC, which encrypts everything that crosses the connection.

**The console remembers each runner's key** the first time it reaches the runner, and checks it every time after. If the key changes, gg refuses to send anything to that runner. Run `gg runner repin <id>` to send to it again. [Add machines to the fleet](/guides/enrol-machines/#when-a-runners-key-changes) covers this.

### Finding a way through

The two machines are often on different networks. Each asks a STUN server how it appears from outside its network. A machine's fleet profile can list these servers under `relays`. gg ships none of its own. When the two machines can reach each other this way, the connection is direct.

When they cannot, the channel can fall back to a **relay**: a server that forwards the encrypted traffic between them without being able to read it. When the organisation's control plane is configured with a relay, each introduction carries short-lived credentials for it, issued separately to each side. The channel reports which way it connected: directly, directly through the network's address translation, or through the relay.

### Limits

- The channel reaches a relay over its standard ports only. gg does not support relaying over the port used for secure web traffic.
- `gg doctor` checks whether this machine can reach the STUN servers. It does not test the relay.
- Only the console offers driving an agent on another machine. No gg command does it.
- gg supports only Claude Code as the agent for these sessions.
