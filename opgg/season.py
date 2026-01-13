from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl, field_serializer


class QueueInfo(BaseModel):
    id: int | None = None
    queue_translate: str | None = None
    game_type: str | None = None


class TierInfo(BaseModel):
    tier: str | None = None
    division: int | None = None
    lp: int | None = None
    level: int | None = None
    tier_image_url: HttpUrl | None = None
    border_image_url: HttpUrl | None = None


class League(BaseModel):
    game_type: str | None = None
    tier_info: TierInfo | None = None
    win: int | None = None
    lose: int | None = None
    is_hot_streak: bool | None = False
    is_fresh_blood: bool | None = False
    is_veteran: bool | None = False
    is_inactive: bool | None = False
    series: dict | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict()

    @field_serializer("updated_at")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        return value.isoformat() if value else None


class RankInfo(BaseModel):
    """Basic rank information."""

    tier: str | None = None
    division: int | None = None
    lp: int | None = None


class RankEntry(BaseModel):
    """Entry containing rank information for a specific game type."""

    game_type: str
    rank_info: RankInfo
    created_at: datetime

    model_config = ConfigDict()

    @field_serializer("created_at")
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()


class SeasonMeta(BaseModel):
    """Metadata describing a season returned from the /meta/seasons endpoint."""

    id: int | None = None
    value: int | None = None
    display_value: int | str | None = None
    split: int | None = None
    season: int | None = None
    is_preseason: bool | None = None


class Season(BaseModel):
    """Represents a League season."""

    season_id: int | None = None
    tier_info: TierInfo | None = None
    created_at: datetime | None = None
    meta: SeasonMeta | None = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_serializer("created_at")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        return value.isoformat() if value else None
