"""gossip -- cross-session observability and communication for Claude Code.

Deliberately no eager submodule imports: `python -m gossip.bus` would otherwise re-execute an
already-imported module and warn about it. Import what you need explicitly:

    from gossip.bus import send, peek, drain, live_sessions
"""

__version__ = "0.1.0"
