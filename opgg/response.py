from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_serializer

from opgg.game import LiveGame


class UpdateData(BaseModel):
    """Data returned from an update request."""

    message: str | None = None
    """Status message from the update operation."""

    last_updated_at: datetime | None = None
    """When the profile was last updated."""

    renewable_at: datetime | None = None
    """When the profile can be updated again."""

    finish: bool | None = None
    """Whether the update operation completed."""

    delay: int | None = None
    """Delay in seconds before next allowed update."""

    model_config = ConfigDict()

    @field_serializer("last_updated_at", "renewable_at")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        return value.isoformat() if value else None


class UpdateResponse(BaseModel):
    """Response from an update request."""

    status: int | None = None
    """HTTP status code of the response."""

    data: UpdateData | None = None
    """The update operation data."""


class LiveGameResponse(BaseModel):
    """Response from a live game request."""

    data: LiveGame | None = None
    """The live game data, if available."""

    status: int | None = None
    """HTTP status code of the response."""

    message: str | None = None
    """Status message from the request."""

    detail: str | None = None
    """Additional details about the request."""
