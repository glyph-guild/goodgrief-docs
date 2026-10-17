---
title: Voice and tone
description: How Good Grief writes to the people who use it, in its documentation and in every message gg prints.
sidebar:
  order: 1
---

This guide covers everything a person reads: these pages, gg's help text, its error messages, the console, and the messages the control plane returns. Its aim is a voice that is formal, clear and useful. Every message should leave the reader knowing what happened and what to do next.

## Register

Write in a neutral, formal register:

- **No second person.** Write "the organisation", "a person", "the runner" or "the flight", not "you" and "your".
- **No contractions.** Write "does not", not "doesn't".
- **Active voice.** Write "The runner pushes the branch", not "The branch is pushed by the runner".
- **Plain imperatives for instructions.** "Run `gg login` again." is direct without being casual.

For example:

> A flight is one piece of requested work, such as finding out why login times out. Every flight has a number, such as `GG-42`.

## Rules

### 1. Say what happened, then what to do

Every error or refusal ends with a next step: a command, a setting, or a person to ask. When there is no next step, say how to get help: `gg bundle` produces a diagnostics bundle to send to the Good Grief team.

The model is `gg doctor`. Each check gives a **detail** that states what is true, followed by a **fix** that states exactly what to do:

> **detail:** no agent binary is configured, so this machine will take flights and never start an agent
>
> **fix:** Run `gg config set executor-binary <path>`, or set GG_EXECUTOR_BINARY for this shell only.

### 2. Give reasons only when they change what the reader does

One clause of explanation is enough, and only when it helps the reader act. Design rationale belongs in these pages and in code comments, not in messages. Do not use aphorisms or sayings in output.

### 3. Use plain words first

Prefer the plain word, and introduce a Good Grief term in brackets when the reader needs it: "waiting for a person to approve it (a gate)". Some words never belong in a message a person reads:

| Avoid | Write instead |
|---|---|
| principal | person |
| tenant | organisation (or the organisation's name) |
| nonce, mint, redeem | describe what the reader can do, such as "request a new one" |
| hold | the specific thing: "the takeover", "the lease" |
| somebody, nobody | someone, no one |

On these pages, link each term to the [glossary](/reference/glossary/) the first time it appears.

### 4. Never show internals

Do not show class or type names, exception text, internal rule names or design-document numbers. If a message has nothing for the reader to act on, it should say what was not changed and how to get help.

### 5. State facts without judgement

State facts plainly. Do not presume why the reader did something, and do not lecture. "A reason is required" is enough; there is no need to explain what a poor reason looks like.

### 6. Mechanics

- Messages are full sentences that start with a capital letter and end with a full stop.
- Labels, table cells, help summaries and `gg doctor` details are fragments: they start in lower case and have no full stop, such as "list this organisation's runners".
- Name the exact argument, file or setting that was wrong.
- These pages show commands in backticks; the terminal shows them plain.
- Say what was **not** changed when a command fails part-way: "Nothing was changed."

### 7. Be honest, and never ahead of the product

- Say plainly what did and did not happen.
- Never blame the reader.
- Give each command its own line in help, so a search for its name finds it.
- Never mention a command, option or behaviour before it exists.

## Before and after

These are real messages from gg and the control plane: what each one said before, and what it says today, following this guide.

| Before | After |
|---|---|
| gg fly takes one of some text, --uri, --ticket or --file, and this has more than one. An intent that says two things says nothing. | gg fly takes only one of: some text, --uri, --ticket or --file. More than one was given. Run it again with one. |
| unrecognised arguments. | gg runners does not recognise `--repos`. The list below shows every command and its options. |
| No repositories are registered. Nothing can be flown against a repository until one is - see gg airspace register. | No repositories are registered yet. To register one, run gg airspace repositories add. |
| not signed in — run \`gg login\` first. Registering a runner is a person's action. | This machine is not signed in. Run gg login, then try again. |
| GG-42 is held by somebody this control plane would not name. It is refused rather than granted: a hold nobody can be attributed to is still a hold. | GG-42 has already been taken over, and the control plane cannot say by whom. Nothing was changed. Run gg show GG-42 to see its current state. |
| this member's nonce buys nothing: it was never minted, it has expired, or it has already been redeemed. A nonce is spent exactly once, and a member cannot mint itself another - the pool has to warm a new one. | This pool machine cannot sign in: its one-time code has expired or has already been used, and a machine cannot request another. Start a new machine from the pool. |
| Control plane acknowledged nothing. | The control plane did not confirm the request, so it may not have been recorded. Run the command again; if this keeps happening, run gg bundle and send the result to the Good Grief team. |
| This tenant has nothing registered to fly against. The control plane answered, and the answer was nothing registered - so a flight here resolves its repository from the envelope or from nothing at all. | No repositories are registered for this organisation yet. A flight can still run without one. To register a repository, run gg airspace repositories add. |
| A withdrawal states why. 'The question ceased to apply' is the easiest sentence in this vocabulary to reach for, and one that does not say which question or what stopped applying is a flight quietly disposed of. | A withdrawal needs a reason that says which question stopped mattering and why. |
| That is not somewhere on this control plane. A signup can only return to a local path - anything naming another host would send a browser off this site immediately after it signed in here, which is the shape of a phish. | That link points to another website, so sign-up cannot return to it. Start again from the sign-up link the organisation provided. |

## Code comments

The same register applies to code comments. Contributors read comments, not customers, so a comment may explain design reasoning at length, but it stays plain and free of sarcasm.
