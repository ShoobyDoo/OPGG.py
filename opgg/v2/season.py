from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl


class QueueInfo(BaseModel):
    id: int
    queue_translate: str
    game_type: str


class TierInfo(BaseModel):
    tier: Optional[str] = None
    division: Optional[int] = None
    lp: Optional[int] = None
    level: Optional[int] = None
    tier_image_url: HttpUrl
    border_image_url: Optional[HttpUrl] = None


class League(BaseModel):
    game_type: str
    tier_info: TierInfo
    win: Optional[int] = None
    lose: Optional[int] = None
    is_hot_streak: bool = False
    is_fresh_blood: bool = False
    is_veteran: bool = False
    is_inactive: bool = False
    series: Optional[dict] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class RankInfo(BaseModel):
    """Basic rank information."""

    tier: str
    division: int
    lp: int


class RankEntry(BaseModel):
    """Entry containing rank information for a specific game type."""

    game_type: str
    rank_info: RankInfo
    created_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class Season(BaseModel):
    """Represents a League season."""

    season_id: int
    tier_info: TierInfo
    # Make created_at optional since API doesn't always include it
    created_at: Optional[datetime] = None

    class Config:
        """Pydantic model configuration."""

        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat()}
