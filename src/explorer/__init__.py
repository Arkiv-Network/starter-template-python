"""Explorer CLI package for inspecting Arkiv entities.

Usage examples:

  uv run -m explorer entity 0xabc123...

The CLI supports connecting to a remote node via ARKIV_RPC_URL environment variable.
If not provided, it will use a local ephemeral node with `Arkiv()`.
"""

__all__ = ["main"]
