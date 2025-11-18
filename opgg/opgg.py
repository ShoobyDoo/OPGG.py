import os
import logging
import asyncio
import pprint

from datetime import datetime
from fake_useragent import UserAgent

from opgg.champion import Champion
from opgg.game import Game
from opgg.keyword import Keyword
from opgg.summoner import Summoner
from opgg.season import SeasonMeta
from opgg.utils import Utils
from opgg.cacher import Cacher
from opgg.params import (
    By,
    CacheType,
    GameType,
    LangCode,
    Queue,
    Region,
    SearchReturnType,
    StatsRegion,
    Tier,
    GenericReqParams,
)
from opgg.search_result import SearchResult

# All api endpoints pulled out of the main OPGG class to reduce clutter on the library object

# ===== BASE URLS ===== #
_SUMMONER_API_URL = "https://lol-api-summoner.op.gg/api"
_CHAMPION_API_URL = "https://lol-api-champion.op.gg/api"

# ===== MAIN SEARCH AND SUMMONER DETAILS API - SEARCH SUPPORTS FUZZY MATCH ===== #
_SEARCH_API_URL = (
    f"{_SUMMONER_API_URL}/v3/{{region}}/summoners?riot_id={{riot_id}}&hl={{hl}}"
)
_SUMMARY_API_URL = (
    f"{_SUMMONER_API_URL}/{{region}}/summoners/{{summoner_id}}/summary?hl={{hl}}"
)

# ===== GAMES API ===== #
_GAMES_API_URL = (
    f"{_SUMMONER_API_URL}/{{region}}/summoners/{{summoner_id}}/games?"
    "limit={{limit}}&game_type={{game_type}}&hl={{hl}}"
)

# ===== METADATA API ===== #
_SEASONS_API_URL = f"{_SUMMONER_API_URL}/meta/seasons?hl={{hl}}"
_KEYWORDS_API_URL = f"{_SUMMONER_API_URL}/meta/keywords?hl={{hl}}"
_CHAMPIONS_API_URL = f"{_CHAMPION_API_URL}/meta/champions?hl={{hl}}"
_CHAMPION_BY_ID_API_URL = (
    f"{_CHAMPION_API_URL}/meta/champions/{{champion_id}}?hl={{hl}}"
)
_VERSIONS_API_URL = f"{_CHAMPION_API_URL}/meta/versions?hl={{hl}}"

# ===== CHAMPION STATS API ===== #
# Incomplete: more routes than ranked.
# Tested and confirmed working: ranked, aram, urf, doom (likely doombots), arena, nexus_blitz
_CHAMPION_STATS_API_URL = (
    f"{_CHAMPION_API_URL}/{{region}}/champions/ranked?tier={{tier}}"
)


class OPGG:
    """
    ### OPGG.py

    Copyright (c) 2025, ShoobyDoo

    License: BSD-3-Clause, See LICENSE for more details.
    """

    __author__ = "ShoobyDoo"
    __license__ = "BSD-3-Clause"

    def __init__(self) -> None:
        self._ua = UserAgent()
        self._headers = {"User-Agent": self._ua.random}

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
            format="[%(asctime)s][%(name)s->%(module)-10s:%(lineno)3d][%(levelname)-7s] : %(message)s",
            datefmt="%d-%b-%y %H:%M:%S",
            level=logging.INFO,
        )
        # ===== SETUP END =====

        # allow the user to interact with the logger
        self._logger = logging.getLogger("OPGG.py")

        self.logger.info(
            f"OPGG.__init__(SUMMONER_API_URL={_SUMMONER_API_URL}, "
            f"headers={self._headers})"
        )

        # at object creation, setup and query the cache
        self._cacher = Cacher()
        self._cacher.setup()

        ttl_env = os.getenv("OPGG_CHAMPION_CACHE_TTL")
        default_ttl = 60 * 60 * 24 * 7  # 1 week
        try:
            parsed_ttl = int(ttl_env) if ttl_env not in (None, "") else default_ttl
        except ValueError:
            self.logger.warning(
                "Invalid OPGG_CHAMPION_CACHE_TTL value '%s'. Falling back to %s seconds.",
                ttl_env,
                default_ttl,
            )
            parsed_ttl = default_ttl

        self._champion_cache_ttl = max(parsed_ttl, 0)
        # lang_code value -> {season_id: SeasonMeta}
        self._season_meta_cache: dict[str, dict[int, SeasonMeta]] = {}

    @property
    def logger(self) -> logging.Logger:
        """
        A `Logger` object representing the logger instance.

        The logging level is set to `INFO` by default.
        """
        return self._logger

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
    def champion_cache_ttl(self) -> int:
        """
        Current TTL (in seconds) for long-lived cache entries such as champions.
        """
        return self._champion_cache_ttl

    @champion_cache_ttl.setter
    def champion_cache_ttl(self, value: int) -> None:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            raise ValueError("champion_cache_ttl must be an integer value") from None

        if parsed < 0:
            raise ValueError("champion_cache_ttl must be 0 or greater")

        self._champion_cache_ttl = parsed

    def search(
        self,
        query: str,
        region: Region = Region.ANY,
        returns: SearchReturnType = SearchReturnType.FULL,
        lang_code: LangCode = LangCode.ENGLISH,
    ) -> list[SearchResult]:
        """
        Search for League of Legends summoners by name across one or all regions.

        #### Args:
            - `query` (`str`): Summoner name to search for. Can include tagline (e.g., "name#tag")
            - `region` (`Region`, optional): Specific region to search in. Defaults to `Region.ANY` which searches all regions concurrently.
            - `returns` (`SearchReturnType`, optional): Level of detail in results. Defaults to `SearchReturnType.FULL`.
            - `lang_code` (`LangCode`, optional): Language for localized results. Defaults to `LangCode.ENGLISH`.

        #### Returns:
            - `list[SearchResult]`: List of `SearchResult` objects containing the found summoners.
              Each `SearchResult` object contains formatted summoner data and the region it was found in.

        #### Example:
        ```python
        >>> from opgg import OPGG
        >>> from opgg.params import Region, SearchReturnType
        >>> opgg = OPGG()
        >>>
        >>> results = opgg.search("faker", Region.KR) # Search specific region (recommended)
        >>> simple_results = opgg.search("faker", Region.KR, SearchReturnType.SIMPLE) # Get basic results only
        >>> all_results = opgg.search("faker") # Search all regions (resource-intensive)
        >>>
        >>> [print(result) for result in results]
        >>> [print(result) for result in all_results]
        ```

        #### Note:
        Searching with `Region.ANY` is significantly more resource-intensive as it
        queries all regional endpoints concurrently. Additionally, when searching all
        regions, there is a hard limit of 10 search results per region.
        """
        returns_value = (
            returns.value if isinstance(returns, SearchReturnType) else str(returns)
        )

        normalized_query = query.strip()

        self.logger.info(
            f"Starting summoner search for '{normalized_query}' in region '{region}'"
        )

        search_params: GenericReqParams = {
            "base_api_url": _SEARCH_API_URL,
            "headers": self.headers,
            "lang_code": lang_code,
        }

        if region == Region.ANY:
            self.logger.info("Searching all regions...")
            results = asyncio.run(
                Utils._search_all_regions(normalized_query, search_params)
            )
        else:
            self.logger.info(f"Searching specific region: {region}")
            results = asyncio.run(
                Utils._single_region_search(
                    normalized_query,
                    region,
                    search_params,
                )
            )

        # Inner object instantiation BEFORE SearchResult wrapper
        search_results = [
            SearchResult(
                **{
                    "summoner": Summoner(**result["summoner"]),
                    "region": result["region"],
                }
            )
            for result in results
        ]

        search_results = Utils.filter_results_with_summoner_id(
            search_results, self.logger
        )

        if returns_value == "full":
            # set each summoner property in the search_results array
            # to the corresponding Summoner object
            self.logger.info(
                f"Fetching profiles for {len(search_results)} summoners..."
            )

            # This call is done passing the array because if there are multiple, we want the benefit of concurrency
            # provided by the asychonous nature of the call
            summoners = self.get_summoner(search_results, lang_code=lang_code)

            # We then build the search_results array with the Summoner objects
            for sr, s in zip(search_results, summoners):
                sr.summoner = s

        return search_results

    def get_summoner(
        self,
        search_result: SearchResult | list[SearchResult] | None = None,
        summoner_id: str | list[str] | None = None,
        region: Region | list[Region] | None = None,
        lang_code: LangCode = LangCode.ENGLISH,
    ) -> Summoner | list[Summoner]:
        if search_result is None and summoner_id is not None and region is not None:
            if isinstance(summoner_id, str) and isinstance(region, Region):
                search_result = SearchResult(
                    **{
                        "summoner": Summoner(**{"summoner_id": summoner_id}),
                        "region": region,
                    }
                )
            elif isinstance(summoner_id, list) and isinstance(region, list):
                search_result = [
                    SearchResult(
                        **{"summoner": Summoner(**{"summoner_id": sid}), "region": reg}
                    )
                    for sid, reg in zip(summoner_id, region)
                ]
            else:
                raise ValueError("Mismatched types for summoner_id and region")

        if isinstance(search_result, SearchResult):
            if not search_result.summoner.summoner_id:
                self.logger.critical(
                    "Cannot fetch profile for region '%s' because the search result is missing a summoner_id. Raw payload: %s",
                    search_result.region,
                    pprint.pformat(
                        search_result.summoner.model_dump()
                        if hasattr(search_result.summoner, "model_dump")
                        else search_result.summoner
                    ),
                )
                return search_result.summoner

            self.logger.info(f"Fetching profile for summoner result: {search_result}")
            profile_data = asyncio.run(
                Utils._fetch_profile(
                    search_result.summoner.summoner_id,
                    params={
                        "base_api_url": _SUMMARY_API_URL.format_map(
                            {
                                "region": search_result.region,
                                "summoner_id": search_result.summoner.summoner_id,
                                "hl": lang_code,
                            }
                        ),
                        "headers": self.headers,
                    },
                )
            )
            summoner = Summoner(**profile_data["summoner"])
            self._attach_season_meta(summoner, lang_code)
            return summoner

        elif isinstance(search_result, list):
            self.logger.debug(
                f"Raw summoner results: \n{pprint.pformat(search_result)}"
            )

            filtered_results = Utils.filter_results_with_summoner_id(
                search_result, self.logger
            )
            if not filtered_results:
                self.logger.warning(
                    "All provided search results were missing summoner IDs. Skipping profile fetch."
                )
                return []

            self.logger.info(
                f"Fetching profiles for {len(filtered_results)} summoner results"
            )
            profile_data = asyncio.run(
                Utils._fetch_profile_multiple(
                    {
                        "base_api_url": _SUMMARY_API_URL,
                        "headers": self.headers,
                        "lang_code": lang_code,
                    },
                    filtered_results,
                )
            )
            summoners = [Summoner(**profile["summoner"]) for profile in profile_data]
            self._attach_season_meta(summoners, lang_code)
            return summoners

        else:
            raise ValueError("Invalid type for search_result")

    def get_recent_games(
        self,
        search_result: SearchResult | list[SearchResult] | None = None,
        summoner_id: str | list[str] | None = None,
        region: Region | list[Region] | None = None,
        results: int = 15,
        game_type: GameType = GameType.TOTAL,
        lang_code: LangCode = LangCode.ENGLISH,
    ) -> list[Game] | list[list[Game]]:
        """
        Retrieve recent games for the given summoner(s).

        #### Args:
            - `search_result` (`SearchResult` or `list[SearchResult]`, optional): The search result(s) representing the summoner(s) whose recent games are to be retrieved. If not provided, you must supply `summoner_id` and `region`.
            - `summoner_id` (`str` or `list[str]`, optional): Summoner ID(s) for which to fetch recent games (used when `search_result` is not provided).
            - `region` (`Region` or `list[Region]`, optional): The region(s) corresponding to the summoner ID(s).
            - `results` (`int`, optional): The number of recent games to retrieve. Defaults to 15.
            - `game_type` (`GameType`, optional): The type of games to retrieve. Defaults to GameType.TOTAL.
            - `lang_code` (`LangCode`, optional): Language code for localization. Defaults to `LangCode.ENGLISH`.

        #### Returns:
        - If a single `SearchResult` is provided:
            `list[Game]`: A list of `Game` objects representing the recent games for that summoner.
        - If a list of `SearchResult` objects is provided:
            `list[list[Game]]`: A list of lists, where each inner list contains `Game` objects corresponding to each individual `SearchResult`.

        #### Example:
        ```python
        >>> from opgg import OPGG
        >>> from opgg.params import GameType
        >>> opgg = OPGG()
        >>> # For a single summoner:
        >>> games = opgg.get_recent_games(search_result=some_search_result)
        >>> # For ranked games only:
        >>> ranked_games = opgg.get_recent_games(search_result=some_search_result, game_type=GameType.RANKED)
        >>> # For multiple summoners:
        >>> grouped_games = opgg.get_recent_games(search_result=[result1, result2])
        ```
        """
        game_type_value = (
            game_type.value if isinstance(game_type, GameType) else str(game_type)
        )

        if search_result is None and summoner_id is not None and region is not None:
            if isinstance(summoner_id, str) and isinstance(region, Region):
                search_result = SearchResult(
                    summoner=Summoner(**{"summoner_id": summoner_id}),
                    region=region,
                )
            elif isinstance(summoner_id, list) and isinstance(region, list):
                search_result = [
                    SearchResult(
                        summoner=Summoner(**{"summoner_id": sid}),
                        region=reg,
                    )
                    for sid, reg in zip(summoner_id, region)
                ]
            else:
                raise ValueError("Mismatched types for summoner_id and region")

        if isinstance(search_result, SearchResult):
            self.logger.info(
                f'Fetching {results} recent games of type "{game_type_value}" for summoner result: {search_result}'
            )
            game_params: GenericReqParams = {
                "base_api_url": _GAMES_API_URL.format_map(
                    {
                        "region": search_result.region,
                        "summoner_id": search_result.summoner.summoner_id,
                        "limit": results,
                        "game_type": game_type_value,
                        "hl": lang_code,
                    }
                ),
                "headers": self.headers,
            }
            game_data = asyncio.run(
                Utils._fetch_recent_games(
                    game_params,
                )
            )

            return [Game(**game) for game in game_data]

        elif isinstance(search_result, list):
            self.logger.info(
                f'Fetching {results} recent games of type "{game_type_value}" for {len(search_result)} summoner results'
            )
            game_params_list = [
                {
                    "base_api_url": _GAMES_API_URL.format_map(
                        {
                            "region": sr.region,
                            "summoner_id": sr.summoner.summoner_id,
                            "limit": results,
                            "game_type": game_type_value,
                            "hl": lang_code,
                        }
                    ),
                    "headers": self.headers,
                }
                for sr in search_result
            ]
            game_data_list = asyncio.run(
                Utils._fetch_recent_games_multiple(
                    game_params_list,
                )
            )
            return [
                [Game(**game) for game in game_data] for game_data in game_data_list
            ]

        else:
            raise ValueError("Invalid type for search_result")

    def get_all_champions(
        self,
        lang_code: LangCode = LangCode.ENGLISH,
        force_refresh: bool = False,
    ) -> list[Champion]:
        """
        Retrieve all champions from the OPGG Champion API.

        ### Parameters
            `lang_code` : LangCode (default: LangCode.ENGLISH)
                The language code for champion data localization.

        ### Returns
            `list[Champion]` : List of all champion objects with their static data.

        ### Example
            ```python
            from opgg import OPGG
            from opgg.params import LangCode

            opgg = OPGG()
            champions = opgg.get_all_champions(lang_code=LangCode.KOREAN)
            ```
        """
        lang_value = (
            lang_code.value if isinstance(lang_code, LangCode) else str(lang_code)
        )

        if not force_refresh:
            cached_champions = self._cacher.get_cached_champions(
                lang_code, ttl_seconds=self._champion_cache_ttl
            )
            if cached_champions:
                self.logger.info(
                    "Returning %d cached champions for lang=%s",
                    len(cached_champions),
                    lang_value,
                )
                return cached_champions
        else:
            self.logger.info(
                "Force refresh requested; bypassing cached champions for lang=%s",
                lang_value,
            )

        get_champs_params: GenericReqParams = {
            "base_api_url": _CHAMPIONS_API_URL.format_map({"hl": lang_value}),
            "headers": self.headers,
        }

        champions_list = asyncio.run(Utils._fetch_all_champions(get_champs_params))
        champions_list_objs = [Champion(**champ) for champ in champions_list]

        self.logger.info(f"Got {len(champions_list_objs)} champions")

        if champions_list_objs:
            cached_count = self._cacher.get_cached_champs_count(lang_code)
            if len(champions_list_objs) != cached_count:
                self.logger.info(
                    "Champion response size differs from cached count (%s vs %s). Rebuilding cache...",
                    len(champions_list_objs),
                    cached_count,
                )
            self._cacher.cache_champs(champions_list_objs, lang_code)

        return champions_list_objs

    def force_refresh_cache(
        self,
        cache_types: list[CacheType] | CacheType = CacheType.ALL,
        lang_code: LangCode | None = None,
        all_languages: bool = False,
    ) -> dict:
        """
        Force refresh long-lived cache entries (champions, seasons, versions, keywords).

        ### Parameters
            `cache_types` : list[CacheType] | CacheType (default: CacheType.ALL)
                Cache types to refresh. Can be a single CacheType or list of CacheTypes.
            `lang_code` : LangCode | None (default: None)
                Language scope to refresh. If None and all_languages=False, defaults to English.
                Ignored if all_languages=True.
            `all_languages` : bool (default: False)
                If True, refresh cache for all currently cached languages.
                If True, lang_code parameter is ignored.

        ### Returns
            `dict` : Statistics about what was refreshed

        ### Example
            ```python
            from opgg import OPGG
            from opgg.params import CacheType, LangCode

            opgg = OPGG()

            # Refresh all cache types for English
            stats = opgg.force_refresh_cache()

            # Refresh only champions for Korean
            stats = opgg.force_refresh_cache(cache_types=CacheType.CHAMPIONS, lang_code=LangCode.KOREAN)

            # Refresh champions and seasons for all cached languages
            stats = opgg.force_refresh_cache(cache_types=[CacheType.CHAMPIONS, CacheType.SEASONS], all_languages=True)

            # Refresh everything for all languages
            stats = opgg.force_refresh_cache(cache_types=CacheType.ALL, all_languages=True)
            ```
        """
        # Normalize cache_types to list of strings
        if isinstance(cache_types, CacheType):
            if cache_types == CacheType.ALL:
                cache_types_list = ["champions", "seasons", "versions", "keywords"]
            else:
                cache_types_list = [cache_types.value]
        elif isinstance(cache_types, list):
            cache_types_list = [
                ct.value if isinstance(ct, CacheType) else str(ct) for ct in cache_types
            ]
        else:
            # Handle string for backward compatibility
            if cache_types == "all":
                cache_types_list = ["champions", "seasons", "versions", "keywords"]
            else:
                cache_types_list = [str(cache_types)]

        # Determine languages to refresh
        if all_languages:
            # Get all currently cached languages from cache stats
            cache_stats = self._cacher.get_cache_stats()
            languages_set = set()
            for cache_type in cache_types_list:
                languages_set.update(
                    cache_stats.get(cache_type, {}).get("languages", [])
                )

            # If no languages cached yet, default to English
            languages = (
                [LangCode(lang) for lang in languages_set]
                if languages_set
                else [LangCode.ENGLISH]
            )
            self.logger.info(
                "Refreshing cache types %s for all cached languages: %s",
                cache_types_list,
                [lang.value for lang in languages],
            )
        else:
            languages = [lang_code if lang_code is not None else LangCode.ENGLISH]
            self.logger.info(
                "Refreshing cache types %s for lang=%s",
                cache_types_list,
                languages[0].value,
            )

        # Track what was refreshed
        stats = {
            "champions": {"languages": [], "count": 0},
            "seasons": {"languages": [], "count": 0},
            "versions": {"languages": [], "count": 0},
            "keywords": {"languages": [], "count": 0},
        }

        # Refresh each cache type for each language
        for lang in languages:
            if "champions" in cache_types_list:
                try:
                    champs = self.get_all_champions(lang_code=lang, force_refresh=True)
                    stats["champions"]["languages"].append(lang.value)
                    stats["champions"]["count"] += len(champs)
                    self.logger.info(
                        "Refreshed %d champions for lang=%s", len(champs), lang.value
                    )
                except Exception as exc:
                    self.logger.error(
                        "Failed to refresh champions for lang=%s: %s", lang.value, exc
                    )

            if "seasons" in cache_types_list:
                try:
                    seasons = self.get_all_seasons(lang_code=lang, force_refresh=True)
                    stats["seasons"]["languages"].append(lang.value)
                    # Count seasons if it's a dict with 'seasons' key
                    if isinstance(seasons, dict) and "seasons" in seasons:
                        stats["seasons"]["count"] += len(seasons["seasons"])
                    elif isinstance(seasons, list):
                        stats["seasons"]["count"] += len(seasons)
                    self.logger.info("Refreshed seasons for lang=%s", lang.value)
                except Exception as exc:
                    self.logger.error(
                        "Failed to refresh seasons for lang=%s: %s", lang.value, exc
                    )

            if "versions" in cache_types_list:
                try:
                    # no assignment needed, just call to refresh cache
                    self.get_versions(lang_code=lang, force_refresh=True)
                    stats["versions"]["languages"].append(lang.value)
                    stats["versions"]["count"] += 1
                    self.logger.info("Refreshed versions for lang=%s", lang.value)
                except Exception as exc:
                    self.logger.error(
                        "Failed to refresh versions for lang=%s: %s", lang.value, exc
                    )

            if "keywords" in cache_types_list:
                try:
                    keywords = self.get_keywords(lang_code=lang, force_refresh=True)
                    stats["keywords"]["languages"].append(lang.value)
                    stats["keywords"]["count"] += len(keywords)
                    self.logger.info(
                        "Refreshed %d keywords for lang=%s", len(keywords), lang.value
                    )
                except Exception as exc:
                    self.logger.error(
                        "Failed to refresh keywords for lang=%s: %s", lang.value, exc
                    )

        self.logger.info("Force refresh complete. Stats: %s", stats)
        return stats

    def get_cache_stats(self) -> dict:
        """
        Get statistics about cached data.

        ### Returns
            `dict` : Dictionary containing cache statistics for all cache types

        ### Example
            ```python
            from opgg import OPGG

            opgg = OPGG()

            # Get cache statistics
            stats = opgg.get_cache_stats()
            print(f"Champions cached: {stats['champions']['total_count']}")
            print(f"Languages: {stats['champions']['languages']}")
            ```
        """
        return self._cacher.get_cache_stats()

    def clear_cache(
        self,
        cache_type: CacheType = CacheType.ALL,
        lang_code: LangCode | None = None,
    ) -> dict:
        """
        Clear cached data (champions, seasons, versions, keywords).

        ### Parameters
            `cache_type` : CacheType (default: CacheType.ALL)
                Type of cache to clear
            `lang_code` : LangCode | None (default: None)
                Optional language code to limit clearing to specific language

        ### Returns
            `dict` : Dictionary with counts of cleared items

        ### Example
            ```python
            from opgg import OPGG
            from opgg.params import CacheType, LangCode

            opgg = OPGG()

            # Clear all cache
            cleared = opgg.clear_cache()

            # Clear only champion cache
            cleared = opgg.clear_cache(cache_type=CacheType.CHAMPIONS)

            # Clear champion cache for Korean language only
            cleared = opgg.clear_cache(cache_type=CacheType.CHAMPIONS, lang_code=LangCode.KOREAN)
            ```
        """
        return self._cacher.clear_cache(cache_type=cache_type, lang_code=lang_code)

    def get_champion_by(
        self,
        by: By,
        value: str | int,
        lang_code: LangCode = LangCode.ENGLISH,
        force_refresh: bool = False,
    ) -> Champion | list[Champion]:
        """
        Retrieve a specific champion or champions by ID or name.

        ### Parameters
            `by` : By
                Search method - By.ID or By.NAME
            `value` : str | int
                Champion ID (int) or name (str) to search for
            `lang_code` : LangCode (default: LangCode.ENGLISH)
                The language code for champion data localization
            `force_refresh` : bool (default: False)
                If True, bypass cache and fetch fresh data from API

        ### Returns
            `Champion | list[Champion]` : Single champion object or list if multiple matches found (name search only)

        ### Example
            ```python
            from opgg import OPGG
            from opgg.params import By, LangCode

            opgg = OPGG()

            # Get champion by ID
            aatrox = opgg.get_champion_by(By.ID, 266)

            # Force refresh champion by ID
            aatrox = opgg.get_champion_by(By.ID, 266, force_refresh=True)

            # Get champion by name
            aatrox = opgg.get_champion_by(By.NAME, "Aatrox", LangCode.ENGLISH)
            ```
        """
        if by == By.ID:
            # Check cache unless force refresh is requested
            if not force_refresh:
                cached_champion = self._cacher.get_cached_champion_by_id(
                    value, lang_code, ttl_seconds=self._champion_cache_ttl
                )
                if cached_champion:
                    self.logger.info("Returning cached champion for ID %s", value)
                    return cached_champion
            else:
                self.logger.info(
                    "Force refresh requested; bypassing cache for champion ID %s", value
                )

            # Fetch from API
            get_champ_by_id_params: GenericReqParams = {
                "base_api_url": _CHAMPION_BY_ID_API_URL,
                "headers": self.headers,
            }

            champ_data = asyncio.run(
                Utils._fetch_champion_by_id(value, get_champ_by_id_params, lang_code)
            )
            champion = Champion(**champ_data)
            self._cacher.cache_champs([champion], lang_code)
            return champion

        elif by == By.NAME:
            # Check cache unless force refresh is requested
            if not force_refresh:
                self.logger.info(f"Attempting to satisfy '{value}' from cache...")

                cached_matches = self._cacher.get_cached_champions_by_name(
                    value, lang_code, ttl_seconds=self._champion_cache_ttl
                )
                if cached_matches:
                    if len(cached_matches) == 1:
                        return cached_matches[0]
                    return cached_matches

                champ_id = self._cacher.get_champ_id_by_name(value)
                if champ_id is not None:
                    cached = self._cacher.get_cached_champion_by_id(
                        champ_id, lang_code, ttl_seconds=self._champion_cache_ttl
                    )
                    if cached:
                        return cached

                    get_champ_by_id_params: GenericReqParams = {
                        "base_api_url": _CHAMPION_BY_ID_API_URL,
                        "headers": self.headers,
                    }
                    champ_data = asyncio.run(
                        Utils._fetch_champion_by_id(
                            champ_id, get_champ_by_id_params, lang_code
                        )
                    )
                    champion = Champion(**champ_data)
                    self._cacher.cache_champs([champion], lang_code)
                    return champion
            else:
                self.logger.info(
                    "Force refresh requested; bypassing cache for champion name '%s'",
                    value,
                )

            # Fetch from roster (either because not cached or force refresh)
            self.logger.info(f"Champion {value} not cached. Fetching roster...")

            all_champs = self.get_all_champions(
                lang_code=lang_code, force_refresh=force_refresh
            )
            champs = [
                champ
                for champ in all_champs
                if champ.name and value.lower() in champ.name.lower()
            ]

            if len(champs) == 0:
                raise ValueError(f"Champion {value} not found")

            if len(champs) > 1:
                return champs

            self._cacher.cache_champs([champs[0]], lang_code)
            return champs[0]

        else:
            raise ValueError(f"Invalid value for by: {by}")

    def get_champion_stats(
        self,
        tier: Tier = Tier.EMERALD_PLUS,
        version: str | None = None,
        region: StatsRegion = StatsRegion.GLOBAL,
        queue_type: Queue = Queue.SOLO,
        season_id: int | None = None,
    ) -> dict:
        """
        Retrieve champion statistics for ranked games from OPGG Champion API.

        ### Parameters
            `tier` : Tier (default: Tier.EMERALD_PLUS)
                Rank tier to filter statistics
            `version` : str | None (default: None)
                Game version to filter statistics (e.g., "15.22"). If None, uses latest version.
            `region` : StatsRegion (default: StatsRegion.GLOBAL)
                Region to get statistics for
            `queue_type` : Queue (default: Queue.SOLO)
                Queue/game type filter. Supports Solo/Flex/Arena queues.
            `season_id` : int | None (default: None)
                Season identifier (from `/meta/seasons`) for historical split data. When omitted, OPGG returns the latest split.

        ### Returns
            `dict` : Dictionary containing champion statistics data including win rates, pick rates, ban rates, etc.

        ### Example
            ```python
            from opgg import OPGG
            from opgg.params import Queue, StatsRegion, Tier

            opgg = OPGG()

            # Get global Emerald+ statistics
            stats = opgg.get_champion_stats(tier=Tier.EMERALD_PLUS)

            # Get specific version, region, queue, and split
            kr_stats = opgg.get_champion_stats(
                tier=Tier.DIAMOND_PLUS,
                version="15.22",
                region=StatsRegion.GLOBAL,
                queue_type=Queue.SOLO,
                season_id=25,  # 2024 Split 1
            )
            ```
        """
        tier_value = tier.value if isinstance(tier, Tier) else str(tier)
        region_value = region.value if isinstance(region, StatsRegion) else str(region)

        url = _CHAMPION_STATS_API_URL.format(region=region_value, tier=tier_value)

        query_params: list[str] = []

        if version:
            query_params.append(f"version={version}")

        queue_value = queue_type.value if isinstance(queue_type, Queue) else queue_type
        if queue_value:
            query_params.append(f"queue_type={queue_value}")

        if season_id is not None:
            query_params.append(f"season_id={season_id}")

        if query_params:
            url += f"&{'&'.join(query_params)}"

        self.logger.info(
            "Fetching champion stats for tier=%s, region=%s, version=%s, queue_type=%s, season_id=%s",
            tier_value,
            region_value,
            version,
            queue_value,
            season_id,
        )

        champion_stats_params: GenericReqParams = {
            "base_api_url": url,
            "headers": self.headers,
        }

        return asyncio.run(Utils._fetch_champion_stats(champion_stats_params))

    def get_versions(
        self,
        lang_code: LangCode = LangCode.ENGLISH,
        force_refresh: bool = False,
    ) -> dict | list:
        """
        Retrieve available game versions from OPGG Champion API.

        ### Parameters
            `lang_code` : LangCode (default: LangCode.ENGLISH)
                The language code for version data localization.
            `force_refresh` : bool (default: False)
                If True, bypass cache and fetch fresh data from API.

        ### Returns
            `dict | list` : Dictionary or list containing available game versions and related metadata.

        ### Example
            ```python
            from opgg import OPGG
            from opgg.params import LangCode

            opgg = OPGG()

            # Get available versions (from cache if available)
            versions = opgg.get_versions()

            # Force refresh from API
            versions = opgg.get_versions(force_refresh=True)

            # Get versions with Korean localization
            kr_versions = opgg.get_versions(lang_code=LangCode.KOREAN)
            ```
        """
        # Check cache first unless force refresh is requested
        if not force_refresh:
            cached_versions = self._cacher.get_cached_versions(
                lang_code, ttl_seconds=self._champion_cache_ttl
            )
            if cached_versions:
                self.logger.info(
                    "Returning cached versions data for lang=%s", lang_code
                )
                return cached_versions
        else:
            self.logger.info(
                "Force refresh requested; bypassing cached versions for lang=%s",
                lang_code,
            )

        # Fetch from API
        url = _VERSIONS_API_URL.format(hl=lang_code.value)
        self.logger.info(f"Fetching game versions from API with language={lang_code}")

        versions_params: GenericReqParams = {
            "base_api_url": url,
            "headers": self.headers,
        }

        versions_data = asyncio.run(Utils._fetch_versions(versions_params))

        # Cache the fetched data
        self._cacher.cache_versions(versions_data, lang_code)

        return versions_data

    def get_keywords(
        self,
        lang_code: LangCode = LangCode.ENGLISH,
        force_refresh: bool = False,
    ) -> list[Keyword]:
        """
        Retrieve OP.GG keyword metadata (Leader, Struggle, etc.) for OP Score analysis.

        ### Parameters
            `lang_code` : LangCode (default: LangCode.ENGLISH)
                The language code for keyword localization.
            `force_refresh` : bool (default: False)
                If True, bypass cache and fetch fresh keyword data from API.

        ### Returns
            `list[Keyword]` : List of keyword entries describing OP score highlights.
        """
        lang_value = (
            lang_code.value if isinstance(lang_code, LangCode) else str(lang_code)
        )

        if not force_refresh:
            cached_keywords = self._cacher.get_cached_keywords(
                lang_code, ttl_seconds=self._champion_cache_ttl
            )
            if cached_keywords:
                self.logger.info(
                    "Returning %d cached keywords for lang=%s",
                    len(cached_keywords),
                    lang_value,
                )
                return [Keyword(**entry) for entry in cached_keywords]
        else:
            self.logger.info(
                "Force refresh requested; bypassing cached keywords for lang=%s",
                lang_value,
            )

        url = _KEYWORDS_API_URL.format(hl=lang_code.value)
        self.logger.info(
            "Fetching keywords from API with language=%s (url=%s)", lang_value, url
        )

        keywords_params: GenericReqParams = {
            "base_api_url": url,
            "headers": self.headers,
        }

        keywords_data = asyncio.run(Utils._fetch_keywords(keywords_params))

        if isinstance(keywords_data, dict):
            if isinstance(keywords_data.get("data"), list):
                keywords_list = keywords_data.get("data", [])
            elif isinstance(keywords_data.get("keywords"), list):
                keywords_list = keywords_data.get("keywords", [])
            else:
                keywords_list = []
        elif isinstance(keywords_data, list):
            keywords_list = keywords_data
        else:
            keywords_list = []

        if not keywords_list:
            self.logger.warning(
                "Keyword API returned no entries for lang=%s. Raw payload=%s",
                lang_value,
                keywords_data,
            )

        keyword_models = [Keyword(**entry) for entry in keywords_list]

        if keyword_models:
            self._cacher.cache_keywords(keywords_list, lang_code)

        return keyword_models

    def get_all_seasons(
        self,
        lang_code: LangCode = LangCode.ENGLISH,
        force_refresh: bool = False,
    ) -> list[SeasonMeta]:
        """
        Retrieve available seasons from OPGG Summoner API.

        ### Parameters
            `lang_code` : LangCode (default: LangCode.ENGLISH)
                The language code for season data localization.
            `force_refresh` : bool (default: False)
                If True, bypass cache and fetch fresh data from API.

        ### Returns
            `list[SeasonMeta]` : Collection containing available seasons and related metadata.

        ### Example
            ```python
            from opgg import OPGG
            from opgg.params import LangCode

            opgg = OPGG()

            # Get available seasons (from cache if available)
            seasons = opgg.get_all_seasons()

            # Force refresh from API
            seasons = opgg.get_all_seasons(force_refresh=True)

            # Get seasons with Korean localization
            kr_seasons = opgg.get_all_seasons(lang_code=LangCode.KOREAN)
            ```
        """
        lang_value = (
            lang_code.value if isinstance(lang_code, LangCode) else str(lang_code)
        )

        if not force_refresh:
            in_memory = self._season_meta_cache.get(lang_value)
            if in_memory:
                self.logger.info(
                    "Returning in-memory seasons data for lang=%s", lang_code
                )
                return list(in_memory.values())

            cached_seasons = self._cacher.get_cached_seasons(
                lang_code, ttl_seconds=self._champion_cache_ttl
            )
            if cached_seasons:
                self.logger.info("Returning cached seasons data for lang=%s", lang_code)
                return self._hydrate_season_meta(cached_seasons, lang_value)
        else:
            self.logger.info(
                "Force refresh requested; bypassing cached seasons for lang=%s",
                lang_code,
            )

        if not force_refresh:
            self.logger.info("No cached season data available for lang=%s", lang_code)

        # Fetch from API
        url = _SEASONS_API_URL.format(hl=lang_code.value)
        self.logger.info(f"Fetching seasons from API with language={lang_code}")

        seasons_params: GenericReqParams = {
            "base_api_url": url,
            "headers": self.headers,
        }

        seasons_data = asyncio.run(Utils._fetch_seasons(seasons_params))
        normalized_payload = self._normalize_seasons_payload(seasons_data)

        # Cache the fetched data
        self._cacher.cache_seasons(normalized_payload, lang_code)

        return self._hydrate_season_meta(normalized_payload, lang_value)

    def _normalize_seasons_payload(self, seasons_data) -> list[dict]:
        """Normalize raw seasons payload into a list of dictionaries."""
        if not seasons_data:
            return []

        if isinstance(seasons_data, list):
            return [s for s in seasons_data if isinstance(s, dict)]

        if isinstance(seasons_data, dict):
            seasons = seasons_data.get("seasons")
            if isinstance(seasons, list):
                return [s for s in seasons if isinstance(s, dict)]
            return [seasons_data]

        self.logger.warning(
            "Unexpected seasons payload type: %s. Returning empty list.",
            type(seasons_data),
        )
        return []

    def _hydrate_season_meta(
        self, payload: list[dict], lang_value: str
    ) -> list[SeasonMeta]:
        """Convert normalized payload into SeasonMeta objects and update cache."""
        if not payload:
            self._season_meta_cache.pop(lang_value, None)
            return []

        meta_map: dict[int, SeasonMeta] = {}
        hydrated: list[SeasonMeta] = []

        for season_entry in payload:
            if isinstance(season_entry, SeasonMeta):
                meta = season_entry
            elif isinstance(season_entry, dict):
                try:
                    meta = SeasonMeta(**season_entry)
                except Exception as exc:  # pragma: no cover - defensive logging
                    self.logger.error(
                        "Failed to hydrate SeasonMeta for lang=%s: %s",
                        lang_value,
                        exc,
                    )
                    continue
            else:
                self.logger.warning(
                    "Skipping unexpected season entry type '%s' while hydrating metadata.",
                    type(season_entry),
                )
                continue

            hydrated.append(meta)
            if meta.id is not None:
                meta_map[meta.id] = meta

        if meta_map:
            self._season_meta_cache[lang_value] = meta_map
        else:
            self._season_meta_cache.pop(lang_value, None)

        return hydrated

    def _get_season_meta_map(self, lang_code: LangCode) -> dict[int, SeasonMeta]:
        """Return a mapping of season_id -> SeasonMeta for the requested language."""
        lang_value = (
            lang_code.value if isinstance(lang_code, LangCode) else str(lang_code)
        )
        meta_map = self._season_meta_cache.get(lang_value)
        if meta_map is not None:
            return meta_map

        seasons = self.get_all_seasons(lang_code=lang_code)
        if seasons:
            return self._season_meta_cache.get(lang_value, {})
        return {}

    def _attach_season_meta(
        self,
        summoner: Summoner | list[Summoner] | None,
        lang_code: LangCode,
    ) -> None:
        """Enrich a `Summoner` or list of `Summoner` objects with SeasonMeta info."""
        if summoner is None:
            return

        if isinstance(summoner, list):
            for s in summoner:
                self._attach_season_meta(s, lang_code)
            return

        previous_seasons = getattr(summoner, "previous_seasons", None)
        if not previous_seasons:
            return

        meta_map = self._get_season_meta_map(lang_code)
        if not meta_map:
            return

        for season in previous_seasons:
            season_id = getattr(season, "season_id", None)
            if season_id is None:
                continue
            season.meta = meta_map.get(season_id)
