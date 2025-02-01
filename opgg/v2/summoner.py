from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl

from opgg.v2.season import League, Season, TierInfo
from opgg.v2.champion import MostChampions


class Summoner(BaseModel):
    """Represents a League of Legends summoner."""

    # Base summoner attributes
    id: int
    """The internal OPGG id."""

    summoner_id: str
    """The summoner ID."""

    acct_id: str
    """The account ID used by Riot's API."""

    puuid: str
    """The PUUID (`P`layer `U`niversally `U`nique `ID`entifier)."""

    game_name: str
    """The summoner's display name."""

    tagline: str
    """The summoner's tagline (e.g. NA1, EUW)."""

    name: str
    """The summoner's previous name before Riot ID system."""

    internal_name: str
    """OPGG's internal name format (lowercase, no spaces)."""

    profile_image_url: HttpUrl
    """URL to the summoner's profile icon image."""

    level: int
    """The summoner's current level."""

    updated_at: datetime
    """When the summoner's data was last updated."""

    renewable_at: datetime
    """When the summoner's data can be updated again."""

    revision_at: datetime
    """When the summoner's data was last revised."""

    # Search result specific attributes
    solo_tier_info: Optional[TierInfo] = Field(default=None)
    """Solo tier ranking information."""

    team_info: Optional[dict] = Field(default=None)
    """Team information."""

    # Full profile specific attributes
    previous_seasons: Optional[list[Season]] = Field(default=None)
    """Previous season information."""

    league_stats: Optional[list[League]] = Field(default=None)
    """League statistics."""

    most_champions: Optional[MostChampions] = Field(default=None)
    """Most played champions."""

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
