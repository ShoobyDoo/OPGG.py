import json
import logging
import asyncio
import aiohttp
from typing import List, Tuple
from enum import Enum

from opgg.v2.params import Region

logger = logging.getLogger("OPGG.py")


class Utils:
    """
    ### utils.py
    A collection of static utility helper methods that perform various opgg and league specific tasks such as fetching champions, seasons, etc.

    Copyright (c) 2023-2024, ShoobyDoo
    License: BSD-3-Clause, See LICENSE for more details.
    """

    @staticmethod
    def read_local_json(file: str) -> dict[str, any]:
        """
        Read and parse a local JSON file.

        Args:
            `file` (`str`): Path to the JSON file

        Returns:
            `dict[str, any]`: Parsed JSON data as a dictionary
        """
        with open(file, "r") as f:
            return json.loads(f.read())

    @staticmethod
    async def _search_region(
        session: aiohttp.ClientSession,
        query: str,
        region: Region,
        search_api_url: str,
        headers: dict,
    ) -> Tuple[Region, List[dict]]:
        """
        `[Internal Helper Method]` Search for a summoner in a specific region using the OP.GG API.

        Args:
            `session` (`aiohttp.ClientSession`): Active session for making requests
            `query` (`str`): Summoner name to search for
            `region` (`Region`): Region to search in
            `bypass_api_url` (`str`): Base API URL for bypass requests
            `search_api_url` (`str`): Full search API URL template
            `headers` (`dict`): Headers to use for the request

        Returns:
            `Tuple[Region, List[dict]]`: Region and list of found summoners
        """
        data = {
            "summoner_name": query,
            "region": str(region),
            "tagline": "",
        }

        if "#" in query:
            summoner_name, tagline = query.split("#")
            data["summoner_name"] = summoner_name
            data["tagline"] = tagline

        logger.debug(f"Constructed search data: {data}")
        search_url = search_api_url.format_map(data)
        logger.info(
            f"Sending search request to OPGG API... (API_URL = {search_url}, HEADERS = {headers})"
        )

        try:
            async with session.get(search_url, headers=headers) as res:
                logger.debug(f"Response status: {res.status}")
                logger.debug(f"Response headers: {dict(res.headers)}")

                if res.status == 200:
                    content: dict = await res.json()
                    logger.debug(f"Raw response payload: {content}")
                    data = content.get("data", [])
                    logger.info(f"Found {len(data)} results for region {region}")
                res.raise_for_status()
        except Exception as e:
            logger.error(f"Error searching region {region}: {str(e)}")
            data = []

        return region, data

    @staticmethod
    async def _search_all_regions(
        query: str, search_api_url: str, headers: dict
    ) -> List[dict]:
        """
        `[Internal Helper Method]` Concurrently searches for a summoner across all available regions.

        Args:
            `query` (`str`): Summoner name to search for
            `bypass_api_url` (`str`): Base API URL for bypass requests
            `search_api_url` (`str`): Full search API URL template
            `headers` (`dict`): Headers to use for the request

        Returns:
            `List[dict]`: List of unique summoner results across all regions
        """
        logger.info(f"Starting concurrent search across all regions for query: {query}")

        async with aiohttp.ClientSession() as session:
            tasks = [
                Utils._search_region(session, query, region, search_api_url, headers)
                for region in Region
                if region != Region.ANY
            ]
            logger.debug(f"Created {len(tasks)} search tasks")

            results = await asyncio.gather(*tasks)
            logger.debug(f"Raw results from all regions: {results}")

            # Flatten results and remove duplicates
            all_results = []
            seen = set()
            for region, data in results:
                logger.debug(f"Processing {len(data)} results from region {region}")

                result: dict
                for result in data:
                    unique_id = result.get("summoner_id")
                    if unique_id not in seen:
                        seen.add(unique_id)
                        all_results.append(
                            {"region": region, "summoner_result": result}
                        )

            logger.info(f"Found {len(all_results)} unique results across all regions")
            return all_results

    @staticmethod
    async def _single_region_search(query: str, region: Region, search_api_url: str, headers: dict):
        async with aiohttp.ClientSession() as session:
            region, data = await Utils._search_region(
                session, query, region, search_api_url, headers
            )
            # Format results the same way as _search_all_regions
            return [{"region": region, "summoner_result": result} for result in data]

    @staticmethod
    async def _fetch_profile(summoner_id: str, summary_api_url: str, headers: dict):
        logger.info(
            f"Fetching profile for summoner ID: {summoner_id} (API_URL = {summary_api_url}, HEADERS = {headers})"
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(summary_api_url, headers=headers) as res:
                logger.debug(f"Response status: {res.status}")

                if res.status == 200:
                    content = await res.json()
                    logger.info(
                        f"Request to OPGG API was successful (Content Length: {len(str(content))})"
                    )
                    logger.debug(f"SUMMONER DATA AT /SUMMARY ENDPOINT:\n{content}\n")
                    return content["data"]

                res.raise_for_status()
