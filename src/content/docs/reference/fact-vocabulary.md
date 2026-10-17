---
title: Fact vocabulary
description: Every family of fact a runner can report about a flight, with its category and what it records, as of fact vocabulary 0.44.0.
sidebar:
  order: 6
---

A [fact](/reference/glossary/#fact) is a recorded observation about a flight, which the [runner](/reference/glossary/#runner) that carried it out reports. The control plane checks the rules against facts. An [obligation](/reference/glossary/#obligation) reads facts, and a work kind's [`produces:`](/concepts/envelope/#produces) lists the fact families its work can yield.

The facts a runner may report come from a fixed list, the **fact vocabulary**. A runner cannot report a fact outside it. The vocabulary has a version, which changes whenever the vocabulary adds or changes a family, or a value a family may hold. `gg version` prints the version a release of gg reports.

This page describes **fact vocabulary 0.44.0**.

To list the facts one flight recorded, run `gg facts <flight>`.

## Categories

Each family belongs to one of three categories, which say what the fact describes:

| Category | What it describes |
|---|---|
| `subject` | A standing property of something that exists between flights, such as the environment the work ran in. |
| `tree` | Something measured from the repository's working tree that the flight touched. A flight with no repository cannot produce these. |
| `flight` | The flight itself: what the agent did, what it said, who took it over, and where the work went. Any work kind that runs can produce these. |

An obligation that reads a `tree` fact cannot apply to a flight that has no repository. The control plane marks such an obligation **not attached** rather than halting the flight.

## Families

| Family | Category | What it records |
|---|---|---|
| `environment.identity` | subject | The environment the work ran in: a fingerprint of the operating system, architecture, runtime and image, the versions of tools such as Git, hashes of the repository's dependency lock files, and which of the declared moves this machine was measured to enforce. |
| `source.provenance` | tree | What the runner actually put on disk: the repository, the ref requested and the ref it resolved to, the commit, whether that commit came from a fork, and how many files and bytes the tree held. |
| `change.manifest` | tree | The files the flight changed, at any point during its work, with line counts. This is the fact the scope check reads. |
| `intent.read` | flight | The file a flight's intent named, as the runner read it: where, and at which commit. |
| `loop.outcome` | flight | What the agent's run did: its attempts, the moves it used, how it ended and why. |
| `loop.transcript` | flight | Where the run's transcript is kept, without carrying the transcript itself. |
| `loop.session` | flight | Where the agent's own record of its session is kept, as a reference, without carrying it. |
| `loop.model` | flight | Which model one launch of the agent was given. A flight moved to another model while running has two. |
| `loop.digest` | flight | A summary of what the agent did, so that a person can pick the work up without reading the transcript. |
| `loop.question` | flight | A question the agent could not answer from the work itself. |
| `loop.attended` | flight | A session a person ran by hand, and how long the person held the terminal. |
| `handoff.account` | flight | What a person who took a flight over says they did, confirmed in their own name. |
| `flight.nomination` | flight | A work kind the agent nominates for a flight of its own, and why. The destination, not the nomination, decides whether a flight opens. |
| `work-item.proposal` | flight | A change the agent proposes be made to a work item in a tracker. |
| `document.proposal` | flight | An airspace document the flight drafted, asking that it be applied. |
| `landing.proposal` | flight | What the agent asks its own proposal be called, such as a pull request's title and description. |
| `destination.pushed` | flight | The runner pushed a branch and proposed nothing, such as when it keeps the work for a person to take over. |
| `destination.landed` | flight | Where the flight's work landed, once a destination accepted it. |
| `environment.reclaimed` | flight | What preparing the environment removed from the machine the flight was given, before the flight's application started. |
| `stack.performed` | flight | What happened when the runner ran the project's own script for bringing its application up or down. |
| `preview.url` | flight | Where the flight's running application was published, so that a person asked to look at it knows where to go. |

## What a fact never carries

No family has a place for a file's contents, a credential's value or anything an agent printed. A fact that concerns a file names it, and a fact that concerns a transcript or a session says where it is kept, with its size and a hash. [What leaves the machine](/concepts/what-leaves-the-machine/) explains this boundary.

## Related

- [The envelope: `produces:`](/concepts/envelope/#produces): how a work kind declares the facts it can yield.
- [Anatomy of a flight](/concepts/anatomy-of-a-flight/): when facts are reported and checked.
- [Glossary](/reference/glossary/): every term on this page.
