# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : Doomlad
# Date    : 2023-07-05
# Edit    : 2023-07-05
# License : BSD-3-Clause


class Passive:
    def __init__(self,
                 name: str,
                 description: str,
                 image_url: str,
                 video_url: str) -> None:
        self._name = name
        self._description = description 
        self._image_url = image_url
        self._video_url = video_url


class Spell:
    def __init__(self,
                 key: str,
                 name: str,
                 description: str,
                 max_rank: int,
                 range_burn: list,
                 cooldown_burn: list,
                 cost_burn: list,
                 tooltip: str,
                 image_url: str,
                 video_url: str) -> None:
        self._key = key
        self._name = name
        self._description = description
        self._max_rank = max_rank
        self._range_burn = range_burn
        self._cooldown_burn = cooldown_burn
        self._cost_burn = cost_burn
        self._tooltip = tooltip
        self._image_url = image_url
        self._video_url = video_url


class Price:
    def __init__(self,
                 currency: str,
                 cost: int) -> None:
        self._currency = currency
        self._cost = cost

class Skin:
    def __init__(self,
                 id: int,
                 name: str,
                 centered_image: str,
                 skin_video_url: str, 
                 prices: list[Price],
                 sales = None) -> None:
        self._id = id
        self._name = name
        self._centered_image = centered_image 
        self._skin_video_url = skin_video_url 
        self._prices = prices 
        self._sales = sales
        

class Champion:
    def __init__(self,
                 id: int,
                 key: str,
                 name: str,
                 image_url: str,
                 evolve: list,
                 passive: Passive,
                 spells: list[Spell],
                 skins: list[Skin]) -> None:
        self._id = id
        self._key = key
        self._name = name
        self._image_url = image_url
        self._evolve = evolve
        self._passive = passive
        self._spells = spells
        self._skins = skins
        
