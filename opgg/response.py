from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator
import logging

from opgg.game import LiveGame

logger = logging.getLogger("OPGG.py")


class UpdateData(BaseModel):
    """Data returned from an update request."""

    message: Optional[str] = None
    """Status message from the update operation."""

    last_updated_at: Optional[datetime] = None
    """When the profile was last updated."""

    renewable_at: Optional[datetime] = None
    """When the profile can be updated again."""

    finish: Optional[bool] = None
    """Whether the update operation completed."""

    delay: Optional[int] = None
    """Delay in seconds before next allowed update."""

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in UpdateData model")
        return v

    class Config:
        """Pydantic model configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class UpdateResponse(BaseModel):
    """Response from an update request."""

    status: Optional[int] = None
    """HTTP status code of the response."""

    data: Optional[UpdateData] = None
    """The update operation data."""

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in UpdateResponse model")
        return v


class LiveGameResponse(BaseModel):
    """Response from a live game request."""

    data: Optional[LiveGame] = None
    """The live game data, if available."""

    status: Optional[int] = None
    """HTTP status code of the response."""

    message: Optional[str] = None
    """Status message from the request."""

    detail: Optional[str] = None
    """Additional details about the request."""

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(
                f"Field '{info.field_name}' is None in LiveGameResponse model"
            )
        return v
