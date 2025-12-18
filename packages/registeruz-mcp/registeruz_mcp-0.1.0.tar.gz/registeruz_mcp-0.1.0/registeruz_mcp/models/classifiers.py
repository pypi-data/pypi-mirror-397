"""Classifier models."""

from pydantic import BaseModel, Field, model_validator


class LocalizedName(BaseModel):
    """Localized name with Slovak and English variants."""

    sk: str | None = Field(default=None, description="Slovak name")
    en: str | None = Field(default=None, description="English name")


class Klasifikacia(BaseModel):
    """Generic classifier item."""

    kod: str = Field(description="Classification code")
    nazov: LocalizedName = Field(description="Localized name")
    nadradenaLokacia: str | None = Field(
        default=None,
        description="Parent location code (for regions/districts/settlements)",
    )


class KlasifikacieResponse(BaseModel):
    """Response for classifier endpoints.

    Note: The API returns 'klasifikacie' for most classifiers but 'lokacie'
    for geographical data (regions, districts, settlements). This model
    normalizes both to 'klasifikacie'.
    """

    klasifikacie: list[Klasifikacia] = Field(
        default_factory=list, description="List of classifications"
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_field_name(cls, data: dict) -> dict:
        """Normalize 'lokacie' field to 'klasifikacie'."""
        if isinstance(data, dict) and "lokacie" in data and "klasifikacie" not in data:
            data["klasifikacie"] = data.pop("lokacie")
        return data
