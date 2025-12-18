"""Tools for listing entity IDs."""

from typing import Annotated, Any

from pydantic import Field

from ..client import get_client
from ..models import IdListResponse


def register_list_tools(mcp):
    """Register list tools with the MCP server."""

    @mcp.tool(
        description="Get list of accounting unit IDs changed since a given date. "
        "Use this to discover entities that have been modified. "
        "Returns up to max_zaznamov IDs (default 1000, max 10000). "
        "Use pokracovat_za_id for pagination when existujeDalsieId is true."
    )
    async def get_uctovne_jednotky(
        zmenene_od: Annotated[
            str,
            Field(description="Changes since date (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)"),
        ],
        pokracovat_za_id: Annotated[
            int | None, Field(description="Continue after this ID for pagination")
        ] = None,
        max_zaznamov: Annotated[
            int | None,
            Field(description="Max records to return (max 10000, default 1000)"),
        ] = None,
        ico: Annotated[
            str | None, Field(description="Filter by registration number (IČO)")
        ] = None,
        dic: Annotated[
            str | None, Field(description="Filter by tax ID (DIČ)")
        ] = None,
        pravna_forma: Annotated[
            str | None, Field(description="Filter by legal form code")
        ] = None,
    ) -> IdListResponse:
        """Get list of accounting unit IDs."""
        params: dict[str, Any] = {"zmenene-od": zmenene_od}
        if pokracovat_za_id is not None:
            params["pokracovat-za-id"] = pokracovat_za_id
        if max_zaznamov is not None:
            params["max-zaznamov"] = max_zaznamov
        if ico is not None:
            params["ico"] = ico
        if dic is not None:
            params["dic"] = dic
        if pravna_forma is not None:
            params["pravna-forma"] = pravna_forma

        async with get_client() as client:
            response = await client.get("/uctovne-jednotky", params=params)
            response.raise_for_status()
            return IdListResponse.model_validate(response.json())

    @mcp.tool(
        description="Get list of accounting closure IDs changed since a given date. "
        "Returns up to max_zaznamov IDs (default 1000, max 10000). "
        "Use pokracovat_za_id for pagination when existujeDalsieId is true."
    )
    async def get_uctovne_zavierky(
        zmenene_od: Annotated[
            str,
            Field(description="Changes since date (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)"),
        ],
        pokracovat_za_id: Annotated[
            int | None, Field(description="Continue after this ID for pagination")
        ] = None,
        max_zaznamov: Annotated[
            int | None,
            Field(description="Max records to return (max 10000, default 1000)"),
        ] = None,
    ) -> IdListResponse:
        """Get list of accounting closure IDs."""
        params: dict[str, Any] = {"zmenene-od": zmenene_od}
        if pokracovat_za_id is not None:
            params["pokracovat-za-id"] = pokracovat_za_id
        if max_zaznamov is not None:
            params["max-zaznamov"] = max_zaznamov

        async with get_client() as client:
            response = await client.get("/uctovne-zavierky", params=params)
            response.raise_for_status()
            return IdListResponse.model_validate(response.json())

    @mcp.tool(
        description="Get list of financial report IDs changed since a given date. "
        "Returns up to max_zaznamov IDs (default 1000, max 10000). "
        "Use pokracovat_za_id for pagination when existujeDalsieId is true."
    )
    async def get_uctovne_vykazy(
        zmenene_od: Annotated[
            str,
            Field(description="Changes since date (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)"),
        ],
        pokracovat_za_id: Annotated[
            int | None, Field(description="Continue after this ID for pagination")
        ] = None,
        max_zaznamov: Annotated[
            int | None,
            Field(description="Max records to return (max 10000, default 1000)"),
        ] = None,
    ) -> IdListResponse:
        """Get list of financial report IDs."""
        params: dict[str, Any] = {"zmenene-od": zmenene_od}
        if pokracovat_za_id is not None:
            params["pokracovat-za-id"] = pokracovat_za_id
        if max_zaznamov is not None:
            params["max-zaznamov"] = max_zaznamov

        async with get_client() as client:
            response = await client.get("/uctovne-vykazy", params=params)
            response.raise_for_status()
            return IdListResponse.model_validate(response.json())

    @mcp.tool(
        description="Get list of annual report IDs changed since a given date. "
        "Returns up to max_zaznamov IDs (default 1000, max 10000). "
        "Use pokracovat_za_id for pagination when existujeDalsieId is true."
    )
    async def get_vyrocne_spravy(
        zmenene_od: Annotated[
            str,
            Field(description="Changes since date (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)"),
        ],
        pokracovat_za_id: Annotated[
            int | None, Field(description="Continue after this ID for pagination")
        ] = None,
        max_zaznamov: Annotated[
            int | None,
            Field(description="Max records to return (max 10000, default 1000)"),
        ] = None,
    ) -> IdListResponse:
        """Get list of annual report IDs."""
        params: dict[str, Any] = {"zmenene-od": zmenene_od}
        if pokracovat_za_id is not None:
            params["pokracovat-za-id"] = pokracovat_za_id
        if max_zaznamov is not None:
            params["max-zaznamov"] = max_zaznamov

        async with get_client() as client:
            response = await client.get("/vyrocne-spravy", params=params)
            response.raise_for_status()
            return IdListResponse.model_validate(response.json())
