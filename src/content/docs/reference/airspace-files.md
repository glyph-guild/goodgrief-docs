---
title: Airspace files
description: Each kind of airspace document, where its file lives, the top-level keys it allows, and a short example of each.
sidebar:
  order: 5
---

The [airspace](/reference/glossary/#airspace) is where an organisation keeps its rules and names. `gg airspace pull` writes it as a working copy of YAML files, one per document, and `gg airspace apply` sends changes back. [Change the airspace](/guides/change-the-airspace/) describes that cycle. This page describes the files themselves.

## Layout

A working copy has this shape:

```
root.yaml
work-kinds/<name>.yaml
narrowings/<name>.yaml
strategies/<name>.yaml
watches/<name>.yaml
fleet/<name>.yaml
exposures/<name>.yaml
```

Each file is named after its document. A name is lower-case letters, digits and dashes, starts with a letter or digit, and is at most 64 characters. Before a new document can be applied, its name must be declared, as described in [Declare a new name first](/guides/change-the-airspace/#declare-a-new-name-first).

## Rules every file follows

- **Keys are closed.** Each kind of document allows a fixed set of keys, listed below. A key that is not on the list is refused, with a message naming it, so a misspelt key is never silently ignored. The same is true of the keys inside each section.
- **`based-on:`** may appear in any file. `gg airspace pull` writes it, naming the version the file was pulled from, such as `based-on: investigate@v7`. It is not a rule; leave it as pull wrote it.
- **Checking a file.** `gg envelope validate <file>` checks a root, work kind, narrowing or strategy file without sending it anywhere, and prints the form it will be stored in. `gg airspace diff` shows what applying the whole working copy would do.

## Root and work kinds

Root (`root.yaml`) holds the organisation's base rules. A work kind (`work-kinds/<name>.yaml`) holds the rules for one kind of work. Both are layers of the [envelope](/concepts/envelope/), the set of rules that governs a flight, and both are read with the same list of keys. Which layer may set a key is decided when the layers are combined.

| Key | Layer | What it says |
|---|---|---|
| `context` | Both | `scope`: the files the agent may change (the flight gets the overlap of root's and the work kind's). `constitution`: the version of the rules in force, set by root. See [`context.scope`](/concepts/envelope/#contextscope). |
| `repositories` | Root | The repositories flights may concern. See [`repositories:`](/concepts/envelope/#repositories). `repository` is accepted as a single-name spelling. |
| `environments` | Root | The environments flights may run in. See [`environments:`](/concepts/envelope/#environments). `environment` is accepted as a single-name spelling. |
| `models` | Root | The models a person may move one flight to. Left out, no one may; an empty list is refused. |
| `mcp-servers` | Root | The external tool servers loops may use, each defined once. See [MCP servers](/concepts/mcp-servers/). |
| `offers` | Root | Settings offered to every machine in the organisation, from the keys that can be offered. See [Offered configuration](/reference/configuration/#offered-configuration). |
| `obligations` | Both, added up | Machine checks and human checks. See [`obligations:`](/concepts/envelope/#obligations). |
| `instructions` | Both, added up | Standing guidance passed to the agent word for word: root's first, then the work kind's. |
| `learned` | Both, added up | What earlier flights found out about an environment, each entry with `against` (the repository and commit, image or environment it applies to) and `advice` (a list of sentences). Drafted by a flight and reviewed by a person before it applies. |
| `variables` | Root or work kind | Environment variables set on what a flight runs, as `NAME: value`. A flight with a work kind receives only the work kind's variables; root's apply only to a flight with no work kind. Never a secret. |
| `loops` | Work kind replaces root | How the work is done. See [`loops:`](/concepts/envelope/#loops). |
| `destinations` | Work kind replaces root | Where finished work goes. See [`destinations:`](/concepts/envelope/#destinations). |
| `produces` | Work kind | The facts the work can yield. See [`produces:`](/concepts/envelope/#produces) and [Fact vocabulary](/reference/fact-vocabulary/). |
| `accepts` | Work kind | What a flight of this kind may be about: `repository`, `tracker` or `envelope`. |
| `consults` | Work kind | The families of work kinds whose earlier findings on the same intent a flight of this kind receives. See [Investigations and findings](/concepts/investigations-and-findings/). |
| `description` | Work kind | One line for people choosing a work kind. No agent sees it. |
| `brief` | Work kind | The job a flight of this kind is to do, in one sentence. It opens the agent's task. |
| `targeting` | Work kind | Which machine gets the work: `any` (whichever asks first, the default) or `least-spent` (the machine whose [allowance](/reference/glossary/#allowance) has the most left is offered it first). |
| `hosts` | Work kind | The environment where the work's running application must be, when that differs from where the agent runs. |
| `abstract` | Work kind | `true` for a work kind that is only extended, never flown itself. |

Root must declare `context`, `obligations`, `loops` and `destinations`. A work kind must also declare `produces`, and need not declare `destinations` when it is abstract.

```yaml
# root.yaml (an example)
context:
  scope: "**"            # the agent may change any file...
  constitution: "1.0.0"  # ...under this version of the rules
environments:            # flights may run on these environments only
  - dev
  - ui
repositories:            # and concern these repositories only
  - "example-org/web-app"
instructions:            # every agent reads this, before the work kind's
  - "Keep the summary under 120 words."
obligations:
  in-scope:
    check: machine
    rule: no-file-outside-scope
  widen-root:            # loosening the rules waits for this approver
    check: human
    when: "envelope widens"
    approver: platform-owner
loops:
  implement:
    executor: frontier
    discharges:
      - in-scope
    moves:
      - read
      - edit
    budget:
      wall-clock: "20m"
    on-exhaustion: handoff-to-human
destinations:
  pull-request:
    kind: pull-request
    requires:
      - in-scope
```

[Write a work kind](/guides/write-a-work-kind/) has an annotated work kind file.

### A work kind that extends another

A work kind that names another with `extends:` states only what it changes. It allows these keys: `extends`, `abstract`, `description`, `brief`, `targeting`, `hosts`, `accepts`, `produces`, `consults`, `instructions`, `obligations`, `loops`, `destinations` and `remove`. `remove` takes things away from the parent, and allows `loops`, `destinations` and `obligations` (by name) and `instructions` (by exact text). It cannot set root's keys or `context`. [Write a work kind: make a variant without copying](/guides/write-a-work-kind/#make-a-variant-without-copying) explains how a child combines with its parent.

## Narrowings

A [narrowing](/reference/glossary/#narrowing) adds obligations to every flight that concerns a repository. It allows one key besides `based-on`:

| Key | What it says |
|---|---|
| `obligations` | Obligations, written as in root. Each is added to the flight's obligations and to its destination's `requires:`. |

Narrowings live in two places: `narrowings/<name>.yaml` in the airspace, and a directory inside a registered repository, named when the repository is registered with `gg airspace repositories add --narrowings <dir>`. By convention that directory is `.goodgrief/narrowings/`. Every file under it is read as a narrowing, so each file should hold one concern, which lets a repository's code-owner rules assign each one to its owner.

```yaml
# .goodgrief/narrowings/migrations.yaml (an example)
obligations:
  migration-review:             # any flight touching a migration...
    check: human
    when: "change.manifest touches migrations/**"
    approver: data-owner        # ...waits for this approver
```

## Watches

A [watch](/reference/glossary/#watch) looks at a work-item query on a schedule and nominates work from what it finds. It lives at `watches/<name>.yaml`.

| Key | Required | What it says |
|---|---|---|
| `shape` | Yes | What is being watched. `work-items` is the only shape. |
| `trigger` | Yes | `every`: the interval between sweeps, such as `"1h"`. |
| `host` | Yes | The tracker's address. |
| `credential` | Yes | A reference to the credential for the tracker. Never the value. |
| `filter` | Yes | The query to ask the tracker. A blank filter is refused. |
| `repository` | Yes | The registered repository that holds the procedure the sweep follows. |
| `skill` | Yes | The procedure's path in that repository. |
| `ref` | Yes | The ref the procedure is read at. |
| `mapping` | Yes | `subject` (the field that identifies an item), `version` (the field that changes when it changes) and `intent-key` (the field that names it outside Good Grief). |
| `pull-point` | Yes | What carries out each sweep, such as `resident-runner`. |
| `nominates` | Yes | One `flight` destination: the work kinds a nomination may open, and whether they open at once. |
| `bounds` | No | `active-hours` (`HH:MM-HH:MMZ`, in UTC), `cap-per-pass` (nominations per sweep) and `budget` (`flights` within a `window`). Each is unlimited when left out. |
| `for` | No | Whose watch it is, for a watch that belongs to one person. |

[Watches and sweeps](/concepts/watches-and-sweeps/) explains each field, and [Set up a watch](/guides/set-up-a-watch/) has an annotated example.

## Strategies

A [strategy](/reference/glossary/#strategy) says how a [pool](/reference/glossary/#pool) of machines for one environment is built, and the limits it runs within. It lives at `strategies/<name>.yaml` and is also applied with `gg strategy apply <name> <file>`.

| Key | Required | What it says |
|---|---|---|
| `kind` | Yes | The infrastructure managed. `docker-host`, containers on the host the maintaining runner lives on, is the only kind. |
| `environment` | Yes | The charted environment this pool provides. |
| `inventory` | Yes | `pool` (the pool's name), `size` (how many machines) and `warm` (how many to keep ready before anything asks; `0` when left out). |
| `pull-point` | Yes | How decided work reaches the pool: `resident-runner`. A strategy without one is refused. |
| `image` | Yes | The image each machine is reset to, pinned by digest. |
| `bounds` | No | `pool-max` (how many machines may be warm at once; `size` when left out) and `active-hours` (`HH:MM-HH:MMZ`). |
| `build` | No | Where the next image is built from: `repository`, `path`, `ref`, and optionally `dockerfile`. |
| `built-from` | No | What the image in force was built from: `repository`, `path` and `commit`. A build writes this. |
| `hooks` | No | The path to the project's own scripts for bringing its application up and down. Never the scripts themselves. |
| `filesystem` | No | How the working tree reaches the place those scripts run: `shared`, `push` or `pull`. |

```yaml
# strategies/dev.yaml (an example)
kind: docker-host
environment: dev
inventory:
  pool: dev-pool
  size: 2             # at most two machines...
  warm: 1             # ...one kept ready before any flight asks
pull-point: resident-runner
image: "registry.example.com/member@sha256:<digest>"
build:                # where `gg strategy build` builds the next image from
  repository: platform
  path: "deploy/member"
  ref: "refs/heads/main"
```

## Fleet profiles

A fleet profile describes one kind of machine in the [fleet](/reference/glossary/#fleet). It lives at `fleet/<name>.yaml`.

| Key | Required | What it says |
|---|---|---|
| `roles` | Yes | What the machine is for: `run`, `maintain`, or both. |
| `environment` | Yes | The environment the machine provides. |
| `agent` | No | The agent it runs, by name, never by path. |
| `forges` | No | The repository hosts it clones from. |
| `destinations` | No | Where it may open pull requests. |
| `relays` | No | STUN servers, so a console elsewhere can reach it. |
| `trackers` | No | Trackers it reads work items from, each with a credential reference. |
| `triage` | No | Trackers it may write work items to, each with a credential reference. |
| `sweeps` | No | `true` when it runs the organisation's watches while idle. |
| `credentials` | No | The credentials it needs, as references. |

[Add machines to the fleet: fleet profiles](/guides/enrol-machines/#fleet-profiles) explains each field and has an example.

## Exposures

An exposure says where a flight's preview may be published, so that a person can open it. It lives at `exposures/<name>.yaml`. There is no default exposure: an organisation that has declared none cannot publish a preview.

| Key | Required | What it says |
|---|---|---|
| `kind` | Yes | How the address is provided. `cloudflare-tunnel`, one named tunnel per slot, is the only kind. |
| `inventory` | Yes | The slots, described below. |

`inventory` allows these keys:

| Key | Required | What it says |
|---|---|---|
| `size` | Yes | How many slots there are. At least one. Each slot serves one flight at a time. |
| `hostnames` | Yes | The address pattern, containing `{slot}`, which becomes `01`, `02` and so on. |
| `credentials` | Yes | The credential reference pattern, also containing `{slot}`. |
| `port` | No | The local port a slot reaches. Left out, the provider decides. |
| `scheme` | No | How the connection reaches that port. `http` when left out. |

```yaml
# exposures/preview.yaml (an example)
kind: cloudflare-tunnel
inventory:
  size: 8                                        # eight previews at once
  hostnames: "preview-{slot}.example.com"        # preview-01 ... preview-08
  credentials: "local:exposure/preview-{slot}"   # one credential per slot
  port: 8080
```

The addresses are fixed in advance on purpose: a sign-in provider that will not accept a wildcard return address can be given each one.

## Related

- [The envelope](/concepts/envelope/): every rule a root or work kind can set, in depth.
- [Change the airspace](/guides/change-the-airspace/): pull, diff, apply, and declaring names.
- [Configuration](/reference/configuration/): a machine's own settings, which are not part of the airspace.
