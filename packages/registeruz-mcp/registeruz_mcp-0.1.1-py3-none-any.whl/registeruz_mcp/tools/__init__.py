"""Tools for the RegisterUZ MCP server."""

from .classifier_tools import register_classifier_tools
from .count_tools import register_count_tools
from .detail_tools import register_detail_tools
from .download_tools import register_download_tools
from .labeled_tools import register_labeled_tools
from .list_tools import register_list_tools
from .template_tools import register_template_tools


def register_all_tools(mcp):
    """Register all tools with the MCP server."""
    register_list_tools(mcp)
    register_count_tools(mcp)
    register_detail_tools(mcp)
    register_template_tools(mcp)
    register_classifier_tools(mcp)
    register_download_tools(mcp)
    register_labeled_tools(mcp)


__all__ = [
    "register_all_tools",
    "register_list_tools",
    "register_count_tools",
    "register_detail_tools",
    "register_template_tools",
    "register_classifier_tools",
    "register_download_tools",
    "register_labeled_tools",
]
