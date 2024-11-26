from typing import Any, Optional
from box import Box

from opgg.v2.league import League
from opgg.v2.season import Season
from opgg.v2.champion import MostChampions


class Summoner(Box):
    """
    Represents a League of Legends summoner.
    Can be instantiated from either search results or full profile data.
    """

    # Base summoner attributes (common to both search and profile)
    id: int
    summoner_id: str
    acct_id: str
    puuid: str
    game_name: str
    tagline: str
    name: str
    internal_name: str
    profile_image_url: str
    level: int
    updated_at: str  # TODO: datetime object conversion?
    renewable_at: str  # TODO: datetime object conversion?
    revision_at: str  # TODO: datetime object conversion?

    # Search result specific attributes
    solo_tier_info: Optional[Any]  # unsure of type...
    team_info: Optional[Any]

    # Full profile specific attributes
    previous_seasons: Optional[list[Season]]
    league_stats: Optional[list[League]]
    most_champions: Optional[MostChampions]

    @property
    def is_full_profile(self) -> bool:
        """
        `[Computed Property]` Check if this instance contains full profile data.

        Returns:
            `bool`: True if this is a full profile, False if it's just a search result
        """
        return all(
            [
                self.previous_seasons is not None,
                self.league_stats is not None,
                self.most_champions is not None,
            ]
        )
