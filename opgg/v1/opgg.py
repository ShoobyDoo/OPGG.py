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
from opgg.v1.game import GameStats, Stats, Team
from opgg.v1.season import RankEntry, Season, SeasonInfo
from opgg.v1.champion import ChampionStats, Champion
from opgg.v1.league_stats import LeagueStats, Tier, QueueInfo
from opgg.v1.summoner import Game, Participant, Summoner
from opgg.v1.params import Region
from opgg.v1.cacher import Cacher
from opgg.v1.utils import Utils

from warnings import warn


class OPGG:
    """
    ### OPGG.py (v1)
    A simple library to access and structure the data from OP.GG's Website & API.

    Copyright (c) 2023-2024, ShoobyDoo
    License: BSD-3-Clause, See LICENSE for more details.

    ---
    #### Deprecation Notice

    This version of OPGG.py is no longer maintained and will be deprecated in the future. Please migrate to v2 as soon as possible.
    """

    __author__ = "ShoobyDoo"
    __license__ = "BSD-3-Clause"

    # Todo: Add support for the following endpoint(s):
    # https://op.gg/api/v1.0/internal/bypass/games/na/summoners/<summoner_id?>/?&limit=20&hl=en_US&game_type=total

    # HUGE find. Incorporate the following endpoint:
    # https://op.gg/api/v1.0/internal/bypass/meta/champions/<champion_id>?hl=<lang_code>

    # METADATA FOR CHAMPIONS -- USE THIS OVER PAGE_PROPS.
    # https://op.gg/api/v1.0/internal/bypass/meta/champions?hl=en_US

    def __init__(self, summoner_id: str = None, region=Region.NA) -> None:
        warn(
            "Deprecation Notice: The OPGG class in v1 is no longer maintained. "
            "Please migrate to v2 as soon as possible.",
            DeprecationWarning,
            stacklevel=2,
        )

        self._summoner_id = summoner_id
        self._region = region

        self._BASE_API_URL = "https://lol-web-api.op.gg/api/v1.0/internal/bypass"
        self._api_url = (
            f"{self._BASE_API_URL}/summoners/{self.region}/{self.summoner_id}/summary"
        )
        self._games_api_url = (
            f"{self._BASE_API_URL}/games/{self.region}/summoners/{self.summoner_id}"
        )

        self._ua = UserAgent()

        # Should randomize EACH request instead of the header of initially init'd obj
        self._headers = {"User-Agent": self._ua.random}

        # in memory data
        self._all_champions = None
        self._all_seasons = None

        # ===== SETUP START =====
        logging.root.name = "OPGG.py"

        if not os.path.exists("./logs"):
            logging.info("Creating logs directory...")
            os.mkdir("./logs")
        else:
            # remove empty log files
            for file in os.listdir("./logs"):
                if (
                    os.stat(f"./logs/{file}").st_size == 0
                    and file != f'opgg_{datetime.now().strftime("%Y-%m-%d")}.log'
                ):
                    logging.info(f"Removing empty log file: {file}")
                    os.remove(f"./logs/{file}")

        logging.basicConfig(
            filename=f'./logs/opgg_{datetime.now().strftime("%Y-%m-%d")}.log',
            filemode="a+",
            format="[%(asctime)s][%(name)s->%(module)s:%(lineno)-10d][%(levelname)-7s] : %(message)s",
            datefmt="%d-%b-%y %H:%M:%S",
            level=logging.INFO,
        )
        # ===== SETUP END =====

        # allow the user to interact with the logger
        self._logger = logging.getLogger("OPGG.py")

        # at object creation, setup and query the cache
        self._cacher = Cacher()
        self._cacher.setup()

        self.logger.info(
            f"OPGG.__init__(summoner_id={self.summoner_id}, "
            f"region={self.region}, "
            f"api_url={self.api_url}, "
            f"headers={self.headers}, "
            f"all_champions={self.all_champions}, "
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
        self.api_url = (
            f"{self._BASE_API_URL}/summoners/{self.region}/{self.summoner_id}/summary"
        )
        self._games_api_url = (
            f"{self._BASE_API_URL}/games/{self.region}/summoners/{self.summoner_id}"
        )

        self.logger.debug(f"self.refresh_api_url() called... See URLs:")
        self.logger.debug(f"self.api_url = {self.api_url}")
        self.logger.debug(f"self._games_api_url = {self._games_api_url}")

    def get_summoner(self, return_content_only=False) -> Summoner | dict:
        """
        A method to get data from the OPGG API and form a Summoner object.

        General flow:\n
            -> Send request to OPGG API\n
            -> Parse data from request (jsonify)\n
            -> Loop through data and form the summoner object.

        ### Returns:
            `Summoner`: A Summoner object representing the summoner.
        """
        self.logger.info(
            f"Sending request to OPGG API... (API_URL = {self.api_url}, HEADERS = {self.headers})"
        )
        res = requests.get(self.api_url, headers=self.headers)

        previous_seasons: list[Season] = []
        league_stats: list[LeagueStats] = []
        most_champions: list[ChampionStats] = []
        recent_game_stats: list[Game] = []

        if res.status_code == 200:
            self.logger.info(
                f"Request to OPGG API was successful, parsing data (Content Length: {len(res.text)})..."
            )
            self.logger.debug(f"SUMMONER DATA AT /SUMMARY ENDPOINT:\n{res.text}\n")
            content = json.loads(res.text)["data"]
        else:
            res.raise_for_status()

        # If return_res is passed in func args, return the content
        # Required in tests to get all the raw content without building the summoner object
        if return_content_only:
            return content

        try:
            previous_seasons = []
            summoner_data = dict(content["summoner"])

            season: dict
            tier_info: dict
            for season in summoner_data.get("previous_seasons", []):
                tmp_season_info = None
                if self.all_seasons:
                    for _season in self.all_seasons:
                        if _season.id == season.get("season_id"):
                            tmp_season_info = _season
                            break

                tmp_rank_entries = []

                rank_entry: dict
                rank_info: dict
                for rank_entry in season.get("rank_entries", []):
                    rank_info = rank_entry.get("rank_info")
                    if not rank_info:
                        continue
                    tmp_rank_entries.append(
                        RankEntry(
                            game_type=rank_entry.get("game_type"),
                            rank_info=Tier(
                                tier=rank_info.get("tier"),
                                division=rank_info.get("division"),
                                lp=rank_info.get("lp"),
                            ),
                            created_at=(
                                datetime.fromisoformat(rank_entry.get("created_at"))
                                if rank_entry.get("created_at")
                                else None
                            ),
                        )
                    )

                tier_info = season.get("tier_info", {})
                previous_seasons.append(
                    Season(
                        season_id=tmp_season_info,
                        tier_info=Tier(
                            tier=tier_info.get("tier"),
                            division=tier_info.get("division"),
                            lp=tier_info.get("lp"),
                            tier_image_url=tier_info.get("tier_image_url"),
                            border_image_url=tier_info.get("border_image_url"),
                        ),
                        rank_entries=tmp_rank_entries,
                        created_at=(
                            datetime.fromisoformat(season.get("created_at"))
                            if season.get("created_at")
                            else None
                        ),
                    )
                )

            league_stats = []
            league: dict
            queue_info: dict
            for league in summoner_data.get("league_stats", []):
                queue_info = league.get("queue_info", {})
                tier_info = league.get("tier_info", {})
                league_stats.append(
                    LeagueStats(
                        queue_info=QueueInfo(
                            id=queue_info.get("id"),
                            queue_translate=queue_info.get("queue_translate"),
                            game_type=queue_info.get("game_type"),
                        ),
                        tier_info=Tier(
                            tier=tier_info.get("tier"),
                            division=tier_info.get("division"),
                            lp=tier_info.get("lp"),
                            tier_image_url=tier_info.get("tier_image_url"),
                            border_image_url=tier_info.get("border_image_url"),
                            level=tier_info.get("level"),
                        ),
                        win=league.get("win"),
                        lose=league.get("lose"),
                        is_hot_streak=league.get("is_hot_streak"),
                        is_fresh_blood=league.get("is_fresh_blood"),
                        is_veteran=league.get("is_veteran"),
                        is_inactive=league.get("is_inactive"),
                        series=league.get("series"),
                        updated_at=league.get("updated_at"),
                    )
                )

            most_champions = []
            # Assign 'most_champions' to a variable to help the linter
            most_champions_data: dict = summoner_data.get("most_champions", {})
            champion_stats: dict = most_champions_data.get("champion_stats", [])

            champion: dict
            for champion in champion_stats:
                tmp_champ = None
                if self.all_champions:
                    for _champion in self.all_champions:
                        if _champion.id == champion.get("id"):
                            tmp_champ = _champion
                            break

                most_champions.append(
                    ChampionStats(
                        champion=tmp_champ,
                        id=champion.get("id"),
                        play=champion.get("play"),
                        win=champion.get("win"),
                        lose=champion.get("lose"),
                        kill=champion.get("kill"),
                        death=champion.get("death"),
                        assist=champion.get("assist"),
                        gold_earned=champion.get("gold_earned"),
                        minion_kill=champion.get("minion_kill"),
                        turret_kill=champion.get("turret_kill"),
                        neutral_minion_kill=champion.get("neutral_minion_kill"),
                        damage_dealt=champion.get("damage_dealt"),
                        damage_taken=champion.get("damage_taken"),
                        physical_damage_dealt=champion.get("physical_damage_dealt"),
                        magic_damage_dealt=champion.get("magic_damage_dealt"),
                        most_kill=champion.get("most_kill"),
                        max_kill=champion.get("max_kill"),
                        max_death=champion.get("max_death"),
                        double_kill=champion.get("double_kill"),
                        triple_kill=champion.get("triple_kill"),
                        quadra_kill=champion.get("quadra_kill"),
                        penta_kill=champion.get("penta_kill"),
                        game_length_second=champion.get("game_length_second"),
                        inhibitor_kills=champion.get("inhibitor_kills"),
                        sight_wards_bought_in_game=champion.get(
                            "sight_wards_bought_in_game"
                        ),
                        vision_wards_bought_in_game=champion.get(
                            "vision_wards_bought_in_game"
                        ),
                        vision_score=champion.get("vision_score"),
                        wards_placed=champion.get("wards_placed"),
                        wards_killed=champion.get("wards_killed"),
                        heal=champion.get("heal"),
                        time_ccing_others=champion.get("time_ccing_others"),
                        op_score=champion.get("op_score"),
                        is_max_in_team_op_score=champion.get("is_max_in_team_op_score"),
                        physical_damage_taken=champion.get("physical_damage_taken"),
                        damage_dealt_to_champions=champion.get(
                            "damage_dealt_to_champions"
                        ),
                        physical_damage_dealt_to_champions=champion.get(
                            "physical_damage_dealt_to_champions"
                        ),
                        magic_damage_dealt_to_champions=champion.get(
                            "magic_damage_dealt_to_champions"
                        ),
                        damage_dealt_to_objectives=champion.get(
                            "damage_dealt_to_objectives"
                        ),
                        damage_dealt_to_turrets=champion.get("damage_dealt_to_turrets"),
                        damage_self_mitigated=champion.get("damage_self_mitigated"),
                        max_largest_multi_kill=champion.get("max_largest_multi_kill"),
                        max_largest_critical_strike=champion.get(
                            "max_largest_critical_strike"
                        ),
                        max_largest_killing_spree=champion.get(
                            "max_largest_killing_spree"
                        ),
                        snowball_throws=champion.get("snowball_throws"),
                        snowball_hits=champion.get("snowball_hits"),
                    )
                )

            # Ensure 'recent_game_stats' is handled properly
            recent_game_stats = (
                self.get_recent_games() if hasattr(self, "get_recent_games") else None
            )

        except Exception as e:
            self.logger.error(f"Error parsing some summoner data: {e}")
            pass

        return Summoner(
            id=summoner_data.get("id"),
            summoner_id=summoner_data.get("summoner_id"),
            acct_id=summoner_data.get("acct_id"),
            puuid=summoner_data.get("puuid"),
            game_name=summoner_data.get("game_name"),
            tagline=summoner_data.get("tagline"),
            name=summoner_data.get("name"),
            internal_name=summoner_data.get("internal_name"),
            profile_image_url=summoner_data.get("profile_image_url"),
            level=summoner_data.get("level"),
            updated_at=summoner_data.get("updated_at"),
            renewable_at=summoner_data.get("renewable_at"),
            previous_seasons=previous_seasons,
            league_stats=league_stats,
            most_champions=most_champions,
            recent_game_stats=recent_game_stats,
        )

    def search(
        self, summoner_names: str | list[str], region=Region.NA
    ) -> list[Summoner]:
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
            if "#" not in summoner_name:
                raise Exception(
                    f'No regional identifier was found for query: "{summoner_name}". Please include the identifier as well and try again. (#NA1, #EUW, etc.)'
                )
            cached_id = self.cacher.get_summoner_id(summoner_name)
            if cached_id:
                cached_summoner_ids.append(cached_id)
            else:
                uncached_summoners.append(summoner_name)

        # pass only uncached summoners to get_page_props()
        page_props = Utils.get_page_props(uncached_summoners, region)

        self.logger.debug(
            f"\n********PAGE_PROPS_START********\n{page_props}\n********PAGE_PROPS_STOP********"
        )

        if len(uncached_summoners) > 0:
            self.logger.info(
                f"No cache for {len(uncached_summoners)} summoners: {uncached_summoners}, fetching... (using get_page_props() site scraper)"
            )
        if len(cached_summoner_ids) > 0:
            self.logger.info(
                f"Cache found for {len(cached_summoner_ids)} summoners: {cached_summoner_ids}, fetching... (using get_summoner() api)"
            )

        # Query cache for champs and seasons
        cached_seasons = self.cacher.get_all_seasons()
        cached_champions = self.cacher.get_all_champs()

        # If we found some cached seasons/champs, use them, otherwise fetch and cache them.
        if cached_seasons:
            self.all_seasons = cached_seasons
        else:
            self.all_seasons = Utils.get_all_seasons(self.region, page_props)
            self.cacher.insert_all_seasons(self.all_seasons)

        if cached_champions:
            self.all_champions = cached_champions
        else:
            self.all_champions = Utils.get_all_champions(self.region, page_props)
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
            if len(page_props["summoners"]) > 1 and "#" in summoner_name:
                logging.debug(
                    f"MULTI-RESULT | page_props->summoners: {page_props['summoners']}"
                )
                only_summoner_name, only_region = summoner_name.split("#")
                for summoner in page_props["summoners"]:
                    if (
                        only_summoner_name.strip() == summoner["game_name"]
                        and only_region.strip() == summoner["tagline"]
                    ):
                        self.summoner_id = summoner["summoner_id"]
                        break

            elif len(page_props["summoners"]) > 1 and "#" not in summoner_name:
                raise Exception(
                    f'Multiple search results were returned for "{summoner_name}". Please include the identifier as well and try again. (#NA1, #EUW, etc.)'
                )

            elif len(page_props["summoners"]) == 1:
                self.summoner_id = page_props["summoners"][0]["summoner_id"]

            summoner = self.get_summoner()
            summoners.append(summoner)
            self.logger.info(
                f"Summoner object built for: {summoner.name} ({summoner.summoner_id}), caching..."
            )
            self.cacher.insert_summoner(summoner.name, summoner.summoner_id)

        # cached summoners go straight to api
        for _cached_summoner_id in cached_summoner_ids:
            self.summoner_id = _cached_summoner_id
            summoner = self.get_summoner()
            summoners.append(summoner)
            self.logger.info(
                f"Summoner object built for: {summoner.name} ({summoner.summoner_id})"
            )

        # todo: add custom exceptions instead of this.
        # todo: raise SummonerNotFound exception
        if len(summoners) == 0:
            raise Exception(f"No summoner(s) matching {summoner_names} were found...")

        return summoners if len(summoners) > 1 else summoners[0]

    def get_recent_games(
        self,
        results: int = 10,
        game_type: Literal["total", "ranked", "normal"] = "total",
        return_content_only=False,
    ) -> list[Game]:
        """
        Get

        Args:
            results (int, optional): _description_. Defaults to 10.
            game_type (Literal[&quot;total&quot;, &quot;ranked&quot;, &quot;normal&quot;], optional): _description_. Defaults to "total".
            return_content_only (bool, optional): _description_. Defaults to False.

        Returns:
            list[Game]: _description_
        """

        recent_games = []
        res = requests.get(
            f"{self._games_api_url}?&limit={results}&game_type={game_type}",
            headers=self.headers,
        )

        self.logger.debug(res.text)

        if res.status_code == 200:
            self.logger.info(
                f"Request to OPGG GAME_API was successful, parsing data (Content Length: {len(res.text)})..."
            )
            game_data: Game = json.loads(res.text)["data"]
        else:
            res.raise_for_status()

        if return_content_only:
            return game_data

        try:
            game: dict
            for game in game_data:

                participants = []

                participant: dict
                participant_summoner: dict
                participant_stats: dict
                participant_tier_info: dict
                for participant in game.get("participants", []):
                    # Assign 'summoner' data to a variable
                    participant_summoner = participant.get("summoner", {})

                    # Create Summoner object with safe key access
                    summoner = Summoner(
                        id=participant_summoner.get("id"),
                        summoner_id=participant_summoner.get("summoner_id"),
                        acct_id=participant_summoner.get("acct_id"),
                        puuid=participant_summoner.get("puuid"),
                        game_name=participant_summoner.get("game_name"),
                        tagline=participant_summoner.get("tagline"),
                        name=participant_summoner.get("name"),
                        internal_name=participant_summoner.get("internal_name"),
                        profile_image_url=participant_summoner.get("profile_image_url"),
                        level=participant_summoner.get("level"),
                        updated_at=participant_summoner.get("updated_at"),
                        renewable_at=participant_summoner.get("renewable_at"),
                    )

                    # Assign 'stats' and 'tier_info' data to variables
                    participant_stats = participant.get("stats", {})
                    participant_tier_info = participant.get("tier_info", {})

                    # Create Participant object
                    participants.append(
                        Participant(
                            summoner=summoner,
                            participant_id=participant.get("participant_id"),
                            champion_id=participant.get("champion_id"),
                            team_key=participant.get("team_key"),
                            position=participant.get("position"),
                            role=participant.get("role"),
                            items=participant.get("items"),
                            trinket_item=participant.get("trinket_item"),
                            rune={
                                participant.get("rune", {}).get("primary_page_id"),
                                participant.get("rune", {}).get("primary_rune_id"),
                                participant.get("rune", {}).get("secondary_page_id"),
                            },  # Consider creating a Rune object in the future
                            spells=participant.get("spells"),
                            stats=Stats(
                                champion_level=participant_stats.get("champion_level"),
                                damage_self_mitigated=participant_stats.get(
                                    "damage_self_mitigated"
                                ),
                                damage_dealt_to_objectives=participant_stats.get(
                                    "damage_dealt_to_objectives"
                                ),
                                damage_dealt_to_turrets=participant_stats.get(
                                    "damage_dealt_to_turrets"
                                ),
                                magic_damage_dealt_player=participant_stats.get(
                                    "magic_damage_dealt_player"
                                ),
                                physical_damage_taken=participant_stats.get(
                                    "physical_damage_taken"
                                ),
                                physical_damage_dealt_to_champions=participant_stats.get(
                                    "physical_damage_dealt_to_champions"
                                ),
                                total_damage_taken=participant_stats.get(
                                    "total_damage_taken"
                                ),
                                total_damage_dealt=participant_stats.get(
                                    "total_damage_dealt"
                                ),
                                total_damage_dealt_to_champions=participant_stats.get(
                                    "total_damage_dealt_to_champions"
                                ),
                                largest_critical_strike=participant_stats.get(
                                    "largest_critical_strike"
                                ),
                                time_ccing_others=participant_stats.get(
                                    "time_ccing_others"
                                ),
                                vision_score=participant_stats.get("vision_score"),
                                vision_wards_bought_in_game=participant_stats.get(
                                    "vision_wards_bought_in_game"
                                ),
                                sight_wards_bought_in_game=participant_stats.get(
                                    "sight_wards_bought_in_game"
                                ),
                                ward_kill=participant_stats.get("ward_kill"),
                                ward_place=participant_stats.get("ward_place"),
                                turret_kill=participant_stats.get("turret_kill"),
                                barrack_kill=participant_stats.get("barrack_kill"),
                                kill=participant_stats.get("kill"),
                                death=participant_stats.get("death"),
                                assist=participant_stats.get("assist"),
                                largest_multi_kill=participant_stats.get(
                                    "largest_multi_kill"
                                ),
                                largest_killing_spree=participant_stats.get(
                                    "largest_killing_spree"
                                ),
                                minion_kill=participant_stats.get("minion_kill"),
                                neutral_minion_kill_team_jungle=participant_stats.get(
                                    "neutral_minion_kill_team_jungle"
                                ),
                                neutral_minion_kill_enemy_jungle=participant_stats.get(
                                    "neutral_minion_kill_enemy_jungle"
                                ),
                                neutral_minion_kill=participant_stats.get(
                                    "neutral_minion_kill"
                                ),
                                gold_earned=participant_stats.get("gold_earned"),
                                total_heal=participant_stats.get("total_heal"),
                                result=participant_stats.get("result"),
                                op_score=participant_stats.get("op_score"),
                                op_score_rank=participant_stats.get("op_score_rank"),
                                is_opscore_max_in_team=participant_stats.get(
                                    "is_opscore_max_in_team"
                                ),
                                lane_score=participant_stats.get("lane_score"),
                                op_score_timeline=participant_stats.get(
                                    "op_score_timeline"
                                ),
                                op_score_timeline_analysis=participant_stats.get(
                                    "op_score_timeline_analysis"
                                ),
                            ),
                            tier_info=Tier(
                                tier=participant_tier_info.get("tier"),
                                division=participant_tier_info.get("division"),
                                lp=participant_tier_info.get("lp"),
                                level=participant_tier_info.get("level"),
                                tier_image_url=participant_tier_info.get(
                                    "tier_image_url"
                                ),
                                border_image_url=participant_tier_info.get(
                                    "border_image_url"
                                ),
                            ),
                        )
                    )

                teams = []

                team: dict
                team_game_stat: dict
                game_queue_info: dict
                game_average_tier_info: dict
                for team in game.get("teams", []):
                    team_game_stat = team.get("game_stat", {})
                    teams.append(
                        Team(
                            key=team.get("key"),
                            game_stat=GameStats(
                                is_win=team_game_stat.get("is_win"),
                                champion_kill=team_game_stat.get("champion_kill"),
                                champion_first=team_game_stat.get("champion_first"),
                                inhibitor_kill=team_game_stat.get("inhibitor_kill"),
                                inhibitor_first=team_game_stat.get("inhibitor_first"),
                                rift_herald_kill=team_game_stat.get("rift_herald_kill"),
                                rift_herald_first=team_game_stat.get(
                                    "rift_herald_first"
                                ),
                                dragon_kill=team_game_stat.get("dragon_kill"),
                                dragon_first=team_game_stat.get("dragon_first"),
                                baron_kill=team_game_stat.get("baron_kill"),
                                baron_first=team_game_stat.get("baron_first"),
                                tower_kill=team_game_stat.get("tower_kill"),
                                tower_first=team_game_stat.get("tower_first"),
                                horde_kill=team_game_stat.get("horde_kill"),
                                horde_first=team_game_stat.get("horde_first"),
                                is_remake=team_game_stat.get("is_remake"),
                                death=team_game_stat.get("death"),
                                assist=team_game_stat.get("assist"),
                                gold_earned=team_game_stat.get("gold_earned"),
                                kill=team_game_stat.get("kill"),
                            ),
                            banned_champions=team.get("banned_champions", []),
                        )
                    )

                # Assign 'queue_info' and 'average_tier_info' data to variables
                game_queue_info = game.get("queue_info", {})
                game_average_tier_info = game.get("average_tier_info", {})

                # Create Game object
                tmp_game = Game(
                    id=game.get("id"),
                    created_at=game.get("created_at"),
                    game_map=game.get("game_map"),
                    queue_info=QueueInfo(
                        id=game_queue_info.get("id"),
                        queue_translate=game_queue_info.get("queue_translate"),
                        game_type=game_queue_info.get("game_type"),
                    ),
                    version=game.get("version"),
                    game_length_second=game.get("game_length_second"),
                    is_remake=game.get("is_remake"),
                    is_opscore_active=game.get("is_opscore_active"),
                    is_recorded=game.get("is_recorded"),
                    record_info=game.get("record_info"),
                    average_tier_info=Tier(
                        tier=game_average_tier_info.get("tier"),
                        division=game_average_tier_info.get("division"),
                        tier_image_url=game_average_tier_info.get("tier_image_url"),
                        border_image_url=game_average_tier_info.get("border_image_url"),
                    ),
                    participants=participants,
                    teams=teams,
                    memo=game.get("memo"),
                    myData=Participant(
                        summoner=Summoner(
                            id=game.get("myData", {}).get("summoner", {}).get("id"),
                            summoner_id=game.get("myData", {})
                            .get("summoner", {})
                            .get("summoner_id"),
                            acct_id=game.get("myData", {})
                            .get("summoner", {})
                            .get("acct_id"),
                            puuid=game.get("myData", {})
                            .get("summoner", {})
                            .get("puuid"),
                            game_name=game.get("myData", {})
                            .get("summoner", {})
                            .get("game_name"),
                            tagline=game.get("myData", {})
                            .get("summoner", {})
                            .get("tagline"),
                            name=game.get("myData", {}).get("summoner", {}).get("name"),
                            internal_name=game.get("myData", {})
                            .get("summoner", {})
                            .get("internal_name"),
                            profile_image_url=game.get("myData", {})
                            .get("summoner", {})
                            .get("profile_image_url"),
                            level=game.get("myData", {})
                            .get("summoner", {})
                            .get("level"),
                            updated_at=game.get("myData", {})
                            .get("summoner", {})
                            .get("updated_at"),
                            renewable_at=game.get("myData", {})
                            .get("summoner", {})
                            .get("renewable_at"),
                        ),
                        participant_id=game.get("myData", {}).get("participant_id"),
                        champion_id=game.get("myData", {}).get("champion_id"),
                        team_key=game.get("myData", {}).get("team_key"),
                        position=game.get("myData", {}).get("position"),
                        role=game.get("myData", {}).get("role"),
                        items=game.get("myData", {}).get("items"),
                        trinket_item=game.get("myData", {}).get("trinket_item"),
                        rune={
                            game.get("myData", {})
                            .get("rune", {})
                            .get("primary_page_id"),
                            game.get("myData", {})
                            .get("rune", {})
                            .get("primary_rune_id"),
                            game.get("myData", {})
                            .get("rune", {})
                            .get("secondary_page_id"),
                        },  # Consider creating a Rune object in the future
                        spells=game.get("myData", {}).get("spells"),
                        stats=Stats(
                            champion_level=game.get("myData", {})
                            .get("stats", {})
                            .get("champion_level"),
                            damage_self_mitigated=game.get("myData", {})
                            .get("stats", {})
                            .get("damage_self_mitigated"),
                            damage_dealt_to_objectives=game.get("myData", {})
                            .get("stats", {})
                            .get("damage_dealt_to_objectives"),
                            damage_dealt_to_turrets=game.get("myData", {})
                            .get("stats", {})
                            .get("damage_dealt_to_turrets"),
                            magic_damage_dealt_player=game.get("myData", {})
                            .get("stats", {})
                            .get("magic_damage_dealt_player"),
                            physical_damage_taken=game.get("myData", {})
                            .get("stats", {})
                            .get("physical_damage_taken"),
                            physical_damage_dealt_to_champions=game.get("myData", {})
                            .get("stats", {})
                            .get("physical_damage_dealt_to_champions"),
                            total_damage_taken=game.get("myData", {})
                            .get("stats", {})
                            .get("total_damage_taken"),
                            total_damage_dealt=game.get("myData", {})
                            .get("stats", {})
                            .get("total_damage_dealt"),
                            total_damage_dealt_to_champions=game.get("myData", {})
                            .get("stats", {})
                            .get("total_damage_dealt_to_champions"),
                            largest_critical_strike=game.get("myData", {})
                            .get("stats", {})
                            .get("largest_critical_strike"),
                            time_ccing_others=game.get("myData", {})
                            .get("stats", {})
                            .get("time_ccing_others"),
                            vision_score=game.get("myData", {})
                            .get("stats", {})
                            .get("vision_score"),
                            vision_wards_bought_in_game=game.get("myData", {})
                            .get("stats", {})
                            .get("vision_wards_bought_in_game"),
                            sight_wards_bought_in_game=game.get("myData", {})
                            .get("stats", {})
                            .get("sight_wards_bought_in_game"),
                            ward_kill=game.get("myData", {})
                            .get("stats", {})
                            .get("ward_kill"),
                            ward_place=game.get("myData", {})
                            .get("stats", {})
                            .get("ward_place"),
                            turret_kill=game.get("myData", {})
                            .get("stats", {})
                            .get("turret_kill"),
                            barrack_kill=game.get("myData", {})
                            .get("stats", {})
                            .get("barrack_kill"),
                            kill=game.get("myData", {}).get("stats", {}).get("kill"),
                            death=game.get("myData", {}).get("stats", {}).get("death"),
                            assist=game.get("myData", {})
                            .get("stats", {})
                            .get("assist"),
                            largest_multi_kill=game.get("myData", {})
                            .get("stats", {})
                            .get("largest_multi_kill"),
                            largest_killing_spree=game.get("myData", {})
                            .get("stats", {})
                            .get("largest_killing_spree"),
                            minion_kill=game.get("myData", {})
                            .get("stats", {})
                            .get("minion_kill"),
                            neutral_minion_kill_team_jungle=game.get("myData", {})
                            .get("stats", {})
                            .get("neutral_minion_kill_team_jungle"),
                            neutral_minion_kill_enemy_jungle=game.get("myData", {})
                            .get("stats", {})
                            .get("neutral_minion_kill_enemy_jungle"),
                            neutral_minion_kill=game.get("myData", {})
                            .get("stats", {})
                            .get("neutral_minion_kill"),
                            gold_earned=game.get("myData", {})
                            .get("stats", {})
                            .get("gold_earned"),
                            total_heal=game.get("myData", {})
                            .get("stats", {})
                            .get("total_heal"),
                            result=game.get("myData", {})
                            .get("stats", {})
                            .get("result"),
                            op_score=game.get("myData", {})
                            .get("stats", {})
                            .get("op_score"),
                            op_score_rank=game.get("myData", {})
                            .get("stats", {})
                            .get("op_score_rank"),
                            is_opscore_max_in_team=game.get("myData", {})
                            .get("stats", {})
                            .get("is_opscore_max_in_team"),
                            lane_score=game.get("myData", {})
                            .get("stats", {})
                            .get("lane_score"),
                            op_score_timeline=game.get("myData", {})
                            .get("stats", {})
                            .get("op_score_timeline"),
                            op_score_timeline_analysis=game.get("myData", {})
                            .get("stats", {})
                            .get("op_score_timeline_analysis"),
                        ),
                        tier_info=Tier(
                            tier=game.get("myData", {})
                            .get("tier_info", {})
                            .get("tier"),
                            division=game.get("myData", {})
                            .get("tier_info", {})
                            .get("division"),
                            lp=game.get("myData", {}).get("tier_info", {}).get("lp"),
                            level=game.get("myData", {})
                            .get("tier_info", {})
                            .get("level"),
                            tier_image_url=game.get("myData", {})
                            .get("tier_info", {})
                            .get("tier_image_url"),
                            border_image_url=game.get("myData", {})
                            .get("tier_info", {})
                            .get("border_image_url"),
                        ),
                    ),
                )

                recent_games.append(tmp_game)

            return recent_games

        except:
            self.logger.error(
                f"Unable to create game object, see trace: \n{traceback.format_exc()}"
            )
            pass
