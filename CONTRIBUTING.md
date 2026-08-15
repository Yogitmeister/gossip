# Contributing to Gossip

Gossip is an Apache-2.0 local agent fabric. Contributions are welcome when they preserve its small
boundary: correspondence, discovery, observation, history, and transport receipts—not scheduling,
trusted context admission, or terminal authority.

## Before opening a change

- Search existing issues and describe the user-visible problem.
- Keep harness-specific behavior behind an adapter.
- Treat every inbound message body as untrusted peer data.
- Preserve fail-open hook behavior: correspondence must never wedge the host session.
- Do not add network listeners, telemetry, or dependencies without an explicit design discussion.

## Validate

```bash
python -m compileall -q gossip plugin/gossipd
python -m gossip.bus --help
```

Add focused tests or a reproducible probe for behavior changes. Document literal receipt semantics;
never upgrade “stored” or “claimed” into “completed.”

## Developer Certificate of Origin

Contributions use the [Developer Certificate of Origin 1.1](https://developercertificate.org/).
Sign each commit with:

```text
Signed-off-by: Your Name <your.email@example.com>
```

Use `git commit -s` to add the line automatically. By signing, you certify that you have the right
to submit the contribution under this repository's Apache-2.0 license.
