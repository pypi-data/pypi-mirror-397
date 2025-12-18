"""Tests for labeled financial report tools."""

import pytest

from fastmcp import Client

from registeruz_mcp import mcp


class TestLabeledTools:
    """Tests for labeled data tools."""

    @pytest.mark.vcr()
    async def test_get_uctovny_vykaz_with_labeled_tables(self, mcp_client, sample_report_id):
        """Test getting financial report with labeled tables."""
        result = await mcp_client.call_tool(
            "get_uctovny_vykaz_with_labeled_tables",
            {"id": sample_report_id},
        )
        assert result.data is not None
        assert result.data.id == sample_report_id
        assert result.data.idSablony == 687  # Template for this report
        assert len(result.data.labeled_tables) > 0

        # Check first table structure
        table = result.data.labeled_tables[0]
        assert table.table_name is not None
        assert len(table.columns) > 0
        assert len(table.rows) > 0

        # Check first row structure
        row = table.rows[0]
        assert row.label is not None
        assert len(row.values) > 0

        # Check column value structure
        col_val = row.values[0]
        assert col_val.column is not None

    @pytest.mark.vcr()
    async def test_get_uctovny_vykaz_with_labeled_tables_columns(self, mcp_client, sample_report_id):
        """Test that labeled tables have proper column labels."""
        result = await mcp_client.call_tool(
            "get_uctovny_vykaz_with_labeled_tables",
            {"id": sample_report_id},
        )

        for table in result.data.labeled_tables:
            # Should have 2 data columns (current and previous period)
            assert len(table.columns) == 2
            # Column labels should be accounting period related
            assert any("obdobie" in col.lower() for col in table.columns)

    @pytest.mark.vcr()
    async def test_search_by_row_code(self, mcp_client, sample_report_id):
        """Test searching values by row code."""
        result = await mcp_client.call_tool(
            "get_uctovny_vykaz_table_value_by_labels",
            {"id": sample_report_id, "row_code": "A.VI."},
        )
        assert result.data is not None
        assert result.data.report_id == sample_report_id
        assert len(result.data.matches) > 0

        # All matches should have the requested row code
        for match in result.data.matches:
            assert match.row_code == "A.VI."

    @pytest.mark.vcr()
    async def test_search_by_row_label(self, mcp_client, sample_report_id):
        """Test searching values by row label."""
        result = await mcp_client.call_tool(
            "get_uctovny_vykaz_table_value_by_labels",
            {"id": sample_report_id, "row_label": "SPOLU"},
        )
        assert result.data is not None
        assert len(result.data.matches) > 0

        # All matches should contain "SPOLU" in the label
        for match in result.data.matches:
            assert "spolu" in match.row_label.lower()

    @pytest.mark.vcr()
    async def test_search_by_column_label(self, mcp_client, sample_report_id):
        """Test searching values by column label."""
        result = await mcp_client.call_tool(
            "get_uctovny_vykaz_table_value_by_labels",
            {"id": sample_report_id, "row_code": "A.", "column_label": "Bežné"},
        )
        assert result.data is not None
        assert len(result.data.matches) > 0

        # All matches should be from the current period column
        for match in result.data.matches:
            assert "bežné" in match.column_label.lower()

    @pytest.mark.vcr()
    async def test_search_by_table_name(self, mcp_client, sample_report_id):
        """Test searching values filtered by table name."""
        result = await mcp_client.call_tool(
            "get_uctovny_vykaz_table_value_by_labels",
            {"id": sample_report_id, "row_code": "A.", "table_name": "aktív"},
        )
        assert result.data is not None
        assert len(result.data.matches) > 0

        # All matches should be from the assets table
        for match in result.data.matches:
            assert "aktív" in match.table_name.lower()

    @pytest.mark.vcr()
    async def test_search_no_matches(self, mcp_client, sample_report_id):
        """Test search with no matches returns empty list."""
        result = await mcp_client.call_tool(
            "get_uctovny_vykaz_table_value_by_labels",
            {"id": sample_report_id, "row_code": "NONEXISTENT.CODE"},
        )
        assert result.data is not None
        assert len(result.data.matches) == 0

    @pytest.mark.vcr()
    async def test_search_profit_loss_result(self, mcp_client, sample_report_id):
        """Test searching for profit/loss result (Výsledok hospodárenia)."""
        result = await mcp_client.call_tool(
            "get_uctovny_vykaz_table_value_by_labels",
            {"id": sample_report_id, "row_label": "Výsledok hospodárenia", "table_name": "pasív"},
        )
        assert result.data is not None
        # Should find profit/loss result
        assert len(result.data.matches) > 0


class TestLabeledToolsIntegration:
    """Integration tests for labeled tools."""

    @pytest.mark.vcr()
    async def test_compare_current_and_previous_period(self, mcp_client, sample_report_id):
        """Test extracting and comparing values across periods."""
        result = await mcp_client.call_tool(
            "get_uctovny_vykaz_table_value_by_labels",
            {"id": sample_report_id, "row_label": "SPOLU MAJETOK"},
        )

        # Should have matches for both periods
        matches = result.data.matches
        assert len(matches) >= 2

        # Extract values for each period
        values_by_period = {}
        for match in matches:
            values_by_period[match.column_label] = match.value

        # Should have values for current and previous period
        assert len(values_by_period) >= 2
