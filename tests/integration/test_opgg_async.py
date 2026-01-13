"""Integration tests for OPGG async API with mocked responses."""

import asyncio
import re

import pytest

from opgg import OPGG
from opgg.params import By, GameType, Region, SearchReturnType
from opgg.search_result import SearchResult
from opgg.summoner import Summoner

# Case-insensitive URL patterns (shared with sync tests)
SEARCH_URL_PATTERN = re.compile(r".*v3/.*/summoners\?.*", re.IGNORECASE)
PROFILE_URL_PATTERN = re.compile(r".*/summoners/.*/summary.*", re.IGNORECASE)
GAMES_URL_PATTERN = re.compile(r".*/summoners/.*/games.*", re.IGNORECASE)
CHAMPIONS_URL_PATTERN = re.compile(r".*meta/champions\?.*", re.IGNORECASE)
CHAMPION_BY_ID_PATTERN = re.compile(r".*meta/champions/\d+\?.*", re.IGNORECASE)
CHAMPION_STATS_PATTERN = re.compile(r".*/champions/ranked\?.*", re.IGNORECASE)
SEASONS_URL_PATTERN = re.compile(r".*meta/seasons\?.*", re.IGNORECASE)
VERSIONS_URL_PATTERN = re.compile(r".*meta/versions\?.*", re.IGNORECASE)
KEYWORDS_URL_PATTERN = re.compile(r".*meta/keywords\?.*", re.IGNORECASE)


@pytest.mark.asyncio
class TestAsyncContextManager:
    """Test async context manager functionality."""

    async def test_context_manager_initializes(self):
        """Test OPGG initializes within async context."""
        async with OPGG() as opgg:
            assert opgg is not None

    async def test_context_manager_creates_session_on_use(self):
        """Test session is created when needed within context."""
        async with OPGG() as opgg:
            # Session should be None initially
            assert opgg._session is None

            # After calling _get_session, session should exist
            session = await opgg._get_session()
            assert session is not None
            assert not session.closed

    async def test_context_manager_closes_session_on_exit(self):
        """Test session is properly closed when exiting context."""
        opgg = OPGG()
        async with opgg:
            session = await opgg._get_session()
            assert not session.closed

        # After exiting context, session should be closed or None
        assert opgg._session is None or opgg._session.closed

    async def test_session_reuse_within_context(self):
        """Test same session is reused for multiple calls within context."""
        async with OPGG() as opgg:
            session1 = await opgg._get_session()
            session2 = await opgg._get_session()

            assert session1 is session2


@pytest.mark.asyncio
class TestSearchAsync:
    """Test asynchronous search functionality."""

    async def test_search_async_returns_list(
        self, mock_aiohttp, fixture_search_single
    ):
        """Test search_async returns list of SearchResult."""
        mock_aiohttp.get(
            SEARCH_URL_PATTERN,
            payload=fixture_search_single,
        )

        async with OPGG() as opgg:
            results = await opgg.search_async(
                "ColbyFaulkn1", Region.NA, SearchReturnType.SIMPLE
            )

        assert isinstance(results, list)
        assert len(results) > 0

    async def test_search_async_results_have_region(
        self, mock_aiohttp, fixture_search_single
    ):
        """Test search results have correct region attached."""
        mock_aiohttp.get(
            SEARCH_URL_PATTERN,
            payload=fixture_search_single,
        )

        async with OPGG() as opgg:
            results = await opgg.search_async(
                "ColbyFaulkn1", Region.NA, SearchReturnType.SIMPLE
            )

        assert len(results) > 0
        assert results[0].region == Region.NA

    async def test_search_async_empty_response(
        self, mock_aiohttp, fixture_search_empty
    ):
        """Test search_async handles empty response."""
        mock_aiohttp.get(
            SEARCH_URL_PATTERN,
            payload=fixture_search_empty,
        )

        async with OPGG() as opgg:
            results = await opgg.search_async(
                "NonExistent", Region.NA, SearchReturnType.SIMPLE
            )

        assert results == []


@pytest.mark.asyncio
class TestGetSummonerAsync:
    """Test asynchronous get_summoner functionality."""

    async def test_get_summoner_async_with_search_result(
        self, mock_aiohttp, fixture_search_single, fixture_profile_full
    ):
        """Test get_summoner_async with SearchResult input."""
        mock_aiohttp.get(
            PROFILE_URL_PATTERN,
            payload=fixture_profile_full,
        )

        async with OPGG() as opgg:
            search_result = SearchResult(
                summoner=Summoner(**fixture_search_single["data"][0]),
                region=Region.NA,
            )

            summoner = await opgg.get_summoner_async(search_result)

        assert summoner is not None
        assert summoner.summoner_id is not None

    async def test_get_summoner_async_with_id_and_region(
        self, mock_aiohttp, fixture_profile_full
    ):
        """Test get_summoner_async with summoner_id and region."""
        mock_aiohttp.get(
            PROFILE_URL_PATTERN,
            payload=fixture_profile_full,
        )

        async with OPGG() as opgg:
            summoner = await opgg.get_summoner_async(
                summoner_id="test-id-123", region=Region.NA
            )

        assert summoner is not None

    async def test_get_summoner_async_batch(
        self, mock_aiohttp, fixture_profile_full
    ):
        """Test get_summoner_async with list processes concurrently."""
        mock_aiohttp.get(
            PROFILE_URL_PATTERN,
            payload=fixture_profile_full,
            repeat=True,
        )

        async with OPGG() as opgg:
            search_results = [
                SearchResult(
                    summoner=Summoner(summoner_id=f"id-{i}"), region=Region.NA
                )
                for i in range(3)
            ]

            summoners = await opgg.get_summoner_async(search_results)

        assert isinstance(summoners, list)
        assert len(summoners) == 3


@pytest.mark.asyncio
class TestGetRecentGamesAsync:
    """Test asynchronous get_recent_games functionality."""

    async def test_get_recent_games_async_returns_list(
        self, mock_aiohttp, fixture_games_ranked
    ):
        """Test get_recent_games_async returns list of Game."""
        mock_aiohttp.get(
            GAMES_URL_PATTERN,
            payload=fixture_games_ranked,
        )

        async with OPGG() as opgg:
            search_result = SearchResult(
                summoner=Summoner(summoner_id="test-id"),
                region=Region.NA,
            )

            games = await opgg.get_recent_games_async(search_result)

        assert isinstance(games, list)

    async def test_get_recent_games_async_with_filter(
        self, mock_aiohttp, fixture_games_ranked
    ):
        """Test get_recent_games_async with game type filter."""
        mock_aiohttp.get(
            re.compile(r".*game_type=ranked.*"),
            payload=fixture_games_ranked,
        )

        async with OPGG() as opgg:
            search_result = SearchResult(
                summoner=Summoner(summoner_id="test-id"),
                region=Region.NA,
            )

            games = await opgg.get_recent_games_async(
                search_result, game_type=GameType.RANKED
            )

        assert isinstance(games, list)

    async def test_get_recent_games_async_empty(
        self, mock_aiohttp, fixture_games_empty
    ):
        """Test get_recent_games_async handles empty history."""
        mock_aiohttp.get(
            GAMES_URL_PATTERN,
            payload=fixture_games_empty,
        )

        async with OPGG() as opgg:
            search_result = SearchResult(
                summoner=Summoner(summoner_id="new-player"),
                region=Region.NA,
            )

            games = await opgg.get_recent_games_async(search_result)

        assert games == []


@pytest.mark.asyncio
class TestChampionAsync:
    """Test asynchronous champion functionality."""

    async def test_get_all_champions_async(
        self, mock_aiohttp, fixture_champions_all
    ):
        """Test get_all_champions_async returns champion list."""
        mock_aiohttp.get(
            CHAMPIONS_URL_PATTERN,
            payload=fixture_champions_all,
        )

        async with OPGG() as opgg:
            champions = await opgg.get_all_champions_async()

        assert isinstance(champions, list)
        assert len(champions) > 0

    async def test_get_champion_by_async_id(
        self, mock_aiohttp, fixture_champion_by_id
    ):
        """Test get_champion_by_async with ID lookup."""
        mock_aiohttp.get(
            CHAMPION_BY_ID_PATTERN,
            payload=fixture_champion_by_id,
        )

        async with OPGG() as opgg:
            champion = await opgg.get_champion_by_async(By.ID, 266)

        assert champion is not None
        assert champion.id == 266

    async def test_get_champion_stats_async(
        self, mock_aiohttp, fixture_champion_stats
    ):
        """Test get_champion_stats_async returns stats."""
        mock_aiohttp.get(
            CHAMPION_STATS_PATTERN,
            payload=fixture_champion_stats,
        )

        async with OPGG() as opgg:
            stats = await opgg.get_champion_stats_async()

        assert stats is not None


@pytest.mark.asyncio
class TestMetadataAsync:
    """Test asynchronous metadata endpoints."""

    async def test_get_all_seasons_async(self, mock_aiohttp, fixture_seasons):
        """Test get_all_seasons_async returns seasons."""
        mock_aiohttp.get(
            SEASONS_URL_PATTERN,
            payload=fixture_seasons,
        )

        async with OPGG() as opgg:
            seasons = await opgg.get_all_seasons_async()

        assert isinstance(seasons, list)

    async def test_get_versions_async(self, mock_aiohttp, fixture_versions):
        """Test get_versions_async returns version data."""
        mock_aiohttp.get(
            VERSIONS_URL_PATTERN,
            payload=fixture_versions,
        )

        async with OPGG() as opgg:
            versions = await opgg.get_versions_async()

        assert versions is not None

    async def test_get_keywords_async(self, mock_aiohttp, fixture_keywords):
        """Test get_keywords_async returns keywords."""
        mock_aiohttp.get(
            KEYWORDS_URL_PATTERN,
            payload=fixture_keywords,
        )

        async with OPGG() as opgg:
            keywords = await opgg.get_keywords_async()

        assert isinstance(keywords, list)


@pytest.mark.asyncio
class TestConcurrency:
    """Test concurrent async operations."""

    async def test_concurrent_search_operations(
        self, mock_aiohttp, fixture_search_single
    ):
        """Test multiple concurrent search operations."""
        mock_aiohttp.get(
            SEARCH_URL_PATTERN,
            payload=fixture_search_single,
            repeat=True,
        )

        async with OPGG() as opgg:
            tasks = [
                opgg.search_async(f"Player{i}", Region.NA, SearchReturnType.SIMPLE)
                for i in range(3)
            ]
            results = await asyncio.gather(*tasks)

        assert len(results) == 3
        assert all(isinstance(r, list) for r in results)

    async def test_concurrent_profile_fetches(
        self, mock_aiohttp, fixture_profile_full
    ):
        """Test concurrent profile fetches."""
        mock_aiohttp.get(
            PROFILE_URL_PATTERN,
            payload=fixture_profile_full,
            repeat=True,
        )

        async with OPGG() as opgg:
            search_results = [
                SearchResult(
                    summoner=Summoner(summoner_id=f"id-{i}"), region=Region.NA
                )
                for i in range(5)
            ]

            # Use batch method which is internally concurrent
            summoners = await opgg.get_summoner_async(search_results)

        assert len(summoners) == 5

    async def test_concurrent_game_fetches(
        self, mock_aiohttp, fixture_games_ranked
    ):
        """Test concurrent game history fetches."""
        mock_aiohttp.get(
            GAMES_URL_PATTERN,
            payload=fixture_games_ranked,
            repeat=True,
        )

        async with OPGG() as opgg:
            search_results = [
                SearchResult(
                    summoner=Summoner(summoner_id=f"id-{i}"), region=Region.NA
                )
                for i in range(3)
            ]

            # Batch fetch games
            all_games = await opgg.get_recent_games_async(search_results)

        assert len(all_games) == 3


@pytest.mark.asyncio
class TestSessionManagement:
    """Test async session lifecycle management."""

    async def test_session_reuse_across_calls(self):
        """Test the same session is reused for multiple calls."""
        async with OPGG() as opgg:
            session1 = await opgg._get_session()
            session2 = await opgg._get_session()

            assert session1 is session2

    async def test_close_method_closes_session(self):
        """Test close() method properly closes the session."""
        opgg = OPGG()
        session = await opgg._get_session()
        assert not session.closed

        await opgg.close()
        assert session.closed

    async def test_new_session_after_close(self):
        """Test new session can be created after closing."""
        async with OPGG() as opgg:
            session1 = await opgg._get_session()
            await opgg.close()

            # Getting session again should create new session
            session2 = await opgg._get_session()
            assert session1 is not session2
            assert not session2.closed
