<p align="center">
  <img src="docs/logo.png" alt="gossip" width="300">
</p>

<h1 align="center">gossip</h1>

<p align="center">
  <strong>Separate sessions. Shared signal.</strong><br>
  A local correspondence fabric for independently running Claude Code and Codex sessions.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="python 3.9+">
  <img src="https://img.shields.io/badge/dependencies-none-brightgreen" alt="zero dependencies">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey" alt="platforms">
  <img src="https://img.shields.io/badge/license-Apache--2.0-blue" alt="Apache-2.0 license">
</p>

---

## Claude has a team. Gossip connects the sessions outside it.

Claude Code's experimental agent teams give a lead and its live teammates direct messaging and a
shared task list. That is the right native channel inside a Claude team. It does not provide a
cross-harness session directory, passive peer inspection, historical search, pre-boot addressing,
or a model-independent CLI for independently launched sessions.

`gossip` does. It discovers independently launched Claude Code and Codex sessions, shows what they
are doing without interrupting them, searches their transcripts before tokens are spent, and gives
humans, scripts, hooks, and agents one durable message bus.

| Capability | Claude Code agent teams | Outsourcerer | Gossip |
|---|---|---|---|
| Primary job | Coordinate a live Claude team | Route and supervise work across engines | Connect existing sessions as addressable peers |
| Independently launched sessions | No—team membership is explicit | Claude sessions + Outsourcerer jobs; other tools are on its roadmap | **Claude Code + Codex today** |
| Claude Code ↔ Codex correspondence | No | Delegation through a controller | **Yes, independent peer-to-peer** |
| Passive tool/output observation | Not the messaging function | Fleet view for Claude sessions and managed jobs | **Yes, across discovered Claude + Codex peers** |
| Search historical transcripts | Not the messaging function | Session/job transcripts inside its fleet | **Cross-harness local search** |
| Address before recipient boot | No | Launches its own jobs | **Yes, pre-minted UUID + durable queue** |
| Model-independent CLI/protocol | Claude Code native | Cross-harness dispatch CLI | **Yes, correspondence fabric** |
| Self or descendant terminal commands | Not via messaging | Managed job control | No—pair with Agency |
| Routing, retries, worktrees, budgets | Shared tasks, not a general scheduler | **Yes** | No, deliberately |
| Core license | Claude product feature | PolyForm Noncommercial; commercial license available | **Apache-2.0** |

[Claude Code agent teams](https://code.claude.com/docs/en/agent-teams) are the right tool when live
Claude teammates need to coordinate. [Outsourcerer](https://github.com/alexgreensh/outsourcerer) is
the right tool when a controller should choose models, launch jobs, supervise them, track cost, and
show its Claude/managed-job fleet. Use `gossip` when sessions must become independent peers across
Claude Code and Codex, need durable pre-boot addresses, or need searchable correspondence and
history outside any one controller or vendor.

The native feature validates the category; it does not erase Gossip's boundary. Native messaging is
a live Claude-team channel. Outsourcerer is a work orchestrator with a fleet view. Gossip is the
Apache-licensed correspondence fabric both can sit beside.

## tmux plus the trio: four different layers

[tmux](https://github.com/tmux/tmux) keeps terminal processes alive, arranges them into sessions,
windows, and panes, and lets a human detach and reattach. That is valuable infrastructure. It is not
the whole agent protocol.

tmux is more capable than "terminal tabs." Its
[`capture-pane`](https://man.openbsd.org/tmux.1#capture-pane),
[`send-keys`](https://man.openbsd.org/tmux.1#send-keys),
[`wait-for`](https://man.openbsd.org/tmux.1#wait-for), and
[control mode](https://man.openbsd.org/tmux.1#CONTROL_MODE) are strong automation primitives. They
operate on terminals and tmux events, not agent mailboxes, custody relationships, or model context.

| Capability | tmux | Gossip | Agency | Flashback |
|---|---|---|---|---|
| Core object | Session / window / pane | Agent address / inbox | Supervised session / custody tree | Context record / lifecycle target |
| Keep and reattach a terminal | **Yes** | No | No | No |
| Host arbitrary terminal programs | **Yes** | No—Claude Code and Codex adapters | Harness adapter boundary | No |
| Inspect activity | Pane screen and retained scrollback | **Harness transcript and tool activity** | Custody and command receipts | Admitted context and freshness |
| Discover independent Claude + Codex agents | Only if they are already tmux panes | **Yes** | Supervised sessions only | No |
| Send information session-to-session | Raw keys or a convention you build | **Durable addressed correspondence** | Command requests under custody | No |
| Queue before the recipient boots | No built-in agent inbox | **Pre-minted UUID + durable queue** | No—target supervisor must be live | No |
| Prove what happened | tmux accepted a command or input | **Stored / reachable / claimed** | **Queued / refused / injected** | **Verified / unverified / expired** |
| Inject terminal input | **`send-keys`** | Never | **Yes, under policy and custody** | Never |
| Decide what enters model context | No | No | No | **Yes, just in time** |

A transport primitive is not a communication protocol. `tmux send-keys` can carry bytes to a pane;
it does not identify an agent sender, preserve a durable inbox, prove that the recipient claimed a
message, restrict a parent to its descendants, or decide what belongs in context.

The composition is: **tmux keeps terminals alive; Gossip connects agents; Agency governs terminal
commands; Flashback governs context.** Use any one independently or combine them without collapsing
their trust boundaries.

## Three products. Three powers.

| Product | Owns | Never grants by itself |
|---|---|---|
| **Gossip** | Correspondence, discovery, observation, history, and receipts | Context admission or terminal authority |
| **Flashback** | Safe just-in-time context and checked continuity | Permission to act |
| **Agency** | Terminal custody, command policy, and input receipts | Work scheduling or orchestration |

> **A message is not a memory. A memory is not permission.**

The products are independent and useful alone. Together they create explicit separations of power:
Gossip knows the fleet, Flashback brings the right context, and Agency acts. No automatic bridge
turns correspondence into context or context into a command.

## Pair with Agency when sessions must act

Gossip carries correspondence. [Agency](docs/agency.md) grants terminal authority in its own
standalone repository. It launches sessions inside an owned PTY so they can:

- compact with Flashback's safe JIT context and checked continuity, switch model or effort, toggle
  fast or plan mode, reload skills, rename, diagnose, and exit;
- control the terminal of a child session the current session spawned;
- keep a visible custody chain from parent to descendant;
- record queued, refused, failed, and injected outcomes.

That is a stronger capability than messaging, so it stays outside Gossip core. A peer message is
never executable. Agency authority belongs only to the session itself and its descendants, never to
an unrelated session that happens to know an address.

This creates a deliberate seam with Outsourcerer. Agency owns terminal mechanics and custody.
Outsourcerer owns outsourcing policy: which model, which job, which worktree, which retry, and how
much it costs. An orchestrator can use Agency as a substrate without Gossip becoming another
orchestrator.

## Pair with Flashback when the right context matters

Flashback is not a transcript archive and not merely a compaction patch. It admits small, relevant
context just in time, tracks whether retained facts are verified or stale, and can address context
to a lifecycle point such as the next prompt, planning, implementation, a pre-tool hook, or the next
compaction.

Gossip answers **who is there and what was said**. Flashback answers **what belongs in context now**.
Keeping those decisions separate prevents a persuasive peer message from silently becoming trusted
memory.

## Why teams use gossip

### See without asking

<p align="center">
  <img src="docs/gossip-cover.jpg" alt="One agent observes another session without interrupting it" width="1100">
</p>

<p align="center"><strong>See what another session is doing—without making it stop and explain itself.</strong></p>

`observe` reads a peer's actual tool calls and recent output from its transcript. It costs the peer
nothing, adds nothing to its context, and does not interrupt its turn. You can tell the difference
between progress, waiting, drift, and a confident but unsupported status report before deciding to
send anything.

`search` applies a regex across local Claude Code and Codex transcripts before results enter a model
context. In one working corpus, it reduced 937 MB of transcripts to 9.5 MB of relevant user text.
The filter discarded 99% before a model read a byte.

### Cross the harness boundary

Claude Code's native channel speaks Claude Code. `gossip` gives Claude Code and Codex the same
addresses, trust framing, delivery receipts, and transcript tools. A Claude session can inspect or
message a Codex session, and a Codex session can answer through the same filesystem bus.

### Keep coordination durable

A live socket disappears with its process. A gossip address can exist before the recipient boots.
Queue a task to a pre-minted UUID, leave a continuation for your post-compaction self, or keep a
message waiting while a session restarts. `--wait` reports whether the recipient claimed the exact
message instead of treating a successful file write as delivery.

### Automate outside the model

`gossip` is a Python CLI and a transparent file protocol. A human, CI helper, hook, local script,
Claude Code session, or Codex session can use the same commands. The control surface does not depend
on one model deciding to call an internal tool.

## Quick start

No package install, daemon, port, or third-party dependency is required.

```bash
git clone https://github.com/Yogitmeister/gossip
cd gossip
python -m gossip.bus sessions
```

Discovery, observation, and search work without delivery hooks:

```bash
python -m gossip.bus sessions
python -m gossip.bus observe <uuid-or-name>
python -m gossip.bus search "migration|schema" --harness all
```

Alias `python -m gossip.bus` to `gossip` if you prefer the shorter examples below.

## Use

```bash
gossip sessions                                      # live roster and reachability
gossip observe 4f21                                  # inspect without interrupting
gossip search "auth|permission" --harness all        # filter transcript history locally
gossip send --to 4f21 --body "take the API half"     # uuid, prefix, pid, or name
gossip send --to "worker-2" --body "status?" --kind question
gossip send --to self --body "after compaction: finish the migration" --kind continuation
gossip send --to 4f21 --body "stop, wrong branch" --priority high
gossip send --to 4f21 --body "did it land?" --wait 10
gossip peek                                          # inspect your inbox without claiming it
gossip spawn "audit the auth module" --name auditor
```

## Delivery setup

Observation is passive. Delivery requires the receiving session to expose a path that can feed
gossip into its context.

For teammates inside one live Claude Code agent team, prefer native `SendMessage`; delivery is
automatic inside that team. Install Gossip delivery hooks when the route crosses into Codex,
connects independently launched sessions, comes from an external script, or needs Gossip's durable
queue and receipt semantics.

Register the hooks once in `~/.claude/settings.json` or a project
`.claude/settings.local.json`. Use absolute paths and no shell operators:

```json
{
  "hooks": {
    "PostToolUse":  [{ "matcher": "", "hooks": [{ "type": "command", "command": "\"C:/Python311/python.exe\" \"C:/path/to/gossip/gossip/hooks/drain.py\"" }] }],
    "Stop":         [{ "matcher": "", "hooks": [{ "type": "command", "command": "\"C:/Python311/python.exe\" \"C:/path/to/gossip/gossip/hooks/drain.py\"" }] }],
    "SessionStart": [{ "matcher": "", "hooks": [{ "type": "command", "command": "\"C:/Python311/python.exe\" \"C:/path/to/gossip/gossip/hooks/drain.py\"" }] }],
    "PreCompact":   [{ "matcher": "", "hooks": [{ "type": "command", "command": "\"C:/Python311/python.exe\" \"C:/path/to/gossip/gossip/hooks/continuity.py\"" }] }]
  }
}
```

Hooks deliver on the next relevant session activity. To receive Gossip while a CLI session is fully
idle, arm Claude Code's `Monitor` tool on the watch stream before idling:

```bash
gossip watch --for self --mode headline
```

The repository also includes an experimental Claude channel plugin under `plugin/gossipd/`. It
proved that an external Gossip can wake an idle Claude session, but third-party channel admission is
still gated by Claude Code configuration. Native Claude messaging is simpler for Claude-to-Claude
traffic; the channel remains useful research for external and cross-harness push.

Every Gossip hook exits successfully on every error path. A broken install cannot wedge the host
session.

## Reachability means something

`gossip sessions` separates "listed" from "reachable":

| Class | Meaning |
|---|---|
| `idle-wake` | A live transport is armed and can wake the recipient |
| `on-activity` | The recipient is working; delivery occurs on its next hook event |
| `on-next-turn` | The message is queued until the recipient acts again |
| `idle-no-wake` | Stored but not delivered; nothing is currently reading the inbox |
| `unverified` | Seen in the process table but not self-registered |

No sender-side priority can wake a recipient that has no live delivery path. The state and
`--wait` receipt exist so automation can act on evidence instead of optimism.

## How it works

- **Transparent transport:** JSON files under `~/.claude/session-bus`, published with atomic rename.
- **Observed claiming:** a recipient atomically moves a message from `inbox/` to `archive/`; the
  sender can watch that exact state change.
- **Multi-source discovery:** registry rows, live process command lines, and spawn receipts are
  unioned because any one source can miss sessions.
- **Cross-harness transcript readers:** Claude Code and Codex formats are normalized behind
  `observe` and `search`.
- **Recipient authority:** every body is framed as untrusted peer traffic. A gossip cannot approve a
  permission, execute a slash command, or impersonate the human operator.

## What gossip is not

Gossip does not choose models, manage credentials, supervise retries, merge branches, track cost,
admit trusted context, or grant permissions. It is intentionally small: discovery, inspection,
search, durable messaging, and receipts. Pair it with Flashback for safe context admission, Agency
for self and descendant terminal control, and an orchestrator for work allocation and lifecycle
policy.

It is also machine-local. Same-machine coordination stays on your filesystem. Use Claude Code's
Remote Control or another approved network transport when sessions must cross machines.

## Security

A gossip body is untrusted text entering another agent's context. Recipient-side framing is added
before and after the body; attempts to forge system or operator markers are annotated; foreign
sender ids are labelled `UNVERIFIED SENDER`; UUIDs and bus paths are validated; and unread queues
are bounded. Read the complete [security model](SECURITY.md).

## Roadmap

- A first-class MCP surface for `send`, `peek`, `observe`, and `search`.
- Transport adapters that prefer native Claude messaging when it is the best available route.
- Idle delivery for Codex without polling.
- Structured fleet exports for orchestrators and dashboards.
- A stable adapter to the standalone Agency custody contract.

## License

Licensed under the [Apache License 2.0](LICENSE). Commercial use, modification, and distribution are
permitted under its terms. See [NOTICE](NOTICE) for attribution and [CONTRIBUTING.md](CONTRIBUTING.md)
for the DCO-based contribution path.

<p align="center"><img src="docs/gossip-badge.png" alt="gossip" width="220"></p>
