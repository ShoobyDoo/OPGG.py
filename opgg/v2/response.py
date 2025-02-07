from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from opgg.v2.game import LiveGame


class UpdateData(BaseModel):
    """Data returned from an update request."""

    message: str
    """Status message from the update operation."""

    last_updated_at: datetime
    """When the profile was last updated."""

    renewable_at: Optional[datetime] = None
    """When the profile can be updated again."""

    finish: Optional[bool] = None
    """Whether the update operation completed."""

    delay: Optional[int] = None
    """Delay in seconds before next allowed update."""

    class Config:
        """Pydantic model configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class UpdateResponse(BaseModel):
    """Response from an update request."""

    status: int
    """HTTP status code of the response."""

    data: UpdateData
    """The update operation data."""


class LiveGameResponse(BaseModel):
    """Response from a live game request."""

    data: Optional[LiveGame] = None
    """The live game data, if available."""

    status: int
    """HTTP status code of the response."""

    message: str
    """Status message from the request."""

    detail: Optional[str] = None
    """Additional details about the request."""
