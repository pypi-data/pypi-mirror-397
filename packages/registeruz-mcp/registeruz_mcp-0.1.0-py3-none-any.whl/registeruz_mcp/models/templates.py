"""Template models."""

from pydantic import BaseModel, Field

from .classifiers import LocalizedName


class SablonaHlavicka(BaseModel):
    """Template table header cell."""

    text: LocalizedName | str | None = Field(default=None, description="Header text")
    riadok: int | None = Field(default=None, description="Row position in header")
    stlpec: int | None = Field(default=None, description="Column position")
    sirkaStlpca: int | None = Field(default=None, description="Column width")
    vyskaRiadku: int | None = Field(default=None, description="Row height")
    # Legacy field for backward compatibility
    nazov: LocalizedName | str | None = Field(default=None, description="Header name (legacy)")


class SablonaRiadok(BaseModel):
    """Template table row definition."""

    text: LocalizedName | str | None = Field(default=None, description="Row label text")
    oznacenie: str | None = Field(default=None, description="Row designation code (e.g., 'A.', 'A.I.')")
    cisloRiadku: int | None = Field(default=None, description="Row number")
    # Legacy fields for backward compatibility
    nazov: LocalizedName | str | None = Field(default=None, description="Row name (legacy)")
    kod: str | None = Field(default=None, description="Row code (legacy)")


class SablonaTabulka(BaseModel):
    """Template table definition."""

    nazov: LocalizedName | str | None = Field(default=None, description="Table name")
    pocetDatovychStlpcov: int | None = Field(default=None, description="Number of data columns")
    pocetStlpcov: int | None = Field(default=None, description="Total number of columns")
    hlavicka: list[SablonaHlavicka] = Field(
        default_factory=list, description="Table headers"
    )
    riadky: list[SablonaRiadok] = Field(default_factory=list, description="Table rows")


class Sablona(BaseModel):
    """Financial report template."""

    id: int = Field(description="Template ID")
    nazov: str | None = Field(default=None, description="Template name")
    nariadenieMF: str | None = Field(
        default=None, description="Ministry of Finance regulation"
    )
    platneOd: str | None = Field(default=None, description="Valid from date")
    platneDo: str | None = Field(default=None, description="Valid to date")
    tabulky: list[SablonaTabulka] | None = Field(
        default=None, description="Table definitions (only in detail)"
    )


class SablonyResponse(BaseModel):
    """Response for templates list endpoint."""

    sablony: list[Sablona] = Field(default_factory=list, description="List of templates")
