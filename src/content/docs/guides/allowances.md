---
title: Allowances
description: See how much of an agent subscription a machine and the fleet have spent, keep a share back for its owner, and spend that share when it is needed.
sidebar:
  order: 9
---

An [allowance](/reference/glossary/#allowance) is a metered budget of agent time, such as one person's agent subscription, that a machine spends from when it runs flights. gg measures allowances over two windows: a **session** window, the short one a provider resets most often, and a **week** window, which is the last seven days. Use this guide to see what an allowance has left, to keep part of one back for its owner (a [floor](/reference/glossary/#floor)), and, as an administrator, to spend that part when the need is urgent.

When a person lends a machine to the fleet, the machine's flights spend that person's allowance. A floor lends the allowance without lending all of it.

## Prerequisites

- To report an allowance, name it in the machine's `allowance` setting. Naming it lends it to the fleet:

  ```sh
  gg config set allowance ada-subscription
  ```

- To see a share of each window instead of a raw count, also set the window ceilings, as whole numbers of tokens:

  ```sh
  gg config set allowance-limits session=88000,week=2400000
  ```

  gg cannot discover a subscription's limits from the machine, so type them in. Without them, gg shows the tokens spent and says that no ceiling is set.

## 1. See what this machine has spent

`gg allowance` reads this machine's own agent transcripts and contacts nothing:

```sh
gg allowance
```

```
allowance ada-subscription, measured 2026-10-14 15:10:02Z

  session           41,250 of 88,000         46%
  week           1,108,400 of 2,400,000      46%
```

Each window gives the tokens spent and, when it can, how much of the window that is. The share comes from the best source available: the provider's own figure when the agent has reported one, otherwise the configured ceiling. When the provider's window has reset since the agent reported its figure, gg says so instead of showing a share for a window that has ended.

The week window counts the last seven days, which is probably not the provider's own week. It may therefore show less headroom than there really is, never more.

## 2. Tell the fleet

`gg allowances report` sends this machine's reading to the control plane, then prints every allowance in the fleet:

```sh
gg allowances report
```

## 3. See every allowance in the fleet

```sh
gg allowances
```

```
ada-subscription  measured 2026-10-14 15:10:02Z  2 machines
  session           41,250 of 88,000         46%
  week           1,108,400 of 2,400,000      46%
```

gg lists each allowance with the machines under it, not the other way round. Two machines can share one allowance, and listing them this way keeps gg from counting their spending twice. When no machine has reported an allowance, gg says so.

## 4. Keep a share back

A floor keeps a share of an allowance back for its owners, so that fleet work does not spend all of it. The owners are the people whose machines report the allowance, and any of them may set its floor. Set it as a whole percentage for either window, or both:

```sh
gg allowances floor ada-subscription --week 25
gg allowances floor ada-subscription --session 33 --week 25
```

Keeping a share of the week and nothing of the session is reasonable. The session refills in hours, and the week does not. A floor must keep back more than nothing and less than everything.

To remove a floor:

```sh
gg allowances floor ada-subscription --clear
```

`--clear` is required to remove one, and cannot be combined with a share. gg refuses the command with no share at all, so that a forgotten number never clears a floor by accident.

gg measures a floor against the window ceilings. Set `allowance-limits` on the machines that report the allowance.

Both commands print every allowance in the fleet afterwards.

## 5. Spend someone's floor

An administrator can spend a floor that someone else set, for a limited time and with a reason:

```sh
gg allowances override ada-subscription --minutes 60 --reason "Release fix needs both machines tonight."
```

- `--minutes` is required, from 1 to 1,440 (one day). An override always ends.
- `--reason` is required, up to 280 characters. The allowance's owner reads it.

The allowance's owners can see the override, together with who made it and until when. gg prints every allowance in the fleet afterwards.

## The same steps in the console

Run `gg` with no arguments, then `u` to open the runners tab. On this machine's allowance, `o` keeps a share back: `1` keeps a tenth, `2` a quarter, `3` half, and `0` nothing. An administrator whose configuration asks for it can open the fleet's allowances with `v`.

## Related

- [The envelope: loops](/concepts/envelope/#loops): the agent and model a flight spends from.
- [Glossary: Fleet](/reference/glossary/#fleet): the machines that report allowances.
