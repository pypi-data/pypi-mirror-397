"""Enums for the RegisterUZ API."""

from enum import Enum


class TypZavierky(str, Enum):
    """Types of accounting closures."""

    RIADNA = "Riadna"
    MIMORIADNA = "Mimoriadna"
    PRIEBEZNA = "Priebežná"
    KOMBINOVANA = "Kombinovaná"


class TypVyrocnejSpravy(str, Enum):
    """Types of annual reports."""

    ROCNA_FINANCNA_SPRAVA = "Ročná finančná správa"
    INDIVIDUALNA_VYROCNA_SPRAVA = "Individuálna výročná správa"
    KONSOLIDOVANA_VYROCNA_SPRAVA = "Konsolidovaná výročná správa"
    SUHRNNA_VYROCNA_SPRAVA_SR = "Súhrnná výročná správa SR"


class PristupnostDat(str, Enum):
    """Data accessibility levels."""

    VEREJNE = "Verejné"
    VEREJNE_PRILOHY = "Verejné prílohy"
    NEVEREJNE = "Neverejné"


class StavZaznamu(str, Enum):
    """Record state."""

    AKTIVNY = "AKTÍVNY"
    ZMAZANE = "ZMAZANÉ"
    NEVEREJNE = "NEVEREJNÁ"


class ZdrojDat(str, Enum):
    """Data sources."""

    SUSR = "ŠÚSR"  # Statistical Office
    SP = "SP"  # State Treasury System
    DC = "DC"  # DataCentrum
    FRSR = "FRSR"  # Financial Administration
    JUS = "JUS"  # Unified State Accounting
    OVSR = "OVSR"  # Commercial Register
    CKS = "CKS"  # Central Consolidation System
    SAM = "SAM"  # Municipal Budget System
