"""
AI Influencers Agent Registry

This package-level initializer exposes a compact `REGISTRY` mapping and
`get()` helper for simple access to agents.
"""

from .registry import REGISTRY, get

# Re-export for convenience
__all__ = ["REGISTRY", "get"]