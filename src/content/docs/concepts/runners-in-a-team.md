---
title: Runners in a team
description: Whose a machine is, which work the control plane offers each runner and why, and how a person keeps their own machine to their own flights.
sidebar:
  order: 9.5
---

In a team, some [runners](/reference/glossary/#runner) are shared: machines the organisation keeps for everyone's work. Others belong to one person, such as a laptop that should run only its owner's [flights](/reference/glossary/#flight). This page explains whose a machine is, which work each kind of machine receives, and how a person keeps a machine to themselves.

[Runners and the fleet](/concepts/runners-and-the-fleet/) explains how a runner and a flight find each other in general. This page is about what changes when several people share a fleet.

## Whose a machine is

Every runner is in one of three states:

| State | Meaning | Who may change it |
|---|---|---|
| **The organisation's** | A shared machine. Nobody may claim it. | An administrator may make it open. |
| **Open** | A shared machine that anyone in the organisation may claim. | Anyone may claim it. An administrator may make it the organisation's. |
| **Claimed** | One person's machine. | Its owner may unclaim it. So may an administrator, which is how to free a machine whose owner has left. |

A claimed machine can also be **reserved**. A reserved machine takes only flights its owner started; [Which work a machine receives](#which-work-a-machine-receives) says exactly which.

### How a machine starts

| How it joined | It starts as |
|---|---|
| `gg runner up` by a signed-in person | Open. Nothing claims it automatically. |
| An enrolment token with no ownership option | Open |
| An enrolment token made with `--tenant` (administrators only) | The organisation's |
| An enrolment token made with `--claim` | Claimed by the person who made the token |
| An enrolment token made with `--claim --reserve` | Claimed by the person who made the token, and reserved |
| A pool member | The organisation's |

[Add machines to the fleet](/guides/enrol-machines/) covers enrolment tokens.

### Changing it

| Command | What it does | Who may run it |
|---|---|---|
| `gg runner claim <id\|name>` | Makes an open machine the caller's. | Anyone, for an open machine, and only for themselves. |
| `gg runner unclaim <id\|name>` | Returns a claimed machine to open, and ends its reservation. | Its owner, or an administrator. |
| `gg runner reserve <id>` | Keeps a claimed machine to its owner's flights. | Its owner only. |
| `gg runner release <id>` | Lets a reserved machine take anyone's flights again. | Its owner only. An administrator cannot release a reservation, but can unclaim the machine. |
| `gg runner ownership <id> tenant\|open` | Makes a machine the organisation's, or open. | An administrator, once the owner or an administrator has unclaimed the machine. |

Nobody can claim a machine someone else has claimed until they unclaim it, and nobody can ever claim the organisation's machines. A reservation has no expiry: it lasts until its owner releases it or someone unclaims the machine.

`gg runners` shows whose each machine is, for example `organisation's`, `open` or `Ada Lovelace's, reserved`. The console's runners tab shows the same in its **whose** column.

## Which work a machine receives

When a runner asks for work, the control plane offers it the oldest flight that passes every one of these checks. A runner works on one flight at a time and asks again when it is free.

**Checks on the machine, before the control plane looks at any flight:**

1. **The machine is not parked.** The control plane offers a parked runner nothing, including its owner's flights.
2. **Its allowance has not reached its floor.** When the machine spends from an [allowance](/reference/glossary/#allowance) with a [floor](/reference/glossary/#floor), and the allowance has reached that floor, the control plane offers the machine nothing until the allowance recovers or someone overrides the floor.

**Checks on each flight:**

3. **The machine has the flight's environment.** A flight that requires an environment, such as `dev`, goes only to a machine that advertises it.
4. **Nobody opened the flight for a different machine.** A flight opened with `gg fly --runner <id>` goes only to that machine.
5. **The machine can host the work, when the work kind needs it.** A work kind that declares `hosts:` needs a machine with a free environment instance of that kind. Pool members never take such work.
6. **Plan order allows it.** A [leg](/reference/glossary/#leg) of a plan that follows another leg waits until that leg has landed.
7. **The reservation allows it.** A reserved machine takes a flight only if its owner started it. A flight with no recorded author, such as one opened by a repository event, never goes to a reserved machine.
8. **The flight is not someone else's personal work.** Work from a person's own [watch](/reference/glossary/#watch) goes only to a machine that person has claimed. Open and organisation machines never take it.
9. **Nobody else holds it.** The control plane does not offer a flight another runner already holds.
10. **Targeting allows it.** When the envelope sets `targeting: least-spent`, the control plane holds a flight for the runner whose allowance has spent the smallest share, unless the flight has waited more than a minute; then any runner may take it. With `targeting: any`, or no setting, the first runner to ask takes it.

Among the flights that pass, the control plane offers the oldest first.

### What each kind of machine takes

| Machine | Takes |
|---|---|
| The organisation's | Anyone's flights that match its environment. Never personal work. |
| Open | Anyone's flights that match its environment. Never personal work. |
| Claimed, not reserved | Anyone's flights that match its environment, plus its owner's personal work. |
| Claimed and reserved | Only flights its owner started, including the owner's personal work. |
| Pool member | Anyone's flights that match its environment, except work that needs hosting. |

### Who started a flight

A reservation turns on who started each flight. That depends on where the flight came from:

| The flight came from | It counts as started by |
|---|---|
| `gg fly`, or a new flight in the console | The person who ran it |
| A plan a person proposed | The person who proposed it |
| A plan's leg, which opens when a person approves the plan | The person who opened the plan |
| A personal watch | That watch's person |
| An organisation watch | The person who wrote the watch's current version |
| A repository event, a change to the rules, a registration or maintenance | Nobody. These never run on a reserved machine. |

### Credentials on a claimed machine

A claimed machine uses only credentials its owner registered. An open or organisation machine may use any of the organisation's credentials. When the control plane offers a machine a flight but the machine lacks a credential for one of its repositories, the flight stays available to other machines, and this machine waits until a credential arrives. [Credentials](/concepts/credentials/) covers registering and sending them.

On a claimed machine that is not reserved, this means a colleague's flight may wait for a credential the owner never registered. Reserving the machine avoids that.

## Other work a machine may receive

| Work | Which machines receive it |
|---|---|
| **Sweeps of a watch** performed on runners | Machines that have sweeps turned on (the `runner-sweeps` setting, on unless set otherwise) and declare the watch's tracker and credential. A personal watch's sweeps go only to a machine its person has claimed. A reservation does not stop a machine from performing the organisation's sweeps. |
| **Keeping a pool** | Only a machine enrolled under a fleet profile with the `maintain` role. |
| **Agent sessions and console connections** | On a claimed machine, only its owner may start them. On an open or organisation machine, the person who registered it, or an administrator. |
| **Attended flights** | A flight opened with `--runner <id> --attended` runs only on that machine, and only the person who registered the machine may open one. A busy machine refuses it. |

## Keep a machine to its owner's flights

To keep a laptop running only its owner's work:

1. Make it a runner, if it is not one already. It joins the fleet as an open machine:

   ```sh
   gg runner up
   ```

2. Find its id or name:

   ```sh
   gg runners
   ```

3. Claim it, then reserve it:

   ```sh
   gg runner claim <id>
   gg runner reserve <id>
   ```

`gg runners` now shows it as the owner's and reserved. From then on it takes only flights its owner started, and it uses only its owner's credentials.

To lend it to the team again, release the reservation with `gg runner release <id>`. To give it up entirely, `gg runner unclaim <id>` returns it to open.

To start machines claimed and reserved from the beginning, for example a person's own fleet of virtual machines, create their enrolment token with `--claim --reserve`. See [Add machines to the fleet](/guides/enrol-machines/).

## When a flight waits because of ownership

When the control plane cannot offer a flight to any machine, the flight says why, in `gg flights`, `gg show` and `gg why`. The reasons tied to ownership are:

| What gg says | What it means | What to do |
|---|---|---|
| Every runner advertising the environment is reserved to someone else. | The capacity exists, but someone holds it. | Ask the owner to release the reservation, or bring up a machine that is not reserved. |
| The flight is a person's own work, and none of their machines is asking for work. | Personal work runs only on a machine that person has claimed. | Start, or claim, one of that person's machines. |
| The machine someone opened the flight for is not asking for work. | Someone opened the flight with `--runner` for a machine that is offline or busy. | Start that machine, or open the flight without `--runner`. |
| The machine is parked. | A parked machine takes nothing. | Ask whoever parked it. |
| Nobody has registered a credential for a repository. | The machine the control plane offered the flight to lacks a credential. | Register the credential, or send it to the machine. |

## Related

- [Runners and the fleet](/concepts/runners-and-the-fleet/): leases, labels, environments and pools.
- [Add machines to the fleet](/guides/enrol-machines/): enrolment tokens and fleet profiles.
- [Run a runner](/guides/run-a-runner/): making a machine a runner.
- [Credentials](/concepts/credentials/): which credentials a machine can use.
