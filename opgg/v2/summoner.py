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

    def get_summary(self) -> str:
        """Return the summary string of the summoner."""

        # left/right just factor
        LJF = 18
        RJF = 14

        previous_seasons_fmt, league_stats_fmt, champion_stats_fmt = "", "", ""

        if self.previous_seasons:
            for season in self.previous_seasons:
                previous_seasons_fmt += f"{''.ljust(LJF+RJF)}  | {season}\n"

        if self.league_stats:
            for league_stat in self.league_stats:
                league_stats_fmt += f"{''.ljust(LJF+RJF)}  | {league_stat}\n"

        if self.most_champions.champion_stats:
            for champ_stat in self.most_champions.champion_stats:
                champion_stats_fmt += f"{''.ljust(LJF+RJF)}  | {champ_stat}\n"

        return (
            f"[Summoner: {self.game_name}]\n{'-' * 80}\n"
            f"{'Id'.ljust(LJF)} {'(int)'.rjust(RJF)} | {self.id}\n"
            f"{'Summoner Id'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.summoner_id}\n"
            f"{'Account Id'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.acct_id}\n"
            f"{'Puuid'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.puuid}\n"
            f"{'Game Name'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.game_name}\n"
            f"{'Tagline'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.tagline}\n"
            f"{'Name'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.name}\n"
            f"{'Internal Name'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.internal_name}\n"
            f"{'Profile Image Url'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.profile_image_url}\n"
            f"{'Level'.ljust(LJF)} {'(int)'.rjust(RJF)} | {self.level}\n"
            f"{'Updated At'.ljust(LJF)} {'(datetime)'.rjust(RJF)} | {self.updated_at}\n"
            f"{'Renewable At'.ljust(LJF)} {'(datetime)'.rjust(RJF)} | {self.renewable_at}\n"
            f"{'Previous Seasons'.ljust(LJF)} {'(Season)'.rjust(RJF)} | [List ({len(self.previous_seasons) if self.previous_seasons else 0})] \n{previous_seasons_fmt}"
            f"{'League Stats'.ljust(LJF)} {'(LeagueStats)'.rjust(RJF)} | [List ({len(self.league_stats) if self.league_stats else 0})] \n{league_stats_fmt}"
            f"{'Most Champions'.ljust(LJF)} {'(ChampStats)'.rjust(RJF)} | [List ({len(self.most_champions.champion_stats) if self.most_champions.champion_stats else 0})] \n{champion_stats_fmt}"
        )
