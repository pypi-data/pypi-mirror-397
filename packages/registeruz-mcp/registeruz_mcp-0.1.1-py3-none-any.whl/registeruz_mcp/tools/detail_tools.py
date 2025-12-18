"""Tools for getting entity details."""

from typing import Annotated

from pydantic import Field

from ..client import get_client
from ..models import UctovnaJednotka, UctovnaZavierka, UctovnyVykaz, VyrocnaSprava


def register_detail_tools(mcp):
    """Register detail tools with the MCP server."""

    @mcp.tool(
        description="Get detailed information about an accounting unit (company/organization). "
        "Returns company details including name, IČO, DIČ, address, legal form, "
        "and references to related financial documents."
    )
    async def get_uctovna_jednotka(
        id: Annotated[int, Field(description="Accounting unit ID")],
    ) -> UctovnaJednotka:
        """Get accounting unit detail."""
        async with get_client() as client:
            response = await client.get("/uctovna-jednotka", params={"id": id})
            response.raise_for_status()
            return UctovnaJednotka.model_validate(response.json())

    @mcp.tool(
        description="Get detailed information about an accounting closure (financial statement). "
        "Returns closure details including periods, dates, type, and references to financial reports."
    )
    async def get_uctovna_zavierka(
        id: Annotated[int, Field(description="Accounting closure ID")],
    ) -> UctovnaZavierka:
        """Get accounting closure detail."""
        async with get_client() as client:
            response = await client.get("/uctovna-zavierka", params={"id": id})
            response.raise_for_status()
            return UctovnaZavierka.model_validate(response.json())

    @mcp.tool(
        description="Get detailed information about a financial report. "
        "Returns report content including title page data, tables with financial data, "
        "and attachment information. Use idSablony to get the template for interpreting tables."
    )
    async def get_uctovny_vykaz(
        id: Annotated[int, Field(description="Financial report ID")],
    ) -> UctovnyVykaz:
        """Get financial report detail."""
        async with get_client() as client:
            response = await client.get("/uctovny-vykaz", params={"id": id})
            response.raise_for_status()
            return UctovnyVykaz.model_validate(response.json())

    @mcp.tool(
        description="Get detailed information about an annual report. "
        "Returns report details including type, periods, attachments, and references."
    )
    async def get_vyrocna_sprava(
        id: Annotated[int, Field(description="Annual report ID")],
    ) -> VyrocnaSprava:
        """Get annual report detail."""
        async with get_client() as client:
            response = await client.get("/vyrocna-sprava", params={"id": id})
            response.raise_for_status()
            return VyrocnaSprava.model_validate(response.json())
