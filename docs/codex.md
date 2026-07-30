# Codex support

Everything on this page was verified empirically against **Codex CLI 0.144.0** on Windows on
2026-07-30, using an isolated `CODEX_HOME` so no live configuration was touched.

## Status

| Capability | Codex | Claude Code |
|---|---|---|
| Discover live sessions | ✅ | ✅ |
| Read a peer's transcript without interrupting it | ✅ | ✅ |
| Query across all transcripts | ✅ | ✅ |
| Receive a message (next turn) | ✅ **verified** | ✅ |
| Receive a message (mid-turn) | ✅ hook fires; injection not yet verified | ✅ |
| Receive a message while fully idle | ❌ not yet | ✅ |
| Send a message | ✅ (shell, or the planned MCP server) | ✅ |

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
                     "statusMessage": "gossip: checking for messages",
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
                        "additionalContext": "<message text>"}}
```

A hook emitting that on `UserPromptSubmit`, with the model asked to quote back any injected token,
produced the canary verbatim in the assistant's reply. **A Codex session can receive a gossip
message.** Codex also supports `additionalContextLimit` per handler — above it, the full text is
written to disk and only a preview reaches the model, which is a better-behaved version of the
notification clipping gossip works around on Claude Code.

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
- **Mid-turn injection** is expected to work — `PostToolUse` fires with the full payload — but only
  `UserPromptSubmit` has been confirmed end to end.
- **Trust re-review on change.** Editing a gossip hook invalidates its trust hash, so an upgrade
  needs one `/hooks` visit. Worth documenting for users rather than surprising them.
- **`exec`-mode display noise.** Hook lines render as `Completed` *and* `Failed` for the same
  invocation. The hook demonstrably ran and delivered; treat the `Failed` line in `exec` output as
  unexplained cosmetic noise, not a result.
