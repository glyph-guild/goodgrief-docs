---
title: Security
description: How Good Grief keeps code and credentials on the organisation's machines, who can do what, what a person must approve, and where each part is explained in full.
sidebar:
  order: 12.9
---

Good Grief runs AI agents against an organisation's repositories, with the organisation's credentials. This page gathers its security model in one place: where code and credentials live, how people and machines prove who they are, what the rules allow, what a person must approve, and what each machine agrees to. Each section summarises one part and links to the page that explains it in full.

## Code stays where it is

gg talks to a service called the [control plane](/reference/glossary/#control-plane). The control plane keeps the record of the work: what someone asked for, who approved what, and how each piece ended. It **never sees the code or the credentials**. The [runner](/reference/glossary/#runner) clones repositories, holds credentials and runs agents, all on machines the organisation controls. What it sends to the control plane are facts about the work, never the work itself.

Every fact has a type from a fixed, published list, and no type has a field for file contents or a credential's value. The runner cleans and filters each fact before sending it, and the control plane checks each one again when it arrives and refuses any that do not fit. [What leaves the machine](/concepts/what-leaves-the-machine/) lists everything the runner sends and how both ends check it.

## The control plane decides; the runner does

The runner gathers facts and reports them. It does not decide whether work is acceptable. The control plane decides, by evaluating the organisation's rules against those facts. A modified runner could report false facts, but it cannot approve its own work.

The console and the runner run as separate processes. Installed as a service, the runner runs as a dedicated user with no login shell and no group but its own. [What leaves the machine: two parts, two processes](/concepts/what-leaves-the-machine/#two-parts-two-processes) explains the split.

## How people and machines prove who they are

**People** sign in with `gg login`. gg prints an address and a code. Open the address in a browser, sign in with the organisation's usual account, and approve only when the code on the page matches the one gg printed. `gg logout` asks the control plane to end the session before deleting the local copy. [Sign in](/start-here/sign-in/) covers the steps.

:::caution[Anyone with an invitation link can join]
Anyone who opens the link can join the organisation. Send it only to the newcomer, in a way both people can trust.
:::

**Machines** have keys of their own, and people do not use them. gg uses a person's sign-in only to register a runner. After that, the runner works with a credential issued to that machine, and renews it itself. A pool member exchanges a one-time code for a short-lived credential of its own.

**Enrolment tokens** let a machine join the fleet with no one signing in on it. Every token has a limit on how many machines may use it, and expires within at most seven days. gg prints it only once. `gg fleet revoke` ends it early. Neither the installer nor gg takes a token as an argument, because the shell keeps arguments in its history. Each reads it from a prompt or a file instead. [Add machines to the fleet](/guides/enrol-machines/) covers tokens.

## Credentials are sealed to their holders

The control plane holds a **reference** to each credential: what it is for, the account it acts as, and whether it may read or also write. Only machines the organisation controls hold the **value**, and each value is sealed: encrypted so that only its holders, a person's key or a machine's key, can open it.

- **A person's key** is protected by a passphrase that gg never stores or sends. No one can recover a lost passphrase.
- **Sending a credential** to a machine re-locks it for that machine's key without decrypting it, and it travels directly between the two machines, not through the control plane.
- **A flight opens a credential with no one present** because the machine is already a holder. The control plane names only the credentials that flight needs, and the runner hands each value only to the process that needs it, never on a command line.
- **Sealing has a limit.** Anything running as the same user as gg on a machine can read that machine's key. Sealing protects copies of the store taken elsewhere, such as backups.

[Credentials](/concepts/credentials/) explains the model, and [Add and send credentials](/guides/credentials/) gives the commands.

## The rules bound every flight

Every flight runs inside an [envelope](/concepts/envelope/): the organisation's rules for which repositories it may concern, where it may run, what the agent may do and for how long, which files it may change, what a person must approve, and where finished work may go. Only root, the organisation's base rules, may set the repositories and environments. The envelope's scope check covers every file the flight changed at any point, and no approval can excuse a file outside the scope.

:::caution[Moves are enforced only partly]
The runner checks each tool call on its own. A flight that declares `read` cannot edit a file directly, but it can still run shell commands, and a shell command can edit files. The scope check catches the result, and the runner measures and reports what the flight actually did. [The envelope: loops](/concepts/envelope/#loops) explains moves.
:::

**Loosening the rules needs approval.** The control plane compares every change to the rules with what is in force. A change that tightens them applies at once. A change that loosens them, such as a new work kind, a new name or a new MCP server, waits for a person to approve it. [Change the airspace](/guides/change-the-airspace/) covers the cycle.

## People approve what matters

A [gate](/concepts/gates-and-decisions/) stops a flight until a person decides. The rules say who decides. When they name a role, anyone in the organisation who may decide gates can answer. When they name a person, no one else can answer for them, not even an administrator.

- **A decision is about one version of the work.** If the work changes after a decision, the gate opens again and the earlier decision no longer counts.
- **The first answer stands.** The control plane refuses a second, different answer to the same gate.
- **Decisions belong to one flight.** An approval on one flight does not satisfy a gate on another.
- **An agent's proposal gets a person's review.** When an agent proposes a flight, the person answering its gate is the only review the agent's words get.

[Gates and decisions](/concepts/gates-and-decisions/) explains obligations, evidence and halting.

## Whose a machine is, and what it agrees to

A machine is the organisation's, open, or claimed by one person. A claimed machine uses only credentials its owner registered, and a reserved machine takes only its owner's flights. [Runners in a team](/concepts/runners-in-a-team/) explains ownership.

Three abilities stay off until someone turns them on in the machine's own configuration file. gg reads these settings only from that file. No environment variable, `gg config set` or control plane can set them.

| Setting | What it allows |
|---|---|
| `accept-configured` | Receiving credentials that a person sends with `gg credential send`. |
| `accept-agent-login` | Creating an agent's sign-in on the runner, with `gg agent login --runner`. |
| `accept-agent-sessions` | A person driving an agent on the machine from another console. |

Even with `accept-agent-sessions` on, a claimed machine admits only its owner. Any other machine admits the person who registered it, or an administrator. The control plane records who reached which machine and when, but nothing of what the person typed. [Driving an agent](/concepts/driving-an-agent/#who-may-drive-a-machine) covers sessions.

## Connections between machines

When a console reaches a runner, to watch it, drive an agent or send a credential, the control plane introduces the two machines. The connection details it passes along arrive sealed, so it cannot read or alter them, and the connection is encrypted end to end. A relay, when one is needed, forwards encrypted traffic it cannot read. [Driving an agent: how the console reaches a machine](/concepts/driving-an-agent/#how-the-console-reaches-a-machine) explains how.

## Installing gg

goodgrief.dev serves byte-for-byte copies of the newest release's installers, and checks that gg's own release workflow built each one before publishing it. The installer checks each download against the release's build attestation before unpacking it, and installs nothing if they do not match. `gh attestation verify` lets a person check an installer or archive themselves. [Install gg](/start-here/install/) covers each way to install.

## Diagnostics and the editor

- **`gg bundle` sends nothing.** It prints a diagnostics bundle. Read it, then decide whether to send it. A bundle has no field for a secret, but it does name the organisation and the person. [Send a diagnostics bundle](/troubleshooting/diagnostics-bundle/) lists its contents.
- **gg keeps nothing it sees while it hosts an editor.** Everything typed into an editor gg hosts passes through gg, which stores none of it, writes none of it to disk and sends none of it anywhere. [What leaves the machine: while gg hosts an editor](/concepts/what-leaves-the-machine/#while-gg-hosts-an-editor) explains how tests hold it to that.

## What a person can check

Good Grief publishes the definitions of every message that crosses between an organisation's machines and the control plane as one package, `GlyphGuild.Gg.Contracts`. Every flight's log records what happened to it, including every fact the control plane refused and why. The agent's full transcript stays on the machine that ran it, and the control plane holds its hash. [What leaves the machine: what a person can audit](/concepts/what-leaves-the-machine/#what-a-person-can-audit) explains each.

## Related

- [What leaves the machine](/concepts/what-leaves-the-machine/): everything the runner sends, and how both ends check it.
- [Credentials](/concepts/credentials/): sealing, holders and how a flight opens a credential.
- [The envelope](/concepts/envelope/): every rule a flight runs under.
- [Gates and decisions](/concepts/gates-and-decisions/): what a person approves, and who.
- [Runners in a team](/concepts/runners-in-a-team/): whose a machine is and which work it takes.
