---
title: MCP servers
description: How the airspace names the MCP servers an agent may call, how a loop allows their tools, and what the runner does with both.
sidebar:
  order: 11
---

An **MCP server** is a program or service that offers an [agent](/reference/glossary/#agent) extra tools over the Model Context Protocol, such as a code-analysis service that answers questions about a repository. Good Grief lets an organisation give its agents tools like these, under the same rules as everything else a flight does:

- **Root** names the servers, once, for the whole organisation.
- A **[loop](/reference/glossary/#loop)** says which of their tools its agent may call.
- The **[runner](/reference/glossary/#runner)** starts or connects to those servers on its own machine, and resolves any credential they need there.

The [control plane](/reference/glossary/#control-plane) holds the definitions and passes them to the runner with the flight. It never holds a server's credential.

## Root names the servers

The organisation defines servers under `mcp-servers:` in [root](/reference/glossary/#root), the organisation's base rules in the [airspace](/reference/glossary/#airspace). Only root may define them. Good Grief rejects a work kind, a narrowing or any other airspace document that declares `mcp-servers:`, with a message saying that only root may.

Each entry is a **key**, which names the server, and the server's definition. The runner reaches a server in one of two ways.

**At an address**, for a server that runs as a service:

```yaml
mcp-servers:
  analysis:
    type: http
    url: "https://mcp.example.com/mcp"
    headers:
      Authorization: "Bearer ${credential:local:analysis/example}"
      READ_ONLY: "true"
```

**From a command**, for a server the runner starts as a program on the machine:

```yaml
mcp-servers:
  analysis-local:
    command: example-mcp-server
    args: ["--read-only"]
    env:
      EXAMPLE_TOKEN: "${credential:local:analysis/example}"
```

| Field | What it says |
|---|---|
| `type` | `http` or `sse` for a server at an address. `stdio`, or nothing, for one started from a command. |
| `url` | The server's address. |
| `headers` | Settings sent to a server at an address, such as an authorisation header. |
| `command` | The program to start. |
| `args` | Arguments for the program. |
| `env` | Environment variables for the program. |

Good Grief accepts no other field.

### The rules a definition must follow

- **A key is letters, digits, `-` and `_`**, because it becomes the prefix of every tool name the server offers. Two servers may not share a key.
- **The key `gg` is reserved.** gg serves its own tools under that name, and a server with the same key would hide them.
- **A server has exactly one of `command` or `url`.** A server started from a command takes `env`, not `headers`. A server at an address takes `headers`, not `env` or `args`.
- **A definition names a credential, never writes it.** A value may include `${credential:<name>}`, where the name is the one [`gg credential list`](/guides/credentials/#checking-and-removing-credentials) shows, such as `local:analysis/example`. The runner substitutes no other `${…}` form.
- **A credential may not appear in `args`.** Arguments are visible on the command line to every user on the machine. Put it in `env` instead.
- **A setting whose name suggests a secret must use a reference.** Good Grief rejects a setting whose name contains `authorization`, `token`, `secret`, `password`, `passwd` or `apikey` (also `api_key` or `api-key`), and whose value contains no `${credential:…}` reference. This catches a secret pasted into the document by mistake.

### Changing the servers needs approval

Defining a new server, or changing an existing one in any way, gives agents something they could not reach before. Applying either change opens a [gate](/reference/glossary/#gate) on root, so a person approves it before it takes effect. Removing a server applies at once. A person changes airspace documents with `gg airspace pull`, `gg airspace diff` and `gg airspace apply`; [Change the airspace](/guides/change-the-airspace/) covers the steps.

## A loop allows tools

Defining a server gives no agent access to it. A loop in a work kind allows tools under `mcp:`, beside its `moves:`:

```yaml
loops:
  - id: investigate
    executor: frontier
    moves: [read, search]
    mcp:
      analysis:
        allow:
          - "*"
```

- Each entry under `mcp:` is a server key from root, and `allow:` lists the tools the agent may call.
- `"*"` allows every tool the server offers, and must appear on its own.
- Otherwise, list tool names as the server gives them, such as `search_issues`. A name contains letters, digits, `-`, `_` and `.`.
- `allow:` is required and may not be empty. A server may appear only once in a loop.

**Good Grief rejects a loop that names a server root does not define** when it combines the loop's work kind with root, with a message naming the loop and the server. Correct the name, or define the server in root.

Allowing more is also a widening that opens a gate: naming another server, adding a tool, or changing a list of tools to `"*"`.

### Moves do not govern these tools

[Moves](/reference/glossary/#move) bound what an agent may do with gg's own tools and with the repository, such as `read`, `edit` and `run-tests`. They do not apply to an organisation's MCP servers: for those, the `allow:` list is the whole of what is allowed. A loop with the move `anything` runs with no allowed-tool list at all, so `allow:` does not narrow what it may call.

See [The envelope: loops](/concepts/envelope/#loops) for the rest of the loop.

## What the runner does

When a runner takes a flight, the [lease](/reference/glossary/#lease) carries the loop's `mcp:` entries and the definitions of the servers those entries name, and nothing else from `mcp-servers:`. The credential references travel; the credentials do not.

Before it starts the agent, the runner:

1. **Resolves each credential reference on its own machine**, from gg's credential store. [Credentials](/concepts/credentials/) explains how a machine comes to hold one.
2. **Writes the server configuration to a file only the runner's user can read.** The resolved values go into that file, never onto the agent's command line, where other users on the machine could see them. The runner deletes the file as soon as the agent reports that its servers have started, and again when the run ends.
3. **Starts the agent with only these servers.** The runner does not load any MCP servers configured for the machine's own user, so a flight never runs with tools the envelope did not name.
4. **Lists the allowed tools.** Each allowed tool becomes an entry on the agent's allowed-tool list, as `mcp__<key>__<tool>`, or `mcp__<key>` for `"*"`.

The same steps apply when a person flies a flight by hand.

## What happens when something is wrong

| Situation | What happens |
|---|---|
| The runner cannot resolve a credential a server needs. | The runner refuses the flight before the agent starts, and the flight spends nothing. The message names the server and the credential, and says to register it on the machine with `gg credential add` or to send it there. |
| A server does not start or cannot be reached. | The runner reads the agent's own report of which servers connected, and refuses the flight if any did not. |
| A server's key is the same as one gg already uses on that flight. | The runner refuses the flight rather than start two servers under one name. |
| A loop names a server root does not define. | The work kind cannot be combined with root, so no flight runs under it. |

In each case no flight runs with fewer tools than the envelope says. A missing server stops the flight, so the agent never works without a tool it was meant to have.

## What is not supported

- **Servers defined anywhere but root.** A work kind, a repository narrowing or a single flight cannot add a server.
- **A machine's own servers.** The runner never loads, for a flight, MCP servers configured for the user on its machine.
- **Moves for external tools.** `allow:` alone controls access to an organisation's server.
- **Watches.** gg does not give the organisation's MCP servers to the agent that runs a [watch](/reference/glossary/#watch)'s sweep.
- **Substitution other than credentials.** `${credential:<name>}` is the only reference a value may contain.
- **Managing servers from the command line.** No gg command edits `mcp-servers:`; a person changes it like any other part of root.

gg's own tool servers, such as the one that answers an agent's questions about its flight, are separate from these. The airspace does not declare them, and moves still govern them.
