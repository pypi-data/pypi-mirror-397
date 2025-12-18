"""Tools for classifier data (code lists)."""

from ..client import get_client
from ..models import KlasifikacieResponse


def register_classifier_tools(mcp):
    """Register classifier tools with the MCP server."""

    @mcp.tool(
        description="Get list of all legal forms (právne formy) with their codes and names."
    )
    async def get_pravne_formy() -> KlasifikacieResponse:
        """Get all legal forms."""
        async with get_client() as client:
            response = await client.get("/pravne-formy")
            response.raise_for_status()
            return KlasifikacieResponse.model_validate(response.json())

    @mcp.tool(
        description="Get SK NACE classification codes (economic activity classification). "
        "SK NACE is the Slovak statistical classification of economic activities."
    )
    async def get_sk_nace() -> KlasifikacieResponse:
        """Get SK NACE classification."""
        async with get_client() as client:
            response = await client.get("/sk-nace")
            response.raise_for_status()
            return KlasifikacieResponse.model_validate(response.json())

    @mcp.tool(
        description="Get list of ownership types (druhy vlastníctva) with their codes."
    )
    async def get_druhy_vlastnictva() -> KlasifikacieResponse:
        """Get ownership types."""
        async with get_client() as client:
            response = await client.get("/druhy-vlastnictva")
            response.raise_for_status()
            return KlasifikacieResponse.model_validate(response.json())

    @mcp.tool(
        description="Get list of organization sizes (veľkosti organizácie) with their codes."
    )
    async def get_velkosti_organizacie() -> KlasifikacieResponse:
        """Get organization sizes."""
        async with get_client() as client:
            response = await client.get("/velkosti-organizacie")
            response.raise_for_status()
            return KlasifikacieResponse.model_validate(response.json())

    @mcp.tool(description="Get list of Slovak regions (kraje) with their codes.")
    async def get_kraje() -> KlasifikacieResponse:
        """Get Slovak regions."""
        async with get_client() as client:
            response = await client.get("/kraje")
            response.raise_for_status()
            return KlasifikacieResponse.model_validate(response.json())

    @mcp.tool(
        description="Get list of Slovak districts (okresy) with their codes. "
        "Each district includes reference to parent region via nadradenaLokacia."
    )
    async def get_okresy() -> KlasifikacieResponse:
        """Get Slovak districts."""
        async with get_client() as client:
            response = await client.get("/okresy")
            response.raise_for_status()
            return KlasifikacieResponse.model_validate(response.json())

    @mcp.tool(
        description="Get list of Slovak settlements (sídla) with their codes. "
        "Each settlement includes reference to parent district via nadradenaLokacia."
    )
    async def get_sidla() -> KlasifikacieResponse:
        """Get Slovak settlements."""
        async with get_client() as client:
            response = await client.get("/sidla")
            response.raise_for_status()
            return KlasifikacieResponse.model_validate(response.json())
