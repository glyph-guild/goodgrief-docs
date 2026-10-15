---
title: What leaves the machine
description: The security model for deciding whether to trust Good Grief, covering what each part of gg can see, what it sends to the control plane, and what a person can check for themselves.
sidebar:
  order: 13
---

Good Grief runs AI agents against an organisation's repositories. Anyone deciding whether to trust it needs to know where the code, the credentials and the agent's work go. This page answers that, part by part. Each statement on it describes something gg's code does and its tests check, not an intention.

In short:

- **The organisation's code and credentials stay on machines the organisation controls.** The [control plane](/reference/glossary/#control-plane) never receives either.
- **The [runner](/reference/glossary/#runner) sends facts about the work**, drawn from a fixed, published list of fact types. The control plane checks every fact again when it arrives and refuses any that do not fit.
- **The definitions of everything that crosses** are published as a package that can be inspected.

## Two parts, two processes

gg is a single program with two roles, and they run as separate operating-system processes:

- **The console** acts for the person at the keyboard. It uses that person's sign-in.
- **The runner** takes flights and does the work. When the console starts a runner, it starts a separate child process. Installed as a service, the runner runs as a dedicated user with no login shell and no group but its own.

A person's sign-in is used only to register a runner. After that, the runner works with a credential of its own, issued to that machine, and never with the person's sign-in. A pool member, which nobody signs in on, exchanges a one-time code for a short-lived credential of its own.

The two roles see different things, and the rest of the design treats the runner as the less trusted of the two. The runner decides nothing about whether work is acceptable: it gathers facts and reports them, and the control plane evaluates the organisation's rules. A modified runner could report false facts, but it cannot approve its own work. [Anatomy of a flight](/concepts/anatomy-of-a-flight/#what-a-runner-reports-and-what-it-means-for-the-flight) explains how the control plane, not the runner, decides how a flight ended.

## What stays on the machine

| Stays on the machine | Notes |
|---|---|
| The repository | The runner clones it into a working copy for the flight, on its own machine. |
| Credential values | Held in gg's credential store, sealed to their holders. See [Credentials](/concepts/credentials/). |
| The agent's transcript | The full record of what the agent said and did. It is written outside the flight's working copy, so it survives the flight, and nothing deletes it automatically. Facts carry only a reference to it: where it is, its size and a hash of its contents. |
| The agent's live output | Shown to a person watching over a direct channel between the two machines. It is not stored by the control plane. |

Work does leave the machine for places the organisation chose, never for the control plane:

- **The runner pushes branches** to the organisation's own repository host, and opens pull requests there, only where the envelope allows and the credential has write access. The control plane does not push.
- **The agent talks to its own model provider**, under whatever account the agent is signed in with. gg starts the agent on the machine; it does not route or see that traffic.
- **Trackers and MCP servers** are called directly from the machine, with credentials opened there.

## What the runner sends

The runner sends the control plane these kinds of information:

| What | What it contains |
|---|---|
| Registration | The machine's name and the public half of its own key. |
| Check-ins | That the runner is alive, the labels it advertises, the names (never the values) of the credentials it holds, and the agent sessions it is running. |
| Readiness | Whether its agent is present and signed in, and, on a pool host, what each pool and environment it keeps now holds. |
| Machine readings | CPU and memory use. |
| Allowance readings | How much of its agent allowance the machine has spent. |
| Lease requests and releases | Requests for work, and what became of each turn: `completed`, `failed`, `abandoned` or `outstanding`. |
| Facts | Recorded observations about a flight, described below. |

### Facts, from a registered list

A [fact](/reference/glossary/#fact) is one recorded observation about a flight. Every fact has a type from a fixed list, and each type has a fixed shape. The list is versioned: `gg version` prints the fact vocabulary version this gg produces, and the published package records which types each version contains.

Most facts are measurements:

| Fact | What it carries |
|---|---|
| `change.manifest` | Which files changed, and how many lines were added and removed in each. **File paths and counts, never file contents.** |
| `source.provenance` | Which repository and commit the flight worked from, and how many files and bytes it held. |
| `environment.identity` | A fingerprint of the machine, the tools and versions present, and hashes of lock files. |
| `loop.digest` | What the agent did, extracted mechanically from its run rather than summarised by a model: the files it read and left alone, the files it edited, the searches it made, and the errors it hit. |
| `loop.outcome` | How the agent's run ended, how long it took, which moves it used, and a reason. |
| `loop.transcript` | Where the transcript is on the machine, never the transcript itself. |
| `intent.read` | Which file a flight was opened about: its repository, path, commit, hash and size. **Never its text.** |
| `destination.pushed`, `destination.landed` | Where the work was pushed or landed. |

Some facts carry words the agent wrote, because a person needs to read them:

- a question the agent could not answer from the work (`loop.question`);
- a proposed title and description for a pull request (`landing.proposal`);
- a proposed change to a work item, with its reason (`work-item.proposal`);
- an airspace document the flight drafted, for a person to approve (`document.proposal`).

The search terms and error messages in `loop.digest`, and the reason in `loop.outcome`, can also contain text from the repository or from the agent. An organisation should treat these as it would treat a summary of the work written by someone who has read the code.

### Checked before it leaves, and again when it arrives

On the runner, every fact passes through the same three steps, in an order the code's types enforce:

1. **Cleaned.** Every text value is stripped of control characters, so nothing in a fact can drive a terminal that later displays it.
2. **Hashed.** A hash of the fact as observed is computed and kept with it.
3. **Filtered.** File paths that the organisation's sensitivity rules place above its permitted level are removed from the change list, and the list records how many were withheld. The hash is not recomputed, so it still describes what was observed.

Only the result of the third step can be sent. When the facts arrive, the control plane checks each one again, independently of the runner:

- a fact whose type is not on the list is refused, not ignored;
- a fact containing control characters is refused, not cleaned;
- a fact larger than its size limit is refused, not cut short;
- the control plane works out each path's sensitivity again from its own copy of the organisation's rules, ignoring the level the runner claimed, and refuses a fact containing a path above the permitted level.

Each refusal is recorded on the flight's log, with the reason and without the refused content, so that a misconfigured or modified runner is visible to the organisation.

## What the control plane never receives

**Code.** No fact type has a field for file contents. The change list carries paths and line counts, and a fact about a file names it and its hash, never its text.

**Credential values.** Every message type that carries a credential reference, in either direction, is checked by tests to have no field that could hold a value. The single message that carries a credential at all, used when a person sends one to a machine, carries it sealed to the receiving machine's key and travels over a direct channel, not through the control plane. A further test plants a credential value and searches every place the control plane writes, including its tables, flight log, log lines and traces, and fails if the value appears in any of them. On the runner, credentials go only to the process that needs them, through its environment or a request header, never on a command line or in a request body.

**What crosses a channel.** When a console reaches a runner, to watch it, drive an agent or send a credential, the control plane introduces the two machines. The connection details it passes along are sealed so that it cannot read or alter them, and the connection itself is encrypted end to end. If the connection goes through a relay, the relay forwards encrypted traffic it cannot read. [Driving an agent](/concepts/driving-an-agent/#how-the-console-reaches-a-machine) explains how a channel is set up.

## Diagnostics bundles

When something goes wrong, `gg bundle` produces a diagnostics bundle for the Good Grief team. It **prints the bundle to the terminal and sends nothing**: a person reads it and decides whether to send it.

A bundle contains:

- the gg version, protocol version and fact vocabulary version;
- the machine's fingerprint, in the same form a flight records, so the two can be matched;
- every check `gg doctor` ran, passing or not, and a line for each problem it found.

A bundle has no field that could hold anything a runner or agent printed. Tests send a token-shaped string through the real live-output path, and separately place one in a work item's title, then check that neither appears in a bundle or its printed form. The console's own state, which is also used for diagnostics, cannot hold a passphrase typed into the console: tests check that no part of that state could carry one.

## While gg hosts an editor

Some console actions open the editor named by `$EDITOR`. gg runs the editor inside a terminal of its own, so that it can keep its top row on screen. **This puts gg in the middle: every byte typed into the editor, and everything it draws, passes through the gg process.** A program given the terminal directly would be invisible to gg.

What gg does with those bytes:

- **Nothing is kept.** The part of gg that hosts the editor holds no state between sessions; a test checks that it has none.
- **Nothing is written to disk.** A test fails if the hosting code contains any file-writing call.
- **Nothing is sent anywhere.** The hosting code makes no network calls and opens no credentials. It starts the editor, reads its output, draws it, and restores the terminal.

When the editor exits, however it exits, gg restores the terminal's settings as it found them. On a machine where gg cannot host the editor, such as Windows or when its output is piped, gg hands the terminal to the editor directly and says so.

## What a person can audit

**The wire contract.** Every message that crosses between an organisation's machines and the control plane is defined in one package, `GlyphGuild.Gg.Contracts`, published with each gg release. Tests hold it to three rules:

- **One outside dependency, named.** The package depends on exactly one third-party library, a YAML parser, and a test fails if that changes in any way.
- **Every message is listed.** Every type that crosses the wire carries a fixed identifier and appears in the package's own list of messages. A test fails if a type is missing from the list, or the list names one that no longer exists.
- **The version means something.** A fingerprint of everything that crosses the wire is recorded against each version of the package, and changing the wire without changing the version fails the build. The fact vocabulary is versioned the same way, on its own.

**The flight log.** Every flight's log records what happened to it, including every fact the control plane refused and why. `gg log <flight>` and `gg facts <flight>` show it.

**The machine itself.** The transcript of every flight stays on the machine that ran it, and each transcript fact carries a hash of it, so what an agent did can be checked against what was reported.
