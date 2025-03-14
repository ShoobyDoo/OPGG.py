from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, field_validator
import logging

logger = logging.getLogger("OPGG.py")


class QueueInfo(BaseModel):
    id: Optional[int] = None
    queue_translate: Optional[str] = None
    game_type: Optional[str] = None

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in QueueInfo model")
        return v


class TierInfo(BaseModel):
    tier: Optional[str] = None
    division: Optional[int] = None
    lp: Optional[int] = None
    level: Optional[int] = None
    tier_image_url: Optional[HttpUrl] = None
    border_image_url: Optional[HttpUrl] = None

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in TierInfo model")
        return v


class League(BaseModel):
    game_type: Optional[str] = None
    tier_info: Optional[TierInfo] = None
    win: Optional[int] = None
    lose: Optional[int] = None
    is_hot_streak: Optional[bool] = False
    is_fresh_blood: Optional[bool] = False
    is_veteran: Optional[bool] = False
    is_inactive: Optional[bool] = False
    series: Optional[dict] = None
    updated_at: Optional[datetime] = None

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in League model")
        return v

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class RankInfo(BaseModel):
    """Basic rank information."""

    tier: Optional[str] = None
    division: Optional[int] = None
    lp: Optional[int] = None

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in RankInfo model")
        return v


class RankEntry(BaseModel):
    """Entry containing rank information for a specific game type."""

    game_type: str
    rank_info: RankInfo
    created_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class Season(BaseModel):
    """Represents a League season."""

    season_id: Optional[int] = None
    tier_info: Optional[TierInfo] = None
    created_at: Optional[datetime] = None

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in Season model")
        return v

    class Config:
        """Pydantic model configuration."""

        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat()}
