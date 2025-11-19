from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl, field_validator
import logging

from opgg.season import League, Season, TierInfo
from opgg.champion import MostChampions

logger = logging.getLogger("OPGG.py")


class Summoner(BaseModel):
    """Represents a League of Legends summoner."""

    # Base summoner attributes
    id: Optional[int] = None
    """The internal OPGG id."""

    summoner_id: Optional[str] = None
    """The summoner ID."""

    acct_id: Optional[str] = None
    """The account ID used by Riot's API."""

    puuid: Optional[str] = None
    """The PUUID (`P`layer `U`niversally `U`nique `ID`entifier)."""

    game_name: Optional[str] = None
    """The summoner's display name."""

    tagline: Optional[str] = None
    """The summoner's tagline (e.g. NA1, EUW)."""

    name: Optional[str] = None
    """The summoner's previous name before Riot ID system."""

    internal_name: Optional[str] = None
    """OPGG's internal name format (lowercase, no spaces)."""

    profile_image_url: Optional[HttpUrl] = None
    """URL to the summoner's profile icon image."""

    level: Optional[int] = None
    """The summoner's current level."""

    updated_at: Optional[datetime] = None
    """When the summoner's data was last updated."""

    renewable_at: Optional[datetime] = None
    """When the summoner's data can be updated again."""

    revision_at: Optional[datetime] = None
    """When the summoner's data was last revised."""

    # Search result specific attributes
    solo_tier_info: Optional[TierInfo] = None
    """Solo tier ranking information."""

    team_info: Optional[dict] = None
    """Team information."""

    # Full profile specific attributes
    previous_seasons: Optional[list[Season]] = Field(default_factory=list)
    """Previous season information."""

    league_stats: Optional[list[League]] = Field(default_factory=list)
    """League statistics."""

    most_champions: Optional[MostChampions] = None
    """Most played champions."""

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in Summoner model")
        return v

    class Config:
        """Pydantic model configuration."""

        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat()}

    @property
    def is_full_profile(self) -> bool:
        """Check if this instance contains full profile data."""
        return all(
            [
                self.previous_seasons is not None,
                self.league_stats is not None,
                self.most_champions is not None,
            ]
        )
