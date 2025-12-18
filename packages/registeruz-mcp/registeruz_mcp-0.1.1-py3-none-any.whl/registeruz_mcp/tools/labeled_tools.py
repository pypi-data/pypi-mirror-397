"""Tools for labeled financial report data."""

from typing import Any

from ..client import get_client
from ..models import (
    ColumnValue,
    LabeledTableData,
    LabeledTableRow,
    LocalizedName,
    Sablona,
    TableValueMatch,
    TableValueSearchResult,
    UctovnyVykaz,
    UctovnyVykazWithLabeledTables,
)


def get_localized_text(value: LocalizedName | str | None, lang: str = "sk") -> str:
    """Extract text from a LocalizedName or string."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, LocalizedName):
        return value.sk or value.en or ""
    return str(value)


def get_data_column_labels(sablona_table) -> list[str]:
    """Extract data column labels from template header.

    The header contains multiple rows. Row 1 usually has general headers,
    Row 2 has specific column identifiers. Data columns are typically
    the last N columns where N = pocetDatovychStlpcov.
    """
    if not sablona_table.hlavicka:
        return []

    # Get the number of data columns
    num_data_cols = sablona_table.pocetDatovychStlpcov or 2
    total_cols = sablona_table.pocetStlpcov or 5

    # Data columns start after the label columns
    data_col_start = total_cols - num_data_cols + 1

    # Get labels from row 1 (main headers) for data columns
    labels = []
    for hlavicka in sablona_table.hlavicka:
        if hlavicka.riadok == 1 and hlavicka.stlpec is not None:
            if hlavicka.stlpec >= data_col_start:
                text = get_localized_text(hlavicka.text)
                labels.append((hlavicka.stlpec, text))

    # Sort by column position and extract just the labels
    labels.sort(key=lambda x: x[0])
    return [label for _, label in labels]


def build_labeled_table(vykaz_table, sablona_table) -> LabeledTableData:
    """Build a labeled table by combining report data with template structure."""
    table_name = get_localized_text(vykaz_table.nazov)

    # Get column labels
    column_labels = get_data_column_labels(sablona_table)
    num_cols = len(column_labels) if column_labels else (sablona_table.pocetDatovychStlpcov or 2)

    # If no column labels found, use generic ones
    if not column_labels:
        column_labels = [f"Stĺpec {i+1}" for i in range(num_cols)]

    rows = []
    data = vykaz_table.data or []

    for i, riadok in enumerate(sablona_table.riadky):
        row_label = get_localized_text(riadok.text) or get_localized_text(riadok.nazov) or ""
        row_code = riadok.oznacenie or riadok.kod
        row_number = riadok.cisloRiadku

        # Extract values for this row
        start_idx = i * num_cols
        end_idx = start_idx + num_cols
        row_values = data[start_idx:end_idx] if start_idx < len(data) else []

        # Pad with empty strings if needed
        while len(row_values) < num_cols:
            row_values.append("")

        # Build values list with column labels
        values_list = []
        for j, col_label in enumerate(column_labels):
            val = str(row_values[j]) if j < len(row_values) else ""
            values_list.append(ColumnValue(column=col_label, value=val))

        rows.append(LabeledTableRow(
            label=row_label,
            code=row_code,
            row_number=row_number,
            values=values_list,
        ))

    return LabeledTableData(
        table_name=table_name,
        columns=column_labels,
        rows=rows,
    )


def match_table_by_name(vykaz_tables, sablona_tables, table_name: str):
    """Find matching tables by name."""
    vykaz_table = None
    sablona_table = None

    for vt in vykaz_tables:
        vt_name = get_localized_text(vt.nazov)
        if table_name.lower() in vt_name.lower():
            vykaz_table = vt
            break

    for st in sablona_tables:
        st_name = get_localized_text(st.nazov)
        if table_name.lower() in st_name.lower():
            sablona_table = st
            break

    return vykaz_table, sablona_table


def register_labeled_tools(mcp):
    """Register labeled data tools with the MCP server."""

    @mcp.tool(
        description="Get financial report with labeled tables. Fetches both the report and its template, "
        "then combines them to provide labeled data where each value has row and column labels. "
        "This makes it easy to understand what each value represents without manually cross-referencing the template."
    )
    async def get_uctovny_vykaz_with_labeled_tables(
        id: int,
    ) -> UctovnyVykazWithLabeledTables:
        """Get financial report with labeled tables.

        Args:
            id: Financial report ID

        Returns:
            Financial report with labeled tables containing row labels, codes, and column headers.
        """
        async with get_client() as client:
            # Fetch the financial report
            vykaz_response = await client.get("/uctovny-vykaz", params={"id": id})
            vykaz_response.raise_for_status()
            vykaz = UctovnyVykaz.model_validate(vykaz_response.json())

            # If no template ID or no content, return empty labeled tables
            if not vykaz.idSablony or not vykaz.obsah or not vykaz.obsah.tabulky:
                return UctovnyVykazWithLabeledTables(
                    id=vykaz.id,
                    idUctovnejZavierky=vykaz.idUctovnejZavierky,
                    idSablony=vykaz.idSablony,
                    mena=vykaz.mena,
                    labeled_tables=[],
                )

            # Fetch the template
            sablona_response = await client.get("/sablona", params={"id": vykaz.idSablony})
            sablona_response.raise_for_status()
            sablona = Sablona.model_validate(sablona_response.json())

            if not sablona.tabulky:
                return UctovnyVykazWithLabeledTables(
                    id=vykaz.id,
                    idUctovnejZavierky=vykaz.idUctovnejZavierky,
                    idSablony=vykaz.idSablony,
                    mena=vykaz.mena,
                    labeled_tables=[],
                )

            # Build labeled tables by matching vykaz tables with template tables
            labeled_tables = []
            for vykaz_table in vykaz.obsah.tabulky:
                vykaz_table_name = get_localized_text(vykaz_table.nazov)

                # Find matching template table by name
                matching_sablona_table = None
                for sablona_table in sablona.tabulky:
                    sablona_table_name = get_localized_text(sablona_table.nazov)
                    if vykaz_table_name.lower() == sablona_table_name.lower():
                        matching_sablona_table = sablona_table
                        break

                if matching_sablona_table:
                    labeled_table = build_labeled_table(vykaz_table, matching_sablona_table)
                    labeled_tables.append(labeled_table)

            return UctovnyVykazWithLabeledTables(
                id=vykaz.id,
                idUctovnejZavierky=vykaz.idUctovnejZavierky,
                idSablony=vykaz.idSablony,
                mena=vykaz.mena,
                labeled_tables=labeled_tables,
            )

    @mcp.tool(
        description="Search for specific values in a financial report by matching row and/or column labels. "
        "Returns only the values that match the specified criteria. Useful for extracting specific metrics "
        "like 'Výsledok hospodárenia' (profit/loss), 'SPOLU MAJETOK' (total assets), etc."
    )
    async def get_uctovny_vykaz_table_value_by_labels(
        id: int,
        row_label: str | None = None,
        row_code: str | None = None,
        column_label: str | None = None,
        table_name: str | None = None,
    ) -> TableValueSearchResult:
        """Search for values in financial report by labels.

        Args:
            id: Financial report ID
            row_label: Partial row label to match (case-insensitive)
            row_code: Row designation code to match (e.g., 'A.', 'A.I.', 'A.VI.')
            column_label: Partial column label to match (case-insensitive)
            table_name: Partial table name to filter (case-insensitive)

        Returns:
            Search results with matching values and their full context.
        """
        async with get_client() as client:
            # Fetch the financial report
            vykaz_response = await client.get("/uctovny-vykaz", params={"id": id})
            vykaz_response.raise_for_status()
            vykaz = UctovnyVykaz.model_validate(vykaz_response.json())

            # If no template ID or no content, return empty results
            if not vykaz.idSablony or not vykaz.obsah or not vykaz.obsah.tabulky:
                return TableValueSearchResult(
                    report_id=vykaz.id,
                    template_id=vykaz.idSablony,
                    matches=[],
                )

            # Fetch the template
            sablona_response = await client.get("/sablona", params={"id": vykaz.idSablony})
            sablona_response.raise_for_status()
            sablona = Sablona.model_validate(sablona_response.json())

            if not sablona.tabulky:
                return TableValueSearchResult(
                    report_id=vykaz.id,
                    template_id=vykaz.idSablony,
                    matches=[],
                )

            matches = []

            for vykaz_table in vykaz.obsah.tabulky:
                vykaz_table_name = get_localized_text(vykaz_table.nazov)

                # Filter by table name if specified
                if table_name and table_name.lower() not in vykaz_table_name.lower():
                    continue

                # Find matching template table
                matching_sablona_table = None
                for sablona_table in sablona.tabulky:
                    sablona_table_name = get_localized_text(sablona_table.nazov)
                    if vykaz_table_name.lower() == sablona_table_name.lower():
                        matching_sablona_table = sablona_table
                        break

                if not matching_sablona_table:
                    continue

                # Build labeled table and search
                labeled_table = build_labeled_table(vykaz_table, matching_sablona_table)

                for row in labeled_table.rows:
                    # Check row label match
                    if row_label and row_label.lower() not in row.label.lower():
                        continue

                    # Check row code match
                    if row_code and row.code != row_code:
                        continue

                    # Check each column value
                    for col_val in row.values:
                        # Check column label match
                        if column_label and column_label.lower() not in col_val.column.lower():
                            continue

                        # Skip empty values unless specifically searching
                        if not col_val.value and not (row_label or row_code):
                            continue

                        matches.append(TableValueMatch(
                            table_name=labeled_table.table_name,
                            row_label=row.label,
                            row_code=row.code,
                            row_number=row.row_number,
                            column_label=col_val.column,
                            value=col_val.value,
                        ))

            return TableValueSearchResult(
                report_id=vykaz.id,
                template_id=vykaz.idSablony,
                matches=matches,
            )
