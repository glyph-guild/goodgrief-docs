---
title: Update gg
description: Move gg to the release the organisation expects, for each way of installing gg, and take configuration the control plane offers.
sidebar:
  order: 13
---

The organisation's [control plane](/reference/glossary/#control-plane) says which release of gg is current. `gg doctor` compares the installed release against it, on the `binary` line, and says when the organisation expects a newer one.

## `gg update`

Run:

```sh
gg update
```

gg asks the control plane which release is current, works out which kind of install this copy of gg is, and prints one sentence about it:

- If this gg is current, it says so and does nothing.
- If this gg is newer than the release the control plane calls current, it leaves it alone and says so. `gg update` never moves a machine backwards.
- If the control plane cannot say what is current, gg reports that it does not know, rather than calling this release current.
- Otherwise, it prints each step it is about to run, with the reason for it, and runs them in order.

**gg never rewrites its own program.** Each step hands the work to whatever owns that install: `dotnet` for a .NET tool, or the installer for an install made by the installer. The new release goes beside the old one and moves into place by rename, so the program is never half-written.

When a step needs root and gg is not running as root, `sudo` asks for it on the terminal for that step only. Where there is no terminal to ask on, gg stops and prints the command to run instead. If any step fails, gg runs nothing further.

To see the plan without running it, run `gg update --json`, which prints the install type, the installed and current releases, and the commands it would run.

## Each kind of install

### Installed with the installer (macOS and Linux)

Run the installer again. With no version given, it installs the newest release:

```sh
curl -fsSL https://goodgrief.dev/install.sh | sudo sh
```

The new release goes in beside the old one under `/usr/local/lib/gg/`, the `/usr/local/bin/gg` link moves to it, and, on a runner, the service restarts onto it. The installer remembers a name chosen with `--as`, so no flag is needed. The installer keeps the three newest releases, plus the one the link pointed at before, so going back is one more run with the older version. `--keep <n>` changes how many it keeps; `0` keeps all of them.

For `gg update` to do this itself, the machine needs to know where its installer comes from. Set the `installer` setting to a path to the install script, which gg runs, or an address, which gg downloads first:

```sh
gg config set installer <path-or-url>
```

Without it, `gg update` says that no installer is set up and changes nothing. The control plane can say which version is current but never where an installer comes from, so this setting is always the machine's own.

### Installed by hand

Repeat the steps in [Install gg: by hand](/start-here/install/#by-hand) with the newer version, including both native libraries.

### Installed as a .NET tool

`gg update` clears the local package cache, so that a newly published release is not reported as missing, then runs:

```sh
sudo dotnet tool update GlyphGuild.Gg.Cli --version <version> --tool-path /usr/local/lib/gg
```

To update by hand to the newest release, run the same command without `--version`.

### Windows

Run the installer again in PowerShell with the newer version:

```powershell
irm https://goodgrief.dev/install.ps1 | iex
```

The installer remembers a name chosen with `-Alias`.

### Pool members

gg inside a pool container cannot update itself, and `gg update` says so. To move a pool to a new release, build its image at that release and point the pool's [strategy](/reference/glossary/#strategy) at the new image.

## Offered configuration

Beyond the release, the control plane can offer settings to the machines that talk to it, so that no one has to type them on each machine. To see what the control plane is offering this machine, run:

```sh
gg config offered
```

To take it, run `gg config accept` with the version that `gg config offered` printed:

```sh
gg config accept <version>
```

In the console, the help page (`?`) shows the same offer, and `o` takes it.

### What can be offered

The control plane can offer only these settings:

| Setting | What it controls |
|---|---|
| `stun-servers` | The servers a machine asks how it appears from outside its network. |
| `runner-labels` | What the machine's runner advertises, which decides the work the control plane offers it. |
| `vcs-hosts` | Which host to clone from for each repository provider. |
| `destination-apis` | Where to open pull requests. |
| `intent-hosts` | Which trackers to read work items from. |
| `tracker-apis` | Which trackers may receive work items. |
| `control-plane` | The control plane itself. |

A machine may apply the first two with no one watching: a wrong value degrades a connection or offers less work, and grants nothing. The rest change where a machine fetches something from or sends it to, so **a person accepts them**, and sees exactly what changes.

The control plane never offers some settings, because no review makes them safe to take from elsewhere: the agent's location (`executor-binary`), the `installer`, and the switches that decide whether a machine accepts offers or credentials at all. A person always sets those on the machine itself.

### Runners and offers

A runner takes offers by itself only if its configuration file says `"accept-offered": true`. `gg service install`, and the installer with `--control-plane`, set this for the service they install. Such a runner:

- takes what the control plane offers when it starts, before it claims any work;
- notices a changed offer while it is idle, exits, and its service restarts it onto the new values, never while it holds a flight;
- for a setting that needs a person, logs the `gg config accept` command to run and carries on, rather than restarting.

A machine enrolled under a [fleet profile](/guides/enrol-machines/#fleet-profiles) takes the settings its profile names without `gg config accept`, because a person approved them at the profile's gate. If a runner cannot reach the control plane, it starts on the settings it already has.

To see what a service's runner is using and offered, run the commands as its user. On Linux, for example:

```sh
sudo -u gg gg config show
sudo -u gg gg config offered
```

## Next steps

- [Install gg](/start-here/install/): the install routes this page updates.
- [Run a runner](/guides/run-a-runner/): runners as services.
