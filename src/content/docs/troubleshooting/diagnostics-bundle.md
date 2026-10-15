---
title: Send a diagnostics bundle
description: What gg bundle collects about a machine, what it leaves out, where the bundle goes, and how to send it to the Good Grief team.
sidebar:
  order: 2
---

When something is wrong and [`gg doctor`](/troubleshooting/gg-doctor/) does not offer a fix, the next step is a **diagnostics bundle**: a description of the machine and everything `gg doctor` found, in one document for the Good Grief team. Run:

```sh
gg bundle
```

## What a bundle contains

A bundle holds:

- **Whether it is complete.** The first line says `complete` when the [control plane](/reference/glossary/#control-plane) answered, or `local-only` when it could not be reached, with a sentence saying which. A local-only bundle contains only what was found on this machine.
- **When it was taken.**
- **Versions:** the gg release, the protocol it speaks to the control plane, and the [fact](/reference/glossary/#fact) vocabulary it reports.
- **The machine's environment**, in the same form a runner records on a flight, so that the two can be matched. It is a fingerprint, not a description: a hash of the operating system, the processor architecture, the runtime, the number of processors and, inside a container, the image. Beside it are the versions of the tools that did the work, such as Git.
- **Every check `gg doctor` ran**, passing or not, with the same marks and fixes as `gg doctor` prints.
- **The problems among them**, listed again on their own, one line each, marked `STOP` or `warn`, with the fix where there is one. This list says `degradations      none` when there is nothing to act on.

## What a bundle leaves out

- **Anything a runner or an agent printed.** A bundle has no place to put a line of output from a flight. This is a matter of the bundle's shape: there is no field that could hold it.
- **Secrets.** A bundle has no field for a session, a credential's value or any other secret. Where a check names a credential, it names it by its reference, which says where the credential is kept and is not the credential itself.
- **The machine's name.** The environment fingerprint is a hash of the facts listed above, and does not include the host name.

A bundle does contain some names that identify the organisation and the person, because `gg doctor` prints them: the control plane's address, the signed-in person's name, the addresses of configured trackers and repository hosts, and credential references. Read the bundle before sending it.

[What leaves the machine](/concepts/what-leaves-the-machine/#diagnostics-bundles) explains how the bundle's limits are tested.

## Where it goes

`gg bundle` prints the bundle to the terminal and sends nothing. To keep it as a file, redirect it:

```sh
gg bundle > gg-bundle.txt
```

`gg bundle --json` prints the same bundle as JSON, which is the form to send when the Good Grief team asks for one.

`gg bundle` always exits with `0`, even when the machine it describes has a problem, so it can be run from a script that collects bundles without stopping.

## Sending it

1. Run `gg bundle > gg-bundle.txt` on the machine that has the problem. For a runner installed as a service, run it as the service's user, for example `sudo -u gg gg bundle > gg-bundle.txt` on Linux, so that it reads the service's settings.
2. Read the file, and remove anything the organisation does not want to share.
3. Send the file to the Good Grief team, together with a sentence saying what was expected and what happened instead, and the flight number, such as `GG-42`, if a flight was involved.

## Related

- [Check a machine with gg doctor](/troubleshooting/gg-doctor/): what each check in the bundle means.
- [Common problems](/troubleshooting/common-problems/): problems that can be fixed without a bundle.
