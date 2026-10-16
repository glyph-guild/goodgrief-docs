---
title: Install gg
description: Install the newest release of the gg command on a laptop running macOS, Linux or Windows, and check that it works.
sidebar:
  order: 3
---

gg is a single command-line program. The same program opens the [console](/reference/glossary/#console) and, on a machine set up for it, works as a [runner](/reference/glossary/#runner). This page installs it on a laptop: the program and nothing running. Making a machine a runner is a different install, described in [Run a runner](/guides/run-a-runner/).

The commands on this page install the newest release of gg. The installers always install one exact version, so each command first looks up which release is the newest and then installs that one.

## Installing a particular release

To install a particular release instead, such as the one the rest of the organisation runs, replace the first line with that version: `v=<version>` on macOS and Linux, or `$v='<version>'` on Windows. The [releases page](https://github.com/glyph-guild/gg/releases) lists every release.

## macOS or Linux

Run:

```sh
v=$(curl -fsSLo /dev/null -w '%{url_effective}' https://github.com/glyph-guild/gg/releases/latest); v=${v##*/v}
curl -fsSL https://github.com/glyph-guild/gg/releases/download/v$v/install.sh \
  | sudo sh -s -- --version $v
```

The first line asks GitHub which release is the newest; the second downloads that release's installer and runs it.

The installer:

- picks the build for the machine it runs on;
- checks the downloaded bytes against the release's build attestation before unpacking them, and installs nothing if they do not match;
- installs gg under `/usr/local/lib/gg/<version>/`, with its two native libraries beside it, and links `/usr/local/bin/gg` to it;
- makes sure `/usr/local/bin` is on the PATH of the shell it was run from, adding a line to that shell's startup file if it is missing and naming the file;
- **starts nothing.** No service is installed and no user is created.

It ends by printing the two remaining steps, which are covered in [Sign in](/start-here/sign-in/):

```sh
gg config set control-plane <url>
gg login
```

## Windows

In PowerShell, run:

```powershell
$v=(irm https://api.github.com/repos/glyph-guild/gg/releases/latest).tag_name.TrimStart('v')
& ([scriptblock]::Create((irm https://github.com/glyph-guild/gg/releases/download/v$v/install.ps1))) -Version $v
```

The Windows installer installs for the current user only and needs no administrator rights. To write the control-plane address at the same time, add `-ControlPlane <url>`.

On Windows, gg is a command-line tool only. Every command works, but running `gg` with no arguments does not open the console, because the terminal features the console needs are not yet available there.

## When another program is called gg

At least one other program, a Git interface, is also called `gg`. If a different program already sits where the installer would put its link, the installer stops rather than replace it, and asks for another name. To answer in advance, for example on a machine with nobody at the keyboard, pass `--as`:

```sh
v=$(curl -fsSLo /dev/null -w '%{url_effective}' https://github.com/glyph-guild/gg/releases/latest); v=${v##*/v}
curl -fsSL https://github.com/glyph-guild/gg/releases/download/v$v/install.sh \
  | sudo sh -s -- --version $v --as goodgrief
```

On Windows, pass `-Alias goodgrief` instead.

If another `gg` is merely earlier on the PATH, it is not at risk and the install continues; the installer says that the other program will keep the name, and `--as` gives this one its own. Every hint the installer prints then uses the chosen name, and the name is remembered, so a later update needs no flag. These pages always write `gg`.

A runner is always installed as `gg`, because its service runs `/usr/local/bin/gg`.

## By hand

To see every step, download the newest release's archive and install the files directly. On Linux, for example:

```sh
curl -fsSL https://github.com/glyph-guild/gg/releases/latest/download/gg-linux-x64.tar.gz | tar xz
sudo install -m 0755 gg /usr/local/bin/gg
sudo install -m 0644 libporta_pty.so libonigwrap.so /usr/local/bin/
gg --version
```

To download a particular release instead, replace `latest/download` with `download/v<version>`. A release carries archives for `linux-x64`, `linux-arm64`, `osx-arm64`, `osx-x64` and `win-x64`. Choose the archive for the machine, and on macOS use `.dylib` in place of `.so`.

**Both `install` lines are required.** gg loads its two native libraries from its own directory, which is why they go beside the binary. It loads them the first time they are needed, not at startup. Without them, gg starts and runs normally, then opens the editor without the gg bar along the top. At that point it names the missing file.

Unlike the installer, this route does not check the release's build attestation. To check an archive before unpacking it, run `gh attestation verify gg-linux-x64.tar.gz --repo glyph-guild/gg`.

## As a .NET tool

On a machine that already has the .NET SDK, gg can be installed from nuget.org:

```sh
sudo dotnet tool install GlyphGuild.Gg.Cli --tool-path /usr/local/lib/gg
sudo ln -sf /usr/local/lib/gg/gg /usr/local/bin/gg
```

The package is called `GlyphGuild.Gg.Cli` because the name `gg` is taken on nuget.org. The command it installs is still `gg`.

- **`--tool-path`, not `-g`.** A global install lands in the home directory of whoever ran it. On a runner, that is the account the runner runs as, which could then rewrite its own program.
- **`--version <version>`** installs a particular release. Without it, the newest release on nuget.org is installed.

## Check the install

Run:

```sh
gg version
```

This prints the version of the program, the protocol it speaks to the control plane, and the vocabulary of facts it reports.

Then, once gg is pointed at the organisation's control plane, run:

```sh
gg doctor
```

`gg doctor` checks what gg needs in order to work, including whether this release is the one the control plane expects. Each problem it reports comes with a line saying how to fix it. [Sign in](/start-here/sign-in/) covers pointing gg at the control plane.

## Next steps

- [Sign in](/start-here/sign-in/): point gg at the organisation and sign in.
- [Update gg](/guides/update-gg/): move an install to a newer release.
- [Run a runner](/guides/run-a-runner/): make a machine take work.
