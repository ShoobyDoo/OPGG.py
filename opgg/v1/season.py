# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : ShoobyDoo
# Date    : 2023-07-05
# License : BSD-3-Clause

from datetime import datetime
from opgg.v1.league_stats import Tier


class RankEntry:
    """
    Represents a rank entry.
    
    ### Properties:
        `game_type: str` - The type of game associated with the rank entry\n
        `rank_info: Tier` - Information about the tier of the rank entry\n
        `created_at: datetime` - Timestamp of when the rank entry was created\n
    """
    def __init__(self,
                 game_type: str,
                 rank_info: Tier,
                 created_at: datetime) -> None:
        self._game_type = game_type
        self._rank_info = rank_info
        self._created_at = created_at
    
    @property
    def game_type(self) -> str:
        """
        A `str` representing the game type (Solo, Flex, etc.)
        """
        return self._game_type
    
    @property
    def rank_info(self) -> Tier:
        """
        A `Tier` object representing the ranked information for a given queue
        """
        return self._rank_info
    
    @property
    def created_at(self) -> datetime:
        """
        A `datetime` object representing when the rank was created (?)\n
        Unclear what this date represents.
        """
        return self._created_at
    

class Season:
    """
    Represents a season.
    
    ### Properties:
        `season_id: int` - Unique identifier for the season\n
        `tier_info: Tier` - Information about the tier of the season\n
        `rank_entries: list[RankEntry]` - List of rank entries for the season\n
        `created_at: datetime` - Timestamp of when the season was created\n
    """
    def __init__(self,
                 season_id: int,
                 tier_info: Tier,
                 rank_entries: list[RankEntry],
                 created_at: datetime) -> None:
        self._season_id = season_id
        self._tier_info = tier_info
        self._rank_entries = rank_entries
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
    def rank_entries(self) -> list[RankEntry]:
        """
        A `list[RankEntry]` objects containing rank entries for a given season
        """
        return self._rank_entries
    
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
    Represents information about a specific season.\n
    
    ### Properties:
        `id: int` - Unique identifier for the season\n
        `value: int` - Numerical value associated with the season\n
        `display_value: int` - The actual display value\n
        `split: int` - Split information relevant to the season\n
        `is_preseason: bool` - Indicator whether the season is in the preseason\n
    """
    
    def __init__(self,
                 id: int,
                 value: int,
                 display_value: int,
                 split: int,
                 is_preseason: bool) -> None:
        self._id = id
        self._value = value
        self._display_value = display_value
        self._split = split
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
    def split(self) -> int:
        """
        An `int` representing the split in a given season
        """
        return self._split
    
    @property
    def is_preseason(self) -> bool:
        """
        A `bool` representing if the season is preseason
        """
        return self._is_preseason

    def __repr__(self) -> str:
        return f"SeasonInfo(display_value={self._display_value}, is_preseason={self._is_preseason})"