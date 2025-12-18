"""Tests for MCP resources using VCR.py for HTTP mocking."""

import json

import pytest

from fastmcp import Client

from registeruz_mcp import mcp


# =============================================================================
# Static Resources Tests
# =============================================================================


class TestStaticResources:
    """Tests for static classifier resources."""

    @pytest.mark.vcr()
    async def test_resource_pravne_formy(self, mcp_client):
        """Test legal forms resource."""
        result = await mcp_client.read_resource("ruz://classifiers/pravne-formy")
        assert result is not None
        # Parse the JSON response
        data = json.loads(result[0].text)
        assert "klasifikacie" in data
        assert len(data["klasifikacie"]) > 0

    @pytest.mark.vcr()
    async def test_resource_sk_nace(self, mcp_client):
        """Test SK NACE resource."""
        result = await mcp_client.read_resource("ruz://classifiers/sk-nace")
        assert result is not None
        data = json.loads(result[0].text)
        assert "klasifikacie" in data

    @pytest.mark.vcr()
    async def test_resource_druhy_vlastnictva(self, mcp_client):
        """Test ownership types resource."""
        result = await mcp_client.read_resource("ruz://classifiers/druhy-vlastnictva")
        assert result is not None
        data = json.loads(result[0].text)
        assert "klasifikacie" in data

    @pytest.mark.vcr()
    async def test_resource_velkosti_organizacie(self, mcp_client):
        """Test organization sizes resource."""
        result = await mcp_client.read_resource("ruz://classifiers/velkosti-organizacie")
        assert result is not None
        data = json.loads(result[0].text)
        assert "klasifikacie" in data

    @pytest.mark.vcr()
    async def test_resource_kraje(self, mcp_client):
        """Test regions resource."""
        result = await mcp_client.read_resource("ruz://classifiers/kraje")
        assert result is not None
        data = json.loads(result[0].text)
        assert "klasifikacie" in data
        # Slovakia has 8 regions + 2 extra-regio codes
        assert len(data["klasifikacie"]) >= 8

    @pytest.mark.vcr()
    async def test_resource_okresy(self, mcp_client):
        """Test districts resource."""
        result = await mcp_client.read_resource("ruz://classifiers/okresy")
        assert result is not None
        data = json.loads(result[0].text)
        assert "klasifikacie" in data

    @pytest.mark.vcr()
    async def test_resource_sidla(self, mcp_client):
        """Test settlements resource."""
        result = await mcp_client.read_resource("ruz://classifiers/sidla")
        assert result is not None
        data = json.loads(result[0].text)
        assert "klasifikacie" in data

    @pytest.mark.vcr()
    async def test_resource_templates(self, mcp_client):
        """Test templates resource."""
        result = await mcp_client.read_resource("ruz://templates")
        assert result is not None
        data = json.loads(result[0].text)
        assert "sablony" in data
        assert len(data["sablony"]) > 0


# =============================================================================
# Dynamic Resource Templates Tests
# =============================================================================


class TestDynamicResources:
    """Tests for dynamic resource templates."""

    @pytest.mark.vcr()
    async def test_resource_uctovna_jednotka(self, mcp_client, sample_company_id):
        """Test accounting unit resource template."""
        result = await mcp_client.read_resource(f"ruz://uctovna-jednotka/{sample_company_id}")
        assert result is not None
        data = json.loads(result[0].text)
        assert data["id"] == sample_company_id
        assert data["ico"] == "46792511"

    @pytest.mark.vcr()
    async def test_resource_uctovna_zavierka(self, mcp_client, sample_closure_id):
        """Test accounting closure resource template."""
        result = await mcp_client.read_resource(f"ruz://uctovna-zavierka/{sample_closure_id}")
        assert result is not None
        data = json.loads(result[0].text)
        assert data["id"] == sample_closure_id

    @pytest.mark.vcr()
    async def test_resource_uctovny_vykaz(self, mcp_client, sample_report_id):
        """Test financial report resource template."""
        result = await mcp_client.read_resource(f"ruz://uctovny-vykaz/{sample_report_id}")
        assert result is not None
        data = json.loads(result[0].text)
        assert data["id"] == sample_report_id

    @pytest.mark.vcr()
    async def test_resource_sablona(self, mcp_client, sample_template_id):
        """Test template resource template."""
        result = await mcp_client.read_resource(f"ruz://sablona/{sample_template_id}")
        assert result is not None
        data = json.loads(result[0].text)
        assert data["id"] == sample_template_id


# =============================================================================
# Resource Error Handling Tests
# =============================================================================


class TestResourceErrors:
    """Tests for resource error handling."""

    @pytest.mark.vcr()
    async def test_resource_not_found(self, mcp_client):
        """Test accessing non-existent entity raises an error."""
        from mcp.shared.exceptions import McpError

        # The API returns 404 for non-existent entities
        with pytest.raises(McpError) as exc_info:
            await mcp_client.read_resource("ruz://uctovna-jednotka/999999999")

        assert "404" in str(exc_info.value)
