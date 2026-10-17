---
title: First flight
description: Open a flight, follow it as it runs, answer it if it stops at a gate, and read how it ended.
sidebar:
  order: 2
---

This page follows one [flight](/reference/glossary/#flight) from start to finish. The steps take about ten minutes, plus however long the agent spends on the work.

## Prerequisites

- **gg is installed.** See [Install gg](/start-here/install/).
- **gg is pointed at the organisation's control plane and signed in** ([Sign in](/start-here/sign-in/) has the details):

  ```sh
  gg config set control-plane <url>
  gg login
  ```

  Ask an administrator for the control-plane address. `gg login` prints a link and a code. Open the link and enter the code to finish signing in.
- **At least one runner is available.** A runner is a machine that carries out the work. `gg runners` lists the organisation's runners. If the list is empty, ask an administrator, or run `gg runner up` on a suitable machine.

To check all of this at once, run:

```sh
gg doctor
```

`gg doctor` checks what gg needs in order to work. Every problem it reports comes with a line describing the fix.

## 1. Open a flight

Run `gg fly`, followed by a plain description of the work:

```sh
gg fly "Why does the login page sign people out after an hour?" --repo web-app
```

`--repo` names the repository the work concerns, by its registered name. `gg airspace show` lists the registered names.

gg replies with the flight's number:

```
Opened GG-42.
```

A flight can also start from a work item (`--ticket ado#1234`) or a link (`--uri https://…`). The organisation's rules determine the kind of work, such as an investigation or a change. To choose one explicitly, pass `--work-kind <name>`.

## 2. Follow it

`gg flights` lists the flights in the air:

```sh
gg flights
```

```
GG-42       2026-10-14 14:31:59Z  open       Why does the login page sign people out after an hour?
```

`open` means the flight has not ended yet. `gg show` gives its history so far:

```sh
gg show GG-42
```

```
  GG-42  investigate
  stage       ended
  state       landed
  for:        Ada Lovelace

  2026-10-14 14:31:59Z  opened by Ada Lovelace
  2026-10-14 14:32:06Z  #1 handed to runner 01a0bca3-…
  2026-10-14 14:32:46Z  #1 the runner renewed its claim
  2026-10-14 14:38:03Z  the investigate loop ran and ended completed
                          The session timeout is set in auth.config… (the rest is in the transcript)
  2026-10-14 14:38:20Z  #1 the runner let it go, reporting completed
  2026-10-14 14:38:20Z  it ended landed
```

Some of these lines are worth knowing:

- **"handed to runner"** means a machine picked up the flight. `#1` is the attempt number. If the agent attempts the flight again, the next attempt is `#2`.
- **"renewed its claim"** is the runner checking in, about every 40 seconds, to confirm it is still working.
- **"ended landed"** means somewhere accepted the work. This is the intended outcome.

`gg log GG-42` shows the same history as raw events, which helps when investigating a problem.

## 3. Answer a gate

Some work requires a person's decision, such as approval before a pull request opens. In that case the flight stops at a [gate](/reference/glossary/#gate) and waits. `gg gates` lists everything waiting on a person:

```sh
gg gates
```

```
1 decision(s) waiting.

GG-42 - code-review
  approver: ada
  commit:   3f2c1e9
  when:     always (this obligation declares no condition)
  since:    2026-10-14 14:38:03Z
```

`code-review` is the **obligation**, meaning the thing awaiting a decision. `gg why` explains why the flight is stopped and what would let it continue:

```sh
gg why GG-42
```

After reviewing the work, record a decision:

```sh
gg decide GG-42 code-review approved "Correct, and the test covers it."
```

Use `rejected` instead of `approved` to send the work back. The agent makes another attempt, with the reason attached. gg confirms what it recorded:

```
decided: the obligation is now satisfied
```

## 4. Read how it ended

Every flight ends with one word:

| Ending | Meaning |
|---|---|
| `landed` | Somewhere accepted the work. |
| `failed` | The work finished, but nowhere accepted it. |
| `grounded` | A person stopped it. |
| `withdrawn` | The question stopped mattering. |

A flight that has not ended is `open`, even while it waits at a gate or for a free machine. [Anatomy of a flight](/concepts/anatomy-of-a-flight/) explains the difference between waiting and ending.

## The same steps in the console

The console supports everything above. Run `gg` with no arguments, then:

- `n` starts a new flight.
- `,` opens the queue, which lists what is waiting on a person.
- `d` decides the gate of the selected flight.
- `?` lists every key, and `q` quits.

![The gate window for GG-48 in the console, showing the code-review obligation, its approver, the commit, and why it applies, with a to approve and r to reject on the last line.](/screenshots/console/gate-decision.svg)

## Next steps

- [Anatomy of a flight](/concepts/anatomy-of-a-flight/): every stage of a flight, and the ways one can leave early.
- [Glossary](/reference/glossary/): every Good Grief term in one place.
