---
title: Change the airspace
description: Pull the organisation's rules into a working copy, change them, see what a change would do, apply it, and register names, repositories and environments.
sidebar:
  order: 6
---

The [airspace](/reference/glossary/#airspace) is where an organisation keeps its rules and names: [root](/reference/glossary/#root), its [work kinds](/reference/glossary/#work-kind), its registered repositories, its [watches](/reference/glossary/#watch), its [strategies](/reference/glossary/#strategy) and its fleet profiles. The control plane holds what is in force. Use this guide to change any of it. Edit the airspace like a working copy: pull it into files, change them, check the difference, and apply it.

The control plane compares every change with what is in force. A change that tightens the rules applies directly. A change that loosens them waits for approval, as [The envelope: changing the rules](/concepts/envelope/#changing-the-rules) explains.

## Prerequisites

- gg is signed in to the organisation's control plane.
- A directory for the working copy, ideally a git repository, so that the organisation reviews and records every change. gg reads the working copy from the `airspace` setting, or from the current directory when that setting is empty:

  ```sh
  gg config set airspace ~/src/example-org-airspace
  ```

## 1. See what is in force

`gg airspace show` lists every declared name, with its role and its parent:

```sh
gg airspace show
```

```
investigate  role=work-kind  under=root  declared by Ada Lovelace
triage  role=watch  under=root  declared by Ada Lovelace
```

`gg airspace show <name>` prints one document in full, headed by its name, role and version, such as `# investigate   work-kind   v7`. For a work kind that extends another, it also prints the result of applying it over its parent.

`gg envelope show` prints root, the organisation's base rules, with its version.

## 2. Pull a working copy

```sh
gg airspace pull
```

gg writes one file per document, under folders such as `work-kinds/`, `watches/` and `strategies/`, with root as `root.yaml`. It lists the files it wrote and any it removed, or says `the working copy already matches the airspace`. Each file begins with a `based-on:` line naming the version gg pulled it from, such as `based-on: investigate@v7`.

A pull refuses to overwrite uncommitted changes in the working copy. Commit or discard them first.

## 3. Edit, then see the difference

Edit the files, then run:

```sh
gg airspace diff
```

```
work-kinds/review.yaml: tightening
work-kinds/investigate.yaml: widening - loops cannot be shown to tighten
watches/old-queue: missing from the tree - an intent to retire
```

Each line names a file and whether the change tightens or loosens the rules (`tightening` or `widening`). For a loosening change, gg names the field that makes it one. A file missing from the working copy shows as an intent to retire its name. A file that does not read as a document shows with the reason.

## 4. Apply it

```sh
gg airspace apply
```

gg applies the changed documents in a safe order, tightening changes first. For each document it prints one of:

- `<name>: applied as v8`: the change is in force.
- `<name>: nothing changed, still v7`.
- `<name>: widens <what> - flight GG-90 awaits <approver>`: the change loosens the rules, so it opened a flight that waits for approval. The document stays at its old version until someone answers that gate.

gg treats the working copy as one changeset. If a file does not read as a document, gg applies nothing. If the control plane refuses one document, gg stops there, says why, and lists the documents it did not try.

After an apply, commit the working copy, then pull again so the `based-on:` lines name the new versions.

## Declare a new name first

A document applies only to a name the airspace has already declared. A new work kind, watch, narrowing, strategy or fleet profile therefore needs its name declared before its file can apply. There are two ways:

- **Let apply declare it.** `gg airspace apply --declare-names` declares every missing name first, under root, or under the work kind a file extends, and then applies the documents. Without the flag, apply lists the missing names, with the command for each, and applies nothing.
- **Declare it explicitly**, with its role and name:

  ```sh
  gg airspace name work-kind investigate-deep
  gg airspace name work-kind investigate-instructions --under investigate
  ```

  The role is one of `work-kind`, `narrowing`, `strategy`, `watch` or `fleet-profile`. `--under` names the parent when it is not root, such as the work kind a new work kind extends. Declaring the name fixes its parent.

Declaring a name loosens the rules, so it may open a flight that waits for approval. gg then says which flight and who it awaits. No one can use the name until that gate opens, and the control plane refuses a document applied to it before then.

:::caution[A declared name lasts]
Removing a declared name takes a retirement, which itself needs approval. That is why apply declares names only when asked with `--declare-names`.
:::

## Retire a name

```sh
gg airspace retire old-queue
```

Retiring a name removes every rule in its document at once, so it always opens a flight that waits for approval. The name still governs until that gate opens, and it governs flights that start before then.

## Register a repository

Register a repository before any flight names it:

```sh
gg airspace repositories add --name web-app --provider forge --id R_123 --ref refs/heads/main --path example-org/web-app
```

| Option | Meaning |
|---|---|
| `--name` | What envelopes and flights call it. Required. |
| `--provider` | The key a runner resolves to a host of its own. Good Grief never reads it from the path. Required. |
| `--id` | The forge's own identifier for the repository. Required. |
| `--path` | The display path an intent is matched against, such as `example-org/web-app`. Required. |
| `--ref` | The fully qualified ref, such as `refs/heads/main`, that work starts from when a flight names no ref of its own. Without it, a flight about a work item has no checkout of this repository to work in. A bare `main` is refused. |
| `--credential` | `required` (the default) or `none`. Use `none` only for a repository a runner reaches with nothing to authenticate to, such as a local mirror. |
| `--narrowings` | A directory in the repository under which every document is a [narrowing](/reference/glossary/#narrowing). Leaving it out turns narrowings off for this repository. |

Registering a new repository loosens the rules, so it opens a flight that waits for approval. Until that gate opens, the name is not in the registry, and the control plane refuses a flight naming it. When the registration needs no approval, gg says who registered it and that nothing rode a flight.

## Change root directly

A person can also change root on its own, without the rest of the working copy:

```sh
gg envelope validate root.yaml
gg envelope apply root.yaml
```

Both read the file named, or standard input when the file is `-`.

- **`gg envelope validate`** checks the file without sending it anywhere. It prints `This is a valid envelope.` and the form the control plane will store it in, or `This is not an envelope.` with the reason. It exits with an error when the file is invalid, so it can run in a pipeline.
- **`gg envelope apply`** sends it. gg prints `Applied. This envelope is now v21.`, `Nothing changed.`, or, for a loosening change, `Waiting.` with the flight it rides and who it waits on. Applying the same loosening change again opens a second gate. Wait for the first gate to be answered.

## Chart an environment

Chart an [environment](/reference/glossary/#environment) before root lists it:

```sh
gg environment chart ui --means "<predicate>"
gg environments
```

`--means` describes what makes a machine part of that environment. Without a meaning, the chart records the name as a claim that nothing measures. With one, the chart records it as measured. Charting opens a flight that waits for approval. `gg environments` lists every charted environment, with its disposition, who charted it, when, and its meaning.

## The same steps in the console

Run `gg` with no arguments. `e` shows the envelope, and `r` shows the repositories. On the airspace tab, `enter` sets where the working copy is, and `a` opens the airspace actions: `p` pulls, `s` applies, and `o` shows what would change and the last apply.

## Related

- [Write a work kind](/guides/write-a-work-kind/): the document most changes concern.
- [Set up a watch](/guides/set-up-a-watch/): declaring and applying a watch.
- [The envelope](/concepts/envelope/): every rule a document can set.
