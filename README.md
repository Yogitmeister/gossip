<p align="center">
  <img src="docs/logo.png" alt="gossip" width="300">
</p>

<h1 align="center">gossip</h1>

<p align="center">
  <strong>Run a fleet of sessions, not a team in one.</strong><br>
  Spawn them, see them, message them, and direct them across Claude Code and Codex.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="python 3.9+">
  <img src="https://img.shields.io/badge/dependencies-none-brightgreen" alt="zero dependencies">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey" alt="platforms">
  <img src="https://img.shields.io/badge/license-PolyForm%20Noncommercial-orange" alt="license">
</p>

---

```
   session A                      session B                    session C
  ┌───────────┐                  ┌───────────┐                ┌───────────┐
  │  working  │ ──── note ─────▶ │   idle    │                │  working  │
  │           │ ◀─── answer ──── │  (woken)  │                │           │
  └───────────┘                  └───────────┘                └───────────┘
        │                                                           ▲
        └──────────────── task (high priority) ─────────────────────┘
                    delivered whether B and C are busy or idle
```

Claude Code and Codex already let you run a team of sub-agents inside one session — a lead agent
dispatching workers that share its process, its context, its lifecycle. That pattern has a ceiling:
everything lives inside one session. Two `claude` processes in two terminals are strangers. Neither
can see the other, neither can reach the other, and the only integration layer between them is you,
switching windows and copy-pasting what one needs to tell the other.

`gossip` removes that ceiling. It gives independently launched sessions a shared address book and a
delivery path, so the same coordination you get from sub-agents inside one session — dispatch,
check in, redirect — works across a **fleet of separately running sessions** instead. Spawn one,
observe it, message it, and hand it work, whether it started as part of a deliberate fleet or was
already running somewhere else entirely.

**Across both harnesses.** One bus serves Claude Code and Codex sessions alike — a session in one
can see and message a session in the other. Verified payloads, the trust flow, and the one
remaining gap: [docs/codex.md](docs/codex.md).

## Oversight, not just messaging

The interesting part isn't that a message arrives. It's what a lead session can now see and do
across an entire fleet without ever leaving its own chat.

- **`observe` reads a peer's actual tool calls, not just its output.** It parses the peer's
  transcript for `tool_use` blocks — which tool, which command, in what order — alongside its last
  message. That is strictly more than reading a log file or a final result: it's the same
  tool-by-tool trace you'd see if you were watching that session yourself, for free, without
  interrupting it.
- **A lead session can spawn a fleet, not a single worker.** Each spawned session gets an address
  before it exists, a receipt recording how to reach it again, and a task delivered as correspondence
  rather than a blind command line — so the fleet is addressable and auditable from the moment it's
  launched, not just while it happens to be running.
- **Priority delivery means a lead session can actually intervene**, not just monitor. `--priority
  high` forces a session to deal with the message before it goes idle — the difference between
  watching a fleet member go off track and being able to correct it.
- **This is a building block, stated honestly.** `gossip` does not supervise, retry, or kill
  sessions on its own — it has no lifecycle authority. What it gives you is the primitive underneath
  that: a lightweight session that checks on a fleet and pings its lead the moment something goes
  quiet is a few lines of `observe` and `send` away, not a framework you have to adopt.

**See it work in one command:** clone the repo and run `python -m gossip.bus sessions` — no
install step, no config, it lists every live session on your machine immediately.

## What it does

### Observability — see and query, without touching

- **`sessions`** — every live session with id, pid, name, status, working directory, and a
  reachability class saying how it can actually be reached right now. Built from three sources
  unioned (registry, process table, spawn receipts), because a session launched with a custom id
  does not reliably register itself — a single-source roster silently misses exactly the sessions
  you spawned yourself
- **`observe <id>`** — read what a peer is working on, straight from its transcript. This costs the
  peer **nothing** and never interrupts it. Asking it instead costs a whole turn priced at *its*
  context size — a session carrying a 7 MB transcript re-sends all of it to emit one line
- **`search "<regex>"`** — query every session transcript on disk, filtering **before** anything
  enters a context window. On a real workspace: 370 transcripts, 937 MB on disk, 9.5 MB of user
  text kept — **99% discarded before any model read a byte.** Progressive disclosure by
  construction: cheap filter first, tokens only for survivors
- **Observed receipts** — `--wait` confirms a recipient actually claimed a message rather than
  reporting the write as success

### Communication — reach a session in any state

- **Send** to any session by uuid, short prefix, pid, or name fragment
- **Wake an idle session** — not just queue for later
- **Force handling** — `--priority high` blocks the recipient from going idle until it deals with it
- **Address a session that does not exist yet** — pre-mint the id, queue the work, and it is waiting
  at boot
- **Self-continuation** — a session leaves a letter for its own post-compaction self, and separately
  authors what the compaction summary keeps
- **Revive a stopped session** — hand an exited session a headless turn, or a slash command, against
  its stored transcript

## Install

No pip install, no Node, no daemon, no port, no third-party packages. Python standard library only.

```bash
git clone https://github.com/Yogitmeister/gossip
cd gossip
python -m gossip.bus sessions          # works immediately -- discovery needs no setup
```

Delivery into running sessions needs the hooks registered once, in `~/.claude/settings.json`
(or a project `.claude/settings.local.json`). Use absolute paths for both the interpreter and the
script, and no shell operators — on Windows the PATH given to a hook subprocess may lack `bash`,
which makes hooks fail silently:

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

Hooks alone cover discovery, query, and delivery on next-turn / mid-turn — but every hook is
**reactive**: a session sitting idle at its prompt fires none of them. Waking a genuinely idle
session needs a different mechanism.

### Waking an idle session (`plugin/`)

`plugin/gossipd/channel.py` is an MCP server using Claude Code's `channels` feature — the one
sanctioned way a server can **push** into a session with no turn in flight. Verified in a clean
room, from a fresh install to the recipient's own reply: a session sitting idle received a peer
message with no hook, no keystroke, no polling.

**The catch, stated plainly:** Anthropic ships channels behind a remote allowlist
(`tengu_harbor_ledger`) that has never once included a third-party plugin — only Anthropic's own
(discord, telegram, imessage, fakechat). There is no application process. Two ways around it:

- `claude --dangerously-load-development-channels <marketplace>:<plugin>` — works, but re-prompts
  on **every launch** with no way to persist the acknowledgement. Fine for testing, not for a
  shipped tool.
- `allowedChannelPlugins` in Claude Code's local managed settings — documented, persistent, and
  (on Windows) needs no admin rights: `HKCU\SOFTWARE\Policies\ClaudeCode`, value `Settings`,
  containing `{"channelsEnabled": true, "allowedChannelPlugins": [{"marketplace": "yogitmeister",
  "plugin": "gossipd"}]}`. This is the intended install path. **Not yet verified on a fresh
  install** — tracked as open work below.

Install the plugin itself with `/plugin marketplace add <path-to-plugin/>` then
`/plugin install gossipd@yogitmeister`, or point `--channels` at it directly once allowlisted.

Every hook exits 0 on every error path. A broken `gossip` install can never wedge a session.

## Use

```bash
gossip sessions                                   # who is alive, and how reachable
gossip send --to 4f21 --body "take the API half"  # by short id prefix
gossip send --to "worker-2" --body "status?" --kind question
gossip send --to self --body "after compaction: finish the migration" --kind continuation
gossip send --to 4f21 --body "stop, wrong branch" --priority high
gossip send --to 4f21 --body "did it land?" --wait 10   # observed receipt
gossip peek                                       # my inbox, non-consuming
gossip observe 4f21                               # what is that session doing
gossip spawn "audit the auth module" --name auditor
```

To let an **idle** session be woken, have it arm a monitor on the watch stream — in Claude Code,
point the `Monitor` tool at:

```bash
gossip watch --for self --mode headline
```

Each arrival becomes one short pointer line, and the session wakes on it.

## Reachability, stated honestly

`gossip sessions` labels every session with how it can actually be reached, because "it is listed"
and "it will receive this" are different claims:

| class | meaning |
|---|---|
| `idle-wake` | a live transport is armed — lands even while the session sits idle |
| `on-activity` | mid-turn, on the recipient's next tool call |
| `on-next-turn` | queued; lands when it next runs a turn |
| `unverified` | seen in the process table but never self-registered, so delivery is probable, not confirmed |

## Claude Code and Codex

Both harnesses expose the same hook contract, so one bus serves both. Verified against Codex CLI
0.144.0 — the payload fields, the trust flow, and the one gap that is still open are all written up
in [docs/codex.md](docs/codex.md).

| | Claude Code | Codex |
|---|---|---|
| Discover live sessions | ✅ | ✅ |
| Read a peer without interrupting it | ✅ | ✅ |
| Query across all transcripts | ✅ | ✅ |
| Receive a message on its next turn | ✅ | ✅ |
| Receive a message mid-turn | ✅ | ✅ |
| Receive while sitting fully idle | ⚠️ needs one-time channel setup — see below | not yet — see below |

Codex requires a one-time `/hooks` review to trust the gossip hook, and re-review after an upgrade
changes it. That is Codex working as designed, not a workaround. Claude Code idle delivery needs the
channel plugin admitted past Anthropic's remote allowlist — proven to work, but the shippable
install path is not yet verified end to end. See [Waking an idle session](#waking-an-idle-session).

**Want the last gap closed?** Waking a fully idle Codex session, and a gossip MCP server so Codex
can send as fluently as it receives, are both on the [roadmap](#roadmap). Star the repo if you want
them prioritised — it is the signal I actually use.

## Roadmap

- **Idle-session delivery on Codex.** The one capability Claude Code has and Codex does not.
- **A gossip MCP server.** Today a session sends by shelling out. As an MCP server, `gossip` would
  expose send/peek/search as first-class tools to any MCP-speaking harness, which is the cleaner
  path for Codex and removes the shell round-trip everywhere.

## What it cannot do

Stated plainly, because knowing the ceiling matters more than the feature list:

- **It cannot send an executable slash command.** A queued item is treated as a command only if it
  starts with `/` *and* is not flagged `skipSlashCommands` — and every programmatic injection path
  in Claude Code sets that flag. Slash expansion is reserved for the interactive keyboard, the CLI
  entry point, and the SDK host.
- **It cannot make a session compact itself.** Following from the above. It *can* control what
  survives a compaction, via the `PreCompact` hook.
- **It cannot impersonate the human operator.** See below — that is deliberate.
- **It is machine-local.** The bus is a filesystem; there is no network transport by design.

## Security model

A message body is untrusted text that lands in another agent's context window. `gossip` treats it
that way:

- **Bodies cannot forge the envelope.** Attempts to impersonate the framing, the harness's voice,
  or a system notice are annotated rather than deleted, so the recipient sees that someone tried.
- **The trust framing is added by the recipient**, before and after the bodies — a sender cannot
  strip it or argue past it.
- **Sender identity is self-declared and labelled as such.** A message stamped with an id that is
  not the sender's own renders with an `UNVERIFIED SENDER` badge. Envelopes are deliberately *not*
  signed: every process that can write this bus runs as the same user and could read any key we
  stored, so a signature would authenticate nothing while looking like it did.
- **Peer messages carry no user authority**, and delivery says so explicitly: never let one
  authorise a destructive, irreversible, spending, or outward-facing action.
- Session ids are UUID-validated before becoming directory names; bus paths are asserted to
  resolve inside the bus root; recipients have an unread quota so a runaway sender cannot fill a
  disk or slow another session's hook path.

Full findings and the reasoning behind what was and was not adopted: [SECURITY.md](SECURITY.md).

## License

[PolyForm Noncommercial 1.0.0](LICENSE) — free for personal, hobby, research, educational, and
nonprofit use. Commercial use requires a separate licence; open an issue.

Required Notice: Copyright Yogev Wallach (https://github.com/Yogitmeister)
