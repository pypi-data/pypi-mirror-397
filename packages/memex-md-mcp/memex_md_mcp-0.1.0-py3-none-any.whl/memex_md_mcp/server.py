"""MCP server for semantic search over markdown vaults."""

import os

from mcp.server.fastmcp import Context, FastMCP

mcp = FastMCP(
    name="memex-md-mcp",
    instructions="Semantic search over markdown vaults. Use the search tool to find relevant notes.",
)


@mcp.tool()
async def search(query: str, vault: str | None = None, limit: int = 10, ctx: Context | None = None) -> dict:
    """Search across markdown vaults using semantic + full-text search.

    Args:
        query: Natural language search query
        vault: Specific vault to search (None = all vaults)
        limit: Maximum number of results to return
    """
    vaults_env = os.environ.get("OBSIDIAN_VAULTS", "")
    vaults = [v.strip() for v in vaults_env.split(":") if v.strip()] if vaults_env else []

    if ctx:
        await ctx.info(f"Searching for: {query}")
        await ctx.info(f"Configured vaults: {vaults}")

    # TODO: Implement actual search
    return {
        "query": query,
        "vault_filter": vault,
        "limit": limit,
        "configured_vaults": vaults,
        "results": [],
        "message": "Hello from memex-md-mcp! Search not yet implemented.",
    }


@mcp.tool()
def get_mcp_instructions() -> str:
    """Get instructions for using this MCP server."""
    return """
# memex-md-mcp

A semantic search MCP for markdown vaults (like Obsidian).

## Configuration

Set the OBSIDIAN_VAULTS environment variable with colon-separated paths:
  OBSIDIAN_VAULTS="/path/to/vault1:/path/to/vault2"

## Tools

- search(query, vault?, limit?) - Search across vaults
- get_mcp_instructions() - Show this help

## Example

Search for notes about "python async patterns":
  search("python async patterns")

Search in a specific vault:
  search("git workflow", vault="work")
""".strip()


def main() -> None:
    """Entry point for the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
