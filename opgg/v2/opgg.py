import os
import logging
import asyncio

from datetime import datetime
from fake_useragent import UserAgent

from opgg.v2.utils import Utils
from opgg.v2.cacher import Cacher
from opgg.v2.params import *
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
        self.SEARCH_API_URL = "{bypass}/summoners/v2/{region}/autocomplete?gameName={summoner_name}&tagline={tagline}".replace(
            "{bypass}", self.BYPASS_API_URL
        )
        self.SUMMARY_API_URL = (
            "{bypass}/summoners/{region}/{summoner_id}/summary".replace(
                "{bypass}", self.BYPASS_API_URL
            )
        )

        # DOUBLELIFT
        # https://lol-web-api.op.gg/api/v1.0/internal/bypass/spectates/na/AVCaop7DsXMxYghWRgonI__cn6cKD9EssfdNn-A8NhKvW2U?hl=en_US

        # THEBAUSFFS
        # https://lol-web-api.op.gg/api/v1.0/internal/bypass/spectates/euw/q0Oe1wEGx4s84dr8xfeZ3E28MH5HerwL-Y0r_i8PBPhotPF6?hl=en_US

        #  In game? If 404 then not in game, otherwise is in game?

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
    def region(self) -> Region:
        """
        A `Region` object representing the region to search for.
        """
        return self._region

    @region.setter
    def region(self, value: Region) -> None:
        self._region = value

    @property
    def headers(self) -> dict:
        """
        A `dict` representing the headers to send with the request.
        """
        return self._headers

    @headers.setter
    def headers(self, value: dict) -> None:
        self._headers = value

    def search(
        self,
        query: str,
        region: Region = Region.ANY,
    ) -> list[SearchResult]:
        """
        Search for League of Legends summoners by name across one or all regions.

        #### Args:
            `query` (`str`): Summoner name to search for. Can include tagline (e.g., "name#tag")
            `region` (`Region`, optional): Specific region to search in. Defaults to `Region.ANY` which searches all regions concurrently.

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

        # Common data structure used for URL formatting
        data = {
            "summoner_name": query,
            "region": str(region),
            "tagline": "",
        }

        # Handle tagline if present
        if "#" in query:
            summoner_name, tagline = query.split("#")
            data["summoner_name"] = summoner_name
            data["tagline"] = tagline

        if region == Region.ANY:
            self.logger.info("Searching all regions...")
            results = asyncio.run(
                Utils._search_all_regions(query, self.SEARCH_API_URL, self.headers)
            )

        else:
            self.logger.info(f"Searching specific region: {region}")

            # Run single region search
            results = asyncio.run(
                Utils._single_region_search(
                    query, region, self.SEARCH_API_URL, self.headers
                )
            )

        self.logger.debug(f"Final results before conversion: {results}")
        search_results = [SearchResult(result) for result in results]
        self.logger.info(f"Returning {len(search_results)} SearchResult objects")

        return search_results

    def fetch_profile(self, summoner_id: str, region: Region):
        self.logger.info(f"Fetching profile for summoner ID: {summoner_id}")

        profile_data = asyncio.run(
            Utils._fetch_profile(
                summoner_id,
                self.SUMMARY_API_URL.format_map(
                    {"region": region, "summoner_id": summoner_id}
                ),
                self.headers,
            )
        )

        print(profile_data)

    def fetch_games(self, summoner_id: str, count: int = 10):
        pass
