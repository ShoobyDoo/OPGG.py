from datetime import datetime
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_serializer,
)

from opgg.season import League, Season, TierInfo
from opgg.champion import MostChampions


class Summoner(BaseModel):
    """Represents a League of Legends summoner."""

    # Base summoner attributes
    id: int | None = None
    """The internal OPGG id."""

    summoner_id: str | None = None
    """The summoner ID."""

    acct_id: str | None = None
    """The account ID used by Riot's API."""

    puuid: str | None = None
    """The PUUID (`P`layer `U`niversally `U`nique `ID`entifier)."""

    game_name: str | None = None
    """The summoner's display name."""

    tagline: str | None = None
    """The summoner's tagline (e.g. NA1, EUW)."""

    name: str | None = None
    """The summoner's previous name before Riot ID system."""

    internal_name: str | None = None
    """OPGG's internal name format (lowercase, no spaces)."""

    profile_image_url: HttpUrl | None = None
    """URL to the summoner's profile icon image."""

    level: int | None = None
    """The summoner's current level."""

    updated_at: datetime | None = None
    """When the summoner's data was last updated."""

    renewable_at: datetime | None = None
    """When the summoner's data can be updated again."""

    revision_at: datetime | None = None
    """When the summoner's data was last revised."""

    # Search result specific attributes
    solo_tier_info: TierInfo | None = None
    """Solo tier ranking information."""

    team_info: dict | None = None
    """Team information."""

    # Full profile specific attributes
    previous_seasons: list[Season] | None = Field(default_factory=list)
    """Previous season information."""

    league_stats: list[League] | None = Field(default_factory=list)
    """League statistics."""

    most_champions: MostChampions | None = None
    """Most played champions."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_serializer("updated_at", "renewable_at", "revision_at")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        return value.isoformat() if value else None

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
