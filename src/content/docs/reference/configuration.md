---
title: Configuration
description: Every gg setting, what it means, its default, where it is stored, and the gg config commands that read and change it.
sidebar:
  order: 3
---

gg keeps a machine's settings in one file. An environment variable can also give each setting, and it takes precedence over the file. This page lists every setting and the commands that manage them. [Environment variables](/reference/environment-variables/) lists the variables, including those that have no setting in the file.

## Where settings are stored

The file is `config.json`, in a `good-grief` folder under the configuration directory:

| System | Path |
|---|---|
| macOS and Linux | `~/.config/good-grief/config.json`, or `$XDG_CONFIG_HOME/good-grief/config.json` when `XDG_CONFIG_HOME` is set |
| Windows | `%APPDATA%\good-grief\config.json` |

The file belongs to the user who runs gg. A runner installed as a service has its own file, which the service's user owns and only that user can read.

The file is JSON, with one key per setting:

```json
{
  "control-plane": "https://<control-plane-address>",
  "executor-binary": "claude=/usr/local/bin/claude",
  "stun-servers": "stun:<relay-host>:3478"
}
```

The file names credentials but never holds them. gg keeps credential values separately, as described in [Add and send credentials](/guides/credentials/).

## How a value is chosen

For each setting, gg uses the first of these that has a value:

1. the environment variable, when it is set and not empty;
2. the file;
3. the setting's default, where it has one.

A setting with none of these is **unset**. `gg config show` names the source that answered for each setting, and says when an environment variable is hiding a value in the file.

gg checks the file strictly when it reads it:

- gg refuses a key it does not know. A misspelt setting is never silently ignored.
- gg refuses a blank value. To mean "unset", remove the line.
- `control-plane` and `pool-endpoint` must be `http` or `https` addresses.
- `runner-hold-seconds` must be a whole number of at least `1`.

## Settings

Set each setting with `gg config set <key> <value>`. Its environment variable, when set, overrides the file.

| Key | Variable | What it controls | Default |
|---|---|---|---|
| `control-plane` | `GG_CONTROL_PLANE` | The address of the [control plane](/reference/glossary/#control-plane) this machine reads and writes. | `http://localhost:5199` |
| `editor` | `EDITOR` | The editor the console hands the terminal to when a person writes an intent with `n`. An editor that returns at once instead of holding the terminal, as most graphical editors do, leaves the intent empty. | `vi` |
| `take-command` | `GG_TAKE_COMMAND` | The command the console's `t` key starts to hand a person a flight's working tree. | `claude` |
| `intent-hosts` | `GG_INTENT_HOSTS` | The work-item trackers gg reads work items from itself, as comma-separated `key=host\|reference` entries, where the reference names the credential to read with. This is what the console's browse tab offers. | Unset |
| `intent-readers` | `GG_INTENT_READERS` | Trackers that gg reads through a separately installed tool server, for a tracker gg cannot read itself. A key may appear in `intent-hosts` or here, not both. | Unset |
| `vcs-hosts` | `GG_VCS_HOSTS` | Which repository host (forge) each provider key clones from, as comma-separated `key=host` entries. gg refuses a flight against a provider with no host here before it fetches anything. | Unset |
| `destination-apis` | `GG_DESTINATION_APIS` | Where a runner opens a pull request, per provider key. Without it, a runner can push a branch and cannot propose a change. | Unset |
| `tracker-apis` | `GG_TRACKER_APIS` | Where this machine writes an accepted change to a work item, as comma-separated `destination=api` entries, such as `my-board=https://tracker.example/example-org`. Unset means this machine may read a tracker and cannot change one, whatever the envelope says. | Unset |
| `executor-binary` | `GG_EXECUTOR_BINARY` | The [agent](/reference/glossary/#agent) program a runner starts, written as `name=path`, such as `claude=/usr/local/bin/claude`. gg reads a bare path as `claude`. Unset means a runner takes flights and never starts an agent. | Unset |
| `installer` | `GG_INSTALLER` | Where `gg update` gets this machine's installer. gg runs a path, and downloads an address first. Unset means `gg update` says so rather than choosing one. | Unset |
| `runner-labels` | `GG_RUNNER_LABELS` | The labels this machine's runner advertises, as comma-separated `key=value` pairs, such as `environment=dev`. The control plane offers a flight only to a runner whose labels carry what the flight asks for. | Unset |
| `agent-locator` | `GG_AGENT_LOCATOR` | Where this machine keeps its agent credential, when it is not the local file: a vault reference the machine reads with its own identity, or a `local:agent/<name>` reference. Unset means the local file, which `gg credential send` and `gg agent login` write. | Unset |
| `runner-sweeps` | `GG_RUNNER_SWEEPS` | Whether this machine's runner runs the organisation's [watches](/reference/glossary/#watch) by itself when it has no flight: `on` or `off`. A sweep spends this machine's [allowance](/reference/glossary/#allowance). | `on` |
| `runner-hold-seconds` | `GG_RUNNER_HOLD_SECONDS` | How long, in seconds, a runner's request for work waits before coming back empty. | `10` |
| `pool-endpoint` | `GG_POOL_ENDPOINT` | The address of the controlled access point that `gg runner maintain` uses to manage a [pool](/reference/glossary/#pool). Unset means `gg runner maintain` refuses rather than reaching the host directly. | Unset |
| `stun-servers` | `GG_STUN_SERVERS` | STUN servers, comma-separated, such as `stun:<relay-host>:3478`. A STUN server tells a machine how its address appears from outside its network, so that a console on another network can reach a runner. | Unset |
| `airspace` | `GG_AIRSPACE` | The directory that holds the working copy of the [airspace](/reference/glossary/#airspace). Unset means `gg airspace pull`, `diff` and `apply` act on the current directory. | Unset |
| `allowance` | `GG_ALLOWANCE` | The name of the allowance this machine spends from: a name its owner chooses, never an account. Two machines signed in to one subscription may give the same name. Unset means this machine reports no spending. | Unset |
| `allowance-limits` | `GG_ALLOWANCE_LIMITS` | The ceilings gg measures the allowance against, such as `session=88000,week=2400000`. Unset means gg counts usage and shows no percentage. | Unset |

[Allowances](/guides/allowances/) covers the last two settings.

## Switches that live only in the file

Some switches decide whether something else may configure or reach this machine. They have no environment variable, the control plane can never offer them, and `gg config set` does not change them. To turn one on, open the file and add the key with the value `true`. Each is off unless the file says `true`.

| Key | What it allows |
|---|---|
| `accept-offered` | This machine takes configuration the control plane offers. See [Offered configuration](#offered-configuration). |
| `accept-configured` | A person may put a credential on this machine over a direct connection from their console. |
| `accept-agent-login` | A person may make this machine run its agent's sign-in, with `gg agent login`. |
| `accept-agent-sessions` | A person may start, or attach to, an agent session on this machine from their console. |
| `agent-session-roots` | Where those sessions may start, as comma-separated directories. Without it, sessions start in the home directory. |
| `fleet-allowances` | This machine's console shows the allowances of the whole fleet. It changes only what the console draws. The control plane decides what a person may see. |

## Values gg writes

gg writes two more keys itself. They are records. Do not edit them by hand:

| Key | What it records |
|---|---|
| `accepted-offer` | The version of the last offer accepted on this machine. |
| `enrolled-profile` | The [fleet profile](/guides/enrol-machines/#fleet-profiles) this machine enrolled under. This machine takes an offer that names this profile without `gg config accept`. |

## Commands

### `gg config show`

Names the file, says whether this machine accepts offered configuration and whether a person may place a credential on it, then lists every setting gg reads. It lists each setting by its variable name, with the source that answered (`environment`, `file`, `default` or `unset`) and its value. When an environment variable is overriding a value in the file, a second line says so. The list includes the variables that the file cannot set. `gg config show --json` adds one sentence on what each setting controls.

### `gg config init`

Writes a new file containing the settings that environment variables currently give, so that a machine set up with variables can move them into the file. It refuses if the file already exists. To change one value, use `gg config set`.

### `gg config set <key> <value>`

Changes one setting in the file and prints the file as it now stands. It accepts the key written as the file key or as its variable, such as `control-plane` or `GG_CONTROL_PLANE`. If gg cannot read the existing file, it changes nothing, so that the other settings are not lost. It refuses a key that is not a setting, and lists the keys that are.

```sh
gg config set control-plane https://<control-plane-address>
```

### `gg config validate <file>|-`

Checks a configuration file without applying it, and prints it in the form gg would write it. Give `-` to read the file from standard input.

```sh
gg config validate ./config.json
```

### `gg config offered`

Shows the configuration the control plane is offering this machine: its version, each setting with the value offered and the value in force, whether any of it needs a person to accept, and whether this machine has already accepted it.

### `gg config accept <version>`

Takes the offer, by the version `gg config offered` printed. If the offer has changed since, gg writes nothing and names the version now on offer. If `accept-offered` is not `true` in the file, gg writes nothing and says so.

## Offered configuration

The control plane can offer these settings to the machines that talk to it: `stun-servers`, `runner-labels`, `vcs-hosts`, `destination-apis`, `intent-hosts`, `tracker-apis` and `control-plane`. Every other setting is always the machine's own. [Update gg: offered configuration](/guides/update-gg/#offered-configuration) explains which offers a person must accept and how a runner takes them.

## Related

- [Environment variables](/reference/environment-variables/): every variable gg reads.
- [Sign in](/start-here/sign-in/): setting the control-plane address.
- [Run a runner](/guides/run-a-runner/): the settings a runner needs.
