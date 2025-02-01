import json
import logging
import asyncio
import aiohttp

from typing import Optional, Tuple, Any
from pprint import pformat

from opgg.v2.champion import Champion
from opgg.v2.params import LangCode, Region, GenericReqParams
from opgg.v2.search_result import SearchResult
from opgg.v2.summoner import Summoner


logger = logging.getLogger("OPGG.py")


class Utils:
    """
    ### utils.py
    A collection of static utility helper methods that perform various opgg and league specific tasks such as fetching champions, seasons, etc.

    Copyright (c) 2023-2024, ShoobyDoo
    License: BSD-3-Clause, See LICENSE for more details.
    """

    @staticmethod
    def read_local_json(file: str) -> dict[str, Any]:
        """
        Read and parse a local JSON file.

        Args:
            `file` (`str`): Path to the JSON file

        Returns:
            `dict[str, Any]`: Parsed JSON data as a dictionary
        """
        with open(file, "r") as f:
            return json.loads(f.read())

    @staticmethod
    def safe_get(obj, *attrs):
        for attr in attrs:
            try:
                obj = getattr(obj, attr)
            except AttributeError:
                return None
        return obj

    @staticmethod
    async def _search_region(
        session: aiohttp.ClientSession,
        query: str,
        region: Region,
        params: GenericReqParams,
    ) -> Tuple[Region, list[dict]]:
        """
        `[Internal Helper Method]` Search for a summoner in a specific region using the OP.GG API.

        Args:
            `session` (`aiohttp.ClientSession`): Active session for making requests
            `query` (`str`): Summoner name to search for
            `region` (`Region`): Region to search in
            `search_api_url` (`str`): Full search API URL template
            `headers` (`dict`): Headers to use for the request

        Returns:
            `Tuple[Region, list[dict]]`: Region and list of found summoners
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
        search_url = params["base_api_url"].format_map(data)
        logger.info(
            f"Sending search request to OPGG API... (API_URL = {search_url}, HEADERS = {params["headers"]})"
        )

        try:
            async with session.get(search_url, headers=params["headers"]) as res:
                logger.debug(f"Response status: {res.status}")
                logger.debug(f"Response headers: {dict(res.headers)}")

                if res.status == 200:
                    content: dict = await res.json()
                    logger.debug(f"Raw response payload: {pformat(content)}")
                    data = content.get("data", [])
                    logger.info(f"Found {len(data)} results for region {region}")
                res.raise_for_status()
        except Exception as e:
            logger.error(f"Error searching region {region}: {str(e)}")
            data = []

        return region, data

    @staticmethod
    async def _search_all_regions(query: str, params: GenericReqParams) -> list[dict]:
        """
        `[Internal Helper Method]` Concurrently searches for a summoner across all available regions.

        Args:
            `query` (`str`): Summoner name to search for
            `search_api_url` (`str`): Full search API URL template
            `headers` (`dict`): Headers to use for the request

        Returns:
            `list[dict]`: list of unique summoner results across all regions
        """
        logger.info(f"Starting concurrent search across all regions for query: {query}")

        async with aiohttp.ClientSession() as session:
            tasks = [
                Utils._search_region(
                    session,
                    query,
                    region,
                    params,
                )
                for region in Region
                if region != Region.ANY
            ]
            logger.debug(f"Created {len(tasks)} search tasks")

            results = await asyncio.gather(*tasks)
            logger.debug(f"Raw results from all regions: {pformat(results)}")

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
                        all_results.append({"region": str(region), "summoner": result})

            logger.info(f"Found {len(all_results)} unique results across all regions")
            return all_results

    @staticmethod
    async def _single_region_search(
        query: str, region: Region, params: GenericReqParams
    ):
        async with aiohttp.ClientSession() as session:
            region, data = await Utils._search_region(
                session,
                query,
                region,
                params,
            )
            # Format results the same way as _search_all_regions
            return [{"region": str(region), "summoner": result} for result in data]

    @staticmethod
    async def _fetch_profile(summoner_id: str, params: GenericReqParams):
        logger.info(
            f"Fetching profile for summoner ID: {summoner_id} (API_URL = {params['base_api_url']}, HEADERS = {params['headers']})"
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(
                params.get("base_api_url"), headers=params.get("headers")
            ) as res:
                logger.debug(f"Response status: {res.status}")

                if res.status == 200:
                    content: dict = await res.json()
                    logger.info(
                        f"Request to OPGG API was successful (Content Length: {len(str(content))})"
                    )
                    logger.debug(
                        f"SUMMONER DATA AT /SUMMARY ENDPOINT:\n{pformat(content)}\n"
                    )
                    return content.get("data", {})

                res.raise_for_status()

    @staticmethod
    async def _fetch_profile_multiple(
        params: GenericReqParams,
        search_results: list[SearchResult] = None,
        summoner_ids: Optional[list[str]] = None,
        regions: list[Region] = None,
    ):
        if search_results is None and summoner_ids is not None and regions is not None:
            search_results = [
                SearchResult(
                    {
                        "summoner": Summoner({"summoner_id": summoner_id}),
                        "region": region,
                    }
                )
                for summoner_id, region in zip(summoner_ids, regions)
            ]

        tasks = [
            Utils._fetch_profile(
                search_result.summoner.summoner_id,
                params={
                    "base_api_url": params["base_api_url"].format_map(
                        {
                            "summoner_id": search_result.summoner.summoner_id,
                            "region": search_result.region,
                        }
                    ),
                    "headers": params["headers"],
                },
            )
            for search_result in search_results
        ]

        return await asyncio.gather(*tasks)

    @staticmethod
    async def _fetch_recent_games(
        params: GenericReqParams,
    ):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                params["base_api_url"], headers=params["headers"]
            ) as res:
                logger.debug(f"Response status: {res.status}")

                if res.status == 200:
                    content: dict = await res.json()
                    logger.info(
                        f"Request to OPGG API was successful (Content Length: {len(str(content))})"
                    )
                    logger.debug(f"GAME DATA AT /GAMES ENDPOINT:\n{pformat(content)}\n")
                    return content.get("data", {})

                res.raise_for_status()

    @staticmethod
    async def _fetch_recent_games_multiple(
        params_list: list[GenericReqParams],
    ):
        tasks = [Utils._fetch_recent_games(params) for params in params_list]

        return await asyncio.gather(*tasks)

    @staticmethod
    async def _update(search_result: SearchResult, params: GenericReqParams):
        update_api_url = params["base_api_url"].format_map(
            {
                "region": search_result.region,
                "summoner_id": search_result.summoner.summoner_id,
            }
        )

        logger.info(
            f"Updating profile for summoner ID: {search_result.summoner.summoner_id}"
        )
        logger.debug(f"API URL: {update_api_url}")

        async with aiohttp.ClientSession() as session:
            async with session.post(
                update_api_url,
                headers=params["headers"],
            ) as res:
                logger.debug(f"Response status: {res.status}")

                if res.status in [200, 201, 202]:
                    return await res.json()
                else:
                    res.raise_for_status()

    @staticmethod
    async def _fetch_all_champions(params: GenericReqParams):
        async with aiohttp.ClientSession() as session:

            logger.debug(f"API URL: {params['base_api_url']}")

            async with session.get(
                params["base_api_url"], headers=params["headers"]
            ) as res:
                logger.debug(f"Response status: {res.status}")

                if res.status == 200:
                    content: dict = await res.json()
                    logger.info(
                        f"Request to OPGG API was successful (Content Length: {len(str(content))})"
                    )
                    logger.debug(
                        f"CHAMPION DATA AT /CHAMPIONS ENDPOINT:\n{pformat(content, sort_dicts=False)}\n"
                    )
                    return content.get("data", {})

                res.raise_for_status()

    @staticmethod
    async def _fetch_champion_by_id(
        id: int, params: GenericReqParams, lang_code: LangCode
    ):
        async with aiohttp.ClientSession() as session:
            fetch_champ_by_id_url = params["base_api_url"].format_map(
                {"champion_id": id, "hl": lang_code}
            )

            logger.debug(f"API URL: {fetch_champ_by_id_url}")

            async with session.get(
                fetch_champ_by_id_url,
                headers=params["headers"],
            ) as res:
                logger.debug(f"Response status: {res.status}")

                if res.status == 200:
                    content: dict = await res.json()
                    logger.info(
                        f"Request to OPGG API was successful (Content Length: {len(str(content))})"
                    )
                    logger.debug(
                        f"CHAMPION DATA AT /CHAMPIONS ENDPOINT:\n{pformat(content)}\n"
                    )
                    return content.get("data", {})

                res.raise_for_status()

    @staticmethod
    async def _fetch_live_game(params: GenericReqParams):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                params["base_api_url"], headers=params["headers"]
            ) as res:
                logger.debug(f"Response status: {res.status}")

                if res.status == 200:
                    content: dict = await res.json()
                    logger.info(
                        f"Request to OPGG API was successful (Content Length: {len(str(content))})"
                    )
                    logger.debug(
                        f"LIVE GAME DATA AT /spectate ENDPOINT:\n{pformat(content)}\n"
                    )

                elif res.status == 404:
                    content: dict = await res.json()

                    detail = content.get("detail", {}).get("detailMessage", "")
                    code = content.get("code", 404)
                    message = content.get("message", "Not found")

                    content = {
                        "status": code,
                        "detail": (
                            "Provided summoner is not in a live game!"
                            if detail == ""
                            else detail
                        ),
                        "message": message,
                    }

                else:
                    res.raise_for_status()

                # Success response example:
                # {
                #   "status": 200,
                #   "data": {...},
                #   "message": "Success"
                # }

                # Error response example:
                # {
                #   "status": 404,
                #   "message": "Not found",
                #   "detail": "Provided summoner is not in a live game!"
                # }

                content = {
                    "status": res.status,
                    "message": content.get("message", "Success"),
                    **({"data": content.get("data")} if res.status == 200 else {}),
                    **({"detail": content.get("detail")} if res.status != 200 else {}),
                }

                return content
