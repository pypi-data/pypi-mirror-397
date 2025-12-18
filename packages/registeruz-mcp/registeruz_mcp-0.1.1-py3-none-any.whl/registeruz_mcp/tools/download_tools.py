"""Tools for generating download URLs."""

from typing import Annotated

from pydantic import Field

from ..client import get_attachment_download_url, get_financial_report_pdf_download_url


def register_download_tools(mcp):
    """Register download URL tools with the MCP server."""

    @mcp.tool(
        description="Get the download URL for a financial report attachment. "
        "Returns the full URL to download the attachment file."
    )
    async def get_attachment_url(
        id: Annotated[int, Field(description="Attachment ID from prilohy array")],
    ) -> str:
        """Get attachment download URL."""
        return get_attachment_download_url(id)

    @mcp.tool(
        description="Get the URL for PDF version of a financial report. "
        "Returns the full URL to download the PDF."
    )
    async def get_financial_report_pdf_url(
        id: Annotated[int, Field(description="Financial report ID")],
    ) -> str:
        """Get financial report PDF URL."""
        return get_financial_report_pdf_download_url(id)
