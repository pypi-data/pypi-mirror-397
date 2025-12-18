"""Tools for counting remaining entity IDs."""

from typing import Annotated, Any

from pydantic import Field

from ..client import get_client
from ..models import ZostavajuceIdResponse


def register_count_tools(mcp):
    """Register count tools with the MCP server."""

    @mcp.tool(
        description="Get count of remaining accounting unit IDs after a given ID. "
        "Useful for estimating pagination progress."
    )
    async def get_zostavajuce_id_uctovne_jednotky(
        zmenene_od: Annotated[
            str,
            Field(description="Changes since date (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)"),
        ],
        pokracovat_za_id: Annotated[
            int | None, Field(description="Count remaining after this ID")
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
    ) -> ZostavajuceIdResponse:
        """Get count of remaining accounting unit IDs."""
        params: dict[str, Any] = {"zmenene-od": zmenene_od}
        if pokracovat_za_id is not None:
            params["pokracovat-za-id"] = pokracovat_za_id
        if ico is not None:
            params["ico"] = ico
        if dic is not None:
            params["dic"] = dic
        if pravna_forma is not None:
            params["pravna-forma"] = pravna_forma

        async with get_client() as client:
            response = await client.get(
                "/zostavajuce-id/uctovne-jednotky", params=params
            )
            response.raise_for_status()
            return ZostavajuceIdResponse.model_validate(response.json())

    @mcp.tool(
        description="Get count of remaining accounting closure IDs after a given ID. "
        "Useful for estimating pagination progress."
    )
    async def get_zostavajuce_id_uctovne_zavierky(
        zmenene_od: Annotated[
            str,
            Field(description="Changes since date (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)"),
        ],
        pokracovat_za_id: Annotated[
            int | None, Field(description="Count remaining after this ID")
        ] = None,
    ) -> ZostavajuceIdResponse:
        """Get count of remaining accounting closure IDs."""
        params: dict[str, Any] = {"zmenene-od": zmenene_od}
        if pokracovat_za_id is not None:
            params["pokracovat-za-id"] = pokracovat_za_id

        async with get_client() as client:
            response = await client.get(
                "/zostavajuce-id/uctovne-zavierky", params=params
            )
            response.raise_for_status()
            return ZostavajuceIdResponse.model_validate(response.json())

    @mcp.tool(
        description="Get count of remaining financial report IDs after a given ID. "
        "Useful for estimating pagination progress."
    )
    async def get_zostavajuce_id_uctovne_vykazy(
        zmenene_od: Annotated[
            str,
            Field(description="Changes since date (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)"),
        ],
        pokracovat_za_id: Annotated[
            int | None, Field(description="Count remaining after this ID")
        ] = None,
    ) -> ZostavajuceIdResponse:
        """Get count of remaining financial report IDs."""
        params: dict[str, Any] = {"zmenene-od": zmenene_od}
        if pokracovat_za_id is not None:
            params["pokracovat-za-id"] = pokracovat_za_id

        async with get_client() as client:
            response = await client.get("/zostavajuce-id/uctovne-vykazy", params=params)
            response.raise_for_status()
            return ZostavajuceIdResponse.model_validate(response.json())

    @mcp.tool(
        description="Get count of remaining annual report IDs after a given ID. "
        "Useful for estimating pagination progress."
    )
    async def get_zostavajuce_id_vyrocne_spravy(
        zmenene_od: Annotated[
            str,
            Field(description="Changes since date (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)"),
        ],
        pokracovat_za_id: Annotated[
            int | None, Field(description="Count remaining after this ID")
        ] = None,
    ) -> ZostavajuceIdResponse:
        """Get count of remaining annual report IDs."""
        params: dict[str, Any] = {"zmenene-od": zmenene_od}
        if pokracovat_za_id is not None:
            params["pokracovat-za-id"] = pokracovat_za_id

        async with get_client() as client:
            response = await client.get("/zostavajuce-id/vyrocne-spravy", params=params)
            response.raise_for_status()
            return ZostavajuceIdResponse.model_validate(response.json())
