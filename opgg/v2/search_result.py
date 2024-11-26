from box import Box
from typing import Any

from opgg.v2.params import Region
from opgg.v2.summoner import Summoner


class SearchResult(Box):
    """
    #### Represents a search result from the OPGG API.

    ##### Properties:
        `region`: The region of the summoner.
        `summoner`: The summoner result.
    """

    region: Region
    summoner: Summoner

    def __str__(self):
        return f"[{str(self.region):4}] {f'{self.summoner.game_name} #{self.summoner.tagline}':<25} | Level: {self.summoner.level:<4} [Summoner ID: {self.summoner.summoner_id}]"
