#!/usr/bin/env python3
"""session_bus_drain -- delivers peer/self correspondence into a RUNNING session.

Registered on three events, because each covers a different recipient state:

  PostToolUse  -> additionalContext        mid-turn delivery; a busy session gets its message
                                           within seconds (next tool call).
  Stop         -> decision:block + reason  turn-end delivery that FORCES the session to
                                           act on the message instead of idling. This is
                                           what makes a queued self-message a real
                                           self-continuation primitive.
  SessionStart -> additionalContext        catch-up for correspondence that arrived while the
                                           session was down, compacted, or resumed.

Hot path: PostToolUse fires after EVERY tool call, so the no-correspondence case must cost almost
nothing -- it is a single os.scandir on one directory, then exit 0.

Fail-open by contract: any error, missing session id, or unparseable payload exits 0 with
no output. Peer correspondence is never allowed to wedge a session.

Loop guard: the Stop branch respects stop_hook_active, so a blocked stop cannot re-fire
into an infinite continuation loop.
"""

from __future__ import annotations

import json
import os
import sys
import time
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
    from gossip.bus import (  # type: ignore
        BUS_ROOT, CODEX_REGISTRY, agent_ancestor, drain, idle_transport, peek, render,
    )
except ImportError:
    try:
        from bus import (  # type: ignore
            BUS_ROOT, CODEX_REGISTRY, agent_ancestor, drain, idle_transport, peek, render,
        )
    except ImportError:
        _sys.exit(0)


def _register_codex_self(sid: str, cwd: str) -> None:
    """Give a Codex session's own shell-invoked `--to self` calls something to resolve.

    Codex writes no native per-session registry file the way Claude Code does, and its
    session id never appears on the process command line the way `--session-id` does for
    Claude Code -- so `_self_id()` in bus.py has nothing to find on its own for a Codex
    session. This hook DOES receive the real session_id in its stdin payload on SessionStart,
    so it is the only place that can hand that id forward to a later, identity-blind shell call.

    Runs unconditionally on SessionStart (before the peek/early-out below), because a fresh
    session with an empty inbox is the common case, not the exception.
    """
    try:
        found = agent_ancestor()
        if not found:
            return
        pid, _cmdline, stem = found
        if stem != "codex":
            return
        CODEX_REGISTRY.mkdir(parents=True, exist_ok=True)
        (CODEX_REGISTRY / f"{pid}.json").write_text(
            json.dumps({"sessionId": sid, "cwd": cwd, "updatedAtMs": int(time.time() * 1000)}),
            encoding="utf-8",
        )
    except Exception:
        pass


def _audit(session_id: str, event: str, count: int, consumed: bool) -> None:
    """Record who consumed what, so a disappearing message is attributable in one lookup.

    Three mechanisms can now claim a message -- these hooks, the channel server, and a Monitor
    `watch` stream. Without attribution, "the message vanished" is unfalsifiable guesswork; with
    it, one file says which surface took it and on which event.
    """
    try:
        import time
        path = BUS_ROOT / "_logs" / "drain.log"
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(f"{time.strftime('%H:%M:%S')} hook/{event} session={session_id[:8]} "
                     f"count={count} consumed={consumed}\n")
    except Exception:
        pass


def main() -> int:
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return 0

    sid = payload.get("session_id") or os.environ.get("CLAUDE_SESSION_ID") or ""
    if not sid:
        return 0
    event = payload.get("hook_event_name") or ""

    if event == "SessionStart":
        _register_codex_self(sid, payload.get("cwd") or "")

    # Cheapest possible early-out: is there anything at all to deliver?
    if not peek(sid):
        return 0

    if event == "Stop":
        # Already blocked once for this stop intent -> do not chain another block.
        if payload.get("stop_hook_active"):
            return 0

        # This is what `priority` actually means.
        #
        #   high    the recipient may not go idle until it has handled the message: block the
        #           stop and hand the text over. The strongest "deal with this now" primitive
        #           available to a session that is not the user.
        #   normal  never interrupt a stop when something else can deliver to an idle session.
        #           A live Monitor watch or channel will push it within about a second, so
        #           leave it queued and let the session go idle in peace.
        #
        # With NO idle transport armed, normal still has to be forced here, or it would sit
        # unseen until the session happened to do something.
        pending = peek(sid)
        # An idle transport announces a POINTER and deliberately leaves the body queued, so
        # skipping here is only safe while the announcement is still in flight. Once a message is
        # older than a poll interval it has already been announced, and skipping again would
        # strand it: the watch dedupes by id and will never re-announce, and an idle session runs
        # no further hooks. Age is the signal, and it needs no extra bookkeeping.
        UNANNOUNCED_MS = 5000
        now_ms = int(time.time() * 1000)
        all_fresh = all(now_ms - int(m.get("createdAtMs") or 0) < UNANNOUNCED_MS for m in pending)

        if any((m.get("priority") or "normal") == "high" for m in pending):
            reason_suffix = "\n\nThis was sent high priority: handle it now, then stop again."
        elif idle_transport(sid) and all_fresh:
            _audit(sid, event, len(pending), False)
            return 0
        else:
            reason_suffix = "\n\nHandle the message above now, then stop again."

        msgs = drain(sid)
        _audit(sid, event, len(msgs), True)
        text = render(msgs)
        if not text:
            return 0
        print(json.dumps({"decision": "block", "reason": text + reason_suffix}))
        return 0

    if event == "SessionStart":
        # NON-CONSUMING on purpose. additionalContext needs a turn to be acted on, and a
        # session can boot straight to an idle prompt with no turn at all -- observed
        # 2026-07-30, when a spawned worker drained a 5828-char brief on boot, had nothing
        # to process it, and the task was silently swallowed. So announce what is waiting and
        # leave it queued; PostToolUse/Stop consume it once a real turn exists.
        pending = peek(sid)
        _audit(sid, event, len(pending), False)
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": (
                f"You have {len(pending)} unread session message(s) waiting (session_bus). "
                f"They are still queued, not consumed. Read them now with: "
                f"python -m gossip.bus peek -- and act on them. "
                f"First message preview: {(pending[0].get('body') or '')[:300]}"
            ),
        }}))
        return 0

    if event in ("PostToolUse", "UserPromptSubmit"):
        msgs = drain(sid)
        _audit(sid, event, len(msgs), True)
        text = render(msgs)
        if not text:
            return 0
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": event,
            "additionalContext": text,
        }}))
        return 0

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)  # fail-open
