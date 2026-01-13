from pydantic import BaseModel, ConfigDict

from opgg.params import Region
from opgg.summoner import Summoner


class SearchResult(BaseModel):
    """
    #### Represents a search result from the OPGG API.

    ##### Properties:
        `region`: The region of the summoner.
        `summoner`: The summoner result.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    region: Region
    summoner: Summoner

    def __str__(self):
        return f"[{str(self.region):4}] {f'{self.summoner.game_name} #{self.summoner.tagline}':<25} | Level: {str(self.summoner.level):<4} [Summoner ID: {self.summoner.summoner_id}]"
