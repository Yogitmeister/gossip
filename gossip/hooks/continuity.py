#!/usr/bin/env python3
"""session_continuity -- carry a session's own continuation across the compaction boundary.

The problem this removes
------------------------
When context fills, the conversation is summarized. The summary is lossy about *intent*: what
you were mid-way through, which decision you had already made, what the next concrete action
was. So the human ends up pasting a "here is what you were doing, continue" prompt into the
compaction. That paste is the manual step worth deleting.

Note what this does NOT claim: a session cannot trigger its own /compact, and no message
transport can hand it one. That is a deliberate boundary in Claude Code, verified in the
2.1.220 binary rather than inferred from docs:

    isSlashCommand(item) := typeof item.value === "string"
                            && item.value.trim().startsWith("/")
                            && !item.skipSlashCommands

Every programmatic injection site hardcodes `skipSlashCommands: true` -- the MCP channel
handler, the teammate/main-conversation send, the inbound peer bridge, cron fire, and the
scheduled-wakeup loop. Slash expansion stays enabled on exactly three paths: the interactive
keyboard handler, the CLI entry point (`claude -p "/compact"` really does execute), and the
Agent SDK, where the *embedding host* sets the flag per prompt. A hook and an MCP server are
both inside the sandbox; the host is outside it. So this is an authority boundary, not a
missing feature -- which is why an SDK-embedding host (Nimbalyst) can self-send `/compact`
and a peer session can never be given that power by a smarter transport.

That is fine -- the trigger was never the painful part. The *state transfer* was, and this
hook owns it. The one lever a session does hold over its own compaction is what SURVIVES it,
via this hook's stdout (see main()).

So:

  PreCompact  -> snapshot continuation state into the session's own bus inbox (self-addressed)
  PostCompact -> the correspondence is still queued, and the normal drain hooks redeliver it

Because the note lives in the bus (a file), not in the context window, compaction cannot lose
it. The session literally writes a letter to its post-compaction self.

PreCompact also carries `trigger` ("manual" | "auto") and is allowed to BLOCK compaction, so a
session can additionally defer compaction away from a critical section. Blocking is NOT enabled
by default here -- silently refusing a compaction the human asked for is worse than a slightly
awkward boundary.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import sys as _sys
from pathlib import Path as _Path

# Import the bus whether this hook lives inside an installed gossip package or is dropped
# loose into a hooks directory next to bus.py.
for _cand in (_Path(__file__).resolve().parents[1], _Path(__file__).resolve().parents[2],
              _Path(__file__).resolve().parent):
    if str(_cand) not in _sys.path:
        _sys.path.insert(0, str(_cand))
try:
    from gossip.bus import BUS_ROOT, drain, idle_transport, peek, render  # type: ignore
except ImportError:
    try:
        from bus import BUS_ROOT, drain, idle_transport, peek, render  # type: ignore
    except ImportError:
        _sys.exit(0)

MAX_TAIL = 4000


def _recent_state(transcript_path: str) -> str:
    """Pull the last substantive assistant text + recent tool intents from the transcript.

    Deliberately reads the transcript rather than asking the model to summarise: this hook runs
    without a turn, so there is no model available to it. Cheap and deterministic.
    """
    import collections

    if not transcript_path or not os.path.exists(transcript_path):
        return ""
    try:
        with open(transcript_path, encoding="utf-8", errors="ignore") as fh:
            tail = collections.deque(fh, maxlen=80)
    except Exception:
        return ""

    last_text, tools = None, []
    for line in tail:
        try:
            entry = json.loads(line)
        except Exception:
            continue
        msg = entry.get("message") or {}
        content = msg.get("content")
        if msg.get("role") == "assistant" and isinstance(content, list):
            for block in content:
                if block.get("type") == "text" and (block.get("text") or "").strip():
                    last_text = block["text"].strip()
                elif block.get("type") == "tool_use":
                    inp = block.get("input") or {}
                    label = inp.get("description") or inp.get("command") or ""
                    if label:
                        tools.append(str(label)[:80])

    parts = []
    if tools:
        parts.append("Recent actions: " + " | ".join(tools[-6:]))
    if last_text:
        parts.append("Last message: " + last_text[:1200])
    return "\n".join(parts)[:MAX_TAIL]


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0

    sid = payload.get("session_id") or os.environ.get("CLAUDE_CODE_SESSION_ID") or ""
    if not sid:
        return 0
    event = payload.get("hook_event_name") or ""

    if event != "PreCompact":
        return 0

    trigger = payload.get("trigger") or "unknown"

    # If a continuation letter is already queued, do not stack another one.
    try:
        if any(m.get("kind") == "continuation" for m in peek(sid)):
            return 0
    except Exception:
        pass

    state = _recent_state(payload.get("transcript_path") or "")
    body = (
        f"CONTINUATION LETTER (written by your pre-compaction self; trigger={trigger}).\n\n"
        "Context was just summarised, so your memory of intent is lossy but this note is not -- "
        "it was stored on disk, outside the context window.\n\n"
        f"{state}\n\n"
        "Re-establish ground truth before acting: run `git status` and `git log --oneline -5`, "
        "check for uncommitted work, and confirm what actually landed rather than trusting "
        "recollection. Then continue the task instead of waiting to be told to."
    )

    # The letter and the guidance are independent wins: if the letter cannot be written, the
    # guidance is still worth emitting -- it just must not then CLAIM a letter is waiting.
    try:
        send(sid, body, kind="continuation", priority="high")
        lettered = True
    except Exception:
        lettered = False

    # PreCompact stdout is NOT context -- it becomes the compaction's custom instructions.
    #
    # Verified in the 2.1.220 binary rather than assumed: the PreCompact dispatcher collects
    # `results.filter(succeeded && !blocked && output.trim().length > 0).map(output.trim())`
    # and hands the joined text to the summariser as `customInstructions`. So this must be
    # PLAIN TEXT -- a JSON envelope here would be injected verbatim into the compaction prompt,
    # and `hookSpecificOutput.additionalContext` is simply ignored on this event.
    #
    # This is the real answer to "can a session control its own compaction": it cannot pull the
    # trigger, but it CAN author what survives -- which is the half that actually matters.
    print(
        "COMPACTION GUIDANCE (session_continuity):\n"
        "PRESERVE: the active task goal and the user's explicit constraints; files changed with "
        "paths; commands run and their real results; commit hashes and branch state; verified "
        "external facts with dates; decisions AND their rationale; rejected approaches (so they "
        "are not retried); blockers and who owns them; the next concrete action.\n"
        "PRESERVE EXACTLY, never paraphrase: negations and exceptions, safety constraints, "
        "required ordering, test outcomes including failures, and open uncertainty.\n"
        "DROP: raw tool output already acted on, directory listings, superseded plans, "
        "dead-end exploration once falsified.\n"
        + ("NOTE: a continuation letter is queued on disk in this session's own bus inbox and "
           "will be redelivered after compaction, so intent does not depend on this summary "
           "being complete. Resume the task directly; do not wait to be handed a 'continue' "
           "prompt."
           if lettered else
           "NOTE: the continuation letter could NOT be written, so this summary is the only "
           "carrier of intent -- be more complete than usual about the next concrete action.")
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)  # fail-open: never wedge a compaction
