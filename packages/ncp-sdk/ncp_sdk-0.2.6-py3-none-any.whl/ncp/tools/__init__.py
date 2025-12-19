"""Built-in platform tools (SDK stubs).

This package contains type stubs for pre-built tools provided by the NCP platform.
These stubs provide IDE autocomplete and type checking during development.

The actual implementations are provided by the platform at runtime when your
agent is deployed and executed.

Available tool categories:
    - knowledge: Knowledge base search and retrieval tools

Example:
    >>> from ncp import Agent
    >>> from ncp.tools.knowledge import search_knowledge
    >>>
    >>> agent = Agent(
    ...     name="support_agent",
    ...     instructions="Search the knowledge base to answer questions.",
    ...     tools=[search_knowledge]
    ... )
"""

__all__ = []
