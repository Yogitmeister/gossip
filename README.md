<p align="center">
  <img src="docs/logo.png" alt="gossip" width="300">
</p>

<h1 align="center">gossip</h1>

<p align="center">
  <strong>See every session. Peek at any session. Message any session.</strong><br>
  One local bus for your Claude Code and Codex sessions — running, idle, or not yet launched.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="python 3.9+">
  <img src="https://img.shields.io/badge/dependencies-none-brightgreen" alt="zero dependencies">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey" alt="platforms">
  <img src="https://img.shields.io/badge/license-Apache--2.0-blue" alt="Apache-2.0 license">
</p>

---

```bash
gossip sessions                                   # SEE every session — who is running, who is reachable
gossip observe 4f21                               # PEEK at what a session is doing, without interrupting it
gossip send --to 4f21 --body "take the API half"  # MESSAGE any session — even one that has not booted yet
gossip search "auth|migration" --harness all      # SEARCH every local transcript before tokens are spent
```

No daemon, no port, no third-party dependency. A plain Python CLI over transparent JSON files, so
humans, scripts, cron jobs, and hooks use the exact same bus the agents do. Seeing, peeking, and
searching need zero setup; delivering into a live session takes a one-time hook install.

**Why not Claude Code's built-in messaging?** Built-in messaging connects teammates inside one live
Claude agent team; gossip connects **every** session on your machine — independently launched,
Claude Code *or* Codex, live or not yet booted — and adds passive observation, transcript search,
and claimed-or-not delivery receipts on a bus humans and scripts can drive too.[^others]

[^others]: Other tools in this space solve different problems and can sit beside gossip:
[Outsourcerer](https://github.com/alexgreensh/outsourcerer) orchestrates and supervises delegated
jobs across engines, [Firstmate](https://github.com/kunchenguid/firstmate) fronts a crew of spawned
workers with one coordinator agent, and [Watchtower](https://github.com/fahd09/watchtower) monitors
agent API traffic in a live dashboard. None of them is a neutral peer-to-peer correspondence layer
for sessions you launched independently — that is the niche gossip occupies. Deeper positioning
notes: [docs/why-gossip.md](docs/why-gossip.md).

## Quick start

```bash
git clone https://github.com/Yogitmeister/gossip
cd gossip
python -m gossip.bus sessions
```

Discovery, observation, and search work immediately, with no hooks installed:

```bash
python -m gossip.bus sessions
python -m gossip.bus observe <uuid-or-name>
python -m gossip.bus search "migration|schema" --harness all
```

Alias `python -m gossip.bus` to `gossip` for the shorter form used below. The full command tour:

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
gossip spawn "audit the auth module" --name auditor  # convenience launcher, not an orchestrator
```

Message *delivery* into a live session needs a one-time hook registration — see
[Delivery setup](#delivery-setup).

## Where it works

- **Verified today:** interactive **Claude Code CLI** and **Codex CLI** sessions. Discovery unions
  the Claude Code session registry, live process command lines, and spawn receipts, because any one
  source can miss sessions.
- **Same substrate, untested surfaces:** anything that runs the real Claude Code engine with local
  transcripts and hooks — the VS Code extension, the desktop app — writes the files gossip reads.
  `observe` and `search` apply to those transcripts as-is; delivery depends on that surface running
  the registered hooks. Treat these as compatible-by-construction, not yet verified.
- **Out of scope:** cloud sessions with no local filesystem (claude.ai web), and agents that are not
  Claude Code or Codex. Gossip is machine-local by design; use Claude Code's Remote Control or
  another approved network transport when sessions must cross machines.

## Use cases

**You are the message bus, and you are tired of it.**
Two sessions in the same repo, and the only way one learns what the other found is you, copying a
paragraph between windows. `send` gives them an address; `--wait` tells you whether the message was
actually claimed, not just written.

**"Is it still working, or is it stuck?"**
`observe` reads a peer's real tool calls and recent output from its transcript. It costs that peer
no tokens, adds nothing to its context, and does not interrupt its turn. You can tell progress from
drift from a confident-but-unsupported status report — without asking a question that forces the
session to stop and explain itself.

**A Claude session needs something a Codex session already knows.**
They are different harnesses that do not share a native channel. Gossip gives both the same
addresses, receipts, and transcript tools, so the Claude session can read or message the Codex one
directly.

**You want to answer a question you already answered last week.**
`search` runs a regex across local Claude Code and Codex transcripts *before* anything enters a
model context. In one working corpus it reduced 937 MB of transcripts to 9.5 MB of relevant user
text — the filter discarded 99% before a model read a byte.

**The recipient does not exist yet.**
Queue work to a pre-minted UUID and launch that session later. A live socket dies with its process;
a gossip address can exist before its owner boots, and survive a restart.

**You want a note waiting for your own post-compaction self.**
Address a message to your own session id. After the boundary, it is still there — written by the
version of you that actually knew why.

**Something other than a model needs to talk to your sessions.**
A cron job, CI step, git hook, or shell script can send and read on the same bus, with no daemon,
no port, and no dependency on a model choosing to call an internal tool.

<p align="center">
  <img src="docs/gossip-cover.jpg" alt="One agent observes another session without interrupting it" width="1100">
</p>

<p align="center"><strong>See what another session is doing — without making it stop and explain itself.</strong></p>

## Gossip vs. Claude Code's built-in messaging

Claude Code's experimental [agent teams](https://code.claude.com/docs/en/agent-teams) give a lead
and its live teammates direct messaging and a shared task list. Inside one live Claude team, that
native channel is the right choice — simpler, automatic, no hooks. Gossip exists for everything the
team boundary excludes:

| | Built-in (agent teams / `SendMessage`) | Gossip |
|---|---|---|
| Who can talk | A lead and the teammates it spawned, while the team lives | Any session to any session — plus humans, scripts, CI, hooks |
| Harnesses | Claude Code only | **Claude Code + Codex** |
| Independently launched sessions | No — membership is explicit at spawn | **Yes — discovered automatically** |
| Peek at a peer's work | Shared task list and teammate status, inside the team | **`observe`: passive transcript read — no interrupt, no peer tokens** |
| Search history | Your own sessions, via `--resume` and history — not from messaging | **One regex across every local Claude + Codex transcript, before tokens are spent** |
| Message a session that does not exist yet | No | **Yes — pre-minted UUID, durable queue** |
| Delivery proof | In-process tool result inside a live team | **Stored → reachable → claimed receipts a script can wait on** |
| Survives a restart | The team dies with its process | **Durable files — a queued message waits, even for your post-compaction self** |

The native feature validates the category; it does not cover it. Use both: native `SendMessage`
inside a live Claude team, gossip when the route crosses a harness, a team boundary, a restart, or
comes from something that is not a model.

## Delivery setup

Observation and search are passive and need nothing. Delivery requires the receiving session to
expose a path that can feed gossip into its context.

Register the hooks once in `~/.claude/settings.json` or a project
`.claude/settings.local.json`. Use absolute paths and no shell operators — on Windows, spell out
the full `python.exe` path (e.g. `"C:/Python311/python.exe"`):

```json
{
  "hooks": {
    "PostToolUse":  [{ "matcher": "", "hooks": [{ "type": "command", "command": "python3 \"/absolute/path/to/gossip/gossip/hooks/drain.py\"" }] }],
    "Stop":         [{ "matcher": "", "hooks": [{ "type": "command", "command": "python3 \"/absolute/path/to/gossip/gossip/hooks/drain.py\"" }] }],
    "SessionStart": [{ "matcher": "", "hooks": [{ "type": "command", "command": "python3 \"/absolute/path/to/gossip/gossip/hooks/drain.py\"" }] }],
    "PreCompact":   [{ "matcher": "", "hooks": [{ "type": "command", "command": "python3 \"/absolute/path/to/gossip/gossip/hooks/continuity.py\"" }] }]
  }
}
```

Hooks deliver on the next relevant session activity. To receive gossip while a CLI session is fully
idle, arm Claude Code's `Monitor` tool on the watch stream before idling:

```bash
gossip watch --for self --mode headline
```

The repository also includes an experimental Claude channel plugin under `plugin/gossipd/`. It
demonstrated that an external gossip can wake an idle Claude session, but third-party channel admission is
still gated by Claude Code configuration. Native Claude messaging is simpler for Claude-to-Claude
traffic; the channel remains useful research for external and cross-harness push.

Every gossip hook is written to exit 0 on every handled error path, so a broken install is designed
not to wedge the host session.

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

## Grows with Agency and Flashback

Gossip carries correspondence between sessions. Two sibling tools extend what a session can do with
itself — each useful alone, and strongest together:

**[Agency](https://github.com/Yogitmeister/agency) — an extended control surface for sessions.**
Agency launches a session inside an owned PTY so the session can act on itself and on the children
it spawns: message itself and its descendants, and run approved commands —
self-compaction (`/compact <focus>`), effort changes (`/effort`), model changes (`/model`),
fast and plan mode, skill reloads, rename, diagnose, exit. Every request passes a launch-time
policy and custody check and produces a receipt: queued, refused, or injected. Gossip moves words
between peers; Agency gives a session hands on its own terminal. A peer message is never
executable — terminal authority belongs only to a session and its descendants, never to a stranger
who happens to know an address.

**[Flashback](https://github.com/Yogitmeister/flashback) — compaction and context, augmented.**
Flashback lets an agent shape its own context with JIT pins and flashbacks: small context records
that survive compaction verbatim, are re-verified against live state before each delivery, and can
be addressed to a lifecycle point — the next prompt, planning, implementation, a pre-tool hook, or
the next compaction. Checkable facts (branch, hash, path) are re-checked every time they are
shown; judgment calls surface once across a boundary and then expire. It shines when paired with
Agency-driven self-compaction — the session picks the moment, Flashback decides what survives — and
it still improves an ordinary `/compact`.

The seams stay honest without a bridge: a gossip message never becomes trusted context by itself,
and neither a message nor a memory ever becomes a command.

## What gossip is not

Gossip does not choose models, manage credentials, supervise retries, merge branches, track cost,
admit trusted context, or grant permissions. It is intentionally small: discovery, inspection,
search, durable messaging, and receipts. Pair it with Flashback for context admission, Agency for
self and descendant terminal control, and an orchestrator for work allocation and lifecycle policy.

It is not tmux, either: tmux keeps terminal processes alive and lets you reattach; it has no agent
addresses, inboxes, receipts, or transcript search. The two compose — tmux keeps terminals alive,
gossip connects the sessions inside them. Deeper positioning: [docs/why-gossip.md](docs/why-gossip.md).

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
