"""Tests for MCP tools using VCR.py for HTTP mocking."""

import pytest
from pathlib import Path

from fastmcp import Client

from registeruz_mcp import mcp
from registeruz_mcp.models import (
    IdListResponse,
    ZostavajuceIdResponse,
    UctovnaJednotka,
    UctovnaZavierka,
    UctovnyVykaz,
    VyrocnaSprava,
    Sablona,
    SablonyResponse,
    KlasifikacieResponse,
)


# =============================================================================
# List Tools Tests
# =============================================================================


class TestListTools:
    """Tests for ID list tools."""

    @pytest.mark.vcr()
    async def test_get_uctovne_jednotky(self, mcp_client):
        """Test getting accounting unit IDs."""
        result = await mcp_client.call_tool(
            "get_uctovne_jednotky",
            {"zmenene_od": "2024-01-01", "max_zaznamov": 5},
        )
        assert result.data is not None
        assert hasattr(result.data, "id")
        assert isinstance(result.data.id, list)

    @pytest.mark.vcr()
    async def test_get_uctovne_jednotky_by_ico(self, mcp_client, sample_ico):
        """Test getting accounting unit IDs filtered by IČO."""
        result = await mcp_client.call_tool(
            "get_uctovne_jednotky",
            {"zmenene_od": "2020-01-01", "ico": sample_ico},
        )
        assert result.data is not None
        assert len(result.data.id) >= 1

    @pytest.mark.vcr()
    async def test_get_uctovne_zavierky(self, mcp_client):
        """Test getting accounting closure IDs."""
        result = await mcp_client.call_tool(
            "get_uctovne_zavierky",
            {"zmenene_od": "2024-01-01", "max_zaznamov": 5},
        )
        assert result.data is not None
        assert hasattr(result.data, "id")

    @pytest.mark.vcr()
    async def test_get_uctovne_vykazy(self, mcp_client):
        """Test getting financial report IDs."""
        result = await mcp_client.call_tool(
            "get_uctovne_vykazy",
            {"zmenene_od": "2024-01-01", "max_zaznamov": 5},
        )
        assert result.data is not None
        assert hasattr(result.data, "id")

    @pytest.mark.vcr()
    async def test_get_vyrocne_spravy(self, mcp_client):
        """Test getting annual report IDs."""
        result = await mcp_client.call_tool(
            "get_vyrocne_spravy",
            {"zmenene_od": "2024-01-01", "max_zaznamov": 5},
        )
        assert result.data is not None
        assert hasattr(result.data, "id")


# =============================================================================
# Count Tools Tests
# =============================================================================


class TestCountTools:
    """Tests for remaining ID count tools."""

    @pytest.mark.vcr()
    async def test_get_zostavajuce_id_uctovne_jednotky(self, mcp_client):
        """Test counting remaining accounting unit IDs."""
        result = await mcp_client.call_tool(
            "get_zostavajuce_id_uctovne_jednotky",
            {"zmenene_od": "2024-01-01"},
        )
        assert result.data is not None
        assert hasattr(result.data, "pocetZostavajucichId")
        assert result.data.pocetZostavajucichId >= 0

    @pytest.mark.vcr()
    async def test_get_zostavajuce_id_uctovne_zavierky(self, mcp_client):
        """Test counting remaining accounting closure IDs."""
        result = await mcp_client.call_tool(
            "get_zostavajuce_id_uctovne_zavierky",
            {"zmenene_od": "2024-01-01"},
        )
        assert result.data is not None
        assert hasattr(result.data, "pocetZostavajucichId")

    @pytest.mark.vcr()
    async def test_get_zostavajuce_id_uctovne_vykazy(self, mcp_client):
        """Test counting remaining financial report IDs."""
        result = await mcp_client.call_tool(
            "get_zostavajuce_id_uctovne_vykazy",
            {"zmenene_od": "2024-01-01"},
        )
        assert result.data is not None
        assert hasattr(result.data, "pocetZostavajucichId")

    @pytest.mark.vcr()
    async def test_get_zostavajuce_id_vyrocne_spravy(self, mcp_client):
        """Test counting remaining annual report IDs."""
        result = await mcp_client.call_tool(
            "get_zostavajuce_id_vyrocne_spravy",
            {"zmenene_od": "2024-01-01"},
        )
        assert result.data is not None
        assert hasattr(result.data, "pocetZostavajucichId")


# =============================================================================
# Detail Tools Tests
# =============================================================================


class TestDetailTools:
    """Tests for entity detail tools."""

    @pytest.mark.vcr()
    async def test_get_uctovna_jednotka(self, mcp_client, sample_company_id):
        """Test getting accounting unit details."""
        result = await mcp_client.call_tool(
            "get_uctovna_jednotka",
            {"id": sample_company_id},
        )
        assert result.data is not None
        assert result.data.id == sample_company_id
        assert result.data.ico == "46792511"
        assert result.data.nazovUJ == "freevision s. r. o."

    @pytest.mark.vcr()
    async def test_get_uctovna_zavierka(self, mcp_client, sample_closure_id):
        """Test getting accounting closure details."""
        result = await mcp_client.call_tool(
            "get_uctovna_zavierka",
            {"id": sample_closure_id},
        )
        assert result.data is not None
        assert result.data.id == sample_closure_id
        assert result.data.obdobieOd is not None
        assert result.data.obdobieDo is not None

    @pytest.mark.vcr()
    async def test_get_uctovny_vykaz(self, mcp_client, sample_report_id):
        """Test getting financial report details."""
        result = await mcp_client.call_tool(
            "get_uctovny_vykaz",
            {"id": sample_report_id},
        )
        assert result.data is not None
        assert result.data.id == sample_report_id
        assert result.data.idSablony is not None

    @pytest.mark.vcr()
    async def test_get_vyrocna_sprava(self, mcp_client):
        """Test getting annual report details."""
        # First get an annual report ID
        list_result = await mcp_client.call_tool(
            "get_vyrocne_spravy",
            {"zmenene_od": "2024-01-01", "max_zaznamov": 5},
        )
        if list_result.data.id:
            result = await mcp_client.call_tool(
                "get_vyrocna_sprava",
                {"id": list_result.data.id[0]},
            )
            assert result.data is not None
            assert result.data.id == list_result.data.id[0]


# =============================================================================
# Template Tools Tests
# =============================================================================


class TestTemplateTools:
    """Tests for template tools."""

    @pytest.mark.vcr()
    async def test_get_sablona(self, mcp_client, sample_template_id):
        """Test getting template details."""
        result = await mcp_client.call_tool(
            "get_sablona",
            {"id": sample_template_id},
        )
        assert result.data is not None
        assert result.data.id == sample_template_id
        assert result.data.nazov is not None

    @pytest.mark.vcr()
    async def test_get_sablony(self, mcp_client):
        """Test getting all templates."""
        result = await mcp_client.call_tool("get_sablony", {})
        assert result.data is not None
        assert hasattr(result.data, "sablony")
        assert len(result.data.sablony) > 0


# =============================================================================
# Classifier Tools Tests
# =============================================================================


class TestClassifierTools:
    """Tests for classifier tools."""

    @pytest.mark.vcr()
    async def test_get_pravne_formy(self, mcp_client):
        """Test getting legal forms."""
        result = await mcp_client.call_tool("get_pravne_formy", {})
        assert result.data is not None
        assert hasattr(result.data, "klasifikacie")
        assert len(result.data.klasifikacie) > 0
        # Check that we have the common s.r.o. legal form
        codes = [k.kod for k in result.data.klasifikacie]
        assert "112" in codes  # s.r.o.

    @pytest.mark.vcr()
    async def test_get_sk_nace(self, mcp_client):
        """Test getting SK NACE classification."""
        result = await mcp_client.call_tool("get_sk_nace", {})
        assert result.data is not None
        assert hasattr(result.data, "klasifikacie")
        assert len(result.data.klasifikacie) > 0

    @pytest.mark.vcr()
    async def test_get_druhy_vlastnictva(self, mcp_client):
        """Test getting ownership types."""
        result = await mcp_client.call_tool("get_druhy_vlastnictva", {})
        assert result.data is not None
        assert hasattr(result.data, "klasifikacie")

    @pytest.mark.vcr()
    async def test_get_velkosti_organizacie(self, mcp_client):
        """Test getting organization sizes."""
        result = await mcp_client.call_tool("get_velkosti_organizacie", {})
        assert result.data is not None
        assert hasattr(result.data, "klasifikacie")

    @pytest.mark.vcr()
    async def test_get_kraje(self, mcp_client):
        """Test getting regions."""
        result = await mcp_client.call_tool("get_kraje", {})
        assert result.data is not None
        assert hasattr(result.data, "klasifikacie")
        # Slovakia has 8 regions + 2 extra-regio codes
        assert len(result.data.klasifikacie) >= 8

    @pytest.mark.vcr()
    async def test_get_okresy(self, mcp_client):
        """Test getting districts."""
        result = await mcp_client.call_tool("get_okresy", {})
        assert result.data is not None
        assert hasattr(result.data, "klasifikacie")
        # Slovakia has 79 districts
        assert len(result.data.klasifikacie) >= 70

    @pytest.mark.vcr()
    async def test_get_sidla(self, mcp_client):
        """Test getting settlements."""
        result = await mcp_client.call_tool("get_sidla", {})
        assert result.data is not None
        assert hasattr(result.data, "klasifikacie")
        # Slovakia has thousands of settlements
        assert len(result.data.klasifikacie) > 1000


# =============================================================================
# Download Tools Tests
# =============================================================================


class TestDownloadTools:
    """Tests for download URL tools."""

    async def test_get_attachment_url(self, mcp_client):
        """Test getting attachment download URL."""
        result = await mcp_client.call_tool(
            "get_attachment_url",
            {"id": 12345},
        )
        assert result.data is not None
        assert "attachment/12345" in result.data
        assert result.data.startswith("https://www.registeruz.sk/")

    async def test_get_financial_report_pdf_url(self, mcp_client):
        """Test getting financial report PDF URL."""
        result = await mcp_client.call_tool(
            "get_financial_report_pdf_url",
            {"id": 9166748},
        )
        assert result.data is not None
        assert "pdf/9166748" in result.data
        assert result.data.startswith("https://www.registeruz.sk/")


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for common workflows."""

    @pytest.mark.vcr()
    async def test_search_company_and_get_financials(self, mcp_client, sample_ico):
        """Test searching for a company and retrieving its financial data."""
        # Step 1: Search for company by IČO
        search_result = await mcp_client.call_tool(
            "get_uctovne_jednotky",
            {"zmenene_od": "2020-01-01", "ico": sample_ico},
        )
        assert len(search_result.data.id) >= 1
        company_id = search_result.data.id[0]

        # Step 2: Get company details
        company_result = await mcp_client.call_tool(
            "get_uctovna_jednotka",
            {"id": company_id},
        )
        assert company_result.data.ico == sample_ico
        assert company_result.data.idUctovnychZavierok is not None

        # Step 3: Get accounting closure
        closure_ids = company_result.data.idUctovnychZavierok
        if closure_ids:
            closure_result = await mcp_client.call_tool(
                "get_uctovna_zavierka",
                {"id": closure_ids[-1]},  # Get most recent
            )
            assert closure_result.data.id == closure_ids[-1]

            # Step 4: Get financial report if available
            report_ids = closure_result.data.idUctovnychVykazov
            if report_ids:
                report_result = await mcp_client.call_tool(
                    "get_uctovny_vykaz",
                    {"id": report_ids[0]},
                )
                assert report_result.data.id == report_ids[0]

    @pytest.mark.vcr()
    async def test_get_template_for_report(self, mcp_client, sample_report_id):
        """Test getting the template for a financial report."""
        # Get financial report
        report_result = await mcp_client.call_tool(
            "get_uctovny_vykaz",
            {"id": sample_report_id},
        )
        template_id = report_result.data.idSablony

        # Get template
        if template_id:
            template_result = await mcp_client.call_tool(
                "get_sablona",
                {"id": template_id},
            )
            assert template_result.data.id == template_id
            assert template_result.data.tabulky is not None
