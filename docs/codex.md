# Codex support and the native Claude boundary

Everything on this page was verified empirically against **Codex CLI 0.144.0** on Windows on
2026-07-30, using an isolated `CODEX_HOME` so no live configuration was touched.

Claude Code's experimental agent teams later added direct messaging between live teammates inside
one Claude team. That is now the preferred path for simple text on that route. It does not reach
Codex, independently launched sessions, or external scripts, and it does not provide Gossip's peer
transcript inspection or historical search. Codex support is therefore not a compatibility
footnote; it is one of Gossip's primary differentiators.

## Status

| Capability | Gossip on Codex | Gossip on Claude Code | Claude agent teams |
|---|---|---|---|
| Discover live independent sessions | ✅ | ✅ | ❌, explicit team members only |
| Read a peer transcript without interrupting it | ✅ | ✅ | ❌ |
| Query transcript history | ✅ | ✅ | ❌ |
| Receive on the next turn | ✅ verified | ✅ | ✅ |
| Receive mid-turn between tool calls | ✅ verified | ✅ | ✅ |
| Receive while fully idle | ❌ open gap | ⚠️ requires Gossip wake setup | ✅ zero extra setup |
| Send from an external script or another harness | ✅ | ✅ | No general peer CLI |
| Cross-machine delivery | ❌ | ❌ | Not the team-messaging focus |

## Why the first attempts failed

Codex requires every non-managed command hook to be **reviewed and trusted before it runs**. Trust
is recorded against the hook definition's *hash*, so a new or edited hook is silently marked for
review and **skipped** — no error, no log line, and nothing at all from
`RUST_LOG=codex_core::hook_runtime=trace`. An untrusted hook and a hook that does not exist look
identical from the outside.

Two ways through it:

- **Interactive, the normal path.** Run `/hooks` in the Codex TUI, review the hook, trust it. Once.
- **Automation.** `codex exec --dangerously-bypass-hook-trust` runs enabled hooks without persisted
  trust for that invocation. Appropriate when the hook source is vetted outside Codex — which is the
  case if you installed it yourself — and not otherwise.

Two unrelated things also have to be right, and both fail with their own distinct message:

- `--skip-git-repo-check` (or run inside a trusted directory), else Codex refuses to start.
- On Windows, avoid nested double quotes inside the `command` string. `cmd.exe` mangles
  `"a.exe" "b.py"` and the hook is reported as failed. Use unquoted space-free paths, or the
  `commandWindows` / `command_windows` override.

## Where hooks live

`hooks.json`, or an inline `[hooks]` table in `config.toml`, at any active config layer:

```
~/.codex/hooks.json        ~/.codex/config.toml
<repo>/.codex/hooks.json   <repo>/.codex/config.toml
```

All matching sources load; a higher layer does not replace a lower one. Project-local hooks load
only when the project `.codex/` layer is trusted.

```json
{
  "hooks": {
    "UserPromptSubmit": [
      { "hooks": [ { "type": "command",
                     "command": "python C:/path/to/gossip/hooks/drain.py",
                     "statusMessage": "gossip: checking for gossip",
                     "timeout": 20 } ] }
    ]
  }
}
```

## Payload contract

One JSON object on stdin, and it is close enough to Claude Code's that the same hook script can
serve both. Shared on every event: `session_id`, `transcript_path`, `cwd`, `hook_event_name`, plus
Codex additions `model` and `permission_mode`.

| Event | Additional fields (observed) |
|---|---|
| `SessionStart` | `source` (`startup` / `resume` / `clear` / `compact`) |
| `UserPromptSubmit` | `prompt`, `turn_id` |
| `PreToolUse` | `tool_name`, `tool_input`, `tool_use_id`, `turn_id` |
| `PostToolUse` | `tool_name`, `tool_input`, `tool_response`, `tool_use_id`, `turn_id` |
| `Stop` | `last_assistant_message`, `stop_hook_active`, `turn_id` |

Codex offers events Claude Code does not: `PermissionRequest`, `PostCompact`, `SessionEnd`,
`SubagentStart` / `SubagentStop`. `matcher` is a regex, and on `SessionStart` it filters the start
source — so `"matcher": "^compact$"` is a post-compaction-only hook.

## Delivery, verified

The injection contract is Claude Code's, unchanged:

```json
{"hookSpecificOutput": {"hookEventName": "UserPromptSubmit",
                        "additionalContext": "<gossip text>"}}
```

A hook emitting that on `UserPromptSubmit`, with the model asked to quote back any injected token,
produced the canary verbatim in the assistant's reply. **A Codex session can receive a gossip.**
Codex also supports `additionalContextLimit` per handler — above it, the full text is
written to disk and only a preview reaches the model, which is a better-behaved version of the
notification clipping gossip works around on Claude Code.

## `--to self` from inside Codex

A Codex session addressing itself (`gossip send --to self ...`, and anything spawn-related that
resolves its own identity) needed two fixes, both found by testing against a real Codex process
rather than assuming the mechanism that works for Claude Code just carries over:

- Codex has no `--session-id` on its command line and writes no per-session registry file the way
  Claude Code does, so identity resolution had nothing Codex-shaped to find at all. Fixed with a
  gossip-owned registry, populated by the `SessionStart` hook (which does receive the real session
  id) and read back by anything resolving `self`.
- Env vars are inherited down an entire process tree. A Codex session launched as a subprocess of
  a Claude Code session — a real scenario, not just a test setup, any time a Claude Code session
  shells out to `codex exec` for delegated work — would otherwise see its Claude Code ancestor's
  session id and resolve to the wrong session entirely. Fixed by determining which harness is
  actually running *before* trusting any inherited environment variable.

Both verified against a real workspace Codex session, not an isolated test harness.

## Transcripts

```
~/.codex/sessions/YYYY/MM/DD/rollout-<timestamp>-<uuid>.jsonl
```

Line types: `session_meta`, `response_item`, `event_msg`, `turn_context`, `world_state`,
`compacted`. `session_meta` carries `session_id`, `timestamp`, `cwd`, `originator`, `cli_version`,
`model_provider`.

Codex writes considerably more than Claude Code — 1,163 rollouts / 3.3 GB versus 937 MB on the same
machine — which makes filtering before anything enters a context window matter more here, not less.

## Known gaps

- **Idle delivery.** On Claude Code, gossip can wake a session sitting at its prompt. Codex has no
  equivalent surface found so far. `codex exec resume <id>` hands work to a *stopped* session, which
  is useful but is not the same thing.
- **Native transport adaptation.** Gossip does not yet delegate supported Claude-to-Claude sends to
  Claude Code's native `SendMessage`; callers choose the route. A future adapter should prefer the
  native path without weakening Gossip's external CLI and cross-harness semantics.
- **Trust re-review on change.** Editing a gossip hook invalidates its trust hash, so an upgrade
  needs one `/hooks` visit. Worth documenting for users rather than surprising them.
- **`exec`-mode display noise.** Hook lines render as `Completed` *and* `Failed` for the same
  invocation. The hook demonstrably ran and delivered; treat the `Failed` line in `exec` output as
  unexplained cosmetic noise, not a result.
