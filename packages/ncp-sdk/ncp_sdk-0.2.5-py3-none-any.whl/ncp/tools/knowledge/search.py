"""Knowledge base search tool stub (SDK version).

This is a type stub for IDE support and type checking during development.
The actual implementation is provided by the NCP platform at runtime.
"""

from typing import Dict, Any, Optional
from ncp.tool import tool


@tool
def search_knowledge(query: str, n_results: int = 5, filters: Optional[Dict[str, Any]] = None) -> str:
    """Search the agent's knowledge base for relevant information.

    This tool searches the agent's dedicated ChromaDB collection for documents
    matching the query. The collection is automatically scoped to the agent's
    own knowledge base.

    Args:
        query: The search query text. Be specific to get better results.
        n_results: Number of results to return (default: 5, max: 20).
            The tool will return the most relevant documents based on
            semantic similarity.
        filters: Optional metadata filters to narrow search results. Provide as
            a dictionary where keys are metadata field names and values are the
            exact values to match. All filters use AND logic (all conditions must match).
            Common metadata fields:
            - file_name: Filter by specific file (e.g., "guide.pdf")
            - page: Filter by page number (for PDFs/DOCX)
            - ingested_at: Filter by ingestion timestamp
            - Custom fields: Any CSV column names or custom metadata

    Returns:
        Formatted string containing search results with:
        - Document content excerpts
        - Source file names
        - Relevance scores
        - Metadata (page numbers, ingestion date, etc.)

    Examples:
        >>> # Basic search across all documents
        >>> results = search_knowledge("deployment process")

        >>> # Search only in a specific file
        >>> results = search_knowledge("pricing", filters={"file_name": "product_guide.pdf"})

        >>> # Search with multiple filters (AND logic)
        >>> results = search_knowledge("installation", filters={"file_name": "manual.pdf", "page": 5})

        >>> # Filter CSV data by column values
        >>> results = search_knowledge("revenue", filters={"region": "North America", "year": 2024})

        >>> # Limit number of results
        >>> results = search_knowledge("API authentication", n_results=3)

    Note:
        **This is a stub for development-time type checking only.**

        The actual implementation is injected by the NCP platform at runtime
        when your agent is deployed and executed. During local development,
        calling this function will raise NotImplementedError.

        To use this tool:
        1. Deploy your agent with a `knowledge/` directory containing docs
        2. The platform will ingest files into a ChromaDB collection
        3. At runtime, this tool will search that collection
        4. The agent can only search its own knowledge base (scoped by agent ID)

    Raises:
        NotImplementedError: Always raised during local development.
            The tool only works when running on the NCP platform.
    """
    raise NotImplementedError(
        "search_knowledge is a platform-provided tool. "
        "It will be available when your agent runs on the NCP platform. "
        "This stub is for development-time type checking and IDE autocomplete only.\n\n"
        "To use this tool:\n"
        "1. Include it in your agent's tools list\n"
        "2. Deploy your agent with a 'knowledge/' directory containing documents\n"
        "3. The platform will automatically make this tool functional at runtime"
    )
