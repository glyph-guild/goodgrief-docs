---
title: Update gg
description: Move gg to the release the organisation expects, for each way gg can be installed, and take configuration the control plane offers.
sidebar:
  order: 13
---

The organisation's [control plane](/reference/glossary/#control-plane) says which release of gg is current. `gg doctor` compares the installed release against it, on the `binary` line, and says when a newer one is expected.

## `gg update`

Run:

```sh
gg update
```

gg asks the control plane which release is current, works out how this copy of gg was installed, and prints one sentence about it:

- If this gg is current, it says so and does nothing.
- If this gg is newer than the release the control plane calls current, it leaves it alone and says so. `gg update` never moves a machine backwards.
- If the control plane cannot say what is current, gg reports that it does not know, rather than calling this release current.
- Otherwise, it prints each step it is about to run, with the reason for it, and runs them in order.

**gg never rewrites its own program.** Each step hands the work to whatever owns that install: `dotnet` for a .NET tool, or the installer for an install made by the installer. The new release is written beside the old one and moved into place by rename, so the program is never half-written.

When a step needs root and gg is not running as root, `sudo` asks for it on the terminal for that step only. Where there is no terminal to ask on, gg stops and prints the command to run instead. If any step fails, gg runs nothing further.

To see the plan without running it, run `gg update --json`, which prints the install type, the installed and current releases, and the commands it would run.

## Each kind of install

### Installed with the installer (macOS and Linux)

Run the installer again; the first line looks up the newest release:

```sh
v=$(curl -fsSLo /dev/null -w '%{url_effective}' https://github.com/glyph-guild/gg/releases/latest); v=${v##*/v}
curl -fsSL https://github.com/glyph-guild/gg/releases/download/v$v/install.sh \
  | sudo sh -s -- --version $v
```

The new release goes in beside the old one under `/usr/local/lib/gg/`, the `/usr/local/bin/gg` link moves to it, and, on a runner, the service restarts onto it. A name chosen with `--as` is remembered, so no flag is needed. The installer keeps the three newest releases, plus the one the link pointed at before, so going back is one more run with the older version. `--keep <n>` changes how many are kept; `0` keeps all of them.

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
$v=(irm https://api.github.com/repos/glyph-guild/gg/releases/latest).tag_name.TrimStart('v')
& ([scriptblock]::Create((irm https://github.com/glyph-guild/gg/releases/download/v$v/install.ps1))) -Version $v
```

A name chosen with `-Alias` is remembered.

### Pool members

gg inside a pool container cannot update itself, and `gg update` says so. To move a pool to a new release, build its image at that release and point the pool's [strategy](/reference/glossary/#strategy) at the new image.

## Offered configuration

Beyond the release, the control plane can offer settings to the machines that talk to it, so that nobody has to type them on each machine. To see what the control plane is offering this machine, run:

```sh
gg config offered
```

To take it, run `gg config accept` with the version that `gg config offered` printed:

```sh
gg config accept <version>
```

In the console, the help page (`?`) shows the same offer, and `o` takes it.

### What can be offered

Only these settings can be offered:

| Setting | What it controls |
|---|---|
| `stun-servers` | The servers a machine asks how it appears from outside its network. |
| `runner-labels` | What the machine's runner advertises, which decides the work it is offered. |
| `vcs-hosts` | Which host each repository provider is cloned from. |
| `destination-apis` | Where pull requests are opened. |
| `intent-hosts` | Which trackers work items are read from. |
| `tracker-apis` | Which trackers work items may be written to. |
| `control-plane` | The control plane itself. |

The first two may be applied with nobody watching: a wrong value degrades a connection or offers less work, and grants nothing. The rest change where something is fetched from or sent to, so **a person accepts them**, and sees exactly what is being changed.

Some settings are never offered, because no review makes them safe to take from elsewhere: the agent's location (`executor-binary`), the `installer`, and the switches that decide whether a machine accepts offers or credentials at all. Those are always set on the machine itself.

### Runners and offers

A runner takes offers by itself only if its configuration file says `"accept-offered": true`. A service installed with `gg service install`, or by the installer with `--control-plane`, has this set. Such a runner:

- takes what is offered when it starts, before it claims any work;
- notices a changed offer while it is idle, exits, and is restarted by its service onto the new values, never while it holds a flight;
- for a setting that needs a person, logs the `gg config accept` command to run and carries on, rather than restarting.

A machine enrolled under a [fleet profile](/guides/enrol-machines/#fleet-profiles) takes the settings its profile names without `gg config accept`, because a person approved them at the profile's gate. If the control plane cannot be reached, a runner starts on the settings it already has.

To see what a service's runner is using and offered, run the commands as its user. On Linux, for example:

```sh
sudo -u gg gg config show
sudo -u gg gg config offered
```

## Next steps

- [Install gg](/start-here/install/): the install routes this page updates.
- [Run a runner](/guides/run-a-runner/): runners as services.
