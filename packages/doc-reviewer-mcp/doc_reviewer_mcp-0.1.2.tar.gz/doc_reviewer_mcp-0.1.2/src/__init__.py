# Doc Reviewer MCP Server

from fastmcp import FastMCP
from src.adapters.mcp_tools import register_all_tools

mcp = FastMCP("doc-reviewer-mcp")
register_all_tools(mcp)


def main():
    """Run the MCP server."""
    mcp.run()


__all__ = ["main", "mcp"]
