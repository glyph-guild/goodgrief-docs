---
title: Install gg
description: Install the newest release of the gg command on a laptop running macOS, Linux or Windows, and check that it works.
sidebar:
  order: 3
---

gg is a single command-line program. The same program opens the [console](/reference/glossary/#console) and, on a machine set up for it, works as a [runner](/reference/glossary/#runner). This page installs it on a laptop: the program and nothing running. Making a machine a runner is a different install, described in [Run a runner](/guides/run-a-runner/).

The commands on this page install the newest release of gg. The installers are served from goodgrief.dev, and each one is a byte-for-byte copy of the newest release's installer: before goodgrief.dev publishes a script, it checks that gg's own release workflow built it.

## Installing a particular release

To install a particular release, such as the one the rest of the organisation runs, pass its version: `sh -s -- --version <version>` on macOS and Linux, or `-Version <version>` on Windows. The [releases page](https://github.com/glyph-guild/gg/releases) lists every release.

## macOS or Linux

Run:

```sh
curl -fsSL https://goodgrief.dev/install.sh | sudo sh
```

To check the installer before running it, download it, confirm that gg's release workflow built it, then run it:

```sh
curl -fsSLO https://goodgrief.dev/install.sh
gh attestation verify install.sh --repo glyph-guild/gg
sudo sh install.sh
```

`gh attestation verify` needs the [GitHub CLI](https://cli.github.com). It fails if the file differs in any way from what the release published.

The installer:

- runs only once the whole script has arrived, so a download cut off part-way does nothing;
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
irm https://goodgrief.dev/install.ps1 | iex
```

The Windows installer installs for the current user only and needs no administrator rights. To pass options such as `-ControlPlane <url>` or `-Version <version>`, run it as a script block instead: `& ([scriptblock]::Create((irm https://goodgrief.dev/install.ps1))) -ControlPlane <url>`.

On Windows, running `gg` with no arguments opens the console, as on macOS and Linux, in Windows Terminal or the Windows console window. This needs release 0.88.45 or later; an older release on Windows is a command-line tool only, and `gg update` moves it to the newest release.

## When another program is called gg

At least one other program, a Git interface, is also called `gg`. If a different program already sits where the installer would put its link, the installer stops rather than replace it, and asks for another name. To answer in advance, for example on a machine with no one at the keyboard, pass `--as`:

```sh
curl -fsSL https://goodgrief.dev/install.sh | sudo sh -s -- --as goodgrief
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
