"""Response models for list and count endpoints."""

from pydantic import BaseModel, Field


class IdListResponse(BaseModel):
    """Response for list endpoints returning IDs."""

    id: list[int] = Field(default_factory=list, description="List of entity IDs")
    existujeDalsieId: bool = Field(
        default=False, description="Whether more IDs exist for pagination"
    )


class ZostavajuceIdResponse(BaseModel):
    """Response for remaining IDs count endpoints."""

    pocetZostavajucichId: int = Field(description="Count of remaining IDs")
