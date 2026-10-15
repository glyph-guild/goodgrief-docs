---
title: Glossary
description: Every Good Grief term in one place, with a short definition and a link to where it is explained in full.
sidebar:
  order: 100
---

Good Grief borrows several terms from aviation. Each entry below gives a short definition and, where one exists, a link to the page that explains the term in full.

## Agent

The AI program a runner invokes to do a flight's work, such as Claude Code. The envelope's [loop](#loop) decides which agent runs and what it may do.

## Airspace

Where an organisation keeps its rules and names: root, its [work kinds](#work-kind), its registered repositories, its [watches](#watch), its [strategies](#strategy) and its fleet profiles. The airspace is held by the control plane and edited like a working copy: `gg airspace pull`, edit, `gg airspace diff`, then `gg airspace apply`.

## Allowance

A metered budget of agent time that a machine spends from, measured over windows such as a session or a week. A [floor](#floor) keeps part of an allowance back for its owner. `gg allowances` lists what every allowance has left.

## Approver

The person, or role, that may decide a [human check](#obligation). Declared on the obligation as `approver:`.

## Attempt

One try at a flight's work. When a person rejects the work, or the budget runs out and the work is handed back, a new attempt begins. `gg show` numbers attempts `#1`, `#2` and so on. The envelope's `budget.attempts` limits how many times the work is run again automatically after its time runs out.

## Board

The list of [nominations](#nomination) that are waiting for a person: work that has been proposed but not started. `gg board` lists it; `gg board open` turns a nomination into a flight, and `gg board decline` turns it down.

## Console

The terminal application that opens when `gg` is run with no arguments. It shows the queue, flights, the board, runners and more, and every action in it has a key. `?` lists them.

## Control plane

The service gg talks to. It keeps the record of every flight, decides which machine may take which flight, and records every decision. It never sees an organisation's code or credentials. See [What Good Grief is](/start-here/what-good-grief-is/).

## Credential

A secret, such as a repository access token, that a runner uses to act on the organisation's behalf. The control plane holds only a reference to where the secret lives, never the secret itself. `gg credential add` registers one; the value is always prompted for, never passed as an argument.

## Decision

A person's answer at a [gate](#gate): `approved`, which satisfies the obligation, or `rejected`, which sends the work back with the reason attached. Recorded with `gg decide`.

## Destination

Where a flight's finished work goes, such as a pull request, a work-item tracker or new flights. A destination lists the obligations it requires before the work is accepted. See [The envelope: destinations](/concepts/envelope/#destinations).

## Envelope

The set of rules that governs a flight. It combines root, the flight's work kind, and any repository narrowings, and decides which repositories the flight may concern, where it may run, how the agent works, which files it may change, what must be approved, and where the work goes. See [The envelope](/concepts/envelope/).

## Environment

A named kind of place where work runs, such as `dev` or `ui`. An organisation charts its environments with `gg environment chart`, and root lists the ones flights may use. A flight's environment becomes a requirement on the machine that takes it.

## Fact

A recorded observation about a flight, reported by the runner, such as the list of files changed (`change.manifest`) or how the agent's run ended (`loop.outcome`). Facts are what the control plane checks the rules against. `gg facts` lists a flight's facts.

## Fleet

All of an organisation's runners. A machine joins the fleet by enrolment, with a token from `gg fleet enroll`, and a fleet profile describes what kind of machine it is.

## Flight

One piece of requested work, such as finding out why login times out. Every flight has a number, such as `GG-42`. A flight is opened with `gg fly` and ends `landed`, `failed`, `grounded` or `withdrawn`. See [Anatomy of a flight](/concepts/anatomy-of-a-flight/).

## Floor

The share of an [allowance](#allowance) its owner keeps back, so other people's flights cannot spend all of it. Set with `gg allowances floor`.

## Gate

A point where a flight waits for a person to approve or reject something. A gate opens when a human check applies to a flight, and nothing behind it proceeds until the approver answers. `gg gates` lists every open gate.

## Grounded

A flight ending: a person stopped the flight while it could still have been done. Recorded with `gg ground`.

## Intent

What a flight was opened for: a plain-text description, a link (`--uri`), or a work item (`--ticket <provider>#<id>`). `gg flights --intent` lists the flights opened for one intent.

## Itinerary

A plan made of several flights, called legs, that pursue one goal together. An itinerary is proposed as a whole, and its legs open once its gate is approved. `gg itinerary show` displays one.

## Landed

A flight ending: the work was accepted at its destination. This is the intended outcome.

## Lease

A runner's claim on a flight. While a runner holds the lease, no other machine can take the flight. The runner renews its lease regularly; a lease that is not renewed expires, and the flight becomes available again.

## Leg

One flight within an [itinerary](#itinerary). A leg can state which other legs it follows.

## Loop

The part of the envelope that says how the work is done: which agent or person carries it out, what it may do, how long it has, and what happens when time runs out. See [The envelope: loops](/concepts/envelope/#loops).

## Move

One kind of action an agent is allowed to take, such as `read`, `search`, `edit` or `run-tests`. The loop lists the moves an agent may use, and the runner blocks any other.

## Narrowing

A rule a repository declares for itself, which adds an obligation to every flight concerning that repository. A narrowing can only add requirements, never remove them.

## Nomination

A proposal that some work should become a flight, together with the kind of work it needs and why. Nominations wait on the [board](#board) until a person opens or declines them, unless the rules allow them to open automatically.

## Obligation

A condition a flight must meet. A **machine check** is a rule Good Grief evaluates itself, such as whether the agent stayed within the allowed files. A **human check** is a decision a person makes, and opens a [gate](#gate). See [The envelope: obligations](/concepts/envelope/#obligations).

## Open

A flight that has not ended yet. A flight waiting at a gate or for a free machine is still open.

## Pool

A managed set of identical machines, such as containers, that are kept warm and reset between flights. A [strategy](#strategy) says how a pool is built.

## Root

The organisation's base rules: the first layer of every envelope. Only root may say which repositories and environments flights may use.

## Runner

A machine that takes flights and carries them out. It clones the repository, holds the credentials, runs the agent, and reports facts to the control plane. `gg runner up` makes a machine a runner; `gg runners` lists them.

## Scope

The files an agent may change during a flight, written as a path pattern such as `**` or `docs/**`. Declared as `context.scope` in the envelope.

## Strategy

How a [pool](#pool) is furnished, and the limits it runs within. Applied with `gg strategy apply`. `gg strategies` lists them.

## Take over

To take a running flight from its runner and continue the work by hand, then hand it back with an outcome. Done with `gg take`.

## Tenant

An organisation's own Good Grief: its people, rules, machines and flights, kept separate from every other organisation's.

## Watch

A standing instruction to look at something on a schedule, such as a work-item queue, and nominate work from what it finds. Each run of a watch is a **sweep**. `gg watches` shows how each watch is doing.

## Withdrawn

A flight ending: the question the flight was answering stopped mattering.

## Work kind

The rules for one kind of work, such as an investigation, a review or a change. A work kind supplies the loop, what the work produces and where it lands. See [The envelope](/concepts/envelope/#where-the-rules-come-from).
