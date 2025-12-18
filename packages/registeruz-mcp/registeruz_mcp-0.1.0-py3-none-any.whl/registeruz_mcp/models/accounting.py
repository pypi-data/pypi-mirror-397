"""Accounting entity models."""

from typing import Any

from pydantic import BaseModel, Field

from .classifiers import LocalizedName
from .enums import PristupnostDat, StavZaznamu, TypVyrocnejSpravy, TypZavierky


class UctovnaJednotka(BaseModel):
    """Accounting unit (company/organization) detail."""

    id: int = Field(description="Entity ID")
    ico: str | None = Field(default=None, description="Registration number (IČO)")
    dic: str | None = Field(default=None, description="Tax identification number (DIČ)")
    sid: str | None = Field(default=None, description="Statistical ID (SID)")
    nazovUJ: str | None = Field(default=None, description="Entity name")
    mesto: str | None = Field(default=None, description="City")
    ulica: str | None = Field(default=None, description="Street address")
    psc: str | None = Field(default=None, description="Postal code")
    datumZalozenia: str | None = Field(default=None, description="Foundation date")
    datumZrusenia: str | None = Field(default=None, description="Dissolution date")
    pravnaForma: str | None = Field(default=None, description="Legal form code")
    skNace: str | None = Field(default=None, description="SK NACE classification code")
    velkostOrganizacie: str | None = Field(
        default=None, description="Organization size code"
    )
    druhVlastnictva: str | None = Field(default=None, description="Ownership type code")
    kraj: str | None = Field(default=None, description="Region code")
    okres: str | None = Field(default=None, description="District code")
    sidlo: str | None = Field(default=None, description="Settlement code")
    konsolidovana: bool | None = Field(
        default=None, description="Whether entity is consolidated"
    )
    idUctovnychZavierok: list[int] | None = Field(
        default=None, description="IDs of related accounting closures"
    )
    idVyrocnychSprav: list[int] | None = Field(
        default=None, description="IDs of related annual reports"
    )
    zdrojDat: str | None = Field(default=None, description="Data source")
    datumPoslednejUpravy: str | None = Field(
        default=None, description="Last modification datetime"
    )
    stav: StavZaznamu | None = Field(
        default=None, description="Record state (only for deleted records)"
    )


class UctovnaZavierka(BaseModel):
    """Accounting closure (financial statement) detail."""

    id: int = Field(description="Closure ID")
    obdobieOd: str | None = Field(default=None, description="Period start (YYYY-MM)")
    obdobieDo: str | None = Field(default=None, description="Period end (YYYY-MM)")
    datumPodania: str | None = Field(default=None, description="Submission date")
    datumZostavenia: str | None = Field(default=None, description="Preparation date")
    datumSchvalenia: str | None = Field(default=None, description="Approval date")
    datumZostaveniaK: str | None = Field(
        default=None, description="Preparation as-of date"
    )
    datumPrilozeniaSpravyAuditora: str | None = Field(
        default=None, description="Auditor report attachment date"
    )
    nazovFondu: str | None = Field(default=None, description="Fund name (for funds)")
    leiKod: str | None = Field(default=None, description="LEI code")
    idUJ: int | None = Field(default=None, description="Related accounting unit ID")
    konsolidovana: bool | None = Field(
        default=None, description="Whether closure is consolidated"
    )
    konsolidovanaZavierkaUstrednejStatnejSpravy: bool | None = Field(
        default=None, description="Central state admin consolidated closure"
    )
    suhrnnaUctovnaZavierkaVerejnejSpravy: bool | None = Field(
        default=None, description="Summary public admin accounting closure"
    )
    typ: TypZavierky | None = Field(default=None, description="Closure type")
    idUctovnychVykazov: list[int] | None = Field(
        default=None, description="IDs of related financial reports"
    )
    zdrojDat: str | None = Field(default=None, description="Data source")
    datumPoslednejUpravy: str | None = Field(
        default=None, description="Last modification datetime"
    )
    stav: StavZaznamu | None = Field(
        default=None, description="Record state (only for deleted records)"
    )


class Priloha(BaseModel):
    """Attachment metadata."""

    id: int = Field(description="Attachment ID")
    meno: str | None = Field(default=None, description="File name")
    mimeType: str | None = Field(default=None, description="MIME type")
    velkostPrilohy: int | None = Field(default=None, description="File size in bytes")
    pocetStran: int | None = Field(default=None, description="Number of pages")
    digest: str | None = Field(default=None, description="File digest/hash")
    jazyk: str | None = Field(default=None, description="Language code")


class TitulnaStrana(BaseModel):
    """Title page information from financial report content."""

    nazov: str | None = Field(default=None, description="Company name")
    ico: str | None = Field(default=None, description="Registration number")
    dic: str | None = Field(default=None, description="Tax ID")
    sidlo: str | None = Field(default=None, description="Address")
    obdobieOd: str | None = Field(default=None, description="Period from")
    obdobieDo: str | None = Field(default=None, description="Period to")
    datumZostavenia: str | None = Field(default=None, description="Preparation date")
    datumSchvalenia: str | None = Field(default=None, description="Approval date")
    podpisMeno: str | None = Field(default=None, description="Signatory name")
    podpisFunkcia: str | None = Field(default=None, description="Signatory position")


class TabulkaData(BaseModel):
    """Table data from financial report."""

    nazov: LocalizedName | str | None = Field(
        default=None, description="Table name (localized)"
    )
    data: list[Any] = Field(
        default_factory=list, description="Table data values (typically strings)"
    )


class ObsahVykazu(BaseModel):
    """Financial report content."""

    titulnaStrana: TitulnaStrana | None = Field(
        default=None, description="Title page data"
    )
    tabulky: list[TabulkaData] = Field(
        default_factory=list, description="Report tables with data"
    )


class UctovnyVykaz(BaseModel):
    """Financial report detail."""

    id: int = Field(description="Report ID")
    idUctovnejZavierky: int | None = Field(
        default=None, description="Related accounting closure ID"
    )
    idVyrocnejSpravy: int | None = Field(
        default=None, description="Related annual report ID"
    )
    idSablony: int | None = Field(default=None, description="Template ID used")
    mena: str | None = Field(default=None, description="Currency code")
    kodDanovehoUradu: str | None = Field(default=None, description="Tax office code")
    pristupnostDat: PristupnostDat | None = Field(
        default=None, description="Data accessibility level"
    )
    prilohy: list[Priloha] = Field(default_factory=list, description="Attachments")
    obsah: ObsahVykazu | None = Field(default=None, description="Report content")
    zdrojDat: str | None = Field(default=None, description="Data source")
    datumPoslednejUpravy: str | None = Field(
        default=None, description="Last modification datetime"
    )
    stav: StavZaznamu | None = Field(
        default=None, description="Record state (only for deleted records)"
    )


class VyrocnaSprava(BaseModel):
    """Annual report detail."""

    id: int = Field(description="Report ID")
    nazovUJ: str | None = Field(default=None, description="Entity name")
    typ: TypVyrocnejSpravy | None = Field(default=None, description="Report type")
    nazovFondu: str | None = Field(default=None, description="Fund name")
    leiKod: str | None = Field(default=None, description="LEI code")
    obdobieOd: str | None = Field(default=None, description="Period start")
    obdobieDo: str | None = Field(default=None, description="Period end")
    datumPodania: str | None = Field(default=None, description="Submission date")
    datumZostaveniaK: str | None = Field(
        default=None, description="Preparation as-of date"
    )
    pristupnostDat: PristupnostDat | None = Field(
        default=None, description="Data accessibility"
    )
    prilohy: list[Priloha] = Field(default_factory=list, description="Attachments")
    idUctovnychVykazov: list[int] | None = Field(
        default=None, description="Related financial report IDs"
    )
    idUJ: int | None = Field(default=None, description="Related accounting unit ID")
    zdrojDat: str | None = Field(default=None, description="Data source")
    datumPoslednejUpravy: str | None = Field(
        default=None, description="Last modification datetime"
    )
    stav: StavZaznamu | None = Field(
        default=None, description="Record state (only for deleted records)"
    )
