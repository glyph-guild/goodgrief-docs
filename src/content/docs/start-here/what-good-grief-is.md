---
title: What Good Grief is
description: Good Grief lets AI agents do real work in repositories, under rules an organisation sets, with a person deciding wherever it matters.
sidebar:
  order: 1
---

Good Grief lets AI agents do real work in an organisation's repositories, such as investigating a bug, planning a change or making one. The organisation sets the rules for that work, and a person makes the decisions that matter.

All of it happens through **gg**, a single command-line tool. gg has two roles:

- **The console.** Running `gg` with no arguments opens a terminal application for starting work, following what is running, and answering anything that is waiting on a person.
- **The runner.** Running `gg runner up` on a machine makes that machine take work and carry it out. It clones the repository, runs the agent, and reports what happened.

## Code stays where it is

gg talks to a service called the **control plane**. The control plane keeps the record of the work: what was asked for, who approved what, and how each piece ended. It **never sees the code or the credentials**. The runner clones repositories, holds credentials and runs agents, all on machines the organisation controls. What it sends to the control plane are facts about the work, never the work itself.

## Terms that appear first

Good Grief borrows a few terms from aviation. These are the ones that appear first:

- A **[flight](/reference/glossary/#flight)** is one piece of requested work, such as finding out why login times out. Every flight has a number, such as `GG-42`.
- A **[runner](/reference/glossary/#runner)** is a machine that picks up flights and works on them.
- The **[envelope](/reference/glossary/#envelope)** is the organisation's set of rules for flights. It says which agent runs, how long it may take, which files it may change, and where finished work may go.
- A **[gate](/reference/glossary/#gate)** is a point where a flight waits for a person to approve or reject something. Nothing behind a gate proceeds until someone answers.
- The **[airspace](/reference/glossary/#airspace)** is where the organisation keeps its rules and names: the repositories it works on, the kinds of work it does, and the machines it has.

The [glossary](/reference/glossary/) covers the rest.

## A flight from start to finish

1. Someone asks for a piece of work: `gg fly "why does login time out after an hour?"`
2. The control plane checks the organisation's rules, and the flight waits for a runner that is allowed to take it.
3. A runner takes the flight, runs the agent, and reports what it found or changed.
4. If the rules require a person to approve something, such as a pull request, the flight stops at a gate until someone does.
5. The flight ends. It **lands** when the work was accepted somewhere. Otherwise it ends in one of a few other ways, and it always records which one.

[First flight](/start-here/first-flight/) walks through these steps with real commands. [Anatomy of a flight](/concepts/anatomy-of-a-flight/) describes each step in detail.
