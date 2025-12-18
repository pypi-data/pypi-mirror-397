"""MCP server instance for RegisterUZ."""

from fastmcp import FastMCP

from .prompts import register_prompts
from .resources import register_resources
from .tools import register_all_tools

# Create the MCP server instance
mcp = FastMCP(
    name="RegisterUZ",
    instructions="""
    MCP server for the Slovak Registry of Financial Statements (Register účtovných závierok).

    This server provides access to public accounting data from Slovak companies and organizations,
    including financial statements, annual reports, and accounting closures.

    Data sources include: Statistical Office (ŠÚSR), State Treasury (SP), DataCentrum (DC),
    Financial Administration (FRSR), Unified State Accounting (JUS), Commercial Register (OVSR),
    Central Consolidation System (CKS), and Municipal Budget System (SAM).

    All dates use ISO 8601 format (YYYY-MM-DD), periods as (YYYY-MM).
    Data is licensed under CC0 (Public Domain).

    API documentation: https://www.registeruz.sk/cruz-public/home/api
    """,
)

# Register all components
register_all_tools(mcp)
register_resources(mcp)
register_prompts(mcp)
