# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : Doomlad
# Date    : 2023-07-05
# Edit    : 2023-07-05
# License : BSD-3-Clause


from datetime import datetime
from opgg.season import Season
from opgg.league_stats import LeagueStats
from opgg.champion_stats import ChampionStats
from opgg.game import Game


class Summoner:
    def __init__(self,
                 id: int,
                 summoner_id: str,
                 acct_id: str,
                 puuid: str,
                 name: str,
                 internal_name: str,
                 profile_image_url: str,
                 level: int,
                 updated_at: datetime,
                 renewable_at: datetime,
                 previous_seasons: Season | list[Season],
                 league_stats: LeagueStats | list[LeagueStats],
                 most_champions: list[ChampionStats], 
                 recent_game_stats: Game | list[Game]) -> None:
        self._id = id
        self._summoner_id = summoner_id
        self._acct_id = acct_id
        self._puuid = puuid
        self._name = name
        self._internal_name = internal_name
        self._profile_image_url = profile_image_url
        self._level = level
        self._updated_at = updated_at
        self._renewable_at = renewable_at
        self._previous_seasons = previous_seasons
        self._league_stats = league_stats
        # TODO: Inevitably, implement the Champion class & lookup logic. These come in as IDs...
        self._most_champions = most_champions  
        self._recent_game_stats = recent_game_stats
        
    @property
    def id(self) -> int:
        return self._id
    
    @id.setter
    def id(self, value: int) -> None:
        self._id = value
        
    @property
    def summoner_id(self) -> str:
        return self._summoner_id
    
    @summoner_id.setter
    def summoner_id(self, value: str) -> None:
        self._summoner_id = value
        
    @property
    def acct_id(self) -> str:
        return self._acct_id
    
    @acct_id.setter
    def acct_id(self, value: str) -> None:
        self._acct_id = value
        
    @property
    def puuid(self) -> str:
        return self._puuid
    
    @puuid.setter
    def puuid(self, value: str) -> None:
        self._puuid = value
        
    @property
    def name(self) -> str:
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        self._name = value
        
    @property
    def internal_name(self) -> str:
        return self._internal_name
    
    @internal_name.setter
    def internal_name(self, value: str) -> None:
        self._internal_name = value
        
    @property
    def profile_image_url(self) -> str:
        return self._profile_image_url
    
    @profile_image_url.setter
    def profile_image_url(self, value: str) -> None:
        self._profile_image_url = value
        
    @property
    def level(self) -> int:
        return self._level
    
    @level.setter
    def level(self, value: int) -> None:
        self._level = value
        
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    @updated_at.setter
    def updated_at(self, value: datetime) -> None:
        self._updated_at = value
        
    @property
    def renewable_at(self) -> datetime:
        return self._renewable_at
    
    @renewable_at.setter
    def renewable_at(self, value: datetime) -> None:
        self._renewable_at = value
        
    @property
    def previous_seasons(self) -> Season | list[Season]:
        return self._previous_seasons
      
    @previous_seasons.setter
    def previous_seasons(self, value: Season | list[Season]) -> None:
        self._previous_seasons = value
        
    @property
    def league_stats(self) -> LeagueStats | list[LeagueStats]:
        return self._league_stats
    
    @league_stats.setter
    def league_stats(self, value: LeagueStats | list[LeagueStats]) -> None:
        self._league_stats = value
        
    @property
    def most_champions(self) -> list[ChampionStats]:
        return self._most_champions
    
    @most_champions.setter
    def most_champions(self, value: list[ChampionStats]) -> None:
        self._most_champions = value
        
    @property
    def recent_game_stats(self) -> Game | list[Game]:
        return self._recent_game_stats
    
    @recent_game_stats.setter
    def recent_game_stats(self, value: Game | list[Game]) -> None:
        self._recent_game_stats = value

    def __repr__(self) -> str:
        return  f"[Summoner]\n" \
                f"Id: {self.id}\n" \
                f"Summoner Id: {self.summoner_id}\n" \
                f"Account Id: {self.acct_id}\n" \
                f"Puuid: {self.puuid}\n" \
                f"Name: {self.name}\n" \
                f"Internal Name: {self.internal_name}\n" \
                f"Profile Image Url: {self.profile_image_url}\n" \
                f"Level: {self.level}\n" \
                f"Updated At: {self.updated_at}\n" \
                f"Renewable At: {self.renewable_at}\n" \
                f"Previous Seasons: {self.previous_seasons}\n" \
                f"League Stats: {self.league_stats}\n" \
                f"Most Champions: {self.most_champions}\n" \
                f"Recent Game Stats: {self.recent_game_stats}\n"