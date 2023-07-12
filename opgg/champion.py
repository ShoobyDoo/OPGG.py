# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : Doomlad
# Date    : 2023-07-05
# Edit    : 2023-07-09
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

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def image_url(self) -> str:
        return self._image_url
    
    @property
    def video_url(self) -> str:
        return self._video_url
    

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

    @property
    def key(self) -> str:
        return self._key
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def max_rank(self) -> int:
        return self._max_rank
    
    @property
    def range_burn(self) -> list:
        return self._range_burn
    
    @property
    def cooldown_burn(self) -> list:
        return self._cooldown_burn
    
    @property
    def cost_burn(self) -> list:
        return self._cost_burn
    
    @property
    def tooltip(self) -> str:
        return self._tooltip
    
    @property
    def image_url(self) -> str:
        return self._image_url
    
    @property
    def video_url(self) -> str:
        return self._video_url
    
    def __repr__(self) -> str:
        return f"Skill({self.key}: {self.name})"


class Price:
    def __init__(self,
                 currency: str,
                 cost: int) -> None:
        self._currency = currency
        self._cost = cost
    
    @property
    def currency(self) -> str:
        return self._currency
    
    @property
    def cost(self) -> int:
        return self._cost
    
    def __repr__(self) -> str:
        return f"Price({self.currency}: {self.cost})"

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
    
    @property
    def id(self) -> int:
        return self._id
     
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def centered_image(self) -> str:
        return self._centered_image
     
    @property
    def skin_video_url(self) -> str:
        return self._skin_video_url
    
    @property
    def prices(self) -> list[Price]:
        return self._prices
    
    @property
    def sales(self) -> list:
        return self._sales         
    
    def __repr__(self) -> str:
        return f"Skin({self.name})"

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
        
    @property
    def id(self) -> int:
        return self._id
     
    @property
    def key(self) -> str:
        return self._key
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def image_url(self) -> str:
        return self._image_url
    
    @property
    def evolve(self) -> list:
        return self._evolve
    
    @property
    def passive(self) -> Passive:
        return self._passive
    
    @property
    def spells(self) -> list[Spell]:
        return self._spells
    
    @property
    def skins(self) -> list[Skin]:
        return self._skins

    def get_cost_in(self, metric = "BE") -> int | None:
        # Get the cost of the champion in either blue essence or riot points
        metric = "IP" if metric == "BE" else metric.upper()
        
        for skin in self.skins:
            if skin.prices is not None:
                for price in skin.prices:
                    if price.currency == metric:
                        return price.cost
            else:
                return None
        
        
    def __repr__(self) -> str:
        return f"Champion(id={self.id}, name={self.name}, cost_be={self.get_cost_in()}, cost_rp={self.get_cost_in('rp')})"