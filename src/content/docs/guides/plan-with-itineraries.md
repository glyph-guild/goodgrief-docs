---
title: Plan with itineraries
description: Break work that is too large for one flight into legs, check the plan before anything opens, propose it for approval, and follow its legs afterwards.
sidebar:
  order: 5
---

An [itinerary](/reference/glossary/#itinerary) is a plan made of several flights, called [legs](/reference/glossary/#leg), that pursue one goal together. Use this guide when a piece of work is too large or too varied for one flight: for example, investigating an item, then implementing it, then reviewing the result. A plan is proposed as a whole, a person approves its shape once, and only then do its legs open.

A plan can be written by hand as a file, drafted together with an agent in a Claude Code session, or proposed by a planning flight (a flight whose work kind proposes legs instead of doing the work).

## Prerequisites

- gg is signed in to the organisation's control plane.
- The organisation has a planning work kind, `plan` by default, whose destination is of kind `flight`. Its `opens` list is the menu of work kinds a leg may use. To accept plans that people propose, that destination must require a human check, and only human checks, so that a person approves the plan and nothing waits for evidence no runner will produce. [The envelope: destinations](/concepts/envelope/#destinations) describes the fields.

## 1. Write the plan

A plan file names what the plan is about and lists its legs:

```yaml
# plan.yaml (an example)
intent:
  provider: ado
  id: "1234"
legs:
  - subject: find where sessions expire
    work-kind: investigate
    reason: The item does not say which service sets the timeout.
    repository: web-app
  - subject: fix the session expiry
    work-kind: implement
    reason: The change itself, once the cause is known.
    after: find where sessions expire
    repository: web-app
    note: Check the refresh-token path as well as the session cookie.
  - subject: review the expiry fix
    work-kind: review
    reason: A second reading before the change lands.
    after: fix the session expiry
    repository: web-app
```

The top level holds three keys:

- **`intent`** says what every leg is about. It is a sentence, or a block naming a work item (`provider` and `id`), a link (`uri`), or a file in a registered repository (`repository`, `path` and an optional `ref`).
- **`legs`** is the list of legs, at most 50.
- **`planner`** (optional) names the planning work kind whose menu the legs are checked against. It is `plan` when left out.

Each leg takes these keys:

| Key | Meaning |
|---|---|
| `subject` | Which piece of work this leg is, in a few words. Required. Two legs of the same work kind need different subjects. |
| `work-kind` | The kind of flight that does this leg. It must be on the planner's menu. Required. |
| `reason` | Why this leg exists, for the person approving the plan. Required. |
| `after` | The subject of the one leg this leg must wait for. Leave it out for work that can run as soon as a machine is free. |
| `repository` | The registered repository this leg works in. A plan has no repository of its own, so a leg whose kind works in a repository needs one. |
| `environment` | The environment this leg runs in, from the planner's menu. |
| `note` | Advice for whoever flies the leg. It is shown to the next agent as advice and grants nothing. |

Every key is checked, and an unknown one, such as a misspelt `afer:`, is refused by name.

A leg may follow only one other leg, by its subject. A leg that follows itself is refused, and a ring of legs that follow each other is refused when the plan is approved.

## 2. Check it

`gg itinerary check` asks the control plane what it would do with each leg, without opening or writing anything:

```sh
gg itinerary check plan.yaml
```

```
  checked against 'plan' (destination the-plan) - nothing was opened or written

  1. find where sessions expire  (investigate)
     opens
     <the reason admission would record>

  2. fix the session expiry  (implement)
     stands
     <the reason admission would record>
     waits on preview-reviewed - answered by platform-owner
```

Each leg gets one verdict:

- **`opens`**: a flight would open for this leg.
- **`stands`**: the leg would wait as a [nomination](/reference/glossary/#nomination) until someone opens it.
- **`refused`**: a rule refuses the leg, and the line below gives the reason.

The lines under a leg can also name the version of the rules it would run under, each gate it would wait on and who answers it, rules that could never apply to it, and what the fleet would need to run it. If the plan as a whole would be refused, gg says so before the legs.

## 3. Propose it

When the check is clean, propose the plan:

```sh
gg itinerary propose plan.yaml
```

```
proposed ITN-63 - nothing opens until its gate is answered
  pass 01b4…
  waits on plan-reviewed, answered by platform-owner
```

Only a plan the check would accept can be proposed. A proposed plan is held by a flight of the planner's kind that no runner ever takes; it exists only to carry the plan's gate. The same plan proposed twice by the same person is one plan.

A plan drafted with the agent tools can be revised while its gate is unanswered: proposing the revised draft replaces the earlier plan, whose legs are declined. A plan proposed with `gg itinerary propose` is changed by grounding its flight with `gg ground` and proposing a new one.

## 4. Approve it

The plan's gate appears in `gg gates` like any other. [Answer a gate](/guides/answer-a-gate/) explains how to decide it.

- **When it is approved**, each leg opens as a flight, and each leg's flight is attributed to the person who proposed the plan. The plan's own flight then ends `landed`.
- **When it is rejected**, every leg that is still waiting is declined, and the plan's flight ends `withdrawn`.

After approval, a leg with `after` is not offered to any machine until the leg it follows has landed. If that leg is grounded or fails, the legs after it stay held, because their premise is false. `gg why` on a held leg names the leg it follows and how that leg ended. A permanently held leg is something a person ends, for example with `gg ground`.

## 5. Follow it

```sh
gg itineraries
```

```
1 plan(s).

ITN-63 - 3 leg(s), 2 still standing
  about: ado#1234
  1. investigate, opened -> GG-71
     The item does not say which service sets the timeout.
  2. implement, gated
     The change itself, once the cause is known.
  3. review, gated
     A second reading before the change lands.
```

Each plan shows how many legs are still standing, what it is about, and each leg in the order it was written, with its state and, once it has opened, the flight it became. `gg itineraries --intent ado#1234` lists the plans for one intent only.

`gg itinerary show ITN-63` prints one plan with every leg in full.

## Draft a plan with an agent

`gg itinerary tools` is a tool server that any Claude Code session can use to draft a plan. The agent and the person edit the same plan file: the server reads the draft fresh on every call and writes it whole, so a hand edit and a tool call are edits to the same plan. Drafts are kept under gg's state directory, one file per draft.

1. Print the line that registers the server with Claude Code:

   ```sh
   gg itinerary tools --print-registration
   ```

   ```
   claude mcp add gg-itinerary -- gg itinerary tools
   ```

   For a second, separately named draft, add `--draft <name>`: `gg itinerary tools --draft session-fix --print-registration` prints a registration under its own key, so two drafts do not replace each other.

2. Run the printed line, then start Claude Code. The session gains six tools:

   | Tool | What it does |
   |---|---|
   | `set_intent` | Says what the plan is about: text, a link, a work item or a file. |
   | `draft_leg` | Adds a leg, with its subject, work kind and reason. |
   | `revise_leg` | Changes one leg, named by its subject. Legs that follow it follow a rename. |
   | `drop_leg` | Removes one leg. A leg another leg follows is not removed until that leg is revised. |
   | `show_plan` | Shows the whole draft without changing it. |
   | `propose` | Proposes the draft as the signed-in person, exactly as `gg itinerary propose` does. |

   Every tool answers with the whole draft. The work kinds, repositories and environments a leg may choose are offered from the planner's menu.

Nothing about the conversation itself is kept when a plan is proposed: only the plan, and which agent helped write it.

In the console, `n` and then `l` plans the legs of a new flight with an agent, and `l` on the intents tab (`[`) plans from the selected work item.

## Follow plans in the console

Run `gg` with no arguments, then `'` to open the itineraries tab. `enter` opens the selected plan; inside it, `f` goes to the flight a leg became and `t` opens the work item the plan is about.

## Related

- [Itineraries](/concepts/itineraries/): how plans and legs behave.
- [Answer a gate](/guides/answer-a-gate/): approving the plan.
- [Fly from a work item](/guides/fly-from-a-work-item/): when one flight is enough.
