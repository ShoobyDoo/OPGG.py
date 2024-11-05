import os
import json
import logging
import requests
import traceback
import asyncio
import aiohttp
from typing import List

from box import Box
from datetime import datetime
from fake_useragent import UserAgent

from opgg.v2.cacher import Cacher
from opgg.v2.params import *
from opgg.v2.utils import Utils


class OPGG():
    """
    ### OPGG.py

    Copyright (c) 2023-2024, ShoobyDoo

    License: BSD-3-Clause, See LICENSE for more details.
    """

    __author__ = 'ShoobyDoo'
    __license__ = 'BSD-3-Clause'

    def __init__(self) -> None:
        self.BYPASS_API_URL = "https://lol-web-api.op.gg/api/v1.0/internal/bypass"

        self._ua = UserAgent()
        self._headers = {
            "User-Agent": self._ua.random
        }
        
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
            format='[%(asctime)s][%(name)s->%(module)s:%(lineno)-10d][%(levelname)-7s] : %(message)s',
            datefmt='%d-%b-%y %H:%M:%S',
            level=logging.INFO
        )
        # ===== SETUP END =====

        # allow the user to interact with the logger
        self._logger = logging.getLogger("OPGG.py")

        self.logger.info(
            f"OPGG.__init__(BYPASS_API_URL={self.BYPASS_API_URL}, " \
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


    async def _search_region(self, session: aiohttp.ClientSession, query: str, region: Region) -> List[dict]:
        """
        Helper method to search a specific region
        """
        search_url = "{bypass}/summoners/v2/{region}/autocomplete?gameName={summoner_name}&tagline={tagline}"

        data = {
            "summoner_name": query,
            "bypass": self.BYPASS_API_URL,
            "region": str(region),
            "tagline": ""
        }

        if '#' in query:
            summoner_name, tagline = query.split("#")
            data["summoner_name"] = summoner_name
            data["tagline"] = tagline

        search_url = search_url.format_map(data)
        self.logger.info(f"Sending search request to OPGG API... (API_URL = {search_url}, HEADERS = {self.headers})")

        try:
            async with session.get(search_url, headers=self.headers) as res:
                if res.status == 200:
                    content: dict = await res.json()
                    return content.get("data", [])
                res.raise_for_status()
        except Exception as e:
            self.logger.error(f"Error searching region {region}: {str(e)}")
            return []

    async def _search_all_regions(self, query: str) -> List[dict]:
        """Helper method to search all regions concurrently"""
        async with aiohttp.ClientSession() as session:
            tasks = [
                self._search_region(session, query, r) 
                for r in Region 
                if r != Region.ANY
            ]
            # Wait for all searches to complete
            results = await asyncio.gather(*tasks)
            
            # Flatten results and remove duplicates based on some unique identifier
            all_results = []
            seen = set()
            for region_results in results:
                for result in region_results:
                    # Assuming each result has a unique 'summoner_id' field
                    unique_id = result.get('summoner_id')
                    if unique_id not in seen:
                        seen.add(unique_id)
                        all_results.append(result)
            return all_results

    def search(self, query: str, region=Region.ANY):
        """
        ### Search for summoners across one or all regions.

        This method searches for League of Legends summoners by name and region. When region is set to
        `Region.ANY` (default), it performs concurrent searches across all available regions, which is
        significantly more resource-intensive but provides comprehensive results.

        ---

        ### Example:
            >>> opgg = OPGG()
            >>> # Search specific region (recommended)
            >>> results = opgg.search("faker", Region.KR)
            >>> # Search all regions (resource-intensive, searches ALL regions)
            >>> all_results = opgg.search("faker")
        """
        if region == Region.ANY:
            # Run async search across all regions
            return asyncio.run(self._search_all_regions(query))
        else:
            # Original single-region synchronous search
            search_url = "{bypass}/summoners/v2/{region}/autocomplete?gameName={summoner_name}&tagline={tagline}"

            data = {
                "summoner_name": query,
                "bypass": self.BYPASS_API_URL,
                "region": str(region),
                "tagline": ""
            }

            if '#' in query:
                summoner_name, tagline = query.split("#")
                data["summoner_name"] = summoner_name
                data["tagline"] = tagline

            search_url = search_url.format_map(data)
            self.logger.info(f"Sending search request to OPGG API... (API_URL = {search_url}, HEADERS = {self.headers})")

            res = requests.get(search_url, headers=self.headers)

            if res.status_code == 200:
                self.logger.info(f"Request to OPGG API was successful, parsing data (Content Length: {len(res.text)})...")
                self.logger.debug(f"Search payload:\n{res.text}")
                content = dict(res.json()).get("data", {})
            else:
                res.raise_for_status()

            return content

