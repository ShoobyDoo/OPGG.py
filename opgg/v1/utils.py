# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : ShoobyDoo
# Date    : 2024-07-10
# License : BSD-3-Clause

from datetime import datetime
import json
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

from opgg.v1.cacher import Cacher
from opgg.v1.champion import Champion, Passive, Price, Skin, Spell
from opgg.v1.params import By, Region
from opgg.v1.season import SeasonInfo


class Utils:
    """
    ### utils.py
    A collection of static utility helper methods that perform various opgg and league specific tasks such as fetching champions, seasons, etc.\n
    
    Copyright (c) 2023-2024, ShoobyDoo
    License: BSD-3-Clause, See LICENSE for more details.
    """
    
    _base_api_url = "https://lol-web-api.op.gg/api/v1.0/internal/bypass"
    _api_url = f"{_base_api_url}/summoners/{{region}}/{{summoner_id}}/renewal"
    
    ua = UserAgent()
    headers = { 
        "User-Agent": ua.random
    }
    
    @staticmethod
    def update(summoner_id: str, region: Region = Region.NA) -> dict:
        """
        Send an update request to fetch the latest details for a given summoner (id).
        
        ### Parameters
            summoner_id : `str`
                Pass a summoner id as a string to be updated
            
            region : `Region, optional`
                Pass the region you want to perform the update in. Default is "NA".

        ### Returns
            `dict` : Returns a dictionary with the status response.
                Example response:
            ```
            {
                'status': 202, 
                'data': {
                    'message': 'Already renewed.', 
                    'last_updated_at': '2024-07-13T10:06:11+09:00', 
                    'renewable_at': '2024-07-13T10:08:12+09:00'
                }
            }
            ```
        """
        
        res = requests.post(
            Utils._api_url.format(region=region, summoner_id=summoner_id), 
            headers=Utils.headers
        )
        
        if res.status_code in [201, 202]:
            return res.json()
        else:
            res.raise_for_status()
    
    
    @staticmethod
    def get_page_props(summoner_names: str | list[str] = "ColbyFaulkn1", region = Region.NA) -> dict:
        """
        Get the page props from OPGG. (Contains data such as summoner info, champions, seasons, etc.)
        
        ### Parameters
            summoner_names : `str | list[str], optional`
                Pass a single or comma separated `str` or a list of summoner names.\n
                Note: Default is "abc", as this can be any valid summoner if you just want page props. (All champs, seasons, etc.)
            
            region : `Region, optional`
                Pass the region you want to search in. Default is "NA".

        ### Returns
            `dict` : Returns a dictionary with the page props.
        """
        
        if isinstance(summoner_names, list) and len(summoner_names) > 0: 
            summoner_names = ",".join(summoner_names)
        
        url = f"https://www.op.gg/multisearch/{region}?summoners={summoner_names}"

        res = requests.get(url, headers=Utils.headers, allow_redirects=True)
        soup = BeautifulSoup(res.content, "html.parser")
        
        return json.loads(soup.select_one("#__NEXT_DATA__").text)['props']['pageProps']
    
    
    @staticmethod
    def get_all_seasons(region = Region.NA, page_props = None) -> list[SeasonInfo]:
        """
        Get all seasons from OPGG.

        ### Args:
            region : `Region, optional`
                Pass the region you want to search in. Defaults to "NA".
                
            page_props : `dict, optional`
                Pass the page props if the program has queried them once before.\n
                Note: Defaults to None, but if you pass them it reduces the overhead of another request out to OPGG.

        ### Returns:
            `list[SeasonInfo]` : A list of SeasonInfo objects.
        """
        # Check cache, if found, return it, otherwise continue to below logic.
        cached_seasons = Cacher().get_all_seasons()
        if cached_seasons:
            return cached_seasons
        
        seasons = []
        
        # For seasons specifically, if page_props is not passed, we MUST use it.
        # I have not been able to find a seasons endpoint on the api yet.
        if page_props == None:
            page_props = Utils.get_page_props()
        
        for season in dict(page_props['seasonsById']).values():
            seasons.append(SeasonInfo(
                id = season["id"],
                value = season["value"],
                display_value = season["display_value"],
                split = season["split"],
                is_preseason = season["is_preseason"]
            ))
        
        return seasons


    @staticmethod
    def get_season_by(by: By, value: int | str | list) -> SeasonInfo | list[SeasonInfo]:
        """
        Get a season by a specific metric.
        
        ### Args:
            by : `By`
                Pass a By enum to specify how you want to get the season(s).
            
            value : `int | str | list`
                Pass the value(s) you want to search by. (id, display_value, etc.)
        
        ### Returns:
            `SeasonInfo | list[SeasonInfo]` : A single or list of SeasonInfo objects.
        """
        all_seasons = Utils.get_all_seasons()
        result_set = []
        
        if by == By.ID:
            if isinstance(value, list):
                for season in all_seasons:
                    for id in value:
                        if season.id == id:
                            result_set.append(season)
            else:
                for season in all_seasons:
                    if season.id == int(value):
                        result_set.append(season)
        
        # TODO: perhaps add more ways to get season objs, like by is_preseason, or display_name, etc.           
        
        return result_set if len(result_set) > 1 else result_set[0]
    
    
    @staticmethod
    def get_all_champions(region = Region.NA, page_props = None) -> list[Champion]:
        """
        Get all champion info from OPGG.

        ### Args:
            region : `Region, optional`
                Pass the region you want to search in. Defaults to "NA".
                
            page_props : `dict, optional`
                Pass the page props if the program has queried them once before.\n
                Note: Defaults to None, but if you pass them it reduces the overhead of another request out to OPGG.

        Returns:
            `list[Champion]` : A list of Champion objects.
        """
        # Check cache, if found, return it, otherwise continue to below logic.        
        champions = []
        
        if not page_props:
            cached_champions = Cacher().get_all_champs()
            if cached_champions: 
                return cached_champions
            
            res = requests.get(f"{Utils._base_api_url}/meta/champions?hl=en_US", headers=Utils.headers)
            raw_champs_data = json.loads(res.text)["data"]
            
        else:
            raw_champs_data = dict(page_props['championsById']).values()
        
        for champion in raw_champs_data:
            # reset per iteration
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
                    champion_id = skin["champion_id"],
                    name = skin["name"],
                    centered_image = skin["centered_image"],
                    skin_video_url = skin["skin_video_url"],
                    prices = _prices,
                    release_date = datetime.fromisoformat(skin["release_date"]) if skin["release_date"] else None,
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
                    cooldown_burn_float = spell["cooldown_burn_float"],
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
                partype = champion["partype"],
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
        """
        Get a single or list of champions by a specific metric.
        
        ### Args:
            by : `By`
                Pass a By enum to specify how you want to get the champion(s).
                
            value : `int | str | list`
                Pass the value(s) you want to search by. (id, key, name, etc.)
                
            **kwargs : `any`
                Pass any additional keyword arguments to narrow down the search.\n
                Note: Currently only supports "currency" for the cost of a champion.\n
                
                Example: 
                    `get_champion_by(By.COST, 450, currency=By.BLUE_ESSENCE)`
        """
        # Currently kwargs only handles "currency" for the cost of a champion,
        # but I might introduce other metrics of getting champ objs later, idk...
        
        if ("page_props" in kwargs):
            all_champs = Utils.get_all_champions(page_props=kwargs["page_props"])
        else:
            all_champs = Utils.get_all_champions()
        
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
                
        
        # if the result set is larger than one, return the whole list, otherwise just return the object itself.
        return result_set if len(result_set) > 1 else result_set[0]