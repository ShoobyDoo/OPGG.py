# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : Doomlad
# Date    : 2023-07-05
# Edit    : 2023-07-05
# License : BSD-3-Clause

import json
import requests
from bs4 import BeautifulSoup

from opgg.summoner import Summoner
from opgg.season import Season, SeasonInfo
from opgg.champion import ChampionStats, Champion, Spell, Passive, Skin, Price
from opgg.league_stats import LeagueStats, Tier
from opgg.game import Game
from opgg.queue_info import QueueInfo
from opgg.params import Regions, By


__version__ = '1.0.0'
__author__ = 'Doomlad'
__license__ = 'BSD-3-Clause'


class OPGG:
    cached_page_props = None
    
    
    def __init__(self, summoner_id: str, region = "NA") -> None:
        self._summoner_id = summoner_id
        self._region = region
        self._api_url = f"https://op.gg/api/v1.0/internal/bypass/summoners/{self.region}/{self.summoner_id}/summary"
        self._headers = { "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36" }
        self._all_champions = None
        self._all_seasons = None
    
    @property
    def summoner_id(self) -> str:
        return self._summoner_id
    
    @summoner_id.setter
    def summoner_id(self, value: str) -> None:
        self._summoner_id = value
        self.refresh_api_url()
        
    @property
    def region(self) -> str:
        return self._region
    
    @region.setter
    def region(self, value: str) -> None:
        self._region = value
        self.refresh_api_url()
        
    @property
    def api_url(self) -> str:
        return self._api_url
    
    @api_url.setter
    def api_url(self, value: str) -> None:
        self._api_url = value
    
    @property
    def headers(self) -> dict:
        return self._headers
    
    @headers.setter
    def headers(self, value: dict) -> None:
        self._headers = value
    
    @property
    def all_champions(self) -> list[Champion]:
        return self._all_champions
    
    @all_champions.setter
    def all_champions(self, value: list[Champion]) -> None:
        self._all_champions = value
    
    @property
    def all_seasons(self) -> list[Season]:
        return self._all_seasons
    
    @all_seasons.setter
    def all_seasons(self, value: list[Season]) -> None:
        self._all_seasons = value
    
    def refresh_api_url(self) -> None:
        # update api url with new region
        self._api_url = f"https://op.gg/api/v1.0/internal/bypass/summoners/{self.region}/{self.summoner_id}/summary"
    
    def get_summoner(self) -> Summoner:
        req = requests.get(self.api_url, headers=self.headers)
        if req.status_code == 200:
            content = json.loads(req.text)["data"]
            
            previous_seasons: list[Season] = []
            league_stats: list[LeagueStats] = []
            most_champions: list[ChampionStats] = []
            recent_game_stats: list[Game] = []
            
            try:
                for season in content["summoner"]["previous_seasons"]:
                    previous_seasons.append(Season(
                        season_id = season["season_id"],
                        tier_info = Tier(
                            tier = season["tier_info"]["tier"],
                            division = season["tier_info"]["division"],
                            lp = season["tier_info"]["lp"],
                            tier_image_url = season["tier_info"]["tier_image_url"],
                            border_image_url = season["tier_info"]["border_image_url"]
                        ),
                        created_at = season["created_at"]
                    ))
                
                for league in content["summoner"]["league_stats"]:
                    league_stats.append(LeagueStats(
                        queue_info = QueueInfo(
                            id = league["queue_info"]["id"],
                            queue_translate = league["queue_info"]["queue_translate"],
                            game_type = league["queue_info"]["game_type"]
                        ),
                        tier_info = Tier(
                            tier = league["tier_info"]["tier"],
                            division = league["tier_info"]["division"],
                            lp = league["tier_info"]["lp"],
                            tier_image_url = league["tier_info"]["tier_image_url"],
                            border_image_url = league["tier_info"]["border_image_url"]
                        ),
                        win = league["win"],
                        lose = league["lose"],
                        is_hot_streak = league["is_hot_streak"],
                        is_fresh_blood = league["is_fresh_blood"],
                        is_veteran = league["is_veteran"],
                        is_inactive = league["is_inactive"],
                        series = league["series"],
                        updated_at = league["updated_at"]
                    ))
                
                for champion in content["summoner"]["most_champions"]["champion_stats"]:
                    most_champions.append(ChampionStats(
                        id = champion["id"],
                        play = champion["play"],
                        win = champion["win"],
                        lose = champion["lose"],
                        kill = champion["kill"],
                        death = champion["death"],
                        assist = champion["assist"],
                        gold_earned = champion["gold_earned"],
                        minion_kill = champion["minion_kill"],
                        turret_kill = champion["turret_kill"],
                        neutral_minion_kill = champion["neutral_minion_kill"],
                        damage_dealt = champion["damage_dealt"],
                        damage_taken = champion["damage_taken"],
                        physical_damage_dealt = champion["physical_damage_dealt"],
                        magic_damage_dealt = champion["magic_damage_dealt"],
                        most_kill = champion["most_kill"],
                        max_kill = champion["max_kill"],
                        max_death = champion["max_death"],
                        double_kill = champion["double_kill"],
                        triple_kill = champion["triple_kill"],
                        quadra_kill = champion["quadra_kill"],
                        penta_kill = champion["penta_kill"],
                        game_length_second = champion["game_length_second"]
                    ))
                
                for game in content["recent_game_stats"]:
                    recent_game_stats.append(Game(
                        game_id = game["game_id"],
                        champion_id = game["champion_id"],
                        kill = game["kill"],
                        death = game["death"],
                        assist = game["assist"],
                        position = game["position"],
                        is_win = game["is_win"],
                        is_remake = game["is_remake"],
                        op_score = game["op_score"],
                        op_score_rank = game["op_score_rank"],
                        is_opscore_max_in_team = game["is_opscore_max_in_team"],
                        created_at = game["created_at"]
                    ))
            except Exception as e:
                pass
            
            
            return Summoner(
                id = content["summoner"]["id"],
                summoner_id = content["summoner"]["summoner_id"],
                acct_id = content["summoner"]["acct_id"],
                puuid = content["summoner"]["puuid"],
                name = content["summoner"]["name"],
                internal_name = content["summoner"]["internal_name"],
                profile_image_url = content["summoner"]["profile_image_url"],
                level = content["summoner"]["level"],
                updated_at = content["summoner"]["updated_at"],
                renewable_at = content["summoner"]["renewable_at"],
                previous_seasons = previous_seasons,
                league_stats = league_stats,
                most_champions = most_champions,
                recent_game_stats = recent_game_stats
            )
            
        else:
            req.raise_for_status()

    @staticmethod
    def get_page_props(summoner_names: str | list[str] = "Doomlad", region = "NA") -> dict:
        """
        Search multiple summoners at once.
        
        Parameters
        ----------
        `summoner_names : str | list[str]`
            Pass a comma separated string or a list of summoner names.
        `region : str`
            Pass a region. Default is "NA".

        Returns
        -------
        dict
            Returns a dictionary with the page props.
        """
        if isinstance(summoner_names, list): summoner_names = ",".join(summoner_names)
        
        url = f"https://op.gg/multisearch/{region}?summoners={summoner_names}"
        headers = { "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36" }

        req = requests.get(url, headers=headers)
        soup = BeautifulSoup(req.content, "html.parser")
        
        return json.loads(soup.select_one("#__NEXT_DATA__").text)['props']['pageProps']
    
    @staticmethod
    def multi_search(summoner_names: str | list[str], region = "NA") -> list[str]:

        if OPGG.cached_page_props:
            opgg_data = OPGG.cached_page_props
        else:
            opgg_data = OPGG.get_page_props(summoner_names, region)
            OPGG.cached_page_props = opgg_data
            
        ids = []
        for id in opgg_data['summoners']:
            ids.append(id["summoner_id"])
            
        return ids
    
    @staticmethod
    def get_all_seasons(region = "NA") -> list[SeasonInfo]:
        # TODO: Revisit this caching logic, pretty sure there's a better way to do this
        if OPGG.cached_page_props:
            opgg_data = OPGG.cached_page_props
        else:
            opgg_data = OPGG.get_page_props("Doomlad", region)
            OPGG.cached_page_props = opgg_data
        
        seasons = []
        for season in opgg_data['seasonsById']:
            seasons.append(SeasonInfo(
                id = season["id"],
                value = season["value"],
                display_value = season["display_value"],
                is_preseason = season["is_preseason"]
            )
        )
            
        return seasons

    @staticmethod
    def get_all_champions(region = Regions.NA) -> list[Champion]:
        # TODO: Revisit this caching logic, pretty sure there's a better way to do this
        if OPGG.cached_page_props:
            opgg_data = OPGG.cached_page_props
        else:
            # pass any username here, it doesnt matter.
            # we just need the page props, and we dont get them without a username
            opgg_data = OPGG.get_page_props(region)
            OPGG.cached_page_props = opgg_data
        
        champions = []
        
        for champion in dict(opgg_data["championsById"]).values():
            # reinit per iteration
            _spells = []
            _skins = []
            
            for skin in champion["skins"]:
                _prices = []
                
                if skin["prices"]:
                    for price in skin["prices"]:
                        _prices.append(Price(
                            currency = price["currency"] if "RP" in price["currency"] else "BE",
                            cost = price["cost"]
                        ))
                else:
                    _prices = None
                
                _skins.append(Skin(
                    id = skin["id"],
                    name = skin["name"],
                    centered_image = skin["centered_image"],
                    skin_video_url = skin["skin_video_url"],
                    prices = _prices,
                    sales = skin["sales"]
                ))
                    
            for spell in champion["spells"]:
                _spells.append(Spell(
                    key = spell["key"],
                    name = spell["name"],
                    description = spell["description"],
                    max_rank = spell["max_rank"],
                    range_burn = spell["range_burn"],
                    cooldown_burn = spell["cooldown_burn"],
                    cost_burn = spell["cost_burn"],
                    tooltip = spell["tooltip"],
                    image_url = spell["image_url"],
                    video_url = spell["video_url"]
                ))       
              
            champions.append(Champion(
                id = champion["id"],
                key = champion["key"],
                name = champion["name"],
                image_url = champion["image_url"],
                evolve = champion["evolve"],
                passive = Passive(
                    name = champion["passive"]["name"],
                    description = champion["passive"]["description"],
                    image_url = champion["passive"]["image_url"],
                    video_url = champion["passive"]["video_url"]
                ),
                spells = _spells,
                skins = _skins
            ))            
        
        return champions
    
    @staticmethod
    def get_champion_by(by: By, value: int | str | list, **kwargs) -> Champion | list[Champion]:
        all_champs = OPGG.get_all_champions()
        result_set = []
        
        if by == By.ID:
            if isinstance(value, list):
                for champ in all_champs:
                    for id in value:
                        if champ.id == id:
                            result_set.append(champ)
            else:
                for champ in all_champs:
                    if champ.id == int(value):
                        result_set.append(champ)
                
        elif by == By.KEY:
            if isinstance(value, list):
                for champ in all_champs:
                    for key in value:
                        if champ.key == key:
                            result_set.append(champ)
            else:
                for champ in all_champs:
                    if champ.key == value:
                        result_set.append(champ)
        
        elif by == By.NAME:
            if isinstance(value, list):
                for champ in all_champs:
                    for name in value:
                        if champ.name == name:
                            result_set.append(champ)
            else:
                for champ in all_champs:
                    if champ.name == value:
                        result_set.append(champ)
        
        elif by == By.COST:
                for champ in all_champs:
                    if champ.skins[0].prices:
                        for price in champ.skins[0].prices:
                            if str(kwargs["currency"]).upper() == price.currency and price.cost in value:
                                result_set.append(champ)
                
        return result_set