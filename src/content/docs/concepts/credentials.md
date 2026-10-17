---
title: Credentials
description: What a credential is to the control plane and to a machine, how gg seals and moves its value, and how a flight opens one with no one present.
sidebar:
  order: 10
---

A [credential](/reference/glossary/#credential) is a secret, such as an access token, that a [runner](/reference/glossary/#runner) uses to act on the organisation's behalf: to clone a repository, push a branch, read a work item, call an MCP server or run an agent.

Good Grief splits every credential in two:

- The [control plane](/reference/glossary/#control-plane) holds a **reference**: what the credential is for, the account it acts as, and what it may do.
- Machines the organisation controls hold the **value**, encrypted so that only its holders can open it.

The control plane can therefore say which credential a flight needs without ever being able to read one. This page explains that model. [Add and send credentials](/guides/credentials/) gives the commands step by step.

## What the control plane holds

A reference has exactly four parts:

| Part | What it says |
|---|---|
| Name | Where the value is found on a machine, such as `local:example-org/web-app` for a repository or `local:tracker/ado` for a tracker. gg derives the name from what the credential is for. |
| Kind | Where the value is kept. Today this is always `local`: in gg's credential store on a machine. |
| Account | The account the credential acts as, so every flight log can say who read what. |
| Scopes | `read`, or `read` and `write`. |

The control plane also records who registered the reference and when. It holds nothing else. Tests check that every message type that carries a credential reference, in either direction, contains no field that could hold a value.

### What a credential is for

A person registers each credential for exactly one purpose, with one option to `gg credential add`:

| Purpose | Option | Used for |
|---|---|---|
| A repository | `--repo <slug>` | Cloning, and with write access, pushing and opening pull requests. |
| An agent | `--agent <name>` | The agent's own sign-in, so it can run with no one present. |
| A tracker | `--tracker <key>` | Reading work items, and writing them where the rules allow. |
| An analysis service | `--analysis <key>` | A service that scans code and reports findings about a repository. |

gg accepts no other purpose.

### Read and write

A credential may **read**, which is the default, or may also **write**. A runner pushes a branch only when two separate permissions both hold:

1. **The organisation allows it**: the flight's [envelope](/reference/glossary/#envelope) names a destination that the work may land in.
2. **The credential can do it**: the person who registered the credential gave it the `write` scope.

Neither is enough alone. The envelope cannot widen a credential: a flight whose destination needs write access, run with a read-only credential, is refused at the landing, with a message naming the repository and the scopes its credential carries. The token itself must also carry matching permissions at its provider.

## What a machine holds

The value lives in gg's credential store on each machine that uses it, one file per credential, readable only by the user gg runs as.

### Sealed to its holders

Each value is **sealed**: encrypted with a key of its own, and that key is in turn locked separately for each **holder** that may open it. A holder is one of two kinds of key:

- **A person's key**, created with `gg key create`. A passphrase protects its private half, and gg never stores or sends that passphrase anywhere. gg registers its public half with the control plane, and `gg key list` shows it.
- **A machine's key**, which gg creates on each machine and keeps in a file readable only by the user gg runs as.

A credential can have several holders. Who holds it depends on how it arrived:

| How it arrived | Its holders |
|---|---|
| Registered with `gg credential add` | The person who registered it, and no one else. Registering costs no passphrase, because sealing needs only the public half of the person's key. |
| `gg credential trust-this-machine <name>` was run | The person, and now this machine. The person's passphrase unlocks their key for this one step. |
| Sent to a machine with `gg credential send` | The receiving machine. |

**What sealing protects, and what it does not.** Anything running as the same user as gg on a machine can read that machine's key, and so can open what the machine holds. Sealing protects copies of the store taken elsewhere, such as backups or disk images: a store copied to another machine does not open there. No machine can open a credential sealed only to a person without that person's passphrase.

### How a credential rests

`gg credential list` shows how each credential rests on this machine, worked out without opening anything:

| Shown as | Meaning |
|---|---|
| `sealed` | The value is here, sealed to its holders. |
| `plaintext` | The value is here unencrypted, written by an older release of gg. gg seals it the next time it reads it. |
| `not here` | This machine holds no value for the reference. |

`gg doctor` checks that every registered credential can be opened on this machine, and counts how many rest in each state.

A sealed credential carries a format version. A gg that does not recognise the version refuses the credential and says to update gg on the machine. An older gg that cannot see sealed credentials at all reports them as absent; if a person then registers the value again with that older gg, the newer gg uses the newer value and seals it.

## Moving a credential to a machine

A runner can only open a credential it holds, so the value has to reach the machines that need it. `gg credential send` does this.

1. **gg lists the machines first.** Run without `--runner`, gg finds every machine whose [fleet profile](/guides/enrol-machines/#fleet-profiles) names the credential, and prints the list, with whether each machine can be reached, before anything moves.
2. **gg asks for the person's passphrase once.** It unlocks the person's key, however many machines are on the list.
3. **gg re-locks the credential rather than decrypting it.** gg unlocks only the credential's own key and locks it again for each receiving machine's key. gg never decrypts the value itself on the sending machine. If the sending machine holds no copy, gg asks for the value and seals it in memory.
4. **It travels over a channel.** The sealed credential goes directly to each machine over an encrypted connection that the control plane arranges but cannot read. [Driving an agent: how the console reaches a machine](/concepts/driving-an-agent/#how-the-console-reaches-a-machine) explains these channels.
5. **The machine keeps it sealed.** The receiving machine writes the sealed credential to its store without opening it, then adds itself as a holder.

gg never leaves anything for a machine to collect later. It names any machine it cannot reach and sends nothing to it; send again when that machine is back.

**A machine must agree to be given credentials.** It accepts one only if its own configuration file says `"accept-configured": true`. gg reads this setting only from that file: no environment variable, `gg config set` or control plane can set it. A machine without it refuses, and gg names the setting.

A person can also create an agent's sign-in on the runner itself, with `gg agent login --runner <id|name>`. The runner starts the agent's sign-in, the person completes it in a browser and types back the code, and the sign-in creates the resulting token on the runner, which seals it to itself. The token never passes through the person's machine. The runner's configuration file must say `"accept-agent-login": true`, which is a separate setting from `accept-configured`.

## How a flight opens a credential with no one present

When a runner takes a flight, no one is there to type a passphrase. The flight works because the machine is already a holder.

1. **The control plane names the credentials.** When it gives the runner a [lease](/reference/glossary/#lease), it includes references for the repositories that flight works in and that require a credential, and nothing more. It never tells a runner which other credentials the organisation has. For each repository it chooses the current reference, ignoring any that were replaced or removed. On a machine someone has claimed, it chooses that person's reference.
2. **The runner opens each one on its own machine**, with its machine key, before it fetches anything.
3. **The runner hands each value only to what needs it.** For Git, it clears any credential helper configured on the machine and supplies one of its own that reads the value from the Git process's environment, so the value never appears on a command line. Requests to a repository host's or tracker's interface carry the value in a header only, never in an address or a request body. The runner gives the agent its sign-in token in the agent's environment. For MCP servers, see [MCP servers](/concepts/mcp-servers/#what-the-runner-does).

The runner never sends the value to the control plane, in a request, a log line or a trace. A test plants a value and checks every place the control plane writes, including its tables, flight log, log lines and traces, and fails if the value appears in any of them.

## When a credential is missing

What happens depends on where the gap is:

| Situation | What happens |
|---|---|
| No one has registered a credential for a repository the flight needs. | The flight waits, and the control plane gives it to no machine. `gg show` says which repositories need one and to run `gg credential add --repo <slug>`. |
| Someone has registered a credential, but the machine that took the flight cannot open it. | The runner hands the flight back at once, before fetching anything. The flight ends `failed`, and its log names the credential and what went wrong. |
| The machine holds the credential, but is not one of its holders. | gg treats it as a credential that cannot be opened, never as an absent one. The message names `gg credential trust-this-machine` as the fix. |
| The credential can only read, and the flight's destination needs write access. | The landing is refused at the credential, with a message naming the repository and its scopes. |
| An enrolled machine's profile names a credential the machine does not hold. | A maintenance flight for the machine appears, with a gate for the missing credential. The gate clears when the machine confirms it can open it. |

### Where a credential is

Each runner reports, every time it checks in, the names of the credentials it holds, never their values. The console's credentials tab uses these reports to show, for each credential, which machines hold it, which need it and lack it, and which hold it although nothing declares it.

## Replacing and removing a credential

- **Replacing.** Registering a credential again for the same purpose replaces the reference: flights use the new one from then on. Machines that already hold the old value keep it until someone sends them the new one, so send it again after replacing it.
- **Removing.** `gg credential rm <id>` removes the reference from the control plane and deletes the value on this machine. The control plane then tells every runner that checks in to delete its copy, whether or not it is flying, and repeats the instruction for thirty days so a machine that was offline still receives it.

Good Grief does not track when a credential expires at its provider. A token that expires there fails when it is next used.

## What is not built

- **A central store for values.** Machines hold every value; the control plane holds none.
- **Passing credentials from a pool host to its members.** A pool host does not pass the credentials it holds on to the members it creates.
- **Expiry for delivered credentials.** A credential sent to a machine stays until someone removes it.
- **A record of who sent which credential to which machine.**
