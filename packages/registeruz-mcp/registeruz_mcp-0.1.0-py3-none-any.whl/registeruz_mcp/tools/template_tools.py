"""Tools for financial report templates."""

from typing import Annotated

from pydantic import Field

from ..client import get_client
from ..models import Sablona, SablonyResponse


def register_template_tools(mcp):
    """Register template tools with the MCP server."""

    @mcp.tool(
        description="Get detailed information about a financial report template. "
        "Templates define the structure of financial reports including table headers and rows. "
        "Use this to interpret the data in financial reports."
    )
    async def get_sablona(
        id: Annotated[int, Field(description="Template ID")],
    ) -> Sablona:
        """Get financial report template detail."""
        async with get_client() as client:
            response = await client.get("/sablona", params={"id": id})
            response.raise_for_status()
            return Sablona.model_validate(response.json())

    @mcp.tool(
        description="Get list of all available financial report templates. "
        "Returns basic information about each template (id, name, regulation, validity period)."
    )
    async def get_sablony() -> SablonyResponse:
        """Get all financial report templates."""
        async with get_client() as client:
            response = await client.get("/sablony")
            response.raise_for_status()
            return SablonyResponse.model_validate(response.json())
