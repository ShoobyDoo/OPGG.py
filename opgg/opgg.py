# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : ShoobyDoo
# Date    : 2023-07-05
# License : BSD-3-Clause

import os
import json
import logging
import requests
import traceback

from datetime import datetime
from typing import Literal
from fake_useragent import UserAgent

# from opgg.summoner import 
from opgg.season import Season, SeasonInfo
from opgg.champion import ChampionStats, Champion
from opgg.league_stats import LeagueStats, Tier, QueueInfo
from opgg.summoner import Game, Summoner
from opgg.params import Region
from opgg.cacher import Cacher
from opgg.utils import Utils


class OPGG:
    """
    ### OPGG.py
    A simple library to access and structure the data from OP.GG's Website & API.
    
    Copyright (c) 2023-2024, ShoobyDoo
    License: BSD-3-Clause, See LICENSE for more details.
    """
    
    __author__ = 'ShoobyDoo'
    __license__ = 'BSD-3-Clause'
    
    cached_page_props = None
    
    # Todo: Add support for the following endpoint(s):
    # https://op.gg/api/v1.0/internal/bypass/games/na/summoners/<summoner_id?>/?&limit=20&hl=en_US&game_type=total

    # METADATA FOR CHAMPIONS -- USE THIS OVER PAGE_PROPS.
    # https://op.gg/api/v1.0/internal/bypass/meta/champions?hl=en_US
    
    
    def __init__(self, summoner_id: str | None = None, region = Region.NA) -> None:
        self._summoner_id = summoner_id
        self._region = region
        
        self._base_api_url = "https://lol-web-api.op.gg/api/v1.0/internal/bypass"
        self._api_url = f"{self._base_api_url}/summoners/{self.region}/{self.summoner_id}/summary"
        self._games_api_url = f"{self._base_api_url}/games/{self.region}/summoners/{self.summoner_id}"
        
        self._ua = UserAgent()
        self._headers = { 
            "User-Agent": self._ua.random
        }
        
        self._all_champions = None
        self._all_seasons = None
        

        # ===== SETUP START =====
        logging.root.name = 'OPGG.py'

        if not os.path.exists('./logs'):
            logging.info("Creating logs directory...")
            os.mkdir('./logs')
        else:
            # remove empty log files
            for file in os.listdir('./logs'):
                if os.stat(f"./logs/{file}").st_size == 0 and file != f'opgg_{datetime.now().strftime("%Y-%m-%d")}.log':
                    logging.info(f"Removing empty log file: {file}")
                    os.remove(f"./logs/{file}")
                    
        logging.basicConfig(
            filename=f'./logs/opgg_{datetime.now().strftime("%Y-%m-%d")}.log',
            filemode='a+', 
            format='[%(asctime)s][%(name)s->%(module)-10s][%(levelname)-7s] : %(message)s', 
            datefmt='%d-%b-%y %H:%M:%S',
            level=logging.INFO
        )
        # ===== SETUP END =====
        
        # allow the user to interact with the logger
        self._logger = logging.getLogger("OPGG.py")
        
        # at object creation, setup and query the cache
        self._cacher = Cacher()
        self._cacher.setup()
        
        self.logger.info(
            f"OPGG.__init__(summoner_id={self.summoner_id}, " \
            f"region={self.region}, " \
            f"api_url={self.api_url}, " \
            f"headers={self.headers}, " \
            f"all_champions={self.all_champions}, " \
            f"all_seasons={self.all_seasons})"
        )
        
    
    @property
    def logger(self) -> logging.Logger:
        """
        A `Logger` object representing the logger instance.
        
        The logging level is set to `INFO` by default.
        """
        return self._logger
    
    @property
    def summoner_id(self) -> str:
        """
        A `str` representing the summoner id. (Riot API)
        """
        return self._summoner_id
    
    @summoner_id.setter
    def summoner_id(self, value: str) -> None:
        self._summoner_id = value
        self.refresh_api_url()
        
    @property
    def region(self) -> str:
        """
        A `str` representing the region to search in.
        """
        return self._region
    
    @region.setter
    def region(self, value: str) -> None:
        self._region = value
        self.refresh_api_url()
        
    @property
    def api_url(self) -> str:
        """
        A `str` representing the api url to send requests to. (OPGG API)
        """
        return self._api_url
    
    @api_url.setter
    def api_url(self, value: str) -> None:
        self._api_url = value
    
    @property
    def headers(self) -> dict:
        """
        A `dict` representing the headers to send with the request.
        """
        return self._headers
    
    @headers.setter
    def headers(self, value: dict) -> None:
        self._headers = value
    
    @property
    def all_champions(self) -> list[Champion]:
        """
        A `list[Champion]` objects representing all champions in the game.
        """
        return self._all_champions
    
    @all_champions.setter
    def all_champions(self, value: list[Champion]) -> None:
        self._all_champions = value
    
    @property
    def all_seasons(self) -> list[SeasonInfo]:
        """
        A `list[SeasonInfo]` objects representing all seasons in the game.
        """
        return self._all_seasons
    
    @all_seasons.setter
    def all_seasons(self, value: list[SeasonInfo]) -> None:
        self._all_seasons = value
    
    @property
    def cacher(self) -> Cacher:
        """
        A `Cacher` object representing the summoner_id cacher.
        """
        return self._cacher
    
    def refresh_api_url(self) -> None:
        """
        A method to refresh the api url with the current summoner id and region.
        """
        self.api_url = f"{self._base_api_url}/summoners/{self.region}/{self.summoner_id}/summary"
        self._games_api_url = f"{self._base_api_url}/games/{self.region}/summoners/{self.summoner_id}"
        
        self.logger.debug(f"self.refresh_api_url() called... See URLs:")
        self.logger.debug(f"self.api_url = {self.api_url}")
        self.logger.debug(f"self._games_api_url = {self._games_api_url}")
    
    
    def get_summoner(self, return_content_only = False) -> Summoner:
        """
        A method to get data from the OPGG API and form a Summoner object.
        
        General flow:\n
            -> Send request to OPGG API\n
            -> Parse data from request (jsonify)\n
            -> Loop through data and form the summoner object.
            
        ### Returns:
            `Summoner`: A Summoner object representing the summoner.
        """        
        self.logger.info(f"Sending request to OPGG API... (API_URL = {self.api_url}, HEADERS = {self.headers})")
        res = requests.get(self.api_url, headers=self.headers)
        
        previous_seasons: list[Season]      = []
        league_stats: list[LeagueStats]     = []
        most_champions: list[ChampionStats] = []
        recent_game_stats: list[Game]       = []
        
        if res.status_code == 200:
            self.logger.info(f"Request to OPGG API was successful, parsing data (Content Length: {len(res.text)})...")
            content = json.loads(res.text)["data"]
        else:
            res.raise_for_status()
        
        # If return_res is passed in func args, return the content
        # Required in tests to get all the raw content without building the summoner object
        if (return_content_only):
            return content
        
        try:            
            for season in content["summoner"]["previous_seasons"]:
                tmp_season_info = None
                if self.all_seasons:
                    for _season in self.all_seasons:
                        if _season.id == season["season_id"]:
                            tmp_season_info = _season
                            break
                
                previous_seasons.append(Season(
                    season_id = tmp_season_info,
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
                tmp_champ = None
                if self.all_champions:
                    for _champion in self.all_champions:
                        if _champion.id == champion["id"]:
                            tmp_champ = _champion
                            break
                
                most_champions.append(ChampionStats(
                    champion = tmp_champ,
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
            
            # page props did not return any recent games, lets query the /games endpoint instead
            # gets the summoner id from the objects internal self._game_api_url's self.summoner_id ref
            recent_game_stats: Game | list[Game] = self.get_recent_games()
                
                
        except Exception:
            self.logger.error(f"Error parsing some summoner data... (Could be that they just come in as nulls...): {traceback.format_exc()}")
            pass
        
        
        return Summoner(
            id = content["summoner"]["id"],
            summoner_id = content["summoner"]["summoner_id"],
            acct_id = content["summoner"]["acct_id"],
            puuid = content["summoner"]["puuid"],
            game_name = content["summoner"]["game_name"],
            tagline = content["summoner"]["tagline"],
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
    
    
    def search(self, summoner_names: str | list[str], region = Region.NA) -> Summoner | list[Summoner] | str:
        """
        Search for a single or multiple summoner(s) on OPGG.

        ### Args:
            summoner_names : `str` | `list[str]`
                Pass either a `str` (comma seperated) or `list[str]` of summoner names + regional identifier (#NA1, #EUW, etc).
                
            region : `Region, optional`
                Pass the region you want to search in. Defaults to "NA".

        ### Returns:
            `list[Summoner]` | `str` : A single or list of Summoner objects, or a string if no summoner(s) were found.
        """

        if isinstance(summoner_names, str) and "," in summoner_names:
            summoner_names = summoner_names.split(",")
        elif isinstance(summoner_names, str):
            summoner_names = [summoner_names]
            
        # General flow of cache retrieval:
        # 1. Pull from cache db
        #   -> If found, add to list of cached summoner ids, and below iterate over and set the summoner id property
        #   -> As an extension of the above, these requests would go directly to the api to pull summary/full data
        #   -> If not found, add to list of summoner names to query
        # 2. Build the summoner objects accordingly
        cached_summoner_ids = []
        uncached_summoners = []
        
        # TODO: Cache get/set logic needs to be reworked to account for regional identifiers. Currently, you could have 2 of the same users on different regions and the cache will just return whatever the first entry that was cached would've been. This is not ideal, perhaps I should force people to append the regional identifiers? This would result in unique entries in the cache...
        for summoner_name in summoner_names:
            if ('#' not in summoner_name):
                raise Exception(f"No regional identifier was found for query: \"{summoner_name}\". Please include the identifier as well and try again. (#NA1, #EUW, etc.)")
            cached_id = self.cacher.get_summoner_id(summoner_name)
            if cached_id:
                cached_summoner_ids.append(cached_id)
            else:
                uncached_summoners.append(summoner_name)
        
        # pass only uncached summoners to get_page_props()
        page_props = Utils.get_page_props(uncached_summoners, region)
        OPGG.cached_page_props = page_props
        
        self.logger.debug(f"\n********PAGE_PROPS_START********\n{page_props}\n********PAGE_PROPS_STOP********")
        
        if len(uncached_summoners) > 0:
            self.logger.info(f"No cache for {len(uncached_summoners)} summoners: {uncached_summoners}, fetching... (using get_page_props() site scraper)")
        if len(cached_summoner_ids) > 0:
            self.logger.info(f"Cache found for {len(cached_summoner_ids)} summoners: {cached_summoner_ids}, fetching... (using get_summoner() api)")
            
        # these cross reference the page prop season/champ ids to build out season/champ objects
        # todo: build this into caching system
        # todo: metric for when you cache vs not, each run get length of seasons/champs, if they changed, update cache.
        cached_seasons = self.cacher.get_all_seasons()
        cached_champions = self.cacher.get_all_champs()
        
        # If we found some cached seasons/champs, use them, otherwise fetch and cache them.
        if cached_seasons:
            self.all_seasons = cached_seasons
        else:
            self.all_seasons = self.get_all_seasons(self.region, page_props)
            self.cacher.insert_all_seasons(self.all_seasons)
            
        if cached_champions:
            self.all_champions = cached_champions
        else:
            self.all_champions = self.get_all_champions(self.region, page_props)
            self.cacher.insert_all_champs(self.all_champions)
        
        # todo: if more than 5 summoners are passed, break into 5s and iterate over each set
        # note: this would require calls to the refresh_api_url() method each iteration?
        
        # set the region to the passed one. this is what get_summoner() relies on
        self.region = region
        
        # bit of weirdness around generic usernames. If you pass "abc" for example, it will return multiple summoners in the page props.
        # To help, we will check against opgg's "internal_name" property, which seems to be the username.lower() with spaces removed.        
        summoners = []
        for summoner_name in summoner_names:
            # if there are multiple search results for a SINGLE summoner_name, query MUST include the regional identifier
            if (len(page_props["summoners"]) > 1 and '#' in summoner_name):
                logging.debug(f"MULTI-RESULT | page_props->summoners: {page_props['summoners']}")
                only_summoner_name, only_region = summoner_name.split("#")
                for summoner in page_props["summoners"]:
                    if (only_summoner_name.strip() == summoner["game_name"] and only_region.strip() == summoner["tagline"]):
                        self.summoner_id = summoner["summoner_id"]
                        break
            
            elif (len(page_props["summoners"]) > 1 and '#' not in summoner_name):
                raise Exception(f"Multiple search results were returned for \"{summoner_name}\". Please include the identifier as well and try again. (#NA1, #EUW, etc.)")

            elif (len(page_props["summoners"]) == 1):
                self.summoner_id = page_props["summoners"][0]["summoner_id"]
            
            summoner = self.get_summoner()
            summoners.append(summoner)
            self.logger.info(f"Summoner object built for: {summoner.name} ({summoner.summoner_id}), caching...")
            self.cacher.insert_summoner(summoner.name, summoner.summoner_id)
            
        # cached summoners go straight to api
        for _cached_summoner_id in cached_summoner_ids:
            self.summoner_id = _cached_summoner_id
            summoner = self.get_summoner()
            summoners.append(summoner)
            self.logger.info(f"Summoner object built for: {summoner.name} ({summoner.summoner_id})")
        
        # todo: add custom exceptions instead of this.
        # todo: raise SummonerNotFound exception
        if len(summoners) == 0: 
            raise Exception(f"No summoner(s) matching {summoner_names} were found...")
        
        return summoners if len(summoners) > 1 else summoners[0]

    
    def get_recent_games(self, results: int = 10, game_type: Literal["total", "ranked", "normal"] = "total", return_content_only = False) -> list[Game]:
        recent_games = []
        res = requests.get(f"{self._games_api_url}?&limit={results}&game_type={game_type}", headers=self.headers)
        
        if res.status_code == 200:
            self.logger.info(f"Request to OPGG GAME_API was successful, parsing data (Content Length: {len(res.text)})...")
            game_data = json.loads(res.text)["data"]
        else:
            res.raise_for_status()
        
        if return_content_only:
            return game_data
        
        try:
            for game in game_data:
                tmp_game = Game(
                    id = game["id"],
                    champion = next((champion for champion in self.all_champions if champion.id == game["myData"]["champion_id"]), None),
                    kill = int(game["myData"]["stats"]["kill"]),
                    death = int(game["myData"]["stats"]["death"]),
                    assist = int(game["myData"]["stats"]["assist"]),
                    position = game["myData"]["position"],
                    is_win = game["myData"]["stats"]["result"] == "WIN",
                    is_remake = game["is_remake"],
                    op_score = float(game["myData"]["stats"]["op_score"]),
                    op_score_rank = int(game["myData"]["stats"]["op_score_rank"]),
                    is_opscore_max_in_team = game["myData"]["stats"]["is_opscore_max_in_team"],
                    created_at = datetime.strptime(game["created_at"], r"%Y-%m-%dT%H:%M:%S%z")
                )
                recent_games.append(tmp_game)
                
            return recent_games
        
        except:
            self.logger.error(f"Unable to create game object, see trace: \n{traceback.format_exc()}")
            pass
    

    