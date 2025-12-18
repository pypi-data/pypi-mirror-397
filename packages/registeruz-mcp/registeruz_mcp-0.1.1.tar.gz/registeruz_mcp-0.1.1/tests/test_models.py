"""Tests for Pydantic models."""

import pytest

from registeruz_mcp.models import (
    IdListResponse,
    ZostavajuceIdResponse,
    Klasifikacia,
    KlasifikacieResponse,
    LocalizedName,
    Sablona,
    SablonyResponse,
    SablonaTabulka,
    SablonaHlavicka,
    SablonaRiadok,
    UctovnaJednotka,
    UctovnaZavierka,
    UctovnyVykaz,
    VyrocnaSprava,
    Priloha,
    TitulnaStrana,
    TabulkaData,
    ObsahVykazu,
    TypZavierky,
    TypVyrocnejSpravy,
    PristupnostDat,
    StavZaznamu,
    ZdrojDat,
)


class TestEnums:
    """Tests for enum types."""

    def test_typ_zavierky_values(self):
        """Test TypZavierky enum values."""
        assert TypZavierky.RIADNA.value == "Riadna"
        assert TypZavierky.MIMORIADNA.value == "Mimoriadna"
        assert TypZavierky.PRIEBEZNA.value == "Priebežná"
        assert TypZavierky.KOMBINOVANA.value == "Kombinovaná"

    def test_typ_vyrocnej_spravy_values(self):
        """Test TypVyrocnejSpravy enum values."""
        assert TypVyrocnejSpravy.ROCNA_FINANCNA_SPRAVA.value == "Ročná finančná správa"
        assert TypVyrocnejSpravy.INDIVIDUALNA_VYROCNA_SPRAVA.value == "Individuálna výročná správa"

    def test_pristupnost_dat_values(self):
        """Test PristupnostDat enum values."""
        assert PristupnostDat.VEREJNE.value == "Verejné"
        assert PristupnostDat.VEREJNE_PRILOHY.value == "Verejné prílohy"
        assert PristupnostDat.NEVEREJNE.value == "Neverejné"

    def test_stav_zaznamu_values(self):
        """Test StavZaznamu enum values."""
        assert StavZaznamu.AKTIVNY.value == "AKTÍVNY"
        assert StavZaznamu.ZMAZANE.value == "ZMAZANÉ"
        assert StavZaznamu.NEVEREJNE.value == "NEVEREJNÁ"

    def test_zdroj_dat_values(self):
        """Test ZdrojDat enum values."""
        assert ZdrojDat.SUSR.value == "ŠÚSR"
        assert ZdrojDat.SP.value == "SP"
        assert ZdrojDat.FRSR.value == "FRSR"


class TestIdListResponse:
    """Tests for IdListResponse model."""

    def test_parse_empty_response(self):
        """Test parsing empty ID list response."""
        data = {"id": [], "existujeDalsieId": False}
        response = IdListResponse.model_validate(data)
        assert response.id == []
        assert response.existujeDalsieId is False

    def test_parse_with_ids(self):
        """Test parsing ID list with data."""
        data = {"id": [1, 2, 3, 4, 5], "existujeDalsieId": True}
        response = IdListResponse.model_validate(data)
        assert response.id == [1, 2, 3, 4, 5]
        assert response.existujeDalsieId is True

    def test_default_values(self):
        """Test default values when fields are missing."""
        data = {}
        response = IdListResponse.model_validate(data)
        assert response.id == []
        assert response.existujeDalsieId is False


class TestZostavajuceIdResponse:
    """Tests for ZostavajuceIdResponse model."""

    def test_parse_count(self):
        """Test parsing remaining count response."""
        data = {"pocetZostavajucichId": 100}
        response = ZostavajuceIdResponse.model_validate(data)
        assert response.pocetZostavajucichId == 100

    def test_zero_count(self):
        """Test zero remaining count."""
        data = {"pocetZostavajucichId": 0}
        response = ZostavajuceIdResponse.model_validate(data)
        assert response.pocetZostavajucichId == 0


class TestLocalizedName:
    """Tests for LocalizedName model."""

    def test_parse_full(self):
        """Test parsing with both languages."""
        data = {"sk": "Slovenský názov", "en": "English name"}
        name = LocalizedName.model_validate(data)
        assert name.sk == "Slovenský názov"
        assert name.en == "English name"

    def test_parse_partial(self):
        """Test parsing with only Slovak name."""
        data = {"sk": "Len slovenský"}
        name = LocalizedName.model_validate(data)
        assert name.sk == "Len slovenský"
        assert name.en is None


class TestKlasifikacia:
    """Tests for Klasifikacia model."""

    def test_parse_basic(self):
        """Test parsing basic classifier."""
        data = {
            "kod": "112",
            "nazov": {"sk": "Spoločnosť s ručením obmedzeným", "en": "Limited liability company"},
        }
        klasifikacia = Klasifikacia.model_validate(data)
        assert klasifikacia.kod == "112"
        assert klasifikacia.nazov.sk == "Spoločnosť s ručením obmedzeným"

    def test_parse_with_parent(self):
        """Test parsing classifier with parent location."""
        data = {
            "kod": "SK0101",
            "nazov": {"sk": "Okres Bratislava I"},
            "nadradenaLokacia": "SK010",
        }
        klasifikacia = Klasifikacia.model_validate(data)
        assert klasifikacia.nadradenaLokacia == "SK010"


class TestKlasifikacieResponse:
    """Tests for KlasifikacieResponse model."""

    def test_parse_list(self):
        """Test parsing classifier list response."""
        data = {
            "klasifikacie": [
                {"kod": "1", "nazov": {"sk": "Prvá"}},
                {"kod": "2", "nazov": {"sk": "Druhá"}},
            ]
        }
        response = KlasifikacieResponse.model_validate(data)
        assert len(response.klasifikacie) == 2
        assert response.klasifikacie[0].kod == "1"


class TestSablona:
    """Tests for Sablona (template) model."""

    def test_parse_basic(self):
        """Test parsing basic template."""
        data = {
            "id": 687,
            "nazov": "Úč POD",
            "nariadenieMF": "MF/15464/2013-74",
            "platneOd": "2014-01-01",
        }
        sablona = Sablona.model_validate(data)
        assert sablona.id == 687
        assert sablona.nazov == "Úč POD"
        assert sablona.nariadenieMF == "MF/15464/2013-74"

    def test_parse_with_tables(self):
        """Test parsing template with table definitions."""
        data = {
            "id": 687,
            "nazov": "Test",
            "tabulky": [
                {
                    "nazov": "Aktíva",
                    "hlavicka": [{"nazov": "Položka"}],
                    "riadky": [{"nazov": "Riadok 1", "kod": "001"}],
                }
            ],
        }
        sablona = Sablona.model_validate(data)
        assert len(sablona.tabulky) == 1
        assert sablona.tabulky[0].nazov == "Aktíva"


class TestUctovnaJednotka:
    """Tests for UctovnaJednotka (accounting unit) model."""

    def test_parse_full(self):
        """Test parsing full accounting unit data."""
        data = {
            "id": 1217556,
            "ico": "46792511",
            "dic": "2023579580",
            "nazovUJ": "freevision s. r. o.",
            "mesto": "Bratislava",
            "ulica": "Dunajská 8",
            "psc": "81108",
            "datumZalozenia": "2012-08-17",
            "pravnaForma": "112",
            "skNace": "62090",
            "konsolidovana": False,
            "idUctovnychZavierok": [1, 2, 3],
            "zdrojDat": "SUSR",
        }
        uj = UctovnaJednotka.model_validate(data)
        assert uj.id == 1217556
        assert uj.ico == "46792511"
        assert uj.nazovUJ == "freevision s. r. o."
        assert len(uj.idUctovnychZavierok) == 3

    def test_parse_minimal(self):
        """Test parsing minimal accounting unit (deleted record)."""
        data = {"id": 1, "stav": "ZMAZANÉ"}
        uj = UctovnaJednotka.model_validate(data)
        assert uj.id == 1
        assert uj.stav == StavZaznamu.ZMAZANE
        assert uj.nazovUJ is None


class TestUctovnaZavierka:
    """Tests for UctovnaZavierka (accounting closure) model."""

    def test_parse_full(self):
        """Test parsing full accounting closure data."""
        data = {
            "id": 6028050,
            "obdobieOd": "2023-01",
            "obdobieDo": "2023-12",
            "datumPodania": "2024-06-27",
            "typ": "Riadna",
            "idUJ": 1217556,
            "konsolidovana": False,
            "idUctovnychVykazov": [9166748],
        }
        zavierka = UctovnaZavierka.model_validate(data)
        assert zavierka.id == 6028050
        assert zavierka.obdobieOd == "2023-01"
        assert zavierka.typ == TypZavierky.RIADNA
        assert len(zavierka.idUctovnychVykazov) == 1


class TestUctovnyVykaz:
    """Tests for UctovnyVykaz (financial report) model."""

    def test_parse_basic(self):
        """Test parsing basic financial report."""
        data = {
            "id": 9166748,
            "idUctovnejZavierky": 6028050,
            "idSablony": 687,
            "pristupnostDat": "Verejné",
        }
        vykaz = UctovnyVykaz.model_validate(data)
        assert vykaz.id == 9166748
        assert vykaz.idSablony == 687
        assert vykaz.pristupnostDat == PristupnostDat.VEREJNE

    def test_parse_with_content(self):
        """Test parsing financial report with content."""
        data = {
            "id": 1,
            "obsah": {
                "titulnaStrana": {"nazov": "Test Company", "ico": "12345678"},
                "tabulky": [
                    {"nazov": {"sk": "Aktíva", "en": "Assets"}, "data": ["100", "200"]},
                ],
            },
        }
        vykaz = UctovnyVykaz.model_validate(data)
        assert vykaz.obsah is not None
        assert vykaz.obsah.titulnaStrana.nazov == "Test Company"
        assert len(vykaz.obsah.tabulky) == 1
        assert vykaz.obsah.tabulky[0].nazov.sk == "Aktíva"


class TestVyrocnaSprava:
    """Tests for VyrocnaSprava (annual report) model."""

    def test_parse_full(self):
        """Test parsing full annual report."""
        data = {
            "id": 12345,
            "nazovUJ": "Test Company",
            "typ": "Individuálna výročná správa",
            "obdobieOd": "2023-01",
            "obdobieDo": "2023-12",
            "pristupnostDat": "Verejné",
            "idUJ": 1217556,
        }
        sprava = VyrocnaSprava.model_validate(data)
        assert sprava.id == 12345
        assert sprava.typ == TypVyrocnejSpravy.INDIVIDUALNA_VYROCNA_SPRAVA


class TestPriloha:
    """Tests for Priloha (attachment) model."""

    def test_parse_full(self):
        """Test parsing full attachment data."""
        data = {
            "id": 123,
            "meno": "document.pdf",
            "mimeType": "application/pdf",
            "velkostPrilohy": 1024,
            "pocetStran": 10,
            "digest": "abc123",
            "jazyk": "sk",
        }
        priloha = Priloha.model_validate(data)
        assert priloha.id == 123
        assert priloha.meno == "document.pdf"
        assert priloha.mimeType == "application/pdf"
        assert priloha.velkostPrilohy == 1024


class TestTabulkaData:
    """Tests for TabulkaData model."""

    def test_parse_with_localized_name(self):
        """Test parsing table with localized name."""
        data = {
            "nazov": {"sk": "Aktíva", "en": "Assets"},
            "data": ["100", "200", "300"],
        }
        tabulka = TabulkaData.model_validate(data)
        assert tabulka.nazov.sk == "Aktíva"
        assert len(tabulka.data) == 3

    def test_parse_with_string_name(self):
        """Test parsing table with string name."""
        data = {"nazov": "Simple Name", "data": ["100"]}
        tabulka = TabulkaData.model_validate(data)
        assert tabulka.nazov == "Simple Name"
