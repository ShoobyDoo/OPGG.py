import json
import logging
import asyncio
import aiohttp

from typing import Any
from pprint import pformat
from urllib.parse import quote_plus

from opgg.params import LangCode, Region, GenericReqParams
from opgg.search_result import SearchResult
from opgg.summoner import Summoner
from opgg.exceptions import (
    HTTPError,
    ClientHTTPError,
    ServerHTTPError,
    NotFoundError,
    RateLimitError,
    NetworkError,
    OPGGJSONDecodeError,
    ResponseValidationError,
)


logger = logging.getLogger("OPGG.py")


class ResponseHandler:
    """
    Standardized response handling for OPGG API calls.

    Provides consistent:
    - HTTP status code checking
    - JSON parsing with error handling
    - Response structure validation
    - Appropriate exception raising
    - Logging at correct levels
    """

    @staticmethod
    async def handle_response(
        response: aiohttp.ClientResponse,
        url: str,
        expected_keys: list[str] | None = None,
        allow_404: bool = False,
        logger_obj: logging.Logger | None = None,
    ) -> dict:
        """
        Process an aiohttp response with standardized error handling.

        Args:
            response: The aiohttp ClientResponse object
            url: The request URL (for error context)
            expected_keys: Optional list of keys to validate in response
            allow_404: If True, returns empty dict on 404 instead of raising
            logger_obj: Logger instance for logging

        Returns:
            dict: Parsed JSON response data

        Raises:
            NotFoundError: If 404 and allow_404=False
            RateLimitError: If 429
            ClientHTTPError: If 4xx (except 404, 429)
            ServerHTTPError: If 5xx
            OPGGJSONDecodeError: If response body isn't valid JSON
            ResponseValidationError: If expected_keys missing
        """
        log = logger_obj or logger
        status = response.status

        log.debug(f"Response status: {status} for URL: {url}")

        # Handle non-success status codes BEFORE trying to parse JSON
        if status >= 400:
            return await ResponseHandler._handle_error_status(
                response, url, status, allow_404, log
            )

        # Parse JSON with error handling
        try:
            content = await response.json()
        except (json.JSONDecodeError, aiohttp.ContentTypeError) as e:
            try:
                raw_text = await response.text()
            except Exception:
                raw_text = None
            log.error(f"JSON decode failed for {url}: {e}")
            raise OPGGJSONDecodeError(url, raw_text, original_error=e)

        # Validate structure if expected_keys provided
        if expected_keys:
            ResponseHandler._validate_structure(content, expected_keys, url)

        log.debug(f"Successfully parsed response from {url}")
        return content

    @staticmethod
    async def _handle_error_status(
        response: aiohttp.ClientResponse,
        url: str,
        status: int,
        allow_404: bool,
        log: logging.Logger,
    ) -> dict:
        """Handle HTTP error status codes."""
        # Try to get response body for context
        try:
            response_body = await response.text()
        except Exception:
            response_body = None

        headers = dict(response.headers) if response.headers else {}

        # 404 - Not Found
        if status == 404:
            if allow_404:
                log.debug(f"404 returned (allowed) for {url}")
                return {}
            raise NotFoundError(
                resource_type="resource",
                url=url,
                response_body=response_body,
                headers=headers,
            )

        # 429 - Rate Limited
        if status == 429:
            retry_after_header = headers.get("Retry-After")
            retry_seconds = (
                int(retry_after_header)
                if retry_after_header and retry_after_header.isdigit()
                else None
            )
            log.warning(f"Rate limited at {url}, retry after: {retry_after_header}")
            raise RateLimitError(
                retry_after=retry_seconds,
                url=url,
                response_body=response_body,
                headers=headers,
            )

        # 4xx - Client Errors
        if 400 <= status < 500:
            log.error(f"Client error {status} for {url}")
            raise ClientHTTPError(
                message=f"HTTP {status} error from OPGG API",
                status_code=status,
                url=url,
                response_body=response_body,
                headers=headers,
            )

        # 5xx - Server Errors
        if status >= 500:
            log.error(f"Server error {status} for {url}")
            raise ServerHTTPError(
                message=f"HTTP {status} server error from OPGG API",
                status_code=status,
                url=url,
                response_body=response_body,
                headers=headers,
            )

        # Shouldn't reach here, but safety fallback
        raise HTTPError(
            message=f"Unexpected HTTP {status} from OPGG API",
            status_code=status,
            url=url,
            response_body=response_body,
        )

    @staticmethod
    def _validate_structure(content: dict, expected_keys: list[str], url: str) -> None:
        """Validate response contains expected keys."""
        if not isinstance(content, dict):
            raise ResponseValidationError(url, "dict", type(content).__name__)

        missing = [k for k in expected_keys if k not in content]
        if missing:
            raise ResponseValidationError(
                url, f"keys {expected_keys}", f"missing {missing}"
            )

    @staticmethod
    def extract_data(
        content: dict,
        key: str = "data",
        default: Any = None,
    ) -> Any:
        """
        Safely extract data from response with default fallback.

        Args:
            content: Parsed JSON response
            key: Key to extract (default: "data")
            default: Default value if key missing

        Returns:
            Extracted value or default
        """
        return content.get(key, default)


class Utils:
    """
    ### utils.py
    A collection of static utility helper methods that perform various opgg and league specific tasks such as fetching champions, seasons, etc.
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
    def filter_results_with_summoner_id(
        search_results: list[SearchResult],
        logger_obj: logging.Logger | None = None,
    ) -> list[SearchResult]:
        """
        Filter out search results lacking a `summoner_id` while logging the skip.
        """
        if not search_results:
            return []

        logger_to_use = logger_obj or logger
        valid_results: list[SearchResult] = []

        for result in search_results:
            summoner = getattr(result, "summoner", None)
            summoner_id = getattr(summoner, "summoner_id", None)

            if not summoner_id:
                logger_to_use.critical(
                    "Search result is missing a summoner_id. Skipping region '%s' (Riot ID: %s#%s). Raw payload: %s",
                    getattr(result, "region", "unknown"),
                    getattr(summoner, "game_name", None),
                    getattr(summoner, "tagline", None),
                    pformat(
                        summoner.model_dump()
                        if hasattr(summoner, "model_dump")
                        else summoner
                    ),
                )
                continue

            valid_results.append(result)

        return valid_results

    @staticmethod
    async def _search_region(
        session: aiohttp.ClientSession,
        query: str,
        region: Region,
        params: GenericReqParams,
    ) -> tuple[Region, list[dict]]:
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
        # Construct riot_id with or without tagline based on query format
        if "#" in query:
            summoner_name, tagline = query.split("#")
            riot_id = f"{summoner_name}%23{tagline}"
        else:
            riot_id = query

        data = {
            "riot_id": riot_id,
            "region": str(region),
            "hl": params.get("lang_code", LangCode.ENGLISH),
        }

        logger.debug(f"Constructed search data: {data}")
        url = params["base_api_url"].format_map(data)
        logger.info(
            f"Sending search request to OPGG API... (API_URL = {url}, HEADERS = {params['headers']})"
        )

        async with session.get(url, headers=params["headers"]) as res:
            logger.debug(f"Response headers: {dict(res.headers)}")
            content = await ResponseHandler.handle_response(res, url)
            logger.debug(f"Raw response payload: {pformat(content)}")
            results = ResponseHandler.extract_data(content, "data", default=[])
            logger.info(f"Found {len(results)} results for region {region}")

        return region, results

    @staticmethod
    async def _search_all_regions(
        session: aiohttp.ClientSession, query: str, params: GenericReqParams
    ) -> list[dict]:
        """
        `[Internal Helper Method]` Concurrently searches for a summoner across all available regions.

        Args:
            `session` (`aiohttp.ClientSession`): Active session for making requests
            `query` (`str`): Summoner name to search for
            `search_api_url` (`str`): Full search API URL template
            `headers` (`dict`): Headers to use for the request

        Returns:
            `list[dict]`: list of unique summoner results across all regions
        """
        logger.info(f"Starting concurrent search across all regions for query: {query}")

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
        session: aiohttp.ClientSession,
        query: str,
        region: Region,
        params: GenericReqParams,
    ):
        region, data = await Utils._search_region(
            session,
            query,
            region,
            params,
        )
        # Format results the same way as _search_all_regions
        return [{"region": str(region), "summoner": result} for result in data]

    @staticmethod
    async def _fetch_profile(
        session: aiohttp.ClientSession, summoner_id: str, params: GenericReqParams
    ):
        url = params["base_api_url"]
        logger.info(
            f"Fetching profile for summoner ID: {summoner_id} (API_URL = {url}, HEADERS = {params['headers']})"
        )

        async with session.get(url, headers=params["headers"]) as res:
            content = await ResponseHandler.handle_response(res, url)
            logger.info(
                f"Request to OPGG API was successful (Content Length: {len(str(content))})"
            )
            logger.debug(f"SUMMONER DATA AT /SUMMARY ENDPOINT:\n{pformat(content)}\n")
            return ResponseHandler.extract_data(content, "data", default={})

    @staticmethod
    async def _fetch_profile_multiple(
        session: aiohttp.ClientSession,
        params: GenericReqParams,
        search_results: list[SearchResult] = None,
        summoner_ids: list[str] | None = None,
        regions: list[Region] = None,
    ):
        if search_results is None and summoner_ids is not None and regions is not None:
            search_results = [
                SearchResult(summoner=Summoner(summoner_id=summoner_id), region=region)
                for summoner_id, region in zip(summoner_ids, regions)
            ]

        tasks = [
            Utils._fetch_profile(
                session,
                search_result.summoner.summoner_id,
                params={
                    "base_api_url": params["base_api_url"].format_map(
                        {
                            "summoner_id": search_result.summoner.summoner_id,
                            "region": search_result.region,
                            "hl": params.get("lang_code", LangCode.ENGLISH),
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
        session: aiohttp.ClientSession,
        params: GenericReqParams,
    ):
        url = params["base_api_url"]
        logger.debug(f"API URL: {url}")

        async with session.get(url, headers=params["headers"]) as res:
            content = await ResponseHandler.handle_response(res, url)
            logger.info(
                f"Request to OPGG API was successful (Content Length: {len(str(content))})"
            )
            logger.debug(f"GAME DATA AT /GAMES ENDPOINT:\n{pformat(content)}\n")
            return ResponseHandler.extract_data(content, "data", default={})

    @staticmethod
    async def _fetch_recent_games_multiple(
        session: aiohttp.ClientSession,
        params_list: list[GenericReqParams],
    ):
        tasks = [Utils._fetch_recent_games(session, params) for params in params_list]

        return await asyncio.gather(*tasks)

    @staticmethod
    async def _fetch_recent_games_paginated(
        session: aiohttp.ClientSession,
        params: GenericReqParams,
        url_params: dict,
        total_results: int,
        max_per_request: int = 20,
    ) -> list[dict]:
        """
        Fetch recent games with pagination support for a single summoner.

        Fetches games in sequential pages using the last game's created_at timestamp
        as the ended_at parameter for the next page. Continues until either:
        - Accumulated enough games to satisfy total_results
        - Received fewer than max_per_request games (end of data)
        - A request fails (returns partial results accumulated so far)

        Args:
            session: Active aiohttp session for making requests
            params: Generic request parameters containing base URL template and headers
            url_params: URL parameters for template formatting (region, summoner_id, etc.)
            total_results: Total number of games to fetch
            max_per_request: Maximum games per API request (default 20)

        Returns:
            List of game dictionaries (may be less than total_results if data exhausted
            or if a mid-pagination error occurred)

        Raises:
            HTTPError, NetworkError: Only if first page fails (no data accumulated yet)
        """
        all_games = []
        games_remaining = total_results
        ended_at_param = ""

        while games_remaining > 0:
            # Determine how many games to request this page
            limit = min(games_remaining, max_per_request)

            # Build URL for this page using template
            url = params["base_api_url"].format_map(
                {
                    **url_params,
                    "limit": limit,
                    "ended_at": ended_at_param,
                }
            )

            logger.debug(f"Pagination request: {url}")

            async with session.get(url, headers=params["headers"]) as res:
                # Handle errors with partial success support
                try:
                    content = await ResponseHandler.handle_response(res, url)
                except (HTTPError, NetworkError) as e:
                    if all_games:
                        # Return partial data instead of failing completely
                        logger.warning(
                            f"Pagination stopped at {len(all_games)} games due to error: {e}"
                        )
                        break
                    # First page failed - propagate the error
                    raise

                page_games = ResponseHandler.extract_data(content, "data", default=[])

                if not page_games:
                    # No more games available
                    logger.info(
                        f"Pagination complete: received empty page after "
                        f"{len(all_games)} games"
                    )
                    break

                all_games.extend(page_games)
                games_remaining -= len(page_games)

                logger.info(
                    f"Fetched page with {len(page_games)} games "
                    f"({len(all_games)}/{total_results} total)"
                )

                # Check if we've reached end of data
                if len(page_games) < max_per_request:
                    logger.info(
                        f"Pagination complete: received {len(page_games)} games "
                        f"(less than {max_per_request})"
                    )
                    break

                # Extract timestamp from last game for next page
                last_game = page_games[-1]
                if "created_at" not in last_game:
                    logger.warning(
                        "Last game missing 'created_at' field, stopping pagination"
                    )
                    break

                # Use the raw ISO format string from API, URL-encode it
                ended_at_param = quote_plus(last_game["created_at"])
                logger.debug(f"Next page ended_at: {ended_at_param}")

        logger.info(
            f"Pagination complete: fetched {len(all_games)} games "
            f"(requested {total_results})"
        )
        return all_games

    @staticmethod
    async def _fetch_recent_games_multiple_paginated(
        session: aiohttp.ClientSession,
        params: GenericReqParams,
        url_params_list: list[dict],
        total_results: int,
        max_per_request: int = 20,
    ) -> list[list[dict]]:
        """
        Fetch recent games with pagination for multiple summoners concurrently.

        Each summoner's games are fetched sequentially (required for timestamp-based
        pagination), but different summoners are processed in parallel using
        asyncio.gather().

        Args:
            session: Active aiohttp session for making requests
            params: Generic request parameters containing base URL template and headers
            url_params_list: List of URL parameter dicts for template formatting
            total_results: Total number of games to fetch per summoner
            max_per_request: Maximum games per API request (default 20)

        Returns:
            List of lists, where each inner list contains game dictionaries for one summoner

        Raises:
            aiohttp.ClientError: If any request fails for any summoner
        """
        tasks = [
            Utils._fetch_recent_games_paginated(
                session=session,
                params=params,
                url_params=url_params,
                total_results=total_results,
                max_per_request=max_per_request,
            )
            for url_params in url_params_list
        ]

        return await asyncio.gather(*tasks)

    @staticmethod
    async def _update(
        session: aiohttp.ClientSession,
        search_result: SearchResult,
        params: GenericReqParams,
    ):
        url = params["base_api_url"].format_map(
            {
                "region": search_result.region,
                "summoner_id": search_result.summoner.summoner_id,
            }
        )

        logger.info(
            f"Updating profile for summoner ID: {search_result.summoner.summoner_id}"
        )
        logger.debug(f"API URL: {url}")

        async with session.post(url, headers=params["headers"]) as res:
            # _update accepts 200, 201, 202 as success
            # For non-success, ResponseHandler will raise appropriate exception
            if res.status in [200, 201, 202]:
                try:
                    return await res.json()
                except (json.JSONDecodeError, aiohttp.ContentTypeError) as e:
                    raise OPGGJSONDecodeError(url, original_error=e)

            # Use ResponseHandler for error status codes
            await ResponseHandler.handle_response(res, url)

    @staticmethod
    async def _fetch_all_champions(
        session: aiohttp.ClientSession, params: GenericReqParams
    ):
        url = params["base_api_url"]
        logger.debug(f"API URL: {url}")

        async with session.get(url, headers=params["headers"]) as res:
            content = await ResponseHandler.handle_response(res, url)
            logger.info(
                f"Request to OPGG API was successful (Content Length: {len(str(content))})"
            )
            logger.debug(
                f"CHAMPION DATA AT /CHAMPIONS ENDPOINT:\n{pformat(content, sort_dicts=False)}\n"
            )
            return ResponseHandler.extract_data(content, "data", default={})

    @staticmethod
    async def _fetch_champion_by_id(
        session: aiohttp.ClientSession,
        id: int,
        params: GenericReqParams,
        lang_code: LangCode,
    ):
        url = params["base_api_url"].format_map({"champion_id": id, "hl": lang_code})
        logger.debug(f"API URL: {url}")

        async with session.get(url, headers=params["headers"]) as res:
            content = await ResponseHandler.handle_response(res, url)
            logger.info(
                f"Request to OPGG API was successful (Content Length: {len(str(content))})"
            )
            logger.debug(f"CHAMPION DATA AT /CHAMPIONS ENDPOINT:\n{pformat(content)}\n")
            return ResponseHandler.extract_data(content, "data", default={})

    @staticmethod
    async def _fetch_champion_stats(
        session: aiohttp.ClientSession, params: GenericReqParams
    ):
        """
        `[Internal Helper Method]` Fetch champion statistics from the Champion API.

        Args:
            `session` (`aiohttp.ClientSession`): Active session for making requests
            `params` (`GenericReqParams`): Parameters containing API URL and headers

        Returns:
            `dict`: Champion statistics data
        """
        url = params["base_api_url"]
        logger.debug(f"API URL: {url}")

        async with session.get(url, headers=params["headers"]) as res:
            content = await ResponseHandler.handle_response(res, url)
            logger.info(
                f"Request to OPGG Champion API was successful (Content Length: {len(str(content))})"
            )
            logger.debug(
                f"CHAMPION STATS DATA AT /CHAMPIONS/RANKED ENDPOINT:\n{pformat(content)}\n"
            )
            return ResponseHandler.extract_data(content, "data", default={})

    @staticmethod
    async def _fetch_versions(session: aiohttp.ClientSession, params: GenericReqParams):
        """
        `[Internal Helper Method]` Fetch available game versions from the Champion API.

        Args:
            `session` (`aiohttp.ClientSession`): Active session for making requests
            `params` (`GenericReqParams`): Parameters containing API URL and headers

        Returns:
            `dict`: Version data
        """
        url = params["base_api_url"]
        logger.debug(f"API URL: {url}")

        async with session.get(url, headers=params["headers"]) as res:
            content = await ResponseHandler.handle_response(res, url)
            logger.info(
                f"Request to OPGG Champion API was successful (Content Length: {len(str(content))})"
            )
            logger.debug(f"VERSION DATA AT /VERSIONS ENDPOINT:\n{pformat(content)}\n")
            return ResponseHandler.extract_data(content, "data", default={})

    @staticmethod
    async def _fetch_seasons(session: aiohttp.ClientSession, params: GenericReqParams):
        """
        `[Internal Helper Method]` Fetch available seasons from the Summoner API.

        Args:
            `session` (`aiohttp.ClientSession`): Active session for making requests
            `params` (`GenericReqParams`): Parameters containing API URL and headers

        Returns:
            `dict`: Season data
        """
        url = params["base_api_url"]
        logger.debug(f"API URL: {url}")

        async with session.get(url, headers=params["headers"]) as res:
            content = await ResponseHandler.handle_response(res, url)
            logger.info(
                f"Request to OPGG Summoner API was successful (Content Length: {len(str(content))})"
            )
            logger.debug(
                f"SEASONS DATA AT /META/SEASONS ENDPOINT:\n{pformat(content)}\n"
            )
            return ResponseHandler.extract_data(content, "data", default={})

    @staticmethod
    async def _fetch_keywords(session: aiohttp.ClientSession, params: GenericReqParams):
        """
        `[Internal Helper Method]` Fetch keyword metadata from the Summoner API.

        Args:
            `session` (`aiohttp.ClientSession`): Active session for making requests
            `params` (`GenericReqParams`): Parameters containing API URL and headers

        Returns:
            `list[dict]`: Keyword entries
        """
        url = params["base_api_url"]
        logger.debug(f"API URL: {url}")

        async with session.get(url, headers=params["headers"]) as res:
            content = await ResponseHandler.handle_response(res, url)
            logger.info(
                f"Request to OPGG Summoner API was successful (Content Length: {len(str(content))})"
            )
            logger.debug(
                f"KEYWORDS DATA AT /META/KEYWORDS ENDPOINT:\n{pformat(content)}\n"
            )
            return ResponseHandler.extract_data(content, "data", default=[])

    @staticmethod
    async def _fetch_live_game(
        session: aiohttp.ClientSession, params: GenericReqParams
    ):
        url = params["base_api_url"]
        logger.debug(f"API URL: {url}")

        async with session.get(url, headers=params["headers"]) as res:
            logger.debug(f"Response status: {res.status}")

            if res.status == 200:
                # Success - player is in a live game
                try:
                    content: dict = await res.json()
                except (json.JSONDecodeError, aiohttp.ContentTypeError) as e:
                    raise OPGGJSONDecodeError(url, original_error=e)

                logger.info(
                    f"Request to OPGG API was successful (Content Length: {len(str(content))})"
                )
                logger.debug(
                    f"LIVE GAME DATA AT /spectate ENDPOINT:\n{pformat(content)}\n"
                )

                return {
                    "status": 200,
                    "message": content.get("message", "Success"),
                    "data": content.get("data"),
                }

            elif res.status == 404:
                # 404 means "not in a live game" - expected response, not an error
                try:
                    content: dict = await res.json()
                except (json.JSONDecodeError, aiohttp.ContentTypeError):
                    content = {}

                detail = content.get("detail", {}).get("detailMessage", "")
                message = content.get("message", "Not found")

                return {
                    "status": 404,
                    "message": message,
                    "detail": (
                        "Provided summoner is not in a live game!"
                        if detail == ""
                        else detail
                    ),
                }

            else:
                # Other status codes are errors - use ResponseHandler
                await ResponseHandler.handle_response(res, url)
