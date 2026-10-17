---
title: Check a machine with gg doctor
description: What gg doctor checks on a machine, what each failed check means, the fix it prints, and how to read its result from a script.
sidebar:
  order: 1
---

`gg doctor` answers the question "why is this not working?" without opening a [flight](/reference/glossary/#flight). It checks what gg needs on this machine, from reaching the [control plane](/reference/glossary/#control-plane) to the settings a [runner](/reference/glossary/#runner) needs, and it changes nothing. When something seems wrong, run it first:

```sh
gg doctor
```

## Reading the result

Each check prints one line: a mark, the check's name, and a **detail** that states what is true. After a failed check that can be fixed on this machine, gg prints a **fix** line that says exactly what to do. For example:

```
warn  executor          no agent binary is configured, so this machine will take flights and never start an agent
      fix: Run `gg config set executor-binary <path>`, or set GG_EXECUTOR_BINARY for this shell only.
```

The mark says what kind of result the line is:

| Mark | Meaning |
|---|---|
| `ok` | The check passed. |
| `warn` | The check failed, and gg still works. |
| `STOP` | The check failed, and gg cannot work until someone fixes it. |
| `note` | Not a fault. A standing statement about how the product works, which gg prints every time. |

When a check fails and nothing on this machine can fix it, gg prints this line in place of a fix:

```
This machine cannot fix this. Run gg bundle and send the result to the Good Grief team.
```

[Send a diagnostics bundle](/troubleshooting/diagnostics-bundle/) explains `gg bundle`.

gg prints notes last, under the heading `also reported (expected, and not a fault):`, so that a run with nothing wrong is all `ok`.

The checks run in order, and a check that depends on an earlier one says so rather than guessing. When gg cannot reach the control plane, for example, the session check prints `not checked: the control plane could not be asked` instead of reporting the session as broken.

## The checks

### Connection and identity

| Check | What a failure means | Fix it prints |
|---|---|---|
| `control plane` | gg could not connect to the control plane, or the control plane answered with an error. When no one has set an address, the detail adds that the address gg tried is the built-in default because `GG_CONTROL_PLANE` is not set. **Stops gg.** | Only when no address is set: "Run `gg config set control-plane <address>`, or set GG_CONTROL_PLANE for this shell only." Otherwise there is nothing this machine can change. |
| `protocol` | The control plane refuses the protocol this gg speaks. The detail is the control plane's own refusal, which names the versions it accepts. **Stops gg.** | "Run gg update; it shows the command for this install." |
| `binary` | This release is behind the one the control plane calls current, or no one ever published it as a release. Being behind is reported, never refused. | When behind: "Run gg update; it shows the command for this install." When the release is unrecognised, the detail says to check where this copy came from. |
| `session` | This machine is not signed in, or its sign-in has expired or someone has revoked it. **Stops gg.** | "Run gg login." |
| `telemetry` | States whether the control plane exports telemetry, and where to. It fails only as `not checked`, when gg cannot ask the control plane. | None. |

### This machine as a runner

| Check | What a failure means | Fix it prints |
|---|---|---|
| `runner` | This machine is not signed in, or its sign-in has expired, so `gg runner up` cannot register a runner from here. When it passes, the fix line reads "Run gg runner up." | "Run gg login." |
| `channel` | A data channel did not open on this build of gg, so a person on another machine cannot watch a runner here. Everything else still works. | None. |
| `reachable` | No STUN server is configured, so this machine can offer only its address on its own network. A person watching a runner from another network sees "no route between them". Or a STUN server is configured and did not answer. | With none configured: "Run `gg config set stun-servers <stun:host:port,...>`, or set GG_STUN_SERVERS to the same. gg has no built-in default." With no answer: check that the server is reachable from here. STUN uses UDP, which some networks block even when HTTPS works. |
| `handoff account` | Recent flights produced no closing account from the agent, so the material given to a person who takes one over holds measurements only. | None. |

A STUN server is a server a machine asks how its address appears from outside its own network.

### Credentials

| Check | What a failure means | Fix it prints |
|---|---|---|
| `credential store` | Never fails. States how gg protects credentials stored on this machine. | None. |
| `credentials` | This machine does not store a credential registered with the control plane. The detail lists each one by its reference, what it is for, and the identity it acts as. The check counts only credentials that belong to the signed-in person, or to no one in particular. **Stops gg.** | "Run gg credential add --repo <slug> on this machine for each one listed." |

[Add and send credentials](/guides/credentials/) covers registering a credential and sending it to another machine.

### Notices from the organisation

The control plane can hold notices for the organisation, such as a setting that needs attention. Each notice appears as its own line, named by the notice, with the control plane's own detail and, where it gives one, its fix. Whether a notice stops gg is the control plane's to say. `gg whoami` shows the same notices.

### What this machine is set up to do

These checks are about the job the machine was installed for, such as running flights or maintaining a [pool](/reference/glossary/#pool). None of them stops gg, because not every machine does every job.

| Check | What a failure means | Fix it prints |
|---|---|---|
| `executor` | No [agent](/reference/glossary/#agent) program is configured, so this machine will take flights and never start an agent. Or the configured program does not exist at the path given; the detail names the path. | With none configured: "Run `gg config set executor-binary <path>`, or set GG_EXECUTOR_BINARY for this shell only." When an agent program is already on the PATH, the fix names it instead. With a missing program: install the agent, or correct the path with `gg config set executor-binary <path>`. |
| `airspace` | No working copy of the [airspace](/reference/glossary/#airspace) is configured, so `gg airspace pull`, `diff` and `apply` act on the current directory. Or the configured directory is not a Git working tree, so a pull may overwrite an uncommitted edit without warning. | With none configured: "Run `gg config set airspace <path>` for the directory the airspace is written to, or set GG_AIRSPACE for this shell only." With a plain directory: run `git init` in it and commit what pull writes, or point the setting at an existing clone. |
| `trackers` | No work-item tracker is declared, so an agent cannot read the work item a flight is about and the console's browse tab is empty. This is expected when no flight here names a work item. Or a declared tracker names a credential that is not valid, that this machine does not hold, or that this machine holds and cannot open. | With none declared: run `gg config set intent-hosts <key=host\|reference>`, then `gg credential add --tracker <key>`. With a missing credential: run `gg credential add --tracker <key>` on this machine. With one this machine cannot open: if it is sealed to the signed-in person, run `gg credential trust-this-machine <locator>`; otherwise ask the person who holds it to send it here with `gg credential send`. |
| `forge` | No repository host is configured, so a flight that needs a repository cannot clone one here. When it passes, the detail also says whether a destination API is configured; without one, the runner will propose no change. | "Run `gg config set vcs-hosts <key=host>` for the forges this machine should serve, or set GG_VCS_HOSTS for this shell only." |
| `pool` | No pool endpoint is configured, so this machine maintains no pool. This is the ordinary answer on a machine that is not a pool host. | None. |

A **forge** is a repository host, such as a Git server. A **destination API** is where a runner opens a pull request. Both are settings described in [Configuration](/reference/configuration/).

### Standing notes

| Check | What it says |
|---|---|
| `moves` | Printed every time. The runner enforces the [moves](/reference/glossary/#move) an envelope declares only partly. It checks each tool on its own. A flight that declares `read` cannot edit a file directly, but it can still run shell commands, which can edit files. The runner measures and reports what a flight actually did. |
| `runner`, `pool` | When a gg service is installed on the machine, these two checks become notes. The service runs as its own user, with its own settings and its own runner identity, which a check run from a person's shell cannot read. The fix line names the command that shows the service, such as `systemctl status <unit>`. |

## Exit code

`gg doctor` exits with `1` when a check that stops gg has failed (a `STOP` line), and `0` otherwise. A `warn` line does not change the exit code, so a script can run `gg doctor` and act on the exit code alone.

## In a script

`gg doctor --json` prints the same report as JSON. Each entry in `checks` carries the check's `name`, whether it `passed`, its `detail`, whether it is `blocking`, whether it is `fixable`, its `fix`, and whether it `discloses` a standing note. The report also carries `exitCode` and `failed`, the number of checks that failed, not counting notes.

## Related

- [Send a diagnostics bundle](/troubleshooting/diagnostics-bundle/): everything `gg doctor` found, in a form to send to the Good Grief team.
- [Common problems](/troubleshooting/common-problems/): symptoms, causes and fixes.
- [Configuration](/reference/configuration/): every setting the fixes above name.
