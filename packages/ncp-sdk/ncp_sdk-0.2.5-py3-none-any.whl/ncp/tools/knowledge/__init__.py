"""Knowledge base tools (SDK stubs).

This module provides type stubs for knowledge base search tools.
The actual implementations are provided by the NCP platform at runtime.
"""

from .search import search_knowledge
from .peek import peek_knowledge

__all__ = ["search_knowledge", "peek_knowledge"]
