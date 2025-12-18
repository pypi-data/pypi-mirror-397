"""Resources for the RegisterUZ MCP server."""

from .client import API_BASE, DEFAULT_TIMEOUT
from .models import KlasifikacieResponse

import httpx


def register_resources(mcp):
    """Register all resources with the MCP server."""

    # =========================================================================
    # Static classifier resources
    # =========================================================================

    @mcp.resource("ruz://classifiers/pravne-formy")
    async def resource_pravne_formy() -> str:
        """Legal forms classifier resource."""
        async with httpx.AsyncClient(
            base_url=API_BASE, timeout=DEFAULT_TIMEOUT
        ) as client:
            response = await client.get("/pravne-formy")
            response.raise_for_status()
            # Validate and normalize through Pydantic model
            data = KlasifikacieResponse.model_validate(response.json())
            return data.model_dump_json()

    @mcp.resource("ruz://classifiers/sk-nace")
    async def resource_sk_nace() -> str:
        """SK NACE classifier resource."""
        async with httpx.AsyncClient(
            base_url=API_BASE, timeout=DEFAULT_TIMEOUT
        ) as client:
            response = await client.get("/sk-nace")
            response.raise_for_status()
            data = KlasifikacieResponse.model_validate(response.json())
            return data.model_dump_json()

    @mcp.resource("ruz://classifiers/druhy-vlastnictva")
    async def resource_druhy_vlastnictva() -> str:
        """Ownership types classifier resource."""
        async with httpx.AsyncClient(
            base_url=API_BASE, timeout=DEFAULT_TIMEOUT
        ) as client:
            response = await client.get("/druhy-vlastnictva")
            response.raise_for_status()
            data = KlasifikacieResponse.model_validate(response.json())
            return data.model_dump_json()

    @mcp.resource("ruz://classifiers/velkosti-organizacie")
    async def resource_velkosti_organizacie() -> str:
        """Organization sizes classifier resource."""
        async with httpx.AsyncClient(
            base_url=API_BASE, timeout=DEFAULT_TIMEOUT
        ) as client:
            response = await client.get("/velkosti-organizacie")
            response.raise_for_status()
            data = KlasifikacieResponse.model_validate(response.json())
            return data.model_dump_json()

    @mcp.resource("ruz://classifiers/kraje")
    async def resource_kraje() -> str:
        """Regions classifier resource."""
        async with httpx.AsyncClient(
            base_url=API_BASE, timeout=DEFAULT_TIMEOUT
        ) as client:
            response = await client.get("/kraje")
            response.raise_for_status()
            # Normalize 'lokacie' to 'klasifikacie' through Pydantic model
            data = KlasifikacieResponse.model_validate(response.json())
            return data.model_dump_json()

    @mcp.resource("ruz://classifiers/okresy")
    async def resource_okresy() -> str:
        """Districts classifier resource."""
        async with httpx.AsyncClient(
            base_url=API_BASE, timeout=DEFAULT_TIMEOUT
        ) as client:
            response = await client.get("/okresy")
            response.raise_for_status()
            data = KlasifikacieResponse.model_validate(response.json())
            return data.model_dump_json()

    @mcp.resource("ruz://classifiers/sidla")
    async def resource_sidla() -> str:
        """Settlements classifier resource."""
        async with httpx.AsyncClient(
            base_url=API_BASE, timeout=DEFAULT_TIMEOUT
        ) as client:
            response = await client.get("/sidla")
            response.raise_for_status()
            data = KlasifikacieResponse.model_validate(response.json())
            return data.model_dump_json()

    @mcp.resource("ruz://templates")
    async def resource_templates() -> str:
        """All templates resource."""
        async with httpx.AsyncClient(
            base_url=API_BASE, timeout=DEFAULT_TIMEOUT
        ) as client:
            response = await client.get("/sablony")
            response.raise_for_status()
            return response.text

    # =========================================================================
    # Dynamic resource templates
    # =========================================================================

    @mcp.resource("ruz://uctovna-jednotka/{id}")
    async def resource_uctovna_jednotka(id: int) -> str:
        """Accounting unit detail resource."""
        async with httpx.AsyncClient(
            base_url=API_BASE, timeout=DEFAULT_TIMEOUT
        ) as client:
            response = await client.get("/uctovna-jednotka", params={"id": id})
            response.raise_for_status()
            return response.text

    @mcp.resource("ruz://uctovna-zavierka/{id}")
    async def resource_uctovna_zavierka(id: int) -> str:
        """Accounting closure detail resource."""
        async with httpx.AsyncClient(
            base_url=API_BASE, timeout=DEFAULT_TIMEOUT
        ) as client:
            response = await client.get("/uctovna-zavierka", params={"id": id})
            response.raise_for_status()
            return response.text

    @mcp.resource("ruz://uctovny-vykaz/{id}")
    async def resource_uctovny_vykaz(id: int) -> str:
        """Financial report detail resource."""
        async with httpx.AsyncClient(
            base_url=API_BASE, timeout=DEFAULT_TIMEOUT
        ) as client:
            response = await client.get("/uctovny-vykaz", params={"id": id})
            response.raise_for_status()
            return response.text

    @mcp.resource("ruz://vyrocna-sprava/{id}")
    async def resource_vyrocna_sprava(id: int) -> str:
        """Annual report detail resource."""
        async with httpx.AsyncClient(
            base_url=API_BASE, timeout=DEFAULT_TIMEOUT
        ) as client:
            response = await client.get("/vyrocna-sprava", params={"id": id})
            response.raise_for_status()
            return response.text

    @mcp.resource("ruz://sablona/{id}")
    async def resource_sablona(id: int) -> str:
        """Template detail resource."""
        async with httpx.AsyncClient(
            base_url=API_BASE, timeout=DEFAULT_TIMEOUT
        ) as client:
            response = await client.get("/sablona", params={"id": id})
            response.raise_for_status()
            return response.text
