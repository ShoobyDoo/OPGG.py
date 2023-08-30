# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : ShoobyDoo
# Date    : 2023-07-05
# License : BSD-3-Clause

from datetime import datetime


class Tier:
    """
    Represents a tier in a league.
    
    ### Properties:
        `tier` - Tier name\n
        `division` - Division number\n
        `lp` - League points\n
        `tier_image_url` - URL to the tier image\n
        `border_image_url` - URL to the border image\n
    """
    def __init__(self,
                 tier: str,
                 division: int,
                 lp: int,
                 tier_image_url: str,
                 border_image_url: str) -> None:
        self._tier = tier
        self._division = division
        self._lp = lp
        self._tier_image_url = tier_image_url
        self._border_image_url = border_image_url
        
    @property
    def tier(self) -> str:
        """
        A `str` representing the tier (e.g. "Silver")
        """
        return self._tier
    
    @tier.setter
    def tier(self, value: str) -> None:
        self._tier = value
    
    @property
    def division(self) -> int:
        """
        An `int` representing the division
        """
        return self._division
    
    @division.setter
    def division(self, value: int) -> None:
        self._division = value
        
    @property
    def lp(self) -> int:
        """
        An `int` representing the league points
        """
        return self._lp
    
    @lp.setter
    def lp(self, value: int) -> None:
        self._lp = value
        
    @property
    def tier_image_url(self) -> str:
        """
        A `str` representing the URL to the tier image
        """
        return self._tier_image_url
    
    @tier_image_url.setter
    def tier_image_url(self, value: str) -> None:
        self._tier_image_url = value
        
    @property
    def border_image_url(self) -> str:
        """
        A `str` representing the URL to the border image
        """
        return self._border_image_url 
     
    @border_image_url.setter 
    def border_image_url(self, value: str) -> None:
        self._border_image_url = value

    def __repr__(self) -> str:
        return f"Tier(tier={self._tier}, division={self._division}, lp={self._lp})"
    

class QueueInfo:
    """
    Represents a queue in a league.
    
    ### Properties:
        `id` - Queue ID\n
        `queue_translate` - Game type in KOREAN\n
        `game_type` - Queue/Game type\n
    """
    def __init__(self,
                 id: int,
                 queue_translate: str,
                 game_type: str) -> None:
        self._id = id
        self._queue_translate = queue_translate
        self._game_type = game_type
        
    @property
    def id(self) -> int:
        """
        An `int` representing the queue ID
        """
        return self._id
     
    @id.setter
    def id(self, value: int) -> None:
        self._id = value
        
    @property
    def queue_translate(self) -> str:
        """
        A `str` representing the queue/game type in KOREAN
        """
        return self._queue_translate
    
    @queue_translate.setter
    def queue_translate(self, value: str) -> None:
        self._queue_translate = value
        
    @property
    def game_type(self) -> str:
        """
        A `str` representing the queue/game type
        """
        return self._game_type
    
    @game_type.setter
    def game_type(self, value: str) -> None:
        self._game_type = value
    
    def __repr__(self) -> str:
        return f"QueueInfo(game_type={self.game_type})"


class LeagueStats:
    """
    Represents a users league stats.
    
    ### Properties:
        `queue_info` - QueueInfo object\n
        `tier_info` - Tier object\n
        `win` - Number of wins\n
        `lose` - Number of losses\n
        `is_hot_streak` - Whether or not the user is on a hot streak (3+ winstreak)\n
        `is_fresh_blood` - Whether or not the user is fresh blood\n
        `is_veteran` - Whether or not the user is a veteran\n
        `is_inactive` - Whether or not the user is inactive\n
        `series` - Series object\n
        `updated_at` - Datetime object representing the last time the stats were updated\n
    """
    def __init__(self,
                 queue_info: QueueInfo,
                 tier_info: Tier,
                 win: int,
                 lose: int,
                 is_hot_streak: bool,
                 is_fresh_blood: bool,
                 is_veteran: bool,
                 is_inactive: bool,
                 series: bool,
                 updated_at: datetime) -> None:
        self._queue_info = queue_info
        self._tier_info = tier_info
        self._win = win
        self._lose = lose
        self._is_hot_streak = is_hot_streak
        self._is_fresh_blood = is_fresh_blood 
        self._is_veteran = is_veteran 
        self._is_inactive = is_inactive 
        self._series = series 
        self._updated_at = updated_at 
    
    @property
    def queue_info(self) -> QueueInfo:
        """
        A `QueueInfo` object representing the queue
        """
        return self._queue_info
    
    @queue_info.setter
    def queue_info(self, value: QueueInfo) -> None:
        self._queue_info = value
        
    @property
    def tier_info(self) -> Tier:
        """
        A `Tier` object representing the tier
        """
        return self._tier_info
    
    @tier_info.setter
    def tier_info(self, value: Tier) -> None: 
        self._tier_info = value
        
    @property
    def win(self) -> int:
        """
        An `int` representing the number of wins
        """
        return self._win
    
    @win.setter
    def win(self, value: int) -> None:
        self._win = value
        
    @property
    def lose(self) -> int:
        """
        An `int` representing the number of losses
        """
        return self._lose
    
    @lose.setter
    def lose(self, value: int) -> None:
        self._lose = value
        
    @property
    def is_hot_streak(self) -> bool:
        """
        A `bool` representing whether or not the user is on a hot streak (3+ winstreak)
        """
        return self._is_hot_streak
    
    @is_hot_streak.setter
    def is_hot_streak(self, value: bool) -> None:
        self._is_hot_streak = value
        
    @property
    def is_fresh_blood(self) -> bool:
        """
        A `bool` representing whether or not the user is fresh blood
        """
        return self._is_fresh_blood
    
    @is_fresh_blood.setter
    def is_fresh_blood(self, value: bool) -> None:
        self._is_fresh_blood = value
        
    @property
    def is_veteran(self) -> bool:
        """
        A `bool` representing whether or not the user is a veteran
        """
        return self._is_veteran
    
    @is_veteran.setter
    def is_veteran(self, value: bool) -> None:
        self._is_veteran = value
        
    @property
    def is_inactive(self) -> bool:
        """
        A `bool` representing whether or not the user is inactive
        """
        return self._is_inactive
     
    @is_inactive.setter
    def is_inactive(self, value: bool) -> None:
        self._is_inactive = value
        
    @property
    def series(self) -> bool:
        """
        A `bool` representing if the summoner is in a series
        """
        return self._series
     
    @series.setter
    def series(self, value) -> None:
        self._series = value
        
    @property
    def updated_at(self) -> datetime:
        """
        A `datetime` object representing the last time the stats were updated
        """
        return self._updated_at
    
    @updated_at.setter
    def updated_at(self, value: datetime) -> None:
        self._updated_at = value
    
    @property
    def win_rate(self) -> float | None:
        """
        A `float` representing the win rate of the champion.
        """
        if self._win and self._lose:
            return round(float((self._win / (self._win + self._lose)) * 100), 2) if (self._win + self._lose) != 0 else 0
        return None
    
    
    def __repr__(self) -> str:
        return f"LeagueStats(queue_info={self.queue_info}, tier_info={self.tier_info}, win={self.win} / lose={self.lose} (winrate: {self.win_rate}%))"