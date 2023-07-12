# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : Doomlad
# Date    : 2023-07-05
# Edit    : 2023-07-05
# License : BSD-3-Clause


from opgg.queue_info import QueueInfo
from datetime import datetime


class Tier:
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
        return self._tier
    
    @tier.setter
    def tier(self, value: str) -> None:
        self._tier = value
    
    @property
    def division(self) -> int:
        return self._division
    
    @division.setter
    def division(self, value: int) -> None:
        self._division = value
        
    @property
    def lp(self) -> int:
        return self._lp
    
    @lp.setter
    def lp(self, value: int) -> None:
        self._lp = value
        
    @property
    def tier_image_url(self) -> str:
        return self._tier_image_url
    
    @tier_image_url.setter
    def tier_image_url(self, value: str) -> None:
        self._tier_image_url = value
        
    @property
    def border_image_url(self) -> str:
        return self._border_image_url 
     
    @border_image_url.setter 
    def border_image_url(self, value: str) -> None:
        self._border_image_url = value


class LeagueStats:
    def __init__(self,
                 queue_info: QueueInfo,
                 tier_info: Tier,
                 win: int,
                 lose: int,
                 is_hot_streak: bool,
                 is_fresh_blood: bool,
                 is_veteran: bool,
                 is_inactive: bool,
                 series,
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
        return self._queue_info
    
    @queue_info.setter
    def queue_info(self, value: QueueInfo) -> None:
        self._queue_info = value
        
    @property
    def tier_info(self) -> Tier:
        return self._tier_info
    
    @tier_info.setter
    def tier_info(self, value: Tier) -> None: 
        self._tier_info = value
        
    @property
    def win(self) -> int:
        return self._win
    
    @win.setter
    def win(self, value: int) -> None:
        self._win = value
        
    @property
    def lose(self) -> int:
        return self._lose
    
    @lose.setter
    def lose(self, value: int) -> None:
        self._lose = value
        
    @property
    def is_hot_streak(self) -> bool:
        return self._is_hot_streak
    
    @is_hot_streak.setter
    def is_hot_streak(self, value: bool) -> None:
        self._is_hot_streak = value
        
    @property
    def is_fresh_blood(self) -> bool:
        return self._is_fresh_blood
    
    @is_fresh_blood.setter
    def is_fresh_blood(self, value: bool) -> None:
        self._is_fresh_blood = value
        
    @property
    def is_veteran(self) -> bool:
        return self._is_veteran
    
    @is_veteran.setter
    def is_veteran(self, value: bool) -> None:
        self._is_veteran = value
        
    @property
    def is_inactive(self) -> bool:
        return self._is_inactive
     
    @is_inactive.setter
    def is_inactive(self, value: bool) -> None:
        self._is_inactive = value
        
    @property
    def series(self):
        return self._series
     
    @series.setter
    def series(self, value) -> None:
        self._series = value
        
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    @updated_at.setter
    def updated_at(self, value: datetime) -> None:
        self._updated_at = value