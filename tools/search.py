"""Example tool: search a knowledge base."""

from agents import function_tool


@function_tool
def search_knowledge_base(query: str, top_k: int = 3) -> str:
    """Search an internal knowledge base by query string. Replace with Azure AI Search, etc."""
    results = [
        f"{i}. Result {i}: Snippet for '{query}' (#{i})"
        for i in range(1, top_k + 1)
    ]
    return "\n".join(results)
