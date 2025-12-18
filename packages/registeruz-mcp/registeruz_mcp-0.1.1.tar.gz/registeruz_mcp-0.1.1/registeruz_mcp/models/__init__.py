"""Pydantic models for the RegisterUZ API."""

from .accounting import (
    ObsahVykazu,
    Priloha,
    TabulkaData,
    TitulnaStrana,
    UctovnaJednotka,
    UctovnaZavierka,
    UctovnyVykaz,
    VyrocnaSprava,
)
from .classifiers import Klasifikacia, KlasifikacieResponse, LocalizedName
from .enums import (
    PristupnostDat,
    StavZaznamu,
    TypVyrocnejSpravy,
    TypZavierky,
    ZdrojDat,
)
from .labeled import (
    ColumnValue,
    LabeledTable,
    LabeledTableData,
    LabeledTableRow,
    LabeledValue,
    TableValueMatch,
    TableValueSearchResult,
    UctovnyVykazWithLabeledTables,
)
from .responses import IdListResponse, ZostavajuceIdResponse
from .templates import (
    Sablona,
    SablonaHlavicka,
    SablonaRiadok,
    SablonaTabulka,
    SablonyResponse,
)

__all__ = [
    # Enums
    "PristupnostDat",
    "StavZaznamu",
    "TypVyrocnejSpravy",
    "TypZavierky",
    "ZdrojDat",
    # Responses
    "IdListResponse",
    "ZostavajuceIdResponse",
    # Classifiers
    "Klasifikacia",
    "KlasifikacieResponse",
    "LocalizedName",
    # Templates
    "Sablona",
    "SablonaHlavicka",
    "SablonaRiadok",
    "SablonaTabulka",
    "SablonyResponse",
    # Accounting
    "ObsahVykazu",
    "Priloha",
    "TabulkaData",
    "TitulnaStrana",
    "UctovnaJednotka",
    "UctovnaZavierka",
    "UctovnyVykaz",
    "VyrocnaSprava",
    # Labeled
    "ColumnValue",
    "LabeledTable",
    "LabeledTableData",
    "LabeledTableRow",
    "LabeledValue",
    "TableValueMatch",
    "TableValueSearchResult",
    "UctovnyVykazWithLabeledTables",
]
