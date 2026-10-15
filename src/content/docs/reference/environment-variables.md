---
title: Environment variables
description: Every environment variable a person or operator may set for gg, what each one does, and the two that gg sets for a project's own scripts.
sidebar:
  order: 4
---

gg reads its settings from a [configuration file](/reference/configuration/), and every setting in that file can also be given by an environment variable. A variable that is set and not empty takes precedence over the file. A few variables have no setting in the file at all.

To see every variable gg reads on a machine, the value in force and where it came from, run `gg config show`.

## Variables that stand for a setting

Each of these has a key in the configuration file, and the variable overrides it. [Configuration](/reference/configuration/#settings) describes each setting in full.

| Variable | File key | What it does |
|---|---|---|
| `GG_CONTROL_PLANE` | `control-plane` | The address of the [control plane](/reference/glossary/#control-plane). Defaults to `http://localhost:5199`. |
| `EDITOR` | `editor` | The editor the console opens for writing an intent. Defaults to `vi`. |
| `GG_TAKE_COMMAND` | `take-command` | The command the console's `t` key starts to hand a person a flight's working tree. Defaults to `claude`. |
| `GG_INTENT_HOSTS` | `intent-hosts` | The work-item trackers gg reads work items from itself. |
| `GG_INTENT_READERS` | `intent-readers` | Trackers read through a separately installed tool server. |
| `GG_VCS_HOSTS` | `vcs-hosts` | Which repository host each provider key clones from. |
| `GG_DESTINATION_APIS` | `destination-apis` | Where a pull request is opened, per provider key. |
| `GG_TRACKER_APIS` | `tracker-apis` | Where an accepted change to a work item is written. |
| `GG_EXECUTOR_BINARY` | `executor-binary` | The [agent](/reference/glossary/#agent) program a runner starts. |
| `GG_INSTALLER` | `installer` | Where `gg update` gets this machine's installer. |
| `GG_RUNNER_LABELS` | `runner-labels` | The labels this machine's runner advertises, such as `environment=dev`. |
| `GG_AGENT_LOCATOR` | `agent-locator` | Where this machine's agent credential is kept, when it is not the local file. |
| `GG_RUNNER_SWEEPS` | `runner-sweeps` | Whether this machine's runner runs the organisation's watches when it has no flight: `on` (the default) or `off`. |
| `GG_RUNNER_HOLD_SECONDS` | `runner-hold-seconds` | How long a runner's request for work waits before coming back empty. Defaults to `10`. |
| `GG_POOL_ENDPOINT` | `pool-endpoint` | The controlled access point `gg runner maintain` uses to manage a [pool](/reference/glossary/#pool). |
| `GG_STUN_SERVERS` | `stun-servers` | STUN servers, which tell a machine how its address appears from outside its network. |
| `GG_AIRSPACE` | `airspace` | The directory that holds the working copy of the [airspace](/reference/glossary/#airspace). |
| `GG_ALLOWANCE` | `allowance` | The name of the [allowance](/reference/glossary/#allowance) this machine spends from. |
| `GG_ALLOWANCE_LIMITS` | `allowance-limits` | The ceilings that allowance is measured against. |

A variable is the way to change a setting for one shell or one command without touching the file. For example, to point one command at a different control plane:

```sh
GG_CONTROL_PLANE=https://<other-control-plane> gg whoami
```

## Variables with no setting in the file

| Variable | What it does |
|---|---|
| `XDG_CONFIG_HOME` | Where gg keeps the configuration file, the session and the credential store, in a `good-grief` folder. Unset means `~/.config`. Because the file's own location comes from this variable, it cannot be set in the file. |
| `XDG_STATE_HOME` | Where a flight's live view is written and read from. |
| `XDG_CACHE_HOME` | Where a runner clones a working tree, and where a held tree waits. |
| `GG_TIMING` | A file path. When set, the console appends one line to the file for each phase it spends time in: what it was, how long it took, and how many calls it made. See [A slow console](#gg_timing-a-slow-console). |
| `GG_STATE_DUMP` | A file path. When set, the console writes its whole state to the file when it exits, for a bug report. It includes work item titles; it does not include anything a runner printed. |
| `GG_IMAGE_DIGEST` | For a runner inside a container: the image the container was started from, set by whatever started it. The runner records it as part of the environment it reports, and a [diagnostics bundle](/troubleshooting/diagnostics-bundle/) includes it in the machine's fingerprint. Leave it unset outside a container. |

### `GG_TIMING`: a slow console

When the console feels slow, set `GG_TIMING` to a file, reproduce what felt slow, quit, and read the file:

```sh
GG_TIMING=/tmp/gg-timing.txt gg
```

Each line gives a time, a phase, its duration, and sometimes a count:

```
06:12:41.118  boot.round-one                 1426.4ms  reads=11
06:12:47.028  http GET /v1/board              383.1ms
06:12:47.140  refresh.Board                   275.6ms
06:12:47.142  render.Board                      1.3ms
06:12:48.180  paint.period                   1038.0ms
```

| Phase | What it measures |
|---|---|
| `boot`, `boot.*` | The first load, and each round of requests inside it. |
| `refresh.<tab>`, `refresh.lists`, `refresh.logs` | A tab's requests, made every thirty seconds. |
| `http <method> <path>` | Every request to the control plane: the path, never the query. |
| `read.log` | One flight's log, so that one slow request can be told from a slow batch. |
| `render.<tab>`, `paint.*`, `board.*` | Building and placing what a tab shows. |
| `paint.period` | The time from the start of one screen update to the start of the next. |
| `input.<command>`, `input.row-pointed` | A key press or a click, until the console has acted on it. |
| `pool.*`, `mem.mb`, `gc.gen2` | The state of the runtime at that update. |

Compare a phase with its `reads`: three hundred milliseconds for three requests and for twenty are different problems. When every phase is fast but the console still feels slow, look at `paint.period`, which includes time no other phase measures.

The file is written as the console goes, not when it exits, so a console that had to be stopped still shows where it was. It contains phase names, durations and counts, and no flight data. With the variable unset, nothing is measured or written.

## Variables gg sets for a project's scripts

A [strategy](/reference/glossary/#strategy) can name a project's own scripts for bringing its application up and down. When a runner starts one of those scripts for a flight that serves a preview, it sets:

| Variable | What it holds |
|---|---|
| `GG_PREVIEW_PORT` | The local port the application must serve on. |
| `GG_PREVIEW_URL` | The public address a person will open, when there is one. An application that builds links for others, such as a sign-in redirect address, needs this rather than `localhost` and the port. |

Each is set only when it has a value. A script should treat an unset variable as "no preview", not as an empty address.

## Variables not listed here

gg also uses variables to pass information between its own processes, such as from a runner to the agent it starts, or to a new pool machine. They are set and read by gg alone, and setting them by hand has no supported effect.

## Related

- [Configuration](/reference/configuration/): the file, each setting, and the `gg config` commands.
- [Check a machine with gg doctor](/troubleshooting/gg-doctor/): the checks that name these variables.
