"""
RegisterUZ MCP Server

MCP server for Slovak Registry of Financial Statements (Register účtovných závierok).
API Documentation: https://www.registeruz.sk/cruz-public/home/api
"""

from .server import mcp

__all__ = ["mcp", "main"]


def main():
    """Entry point for the MCP server CLI."""
    mcp.run()
