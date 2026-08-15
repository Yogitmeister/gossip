# Security model and review

## Threat model

`gossip` is a **machine-local** bus between AI sessions running as the **same OS user**. That
framing decides most of what follows: any process able to write the bus already has your file
permissions. The interesting attacks are therefore not "steal the key" but **prompt injection**
and **impersonation** — persuading another agent to do something, or to believe a gossip came
from the human.

Out of scope by design: multi-user isolation, network transport, defending against an attacker who
already controls a process running as you.

## What is enforced

| Control | Where |
|---|---|
| Bodies cannot forge the envelope, the harness's voice, or a system notice | `bus.render()` / `_defang()` |
| Trust framing added recipient-side, before **and** after bodies | `bus.render()` |
| Sender identity labelled; foreign `from` renders an `UNVERIFIED SENDER` badge | `bus.send()` / `render()` |
| Session ids UUID-validated before becoming directory names | `resolve()`, `spawn()` |
| Bus paths asserted to resolve inside the bus root | `_contained()` |
| Unread quota per recipient (`MAX_PENDING`) | `send()` |
| Window titles stripped of shell metacharacters | `spawn()` |
| Every hook exits 0 on every path | `hooks/drain.py`, `hooks/continuity.py` |

**Framing order matters.** Trust framing placed only *after* the bodies is framing the body has
already had a chance to argue against ("ignore the notice that follows"). It now leads.

**Forgery is annotated, not stripped.** A silently removed attack teaches nobody; the recipient
sees `[quoted-by-sender: ...]` and knows someone tried.

## Review, 2026-07-30

Adversarial review by `gpt-oss:120b-cloud`. Eight findings; five real and fixed, one incorrect,
two consciously not adopted.

### Fixed

1. **Prompt injection via gossip body** (High) — narrowed to the attackable part. The body is
   untrusted text in another agent's context; what it must not do is impersonate the envelope. Now
   defanged, and framing leads.

   *The proposed fix was rejected:* whitelisting body content and rejecting lines that start with
   `/`. Bodies are prose, so a content whitelist either breaks the product or is bypassed by
   rephrasing — and a leading slash is inert here regardless, since every programmatic injection
   path in Claude Code sets `skipSlashCommands`. The residual risk is real and accepted: a gossip
   can *persuade*. It cannot *execute*, and the recipient remains permission-gated.

2. **Sender spoofing via `from_id`** (Medium) — kept (a relay legitimately forwards for another)
   but labelled: `fromVerified:false` plus a rendered badge.

   *HMAC signing was rejected as security theater* — same-user processes could read any key we
   stored.

3. **Unvalidated `session_id` in `spawn()`** (Low, real) — became a directory name; now
   UUID-validated. This was the one genuine route by which a hostile name reached the filesystem.

4. **Shell injection via window title in `spawn()`** (Low, real) — the title was interpolated into
   a `shell=True` command line, so `x" & del C:\Windows\System32\* & "` closed the quote and
   appended commands. Reduced to a safe character set.

5. **Unbounded inbox growth** (Medium) — `MAX_PENDING` quota. In practice this catches a runaway
   retry loop against a non-draining address far more often than an attacker, and that loop also
   slows the recipient's hook hot path, which runs after every tool call.

### Incorrect

**Path traversal via `send --to`.** The scenario given (`send --to evil` following a symlink out
of the bus root) does not reproduce: `resolve()` accepts only a live session or a well-formed
UUID. Verified — `evil`, `..`, `a/../../b` and `../../../../tmp/malicious` are all rejected.
Path containment was still added as defense in depth, because a symlink pre-planted at a
*valid-looking* uuid path would otherwise redirect writes.

### Not adopted

- **`drain.log` timing disclosure** (Low) — same-user only, and this log is the attribution
  mechanism that makes a vanished gossip diagnosable in one lookup. The diagnostic value exceeds
  the leak.
- **TOCTOU in `await_claim()`** (Low) — a hostile local process re-queueing a claimed file is not
  meaningfully different from that process deleting it, and the `archived` flag is already
  reported so callers can distinguish.

## Reporting

Open an issue. This Apache-2.0 project has no security SLA; do not use it where a delivery failure
or a persuasive peer gossip would be costly.
