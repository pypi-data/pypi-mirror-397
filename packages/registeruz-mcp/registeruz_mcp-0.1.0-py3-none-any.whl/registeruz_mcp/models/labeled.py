"""Models for labeled financial report data."""

from typing import Any

from pydantic import BaseModel, Field

from .classifiers import LocalizedName


class LabeledValue(BaseModel):
    """A single labeled value from a financial report table."""

    row_label: str = Field(description="Row label (text description)")
    row_code: str | None = Field(default=None, description="Row designation code (e.g., 'A.I.', 'B.II.1.')")
    row_number: int | None = Field(default=None, description="Row number in the table")
    column_label: str = Field(description="Column label (e.g., 'Bežné účtovné obdobie')")
    column_index: int = Field(description="Column index (0-based)")
    value: str = Field(description="The actual value")


class LabeledTable(BaseModel):
    """A table with labeled values."""

    table_name: str = Field(description="Table name")
    values: list[LabeledValue] = Field(default_factory=list, description="Labeled values")


class ColumnValue(BaseModel):
    """A column value with its label."""

    column: str = Field(description="Column label")
    value: str = Field(description="Cell value")


class LabeledTableRow(BaseModel):
    """A row in a labeled table."""

    label: str = Field(description="Row label (text description)")
    code: str | None = Field(default=None, description="Row designation code (e.g., 'A.I.')")
    row_number: int | None = Field(default=None, description="Row number in the table")
    values: list[ColumnValue] = Field(
        default_factory=list,
        description="Values with column labels"
    )


class LabeledTableData(BaseModel):
    """Table data with row and column structure."""

    table_name: str = Field(description="Table name")
    columns: list[str] = Field(description="Column headers for data columns")
    rows: list[LabeledTableRow] = Field(
        default_factory=list,
        description="Rows with label, code, row_number, and values"
    )


class UctovnyVykazWithLabeledTables(BaseModel):
    """Financial report with labeled tables."""

    id: int = Field(description="Report ID")
    idUctovnejZavierky: int | None = Field(default=None, description="Related accounting closure ID")
    idSablony: int | None = Field(default=None, description="Template ID used")
    mena: str | None = Field(default=None, description="Currency code")
    labeled_tables: list[LabeledTableData] = Field(
        default_factory=list, description="Tables with labeled data"
    )


class TableValueMatch(BaseModel):
    """A matched value from a table search."""

    table_name: str = Field(description="Table name where value was found")
    row_label: str = Field(description="Row label")
    row_code: str | None = Field(default=None, description="Row designation code")
    row_number: int | None = Field(default=None, description="Row number")
    column_label: str = Field(description="Column label")
    value: str = Field(description="The matched value")


class TableValueSearchResult(BaseModel):
    """Result of searching for table values by labels."""

    report_id: int = Field(description="Financial report ID")
    template_id: int | None = Field(default=None, description="Template ID")
    matches: list[TableValueMatch] = Field(
        default_factory=list, description="Matched values"
    )
