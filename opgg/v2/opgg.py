import os
import logging
import asyncio

from datetime import datetime
import pprint
from typing import Literal
from fake_useragent import UserAgent

from opgg.v2.champion import Champion
from opgg.v2.game import Game, LiveGame
from opgg.v2.summoner import Summoner
from opgg.v2.types.response import LiveGameResponse, UpdateResponse
from opgg.v2.utils import Utils
from opgg.v2.cacher import Cacher
from opgg.v2.params import By, LangCode, Region, GenericReqParams
from opgg.v2.search_result import SearchResult


class OPGG:
    """
    ### OPGG.py

    Copyright (c) 2023-2024, ShoobyDoo

    License: BSD-3-Clause, See LICENSE for more details.
    """

    __author__ = "ShoobyDoo"
    __license__ = "BSD-3-Clause"

    def __init__(self) -> None:
        self.BYPASS_API_URL = "https://lol-web-api.op.gg/api/v1.0/internal/bypass"
        self.SEARCH_API_URL = f"{self.BYPASS_API_URL}/summoners/v2/{{region}}/autocomplete?gameName={{summoner_name}}&tagline={{tagline}}"
        self.SUMMARY_API_URL = (
            f"{self.BYPASS_API_URL}/summoners/{{region}}/{{summoner_id}}/summary"
        )
        self.GAMES_API_URL = f"{self.BYPASS_API_URL}/games/{{region}}/summoners/{{summoner_id}}?&limit={{limit}}&game_type={{game_type}}&hl={{hl}}"
        self.RENEW_API_URL = (
            f"{self.BYPASS_API_URL}/summoners/{{region}}/{{summoner_id}}/renewal"
        )
        self.CHAMPIONS_API_URL = f"{self.BYPASS_API_URL}/meta/champions?hl={{hl}}"
        self.CHAMPION_BY_ID_API_URL = (
            f"{self.BYPASS_API_URL}/meta/champions/{{champion_id}}?hl={{hl}}"
        )
        self.LIVE_GAME_URL = (
            f"{self.BYPASS_API_URL}/spectates/{{region}}/{{summoner_id}}?hl={{hl}}"
        )

        # FIGURE OUT HOW TO FIND THESE PAYLOADS:
        # - seasonById
        # - spells

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
            format="[%(asctime)s][%(name)s->%(module)-15s:%(lineno)10d][%(levelname)-7s] : %(message)s",
            datefmt="%d-%b-%y %H:%M:%S",
            level=logging.INFO,
        )
        # ===== SETUP END =====

        # allow the user to interact with the logger
        self._logger = logging.getLogger("OPGG.py")

        self.logger.info(
            f"OPGG.__init__(BYPASS_API_URL={self.BYPASS_API_URL}, "
            f"headers={self._headers})"
        )

        # at object creation, setup and query the cache
        self._cacher = Cacher()
        self._cacher.setup()

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

    # /AUTOCOMPLETE
    def search(
        self,
        query: str,
        region: Region = Region.ANY,
        returns: Literal["simple", "full"] = "full",
    ) -> list[SearchResult]:
        """
        Search for League of Legends summoners by name across one or all regions.

        #### Args:
        - `query` (`str`): Summoner name to search for. Can include tagline (e.g., "name#tag")
        - `region` (`Region`, optional): Specific region to search in. Defaults to `Region.ANY` which searches all regions concurrently.

        #### Returns:
            `list[SearchResult]`: List of `SearchResult` objects containing the found summoners.
            Each `SearchResult` object contains formatted summoner data and the region it was found in.

        #### Example:
        ```python
        >>> opgg = OPGG()
        >>>
        >>> results = opgg.search("faker", Region.KR) # Search specific region (recommended)
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

        self.logger.info(f"Starting summoner search for '{query}' in region '{region}'")

        search_params: GenericReqParams = {
            "base_api_url": self.SEARCH_API_URL,
            "headers": self.headers,
        }

        if region == Region.ANY:
            self.logger.info("Searching all regions...")
            results = asyncio.run(Utils._search_all_regions(query, search_params))
        else:
            self.logger.info(f"Searching specific region: {region}")
            results = asyncio.run(
                Utils._single_region_search(
                    query,
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

        if returns == "profile":
            # set each summoner property in the search_results array
            # to the corresponding Summoner object
            self.logger.info(
                f"Fetching profiles for {len(search_results)} summoners..."
            )

            # This call is done passing the array because if there are multiple, we want the benefit of concurrency
            # provided by the asychonous nature of the call
            summoners = self.get_summoner(search_results)

            # We then build the search_results array with the Summoner objects
            for sr, s in zip(search_results, summoners):
                sr.summoner = s

        return search_results

    def get_summoner(
        self,
        search_result: SearchResult | list[SearchResult] = None,
        summoner_id: str | list[str] = None,
        region: Region | list[Region] = None,
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
            self.logger.info(f"Fetching profile for summoner result: {search_result}")
            profile_data = asyncio.run(
                Utils._fetch_profile(
                    search_result.summoner.summoner_id,
                    params={
                        "base_api_url": self.SUMMARY_API_URL.format_map(
                            {
                                "region": search_result.region,
                                "summoner_id": search_result.summoner.summoner_id,
                            }
                        ),
                        "headers": self.headers,
                    },
                )
            )
            return Summoner(**profile_data["summoner"])

        elif isinstance(search_result, list):
            self.logger.info(
                f"Fetching profiles for {len(search_result)} summoner results"
            )
            self.logger.debug(
                f"Raw summoner results: \n{pprint.pformat(search_result)}"
            )
            profile_data = asyncio.run(
                Utils._fetch_profile_multiple(
                    {
                        "base_api_url": self.SUMMARY_API_URL,
                        "headers": self.headers,
                    },
                    search_result,
                )
            )
            return [Summoner(**profile["summoner"]) for profile in profile_data]

        else:
            raise ValueError("Invalid type for search_result")

    def get_recent_games(
        self,
        search_result: SearchResult | list[SearchResult] = None,
        summoner_id: str | list[str] = None,
        region: Region | list[Region] = None,
        results: int = 15,
        game_type: Literal["total", "ranked", "normal"] = "total",
        lang_code=LangCode.ENGLISH,
    ) -> list[Game] | list[list[Game]]:

        if search_result is None and summoner_id is not None and region is not None:
            if isinstance(summoner_id, str) and isinstance(region, Region):
                search_result = SearchResult(
                    {
                        "summoner": Summoner(**{"summoner_id": summoner_id}),
                        "region": region,
                    }
                )
            elif isinstance(summoner_id, list) and isinstance(region, list):
                search_result = [
                    SearchResult(
                        {"summoner": Summoner(**{"summoner_id": sid}), "region": reg}
                    )
                    for sid, reg in zip(summoner_id, region)
                ]
            else:
                raise ValueError("Mismatched types for summoner_id and region")

        if isinstance(search_result, SearchResult):
            self.logger.info(
                f'Fetching {results} recent games of type "{game_type}" for summoner result: {search_result}'
            )
            game_params: GenericReqParams = {
                "base_api_url": self.GAMES_API_URL.format_map(
                    {
                        "region": search_result.region,
                        "summoner_id": search_result.summoner.summoner_id,
                        "limit": results,
                        "game_type": game_type,
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
                f'Fetching {results} recent games of type "{game_type}" for {len(search_result)} summoner results'
            )
            game_params_list = [
                {
                    "base_api_url": self.GAMES_API_URL.format_map(
                        {
                            "region": sr.region,
                            "summoner_id": sr.summoner.summoner_id,
                            "limit": results,
                            "game_type": game_type,
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

    def update(self, search_result: SearchResult) -> UpdateResponse:
        """
        Send an update request to fetch the latest details for a given summoner (id).

        #### Note: `This can take several seconds to complete. Assuming there is an update to the profile, this function will not return until the update is complete.`

        ### Parameters
            search_result : `SearchResult`
                Pass a SearchResult object to be updated

        ### Returns
            `UpdateResponse` : Returns an object with the update response payload.

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

        update_params: GenericReqParams = {
            "base_api_url": self.RENEW_API_URL,
            "headers": self.headers,
        }

        return asyncio.run(Utils._update(search_result, update_params))

    def get_all_champions(
        self, lang_code: LangCode = LangCode.ENGLISH
    ) -> list[Champion]:
        get_champs_params: GenericReqParams = {
            "base_api_url": self.CHAMPIONS_API_URL.format_map({"hl": lang_code}),
            "headers": self.headers,
        }

        champions_list = asyncio.run(Utils._fetch_all_champions(get_champs_params))
        champions_list_objs = [Champion(**champ) for champ in champions_list]

        self.logger.info(f"Got {len(champions_list_objs)} champions")

        if (len(champions_list_objs)) != self._cacher.get_cached_champs_count():
            self.logger.info(
                "Champ response has more records than are saved. Rebuilding cache..."
            )
            self._cacher.cache_champs(champions_list_objs)

        return champions_list_objs

    def get_champion_by(
        self, by: By, value: str | int, lang_code: LangCode = LangCode.ENGLISH
    ) -> Champion | list[Champion]:
        if by == By.ID:
            get_champ_by_id_params: GenericReqParams = {
                "base_api_url": self.CHAMPION_BY_ID_API_URL,
                "headers": self.headers,
            }

            champ = asyncio.run(
                Utils._fetch_champion_by_id(value, get_champ_by_id_params, lang_code)
            )

        elif by == By.NAME:
            self.logger.info(f"Fetching {value} from cache...")

            champ = self._cacher.get_champ_id_by_name(value)

            if champ == None:
                self.logger.info(f"Champion {value} not found in cache. Fetching...")

                all_champs = self.get_all_champions()

                # Do a loose search by name
                champs = [
                    champ for champ in all_champs if value.lower() in champ.name.lower()
                ]

                if len(champs) == 0:
                    raise ValueError(f"Champion {value} not found")

                if len(champs) > 1:
                    return [Champion(**champ) for champ in champs]

                return Champion(**champs[0])

            else:
                get_champ_by_id_params: GenericReqParams = {
                    "base_api_url": self.CHAMPION_BY_ID_API_URL,
                    "headers": self.headers,
                }

                champ = asyncio.run(
                    Utils._fetch_champion_by_id(
                        champ, get_champ_by_id_params, lang_code
                    )
                )

        else:
            raise ValueError(f"Invalid value for by: {by}")

        return Champion(**champ)

    def get_live_game(
        self, search_result: SearchResult, lang_code: LangCode = LangCode.ENGLISH
    ) -> LiveGameResponse:
        """
        Get the live game data for a given summoner.

        ### Parameters
            search_result : `SearchResult`
                Pass a SearchResult object to get the live game data

        ### Returns
            `LiveGameResponse` : Returns an object with the live game data payload if available.
        """

        self.logger.info(f"Fetching live game data for {search_result}")

        live_game_params: GenericReqParams = {
            "base_api_url": self.LIVE_GAME_URL.format_map(
                {
                    "region": search_result.region,
                    "summoner_id": search_result.summoner.summoner_id,
                    "hl": lang_code,
                }
            ),
            "headers": self.headers,
        }

        live_game_data = asyncio.run(Utils._fetch_live_game(live_game_params))

        return LiveGameResponse(**live_game_data)
