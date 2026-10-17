---
title: Runners and the fleet
description: How a machine takes a flight, how a flight finds a machine, and how enrolment, ownership and pools decide which machines exist and whose they are.
sidebar:
  order: 9
---

A [runner](/reference/glossary/#runner) is a machine that takes [flights](/reference/glossary/#flight) and carries them out. All of an organisation's runners together are its [fleet](/reference/glossary/#fleet). This page explains how a runner and a flight find each other, what holds a flight to one machine while it runs, and the ways an organisation decides which machines it has and whose they are.

The steps for setting up a runner are in [Run a runner](/guides/run-a-runner/) and [Add machines to the fleet](/guides/enrol-machines/).

## What a runner does

A runner is gg running on a machine the organisation controls, as `gg runner up` or as a service. It:

1. **Checks in** with the [control plane](/reference/glossary/#control-plane) every few seconds, saying that it is alive and what it can take.
2. **Asks for work** that matches what it advertises.
3. **Takes a flight** when the control plane offers one, and holds it with a [lease](/reference/glossary/#lease).
4. **Does the work**: opens the credentials the flight needs on its own machine, clones the repository, runs the [agent](/reference/glossary/#agent), and records what happened as [facts](/reference/glossary/#fact).
5. **Reports** the facts, pushes the work where the rules allow, and hands the lease back with what became of its turn.

The control plane decides; the runner does. The control plane never sees the repository or the credentials. [What leaves the machine](/concepts/what-leaves-the-machine/) describes exactly what the runner sends.

A runner has a credential of its own, issued when it registers. It lasts thirty days, and the runner renews it before it expires, so a machine that has registered once keeps working with no one signed in on it. gg uses a person's sign-in only to register the runner; after that, the runner works with its own credential.

## Leases

A **lease** is a runner's claim on a flight. While a runner holds it, no other machine can take that flight.

### Claiming

A runner asks the control plane for work and states its labels. The control plane accepts the request and the runner checks back every few seconds, for up to half a minute, until the control plane either gives it a flight or tells it there is nothing for it. It then asks again.

The control plane offers a flight to a runner only when all of these hold:

- the runner advertises every label the flight requires (see [Labels](#labels));
- the flight is ready: nothing it needs is missing, and no [gate](/reference/glossary/#gate) is open on it;
- no other runner holds a live lease on it;
- if someone sent the flight to one machine with `gg fly --runner`, this is that machine;
- if the runner is reserved, the flight belongs to the runner's owner (see [Whose a machine is](#whose-a-machine-is)).

### Renewing

A lease lasts one minute. The runner renews it when twenty seconds remain, for as long as it is working on the flight. The control plane sets the new expiry; the runner does not compute its own.

Each lease carries a number that changes whenever the flight changes hands. A runner whose lease has passed to another machine cannot renew it, report facts against it or hand it back: the control plane refuses all three. A machine that stalled and came back late therefore cannot overwrite the work of the machine that replaced it.

### Expiry

A lease that is not renewed expires. The clock decides expiry, not any timer firing: a lease past its expiry is expired whether or not anything has noticed yet. When it expires, the flight stays open and becomes available to another machine. The runner reports nothing in this case; Good Grief records `expired` itself.

[Anatomy of a flight](/concepts/anatomy-of-a-flight/#what-a-runner-reports-and-what-it-means-for-the-flight) lists what a runner can report when it hands a lease back, and what each report means for the flight.

### Checking in

Checking in is separate from renewing. A runner checks in every fifteen seconds, or every second while a console is waiting to reach it. The control plane counts a runner that has not checked in for forty-five seconds as offline.

## Labels

A runner advertises **labels**, written `key=value`, and a flight requires labels. A runner can take a flight only when it advertises every label the flight requires.

Today a flight requires at most one label: `environment=<name>`, from its [environment](#environments). A flight that names no environment requires nothing, and any runner may take it.

Where a runner's labels come from depends on how it joined:

| Runner | Its labels |
|---|---|
| Enrolled under a fleet profile | Exactly `environment=<name>`, from the profile. A runner whose profile is not in force advertises nothing. |
| A member of a pool | Fixed when gg creates the member, from its pool's strategy. |
| Any other runner | The machine's `runner-labels` setting, as a comma-separated list. |

To see what each runner advertises, run:

```sh
gg runner labels
```

The command shows each label with its **disposition**, which says how much weight it carries. `stated` means the label is the machine's own claim: Good Grief admits it, but nothing has checked it. `measured` marks a label whose name has a registered meaning, which is what [charting](#environments) an environment with `--means` provides.

A runner reports its CPU and memory readings separately, and `gg runners` shows them. They are not labels, and no flight can require them.

## Environments

An [environment](/reference/glossary/#environment) is a named kind of place where work runs, such as `dev` or `ui`. Before any flight can use one, the organisation charts it:

```sh
gg environment chart ui --means "<predicate>"
```

Charting a name opens a gate. `gg environments` lists every charted name.

Root's `environments:` field then lists the charted environments flights may use. [The envelope: environments](/concepts/envelope/#environments) describes how the control plane checks a flight's environment when it opens, and how it becomes the label `environment=<name>` that a machine must advertise.

The control plane refuses to apply an envelope that lists an environment no live runner advertises, with a message saying so, unless a [pool](#pools-strategies-and-members) manages that environment and can bring machines up for it.

## When no machine matches

A flight with no machine to take it is **not an error**. It waits in the Ready stage until a matching machine appears, and nothing times it out. Ordinary flights wait indefinitely.

While a flight waits, `gg show` and the console say why, in a sentence such as:

> waiting: no runner advertises environment=ui

When a machine exists but is being kept back, gg gives that reason first, because it has a different remedy:

| Why it waits | What to do |
|---|---|
| No runner advertises the label. | Bring up a runner that advertises it. `gg runner labels` shows what each runner advertises. |
| A machine that could take it is reserved for another person. | Ask its owner to release it, or bring up another machine. |
| Someone sent it to one machine with `--runner`, and that machine is not checking in. | Start that machine again, or open the flight without `--runner`. |
| Its pool is warming a machine for it. | Wait. The pool is bringing one up. |
| Its pool's limits do not allow another machine now, by size or by its active hours. | Wait for a machine to free up or for the active hours to begin, or change the strategy's limits. |
| No one has registered a credential for its repository. | Register one with `gg credential add --repo <slug>`. See [Credentials](/concepts/credentials/). |

`gg plan <flight>` lists everything that must hold before a flight can start, and who can make each item true.

An attended flight, opened with `--attended` for one named machine, is the exception. The control plane refuses to open it if that machine is already flying, and it ends if the machine does not take it promptly. [Driving an agent](/concepts/driving-an-agent/#an-attended-flight) covers it.

## Enrolment and fleet profiles

A machine joins the fleet in one of two ways:

- **Registration.** A person signs in on the machine and runs `gg runner up`. The machine's labels come from its own settings.
- **Enrolment.** A person creates an enrolment token with `gg fleet enroll`, and someone installs the machine with it. No one signs in on the machine. On its first start it exchanges the token for a runner credential of its own, and the token's use is spent.

An enrolment token names a **fleet profile**: a document in the [airspace](/reference/glossary/#airspace), at `airspace/fleet/<name>.yaml`, that describes one kind of machine. The profile says what the machine is for, which environment it provides, which agent it runs (by name, never by path), which repository hosts and destinations it uses, which trackers it reads, and which credentials it needs, as references. The machine takes its configuration from its profile rather than from someone configuring it by hand. [Add machines to the fleet: fleet profiles](/guides/enrol-machines/#fleet-profiles) lists every field.

Changes to a profile follow one rule: **anything that lets machines do more opens a gate; anything that lets them do less applies at once.** Applying a profile for the first time, adding a role, repository host, destination, tracker or credential, turning on sweeps, or changing the environment or agent all open a gate. Removing something applies immediately.

### Bringing a machine up

An enrolled machine checks every five minutes that it can do what its profile asks: that its agent is present and signed in, that it holds the credentials the profile names, and that it can reach its repository hosts. When something is missing that only a person can provide, a maintenance flight for the machine appears in `gg flights`, with one gate for each missing item. Each gate clears by itself once the machine confirms the item works, and the flight ends when the last one clears.

## Whose a machine is

Every runner is in one of three states:

| State | Meaning |
|---|---|
| The organisation's | No one may claim it. |
| Open | Anyone in the organisation may claim it. |
| Claimed | It belongs to one person. |

A claimed machine can also be **reserved**, which keeps it to its owner's flights: the control plane offers it no flight that anyone else opened. gg reports a reserved machine that could have taken a flight as kept back, not as missing, so no one goes to bring up a machine that already exists.

[Runners in a team](/concepts/runners-in-a-team/) explains, for each state, which work the control plane offers a machine and who started each flight. An enrolment token decides the state a machine starts in, and `gg runner claim`, `unclaim`, `reserve`, `release` and `ownership` change it later. [Add machines to the fleet: whose a machine is](/guides/enrol-machines/#whose-a-machine-is) lists who may run each one.

Ownership also decides who may reach a machine directly, for example to [drive an agent on it](/concepts/driving-an-agent/#who-may-drive-a-machine).

## Pools, strategies and members

A [pool](/reference/glossary/#pool) is a managed set of identical machines, run as containers on one host and kept ready for flights. Each machine in a pool is a **member**. Unlike a runner a person set up, gg creates, resets and removes a member.

### The maintaining runner

A runner on the host whose fleet profile includes the `maintain` role keeps a pool, running:

```sh
gg runner maintain <pool>
```

Only a maintaining runner may create members. It checks with the control plane every few seconds, carries out what the control plane decides the pool needs, and **attests** to each action: it reports what it did and what the pool now holds. `gg pools` shows what each pool last attested, and when. gg reports a pool that has never attested, or whose last attestation is more than fifteen minutes old, as needing attention.

### Strategies

A [strategy](/reference/glossary/#strategy) says how to furnish a pool and the limits it runs within:

| Part | What it says |
|---|---|
| `environment` | The environment its members provide. |
| `inventory` | The pool's name, how many members it may hold (`size`), and how many it should keep warm (`warm`). |
| `image` | The image every member starts from, pinned by its digest. |
| `bounds` | How many members may run at once (`pool-max`), and the hours in which the pool may run them (`active-hours`). |
| `build` | Optionally, where to build the image from. `gg strategy build <name>` builds it. |

`gg strategy apply <name> <file>` manages a pool under a strategy, and `gg strategies` lists them.

### What happens to members

The control plane decides each pool action and the maintaining runner carries it out:

- **Kept warm.** When the pool holds fewer ready members than its `warm` target, or flights are waiting for its environment, it starts more, never beyond `pool-max` and never outside its active hours.
- **Reset.** After a member's flight ends and no lease stands, the pool resets a member, so the next flight starts from the strategy's image rather than from what the last flight left behind.
- **Rolled.** When someone applies a strategy with a new image, the pool replaces its members.
- **Removed.** The pool removes stopped members beyond its `size`, and creates nothing in their place.

A new member signs in without a person. The maintaining runner gives it a one-time code that is valid for ten minutes, and the member exchanges the code for a credential of its own, which lasts twelve hours with no renewal. A member cannot create other members.

While a flight waits for a pool, its reason says either that the pool is warming a member or that the pool's limits do not allow another one now.

The [pool host README](https://github.com/glyph-guild/gg/tree/main/deploy/pool-host) covers preparing a machine to host a pool.

## Taking a runner out

`gg runner retire <id|name>` takes a runner out of the fleet for good. Its credential stops working and it leaves the fleet list, but the control plane keeps its history. No one can undo this. [Run a runner](/guides/run-a-runner/#taking-a-runner-out-of-the-fleet) covers the details.
