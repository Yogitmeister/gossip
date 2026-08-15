# Why gossip

## Product position

`gossip` is the local control fabric for independently running AI coding sessions. It gives a human,
script, or agent one way to discover, inspect, search, and coordinate Claude Code and Codex sessions
without forcing them under one orchestrator.

**Category:** cross-harness session observability and coordination.

**One-line pitch:** See what every local AI session is doing, search what it already knows, and reach
it through one durable, scriptable bus.

## The problem it sells against

Running more sessions is easy. Knowing which session owns a task, whether it is making progress, what
it already discovered, and how to redirect it without another expensive status turn is not.

Vendor tools solve parts of the problem:

- Claude Code agent teams message live teammates inside one explicit team.
- Orchestrators launch and supervise the workers they own.
- Terminal multiplexers show windows.
- Transcript files preserve history.

The gaps appear between those surfaces. An independently launched Codex session is invisible to
Claude's roster. A live-session chat channel cannot search yesterday's transcripts. A status request
spends a full model turn to ask a question the transcript can already answer. A model-internal tool
is not a CLI that CI, hooks, and local scripts can call.

`gossip` occupies that gap.

## Differentiation

| Buyer question | Claude Code agent teams | Outsourcerer | Gossip |
|---|---|---|---|
| Can my live Claude sessions exchange text? | Yes | Through managed workflows | Yes |
| Can Claude and Codex act as independent peers? | No | Delegation through a controller | Yes |
| Can I inspect a peer without asking it for status? | No | Claude sessions + managed jobs | Yes, across discovered Claude + Codex peers |
| Can I search historical session knowledge locally? | No | Its Claude/managed-job fleet | Yes, cross-harness |
| Can a script use the same control surface as an agent? | No general peer CLI | Yes, inside its workflow | Yes |
| Can I queue to an address before the session boots? | No | Launches its own job | Yes |
| Can a session run local commands on itself? | Not through team messaging | Not the product focus | No—pair with Agency |
| Can a parent control terminals it spawned? | Team coordination requests | Managed delegates | No—Agency provides an explicit custody chain |
| Does it own model choice, retries, branches, and spend? | No | Yes | No |
| Can my company embed the core commercially without a separate product license? | Claude product terms | No—PolyForm Noncommercial; commercial license available | Yes—Apache-2.0 |

The winning frame is not "better Claude messaging" or "another fleet dashboard." Both Claude and
Outsourcerer have strong native views. The winning frame is "make independently launched Claude and
Codex sessions addressable peers on one inspectable, Apache-licensed fabric."

### Where tmux ends and the modules begin

tmux owns terminal persistence and presentation. It can keep any terminal program alive, list its
own sessions and panes, capture pane contents, send raw keys, expose a text control protocol, and
synchronize clients with `wait-for`. Those are real strengths, not gaps Gossip should copy.

The claim that session-to-session messaging is "basically tmux" collapses four different
capabilities into raw terminal transport:

- **tmux owns terminal continuity:** processes, panes, detach/reattach, screen capture, and raw input.
- **Gossip owns correspondence:** agent identity, discovery, addressed messages, history, and claims.
- **Agency owns custody:** who may request terminal input, for which descendant, under what policy.
- **Flashback owns context:** which facts enter a model context, when, and with what freshness.

| Buyer question | tmux | Gossip | Agency | Flashback |
|---|---|---|---|---|
| Will my shell survive detachment? | Yes | No | No | No |
| Can I inspect any terminal program? | Pane screen/history | Agent transcript/events | Custody/receipts | Context records |
| Can it identify independent Claude + Codex peers? | Only if I model them as panes | Yes | Supervised sessions | No |
| Can it deliver a durable message before boot? | No built-in inbox | Yes | No | No |
| Does it prove the recipient claimed a message? | No | Yes | Not correspondence | Not correspondence |
| Can it inject terminal input? | Raw `send-keys` | Never | Yes, policy + custody | Never |
| Can a parent act only on recorded descendants? | No agent relationship | No authority | Yes | No authority |
| Can it filter and admit safe JIT context? | No | No | No | Yes |

Use them together when useful. tmux is an excellent terminal host for agents that also register
with Gossip. Its control mode may become a POSIX transport adapter for Agency, but the augmentation
is the product: identity, custody, policy, durable state, and receipts. Raw keystroke injection must
not be rebranded as agent messaging.

### Agency and Outsourcerer overlap

Agency does overlap with Outsourcerer wherever both touch spawned sessions. The dividing
line is the decision layer:

- **Agency provides mechanics:** own a PTY, run a local slash command, spawn a supervised child,
  control descendants, enforce custody, and return an execution receipt.
- **Outsourcerer provides orchestration:** choose a model, dispatch a job, isolate a worktree,
  supervise progress, retry, and account for cost.

If Agency starts choosing models, scheduling queues, retrying work, or managing budgets, it has
become an orchestrator and the positioning collapses. If it remains an inspectable terminal
authority substrate, it can sit beneath Outsourcerer, Nimbalyst, or a custom controller.

### Why Claude messaging does not make Agency redundant

Claude Code can deliver text to live teammates. That text is not the same primitive as a local
slash command. Agency operates at the terminal
boundary: a supervised session can compact itself, exit cleanly, change effort, and invoke other
local commands. A parent can do the same for descendants it owns. Unrelated peers still cannot.

## Best-fit users

- Developers running Claude Code and Codex side by side.
- AI-native teams with several independent terminals or worktrees.
- Tool builders that need a local, scriptable session directory and queue.
- Operators who want transcript evidence before spending a peer status turn.
- Users whose sessions were launched independently rather than inside one Claude team.

Gossip is not a fit for someone who runs one Claude session, never inspects history, and only needs
occasional Claude-to-Claude text. Native messaging already serves that user well.

## Sales narrative

### Thirty-second version

You already have a fleet. The problem is that every session lives behind a different terminal,
harness, and transcript. Gossip gives the fleet an address book, a searchable memory, and a durable
local message bus. You can inspect a session without interrupting it, find prior work before paying a
model to repeat it, and coordinate Claude Code and Codex through the same commands.

### Discovery questions

1. How many Claude Code, Codex, or other coding-agent sessions do you run in a normal day?
2. How do you find which session already touched a file or settled a decision?
3. What does it cost when a large-context session must answer a one-line status question?
4. Can a script or CI job reach those sessions, or only another model inside the same vendor tool?
5. What happens to a handoff when the target has not started yet or restarts?

### Objection: Claude Code already added messaging

Correct. Use it for live messages inside a Claude agent team. Gossip adds the parts native messaging
does not: independently launched sessions, Codex, passive transcript inspection, historical search,
pre-boot addresses, durable receipts, and a CLI that exists outside the model.

### Objection: An orchestrator already manages my fleet

Keep it. Outsourcerer now sees local Claude Code sessions as well as the jobs it launches. Gossip's
sharper boundary is the broader peer fabric: independently launched Claude and Codex sessions can
address each other, queue before boot, and share searchable history outside the
controller/delegate relationship. Use the orchestrator to allocate work and Gossip for durable
cross-harness correspondence.

### Objection: tmux already manages my sessions

Keep tmux. It preserves terminals and gives you a pane-level control surface. Gossip adds the agent
layer tmux deliberately does not model: Claude/Codex discovery, transcript-aware observation,
historical search, durable addressed correspondence, and claim receipts. A tmux pane can host a
Gossip participant. Add Agency when raw terminal input needs custody and policy; add Flashback when
selected evidence should enter model context. None of the modules needs to replace tmux.

### Objection: I can read the transcript files myself

You can. Gossip turns that manual forensic path into discovery, normalized Claude/Codex readers,
bounded regex search, consistent addressing, and an atomic message receipt. The value is not access
to a file; it is a small protocol every local tool can share.

## Proof points

- Zero third-party Python dependencies.
- No daemon and no open port.
- Same-machine traffic remains on the local filesystem.
- Atomic publish and claim operations provide transport evidence.
- One measured corpus filtered 937 MB of transcripts down to 9.5 MB before model context.
- Claude Code and Codex next-turn and mid-turn hook delivery were verified empirically.

## Product boundaries

Credibility depends on keeping the boundary visible:

- Gossip does not grant authority, admit trusted context, or execute commands. Flashback governs
  safe context admission; Agency grants terminal authority only to a supervised session and its
  recorded descendants.
- Gossip does not supervise, retry, merge, or track cost.
- Gossip does not claim cross-machine transport.
- A message stored for a hookless idle session is not delivered, and the CLI reports that state.
- Peer messages are untrusted text, not user instructions.

## Call to action

Run `python -m gossip.bus sessions`. The first useful result requires no install or configuration.
