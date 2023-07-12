# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : Doomlad
# Date    : 2023-07-05
# Edit    : 2023-07-09
# License : BSD-3-Clause

from datetime import datetime
from opgg.tier import Tier


class Season:
    def __init__(self,
                 season_id: int,
                 tier_info: Tier,
                 created_at: datetime) -> None:
        self._season_id = season_id
        self._tier_info = tier_info
        self._created_at = created_at
        
    @property
    def season_id(self) -> int: 
        return self._season_id
    
    @season_id.setter
    def season_id(self, value: int) -> None:
        self._season_id = value
        
    @property
    def tier_info(self) -> Tier:
        return self._tier_info
    
    @tier_info.setter
    def tier_info(self, value: Tier) -> None:
        self._tier_info = value
        
    @property
    def created_at(self) -> datetime:
        return self._created_at
     
    @created_at.setter
    def created_at(self, value: datetime) -> None:
        self._created_at = value