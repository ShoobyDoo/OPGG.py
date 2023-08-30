# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : ShoobyDoo
# Date    : 2023-07-05
# License : BSD-3-Clause

from datetime import datetime
from opgg.league_stats import Tier


class Season:
    """
    Represents a season.
    
    ### Properties:
        `season_id` - Season id\n
        `tier_info` - Tier info\n
        `created_at` - When the season was created
    """
    def __init__(self,
                 season_id: int,
                 tier_info: Tier,
                 created_at: datetime) -> None:
        self._season_id = season_id
        self._tier_info = tier_info
        self._created_at = created_at
        
    @property
    def season_id(self) -> int:
        """
        An `int` representing the season id
        """
        return self._season_id
    
    @season_id.setter
    def season_id(self, value: int) -> None:
        self._season_id = value
        
    @property
    def tier_info(self) -> Tier:
        """
        A `Tier` object representing the tier info
        """
        return self._tier_info
    
    @tier_info.setter
    def tier_info(self, value: Tier) -> None:
        self._tier_info = value
        
    @property
    def created_at(self) -> datetime:
        """
        A `datetime` object representing when the season was created
        """
        return self._created_at
     
    @created_at.setter
    def created_at(self, value: datetime) -> None:
        self._created_at = value
    
    def __repr__(self) -> str:
        return f"Season(season={self._season_id}, tier_info={self._tier_info})"
    

class SeasonInfo:
    """
    Represents a season's info.
    
    ### Attributes
        -> id: `int`\n
        -> value: `int`\n
        -> display_value: `int`\n
        -> is_preseason: `bool`
    """
    
    def __init__(self,
                 id: int,
                 value: int,
                 display_value: int,
                 is_preseason: bool) -> None:
        self._id = id
        self._value = value
        self._display_value = display_value
        self._is_preseason = is_preseason
    
    @property
    def id(self) -> int:
        """
        An `int` representing the season id
        """
        return self._id
    
    @property
    def value(self) -> int:
        """
        An `int` representing the season value
        """
        return self._value
    
    @property
    def display_value(self) -> int:
        """
        An `int` representing the season display value
        """
        return self._display_value
    
    @property
    def is_preseason(self) -> bool:
        """
        A `bool` representing if the season is preseason
        """
        return self._is_preseason

    def __repr__(self) -> str:
        return f"SeasonInfo(display_value={self._display_value}, is_preseason={self._is_preseason})"