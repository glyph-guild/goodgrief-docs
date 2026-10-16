---
title: Add machines to the fleet
description: Enrol machines with a token so that nobody signs in on them, describe them with a fleet profile, and decide whose each machine is.
sidebar:
  order: 11
---

A machine joins the organisation's [fleet](/reference/glossary/#fleet) by **enrolment**. A person creates an enrolment token, the machine is installed with that token, and the machine registers itself as a [runner](/reference/glossary/#runner). Nobody signs in on it. It takes its configuration from the **fleet profile** the token names, so it is not configured by hand.

This page assumes the steps in [Run a runner](/guides/run-a-runner/) are familiar.

## Fleet profiles

A fleet profile describes one kind of machine. It is a document in the organisation's [airspace](/reference/glossary/#airspace), kept at `airspace/fleet/<name>.yaml`, and it says:

| Field | What it says |
|---|---|
| `roles` | What the machine is for: `run` (it takes flights), `maintain` (it keeps a [pool](/reference/glossary/#pool) warm), or both. |
| `environment` | The [environment](/reference/glossary/#environment) the machine provides. Flights for that environment can be offered to it. |
| `agent` | The [agent](/reference/glossary/#agent) it runs, by name, never by path. Where the program is stays the machine's own setting. |
| `forges` | The repository hosts it clones from. |
| `destinations` | Where it may open pull requests. |
| `relays` | Servers the machine asks how it appears from outside its network, so that a console elsewhere can reach it. |
| `trackers` | The work-item trackers it reads from, each with the credential to use. |
| `triage` | The trackers it may write work items to, each with the credential to use. |
| `sweeps` | Whether it runs the organisation's [watches](/reference/glossary/#watch) when idle. |
| `credentials` | The credentials it needs, as references, never values. |

For example:

```yaml
roles:
  - run
environment: dev
agent: claude
forges:
  - "ado=dev.azure.com/example-org"
destinations:
  - "ado=https://dev.azure.com/example-org/web-app/_apis/git/"
relays:
  - "stun:<relay-host>:3478"
```

A profile names credentials but never contains them; each machine resolves its own. Applying a profile for the first time, or adding to what it allows, opens a [gate](/reference/glossary/#gate), so a person approves it. Removing something applies at once. Airspace documents are changed with `gg airspace pull`, `gg airspace diff` and `gg airspace apply`.

## 1. Create an enrolment token

Run:

```sh
gg fleet enroll --profile dev-worker --uses 1 --expires 24h
```

- `--profile` names the fleet profile every machine enrolled with this token runs under.
- `--uses` is how many machines may enrol with it.
- `--expires` is how long it lasts, written as minutes, hours or days, such as `30m`, `24h` or `7d`. The longest allowed is seven days.

Both limits are required, so no token stays valid for ever.

The token is printed **once**. Store it somewhere private until it is used.

A token also decides whose each machine starts as:

| Option | The machine starts as |
|---|---|
| (none) | **Open**: anyone in the organisation may claim it. |
| `--claim` | **Claimed** by the person who created the token. |
| `--claim --reserve` | Claimed by that person, and **reserved**: it takes only that person's flights. |
| `--tenant` | **The organisation's**: nobody may claim it. Only an administrator can create this kind of token. |

Ownership is covered in more detail [below](#whose-a-machine-is).

To list the organisation's tokens, without their secrets, run:

```sh
gg fleet tokens
```

If a token gets loose, revoke it so that it enrols nothing more:

```sh
gg fleet revoke <id>
```

In the console, `t` on the runners tab lists the tokens, and `x` revokes the selected one.

## 2. Install the machine with the token

**The token is never passed as an argument**, to the installer or to gg, because arguments are kept in shell history and are visible to anyone on the machine who lists running processes. There are two ways to hand it over.

To type it at a prompt, add `--enroll`. The token is not echoed:

```sh
curl -fsSL https://goodgrief.dev/install.sh \
  | sudo sh -s -- \
      --control-plane <url> \
      --agent-binary /usr/local/bin/claude \
      --enroll
```

For a machine with no terminal, put the token in a file only the installing account can read, pass the file with `--enroll-file`, and delete the file afterwards:

```sh
umask 077
printf '%s' '<token>' > /tmp/enroll
curl -fsSL https://goodgrief.dev/install.sh \
  | sudo sh -s -- \
      --control-plane <url> \
      --agent-binary /usr/local/bin/claude \
      --enroll-file /tmp/enroll
rm -f /tmp/enroll
```

On a machine where gg is already installed, `sudo gg service install --control-plane <url> --enroll` does the same; it reads the token from a prompt or from standard input.

On its first start, the runner exchanges the token for a runner credential of its own. The token's use is spent. A token that has expired, been revoked or been used up is refused, and the refusal does not say which.

## 3. Finish bringing it up

After it registers, the machine appears in `gg runners` with its profile. If it cannot yet meet everything its profile asks for, such as a credential that only a person can provide or an agent that is not signed in, it says what it lacks, and a maintenance flight for the machine appears in `gg flights`, with one gate for each missing item. Answer them from a signed-in machine:

```sh
gg credential send --runner <id|name> --repo example-org/web-app
gg agent login --runner <id|name>
```

[Add and send credentials](/guides/credentials/) explains both commands. Each gate clears by itself once the machine confirms the item works, and the flight ends when the last one clears.

## Whose a machine is

Every runner is in one of three states:

- **The organisation's**: nobody may claim it.
- **Open**: anyone in the organisation may claim it.
- **Claimed** by one person.

A claimed machine can also be **reserved**, which means it takes only its owner's flights.

| Command | What it does | Who may run it |
|---|---|---|
| `gg runner claim <id\|name>` | Makes an open machine the caller's. | Anyone, for an open machine. |
| `gg runner unclaim <id\|name>` | Returns a claimed machine to open, and ends any reservation. | Its owner, or an administrator. |
| `gg runner reserve <id>` | Keeps a claimed machine to its owner's flights. | Its owner. |
| `gg runner release <id>` | Lets a reserved machine take anyone's flights again. | Its owner. |
| `gg runner ownership <id> tenant\|open` | Turns an organisation machine into an open one, or the reverse. | An administrator. |

A machine somebody else has claimed cannot be claimed until they unclaim it. An organisation machine can never be claimed. `gg runner ownership` refuses a claimed machine: it must be unclaimed first, so an owner never loses a machine without that being recorded. An administrator unclaiming a machine is how to free one whose owner has left.

In the console, the window for a runner offers `m` to claim it, `o` to hold it back for the organisation, and `h` to keep it to its owner's flights.

## When a runner's key changes

The console remembers each runner's key the first time it reaches the runner, and checks it every time after. When a machine is reinstalled, its key changes, and gg refuses to send anything to it, because it cannot tell a rebuilt machine from someone substituting a key. If the machine was rebuilt, trust its new key with:

```sh
gg runner repin <id>
```

## Pools

A [pool](/reference/glossary/#pool) is a managed set of identical containers, kept warm and reset between flights. A machine whose profile includes the `maintain` role can keep a pool, by running:

```sh
gg runner maintain <pool>
```

A [strategy](/reference/glossary/#strategy) says how a pool's members are built and the limits it runs within:

- `gg strategy apply <name> <file>` manages a pool under the named strategy.
- `gg strategy build <name>` builds the strategy's image.
- `gg strategies` lists the strategies, and `gg pools` lists what each pool last reported, and when.

Setting up a machine to host a pool involves more than gg; the [pool host README](https://github.com/glyph-guild/gg/tree/main/deploy/pool-host) in the gg repository covers it.

## Next steps

- [Add and send credentials](/guides/credentials/): give enrolled machines the credentials their profiles name.
- [Update gg](/guides/update-gg/): keep the fleet on the release the organisation expects.
