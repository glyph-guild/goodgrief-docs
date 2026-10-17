---
title: Add and send credentials
description: Register a credential for what it is for, keep its value off the control plane, and send it to the machines that need it.
sidebar:
  order: 12
---

A [credential](/reference/glossary/#credential) is a secret, such as an access token, that a runner uses to act on the organisation's behalf: to clone a repository, open a pull request, read a work item, or run an agent.

## What the control plane holds

The [control plane](/reference/glossary/#control-plane) holds a **reference** to each credential: what it is for, the account it acts as, and what it may do. It never holds the value. The value stays on the machines that use it, stored in gg's credential store encrypted (sealed) so that only its holders can open it.

Two rules follow from that:

- **Always type the value at a prompt.** gg does not echo it. No gg command takes a secret as an argument, because the shell keeps arguments in its history, and anyone on the machine who lists running processes can see them.
- **A person authorises moving a credential, not using it.** Sending a credential to another machine costs the sender's passphrase. A machine that has received a credential opens it by itself, with no one present, for as long as it holds it.

## 1. Create a personal key

gg seals a credential to the person who registers it. Create a key before registering a credential. Run:

```sh
gg key create
```

gg asks for a passphrase, which protects the private half of the key on this machine. gg never stores the passphrase or sends it anywhere, and keeps no copy of the key.

:::danger[A lost passphrase cannot be recovered]
No one can recover a lost passphrase. The only way back is to create the credential again at its provider and register it again.
:::

gg registers the public half with the control plane. To list the public keys the organisation's people have registered, run:

```sh
gg key list
```

## 2. Register a credential

`gg credential add` takes exactly one option saying what the credential is for:

| Option | For | Example |
|---|---|---|
| `--repo <slug>` | A repository, by its registered name. | `gg credential add --repo example-org/web-app` |
| `--agent <name>` | An agent's own sign-in token. | `gg credential add --agent claude` |
| `--tracker <key>` | A work-item tracker, by its key. | `gg credential add --tracker ado` |
| `--analysis <key>` | A service that scans code and reports findings about a repository, by its key. | `gg credential add --analysis <key>` |

gg then asks two questions:

1. **Which account the credential acts as**, so that every flight log can say who read what.
2. **The secret itself**, which gg does not echo.

gg stores the secret on this machine and seals it to the person's key. Registering it needs no passphrase. gg then registers the reference with the control plane. If the control plane refuses it, gg removes the stored secret again, so nothing is left behind.

gg files each credential under a name it derives from what it is for, such as `local:example-org/web-app` for a repository or `local:tracker/ado` for a tracker. `gg credential list` shows these names, and machine settings refer to credentials by them.

### Read or write

A credential may **read** or may also **write**. Read is the default. To register one that can also push a branch and open a pull request, add `--scopes read,write`:

```sh
gg credential add --repo example-org/web-app --scopes read,write
```

A flight that lands as a pull request needs a credential with write access. The organisation's rules can say that a flight **may** land in a repository, but they cannot give a credential write access. Only the person who registers the credential decides that. When a flight's destination needs write access and the flight has only a read credential, it fails at the credential with a message saying so. The token itself must also carry the matching permissions at its provider.

## 3. Let this machine use it

A registered credential is sealed to its person, not to the machine. For gg on this machine to open it with no one present, for example for a runner here or for the console reading work items from a tracker, make this machine one of its holders:

```sh
gg credential trust-this-machine local:example-org/web-app
```

gg asks for the passphrase. This changes only who can open the credential on this machine's disk, and sends nothing anywhere.

## 4. Send it to the machines that need it

### To every machine that needs it

[Fleet profiles](/guides/enrol-machines/#fleet-profiles) declare the credentials their machines need. To send a credential to every machine whose profile names it, run:

```sh
gg credential send --repo example-org/web-app
```

gg first prints the list of machines that need it, and whether it can reach each one, before anything moves. It then asks for the passphrase **once**, however many machines are on the list, and sends the credential to each reachable machine. The control plane introduces the two machines but never sees the value. The value travels encrypted, and the receiving machine seals it to its own key on arrival. gg names any machine it cannot reach. Nothing is held for that machine, so send again later.

`--agent`, `--tracker` and `--analysis` work the same way as `--repo`.

### To one machine

To send a credential to one runner, name it with `--runner`:

```sh
gg credential send --runner <id|name> --repo example-org/web-app
```

`gg runners` lists runner ids and names. When sending an agent's token that this machine does not hold yet, gg asks for one. For Claude Code, run `claude setup-token` to get a long-lived token.

### The receiving machine must allow it

A machine accepts a credential this way only if its own configuration file says `"accept-configured": true`. `gg config set` cannot change the setting, and the control plane cannot offer it. To turn it on, edit the file on that machine. A machine without it refuses the credential, and gg names the setting.

### Signing a runner's agent in

Instead of sending an agent's token, the agent can sign in on the runner itself:

```sh
gg agent login --runner <id|name>
```

The runner starts the agent's sign-in. gg shows the address the agent printed, opens a browser if it can, and asks for the code the sign-in page gives back, without echoing it. The code goes back to the runner over the same encrypted connection, and the resulting token never passes through this machine. `--agent <name>` chooses the agent. It defaults to `claude`. The runner's configuration file must say `"accept-agent-login": true`.

## Checking and removing credentials

To list the references the control plane holds, and how each one rests on this machine, run:

```sh
gg credential list
```

To remove one, run:

```sh
gg credential rm <id>
```

gg removes the reference from the control plane first, then deletes the secret on this machine. The control plane tells runners that hold it to forget it the next time they check in.

`gg doctor` checks that gg can open every registered credential on this machine, and says where the credential store is and what protects it.

## In the console

The credentials tab (`r`) lists every credential, what it is for, and how it rests on this machine. `enter` on a credential shows each machine's position: holds it, needs it and lacks it, or holds it although nothing declares it. A machine that has never reported says so. `a` on the tab opens the credential actions, which cover registering, forgetting, creating a key, trusting this machine and sending. On the main screen, `c` registers a credential from any tab.

## Next steps

- [Add machines to the fleet](/guides/enrol-machines/): fleet profiles, which declare who needs what.
- [Run a runner](/guides/run-a-runner/): the machines that use credentials.
