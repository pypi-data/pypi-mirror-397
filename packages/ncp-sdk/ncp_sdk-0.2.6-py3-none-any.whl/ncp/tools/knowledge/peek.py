"""Knowledge base peek tool stub (SDK version).

This is a type stub for IDE support and type checking during development.
The actual implementation is provided by the NCP platform at runtime.
"""

from ncp.tool import tool


@tool
def peek_knowledge(limit: int = 10) -> str:
    """Peek at the agent's knowledge base to see available documents and metadata.

    This tool retrieves sample documents from the agent's knowledge base collection
    to help understand what information is available. Unlike search_knowledge,
    this tool does not perform semantic search - it simply shows what's in the collection.

    Args:
        limit: Number of sample documents to retrieve (default: 10, max: 50).
            The tool will return a random sample from the collection to give
            an overview of available content.

    Returns:
        Formatted string containing:
        - Total document count in the collection
        - List of unique files in the knowledge base
        - Available metadata fields (file_name, page, custom fields, etc.)
        - Sample document previews with metadata

    Examples:
        >>> # Get default sample of 10 documents
        >>> peek_knowledge()
        Knowledge Base Collection: 123
        Total Documents: 45
        Sample Size: 10

        Files in Collection (3):
          - user_manual.pdf
          - faq.md
          - troubleshooting.txt

        Metadata Fields Available:
          - agent_id
          - agent_name
          - file_name
          - ingested_at
          - page

        Sample Documents:

        --- Document 1 ---
        File: user_manual.pdf
        Page: 1
        Content Preview: Introduction to the system...

        >>> # Get larger sample for comprehensive overview
        >>> peek_knowledge(limit=25)

        >>> # Get minimal sample for quick check
        >>> peek_knowledge(limit=5)

    Use Cases:
        - Understanding what documents are available before searching
        - Discovering available metadata fields for filtering with search_knowledge
        - Debugging knowledge base ingestion (verify files were ingested correctly)
        - Viewing the structure of ingested knowledge
        - Getting an overview of document types and sources

    Note:
        **This is a stub for development-time type checking only.**

        The actual implementation is injected by the NCP platform at runtime
        when your agent is deployed and executed. During local development,
        calling this function will raise NotImplementedError.

        To use this tool:
        1. Deploy your agent with a `knowledge/` directory containing docs
        2. The platform will ingest files into a ChromaDB collection
        3. At runtime, this tool will peek at that collection
        4. The agent can only peek at its own knowledge base (scoped by agent ID)

    Raises:
        NotImplementedError: Always raised during local development.
            The tool only works when running on the NCP platform.
    """
    raise NotImplementedError(
        "peek_knowledge is a platform-provided tool. "
        "It will be available when your agent runs on the NCP platform. "
        "This stub is for development-time type checking and IDE autocomplete only.\n\n"
        "To use this tool:\n"
        "1. Include it in your agent's tools list\n"
        "2. Deploy your agent with a 'knowledge/' directory containing documents\n"
        "3. The platform will automatically make this tool functional at runtime"
    )
