# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : Doomlad
# Date    : 2023-07-05
# Edit    : 2023-07-05
# License : BSD-3-Clause


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