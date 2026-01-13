"""Integration tests for OPGG sync API with mocked responses."""

import re

import pytest

from opgg import OPGG
from opgg.params import By, CacheType, GameType, Region, SearchReturnType
from opgg.search_result import SearchResult
from opgg.summoner import Summoner

# Case-insensitive pattern for search endpoint (matches any region)
SEARCH_URL_PATTERN = re.compile(r".*v3/.*/summoners\?.*", re.IGNORECASE)
# Case-insensitive pattern for profile/summary endpoint
PROFILE_URL_PATTERN = re.compile(r".*/summoners/.*/summary.*", re.IGNORECASE)
# Case-insensitive pattern for games endpoint
GAMES_URL_PATTERN = re.compile(r".*/summoners/.*/games.*", re.IGNORECASE)
# Pattern for champion metadata
CHAMPIONS_URL_PATTERN = re.compile(r".*meta/champions\?.*", re.IGNORECASE)
CHAMPION_BY_ID_PATTERN = re.compile(r".*meta/champions/\d+\?.*", re.IGNORECASE)
CHAMPION_STATS_PATTERN = re.compile(r".*/champions/ranked\?.*", re.IGNORECASE)
# Pattern for metadata endpoints
SEASONS_URL_PATTERN = re.compile(r".*meta/seasons\?.*", re.IGNORECASE)
VERSIONS_URL_PATTERN = re.compile(r".*meta/versions\?.*", re.IGNORECASE)
KEYWORDS_URL_PATTERN = re.compile(r".*meta/keywords\?.*", re.IGNORECASE)


@pytest.fixture
def opgg(temp_db):
    """Create OPGG instance with isolated test database."""
    instance = OPGG()
    # Use temp database for cache isolation
    instance._cacher.db_path = temp_db
    instance._cacher.setup()
    return instance


class TestOPGGInitialization:
    """Test OPGG class initialization."""

    def test_opgg_initializes_correctly(self, opgg):
        """Test that OPGG initializes with required attributes."""
        assert opgg is not None
        assert opgg.headers is not None
        assert "User-Agent" in opgg.headers

    def test_opgg_has_cacher(self, opgg):
        """Test that OPGG has cacher instance."""
        assert opgg._cacher is not None


class TestSearchSync:
    """Test synchronous search functionality."""

    def test_search_returns_list(self, opgg, mock_aiohttp, fixture_search_single):
        """Test search in specific region returns list of SearchResult."""
        mock_aiohttp.get(SEARCH_URL_PATTERN, payload=fixture_search_single)

        results = opgg.search("ColbyFaulkn1", Region.NA, SearchReturnType.SIMPLE)

        assert isinstance(results, list)
        assert len(results) > 0
        assert isinstance(results[0], SearchResult)

    def test_search_result_has_region(self, opgg, mock_aiohttp, fixture_search_single):
        """Test search results have correct region attached."""
        mock_aiohttp.get(SEARCH_URL_PATTERN, payload=fixture_search_single)

        results = opgg.search("ColbyFaulkn1", Region.NA, SearchReturnType.SIMPLE)

        assert len(results) > 0
        assert results[0].region == Region.NA

    def test_search_result_has_summoner(self, opgg, mock_aiohttp, fixture_search_single):
        """Test search results have Summoner object."""
        mock_aiohttp.get(SEARCH_URL_PATTERN, payload=fixture_search_single)

        results = opgg.search("ColbyFaulkn1", Region.NA, SearchReturnType.SIMPLE)

        assert len(results) > 0
        assert results[0].summoner is not None
        assert results[0].summoner.summoner_id is not None

    def test_search_empty_response(self, opgg, mock_aiohttp, fixture_search_empty):
        """Test search handles empty API response gracefully."""
        mock_aiohttp.get(SEARCH_URL_PATTERN, payload=fixture_search_empty)

        results = opgg.search("NonExistentPlayer999", Region.NA, SearchReturnType.SIMPLE)

        assert results == []

    def test_search_filters_missing_summoner_id(self, opgg, mock_aiohttp):
        """Test search filters out results missing summoner_id."""
        mock_aiohttp.get(
            SEARCH_URL_PATTERN,
            payload={"data": [{"game_name": "NoID", "tagline": "NA1"}]},
        )

        results = opgg.search("NoID", Region.NA, SearchReturnType.SIMPLE)

        # Results without summoner_id should be filtered out
        assert len(results) == 0


class TestGetSummonerSync:
    """Test synchronous get_summoner functionality."""

    def test_get_summoner_with_search_result(
        self, opgg, mock_aiohttp, fixture_search_single, fixture_profile_full, fixture_seasons
    ):
        """Test get_summoner using SearchResult input."""
        mock_aiohttp.get(PROFILE_URL_PATTERN, payload=fixture_profile_full)
        mock_aiohttp.get(SEASONS_URL_PATTERN, payload=fixture_seasons)

        # Create SearchResult from fixture
        search_result = SearchResult(
            summoner=Summoner(**fixture_search_single["data"][0]),
            region=Region.NA,
        )

        summoner = opgg.get_summoner(search_result)

        assert summoner is not None
        assert summoner.summoner_id is not None

    def test_get_summoner_with_id_and_region(
        self, opgg, mock_aiohttp, fixture_profile_full, fixture_seasons
    ):
        """Test get_summoner using summoner_id and region parameters."""
        mock_aiohttp.get(PROFILE_URL_PATTERN, payload=fixture_profile_full)
        mock_aiohttp.get(SEASONS_URL_PATTERN, payload=fixture_seasons)

        summoner = opgg.get_summoner(summoner_id="test-id-123", region=Region.NA)

        assert summoner is not None
        assert summoner.summoner_id is not None

    def test_get_summoner_batch_processing(
        self, opgg, mock_aiohttp, fixture_profile_full, fixture_seasons
    ):
        """Test get_summoner with list of SearchResults processes all."""
        mock_aiohttp.get(PROFILE_URL_PATTERN, payload=fixture_profile_full, repeat=True)
        mock_aiohttp.get(SEASONS_URL_PATTERN, payload=fixture_seasons)

        search_results = [
            SearchResult(summoner=Summoner(summoner_id=f"id-{i}"), region=Region.NA)
            for i in range(3)
        ]

        summoners = opgg.get_summoner(search_results)

        assert isinstance(summoners, list)
        assert len(summoners) == 3


class TestGetRecentGamesSync:
    """Test synchronous get_recent_games functionality."""

    def test_get_recent_games_returns_list(
        self, opgg, mock_aiohttp, fixture_games_ranked
    ):
        """Test get_recent_games returns list of Game objects."""
        mock_aiohttp.get(GAMES_URL_PATTERN, payload=fixture_games_ranked)

        search_result = SearchResult(
            summoner=Summoner(summoner_id="test-id"),
            region=Region.NA,
        )

        games = opgg.get_recent_games(search_result)

        assert isinstance(games, list)

    def test_get_recent_games_with_game_type_filter(
        self, opgg, mock_aiohttp, fixture_games_ranked
    ):
        """Test get_recent_games with RANKED game type filter."""
        mock_aiohttp.get(GAMES_URL_PATTERN, payload=fixture_games_ranked)

        search_result = SearchResult(
            summoner=Summoner(summoner_id="test-id"),
            region=Region.NA,
        )

        games = opgg.get_recent_games(search_result, game_type=GameType.RANKED)

        assert isinstance(games, list)

    def test_get_recent_games_empty_history(
        self, opgg, mock_aiohttp, fixture_games_empty
    ):
        """Test handling player with no game history."""
        mock_aiohttp.get(GAMES_URL_PATTERN, payload=fixture_games_empty)

        search_result = SearchResult(
            summoner=Summoner(summoner_id="new-player"),
            region=Region.NA,
        )

        games = opgg.get_recent_games(search_result)

        assert games == []

    def test_get_recent_games_validates_results_min(self, opgg):
        """Test get_recent_games validates minimum results parameter."""
        search_result = SearchResult(
            summoner=Summoner(summoner_id="test-id"),
            region=Region.NA,
        )

        with pytest.raises(ValueError):
            opgg.get_recent_games(search_result, results=0)

    def test_get_recent_games_validates_results_max(self, opgg):
        """Test get_recent_games validates maximum results parameter."""
        search_result = SearchResult(
            summoner=Summoner(summoner_id="test-id"),
            region=Region.NA,
        )

        with pytest.raises(ValueError):
            opgg.get_recent_games(search_result, results=201)


class TestChampionSync:
    """Test synchronous champion functionality."""

    def test_get_all_champions_returns_list(
        self, opgg, mock_aiohttp, fixture_champions_all
    ):
        """Test get_all_champions returns list of Champion objects."""
        mock_aiohttp.get(CHAMPIONS_URL_PATTERN, payload=fixture_champions_all)

        champions = opgg.get_all_champions()

        assert isinstance(champions, list)
        assert len(champions) > 0

    def test_get_all_champions_uses_cache(
        self, opgg, mock_aiohttp, fixture_champions_all
    ):
        """Test get_all_champions uses cache on subsequent calls."""
        mock_aiohttp.get(CHAMPIONS_URL_PATTERN, payload=fixture_champions_all)

        # First call - should hit API
        champions1 = opgg.get_all_champions()

        # Second call - should use cache (mock won't be called again)
        champions2 = opgg.get_all_champions()

        assert len(champions1) == len(champions2)

    def test_get_all_champions_force_refresh(
        self, opgg, mock_aiohttp, fixture_champions_all
    ):
        """Test get_all_champions with force_refresh bypasses cache."""
        mock_aiohttp.get(CHAMPIONS_URL_PATTERN, payload=fixture_champions_all, repeat=True)

        # First call
        opgg.get_all_champions()

        # Force refresh - should hit API again
        champions = opgg.get_all_champions(force_refresh=True)

        assert len(champions) > 0

    def test_get_champion_by_id(self, opgg, mock_aiohttp, fixture_champion_by_id):
        """Test get_champion_by with By.ID returns specific champion."""
        mock_aiohttp.get(CHAMPION_BY_ID_PATTERN, payload=fixture_champion_by_id)

        champion = opgg.get_champion_by(By.ID, 266)

        assert champion is not None
        assert champion.id == 266

    def test_get_champion_by_name(self, opgg, mock_aiohttp, fixture_champions_all):
        """Test get_champion_by with By.NAME finds champion by name."""
        mock_aiohttp.get(CHAMPIONS_URL_PATTERN, payload=fixture_champions_all)

        # Get first champion name from fixture
        first_champ_name = fixture_champions_all["data"][0]["name"]
        champion = opgg.get_champion_by(By.NAME, first_champ_name)

        assert champion is not None
        assert champion.name.lower() == first_champ_name.lower()

    def test_get_champion_stats_returns_data(
        self, opgg, mock_aiohttp, fixture_champion_stats
    ):
        """Test get_champion_stats returns statistics data."""
        mock_aiohttp.get(CHAMPION_STATS_PATTERN, payload=fixture_champion_stats)

        stats = opgg.get_champion_stats()

        assert stats is not None


class TestMetadataSync:
    """Test synchronous metadata endpoints."""

    def test_get_all_seasons_returns_list(self, opgg, mock_aiohttp, fixture_seasons):
        """Test get_all_seasons returns season metadata."""
        mock_aiohttp.get(SEASONS_URL_PATTERN, payload=fixture_seasons)

        seasons = opgg.get_all_seasons()

        assert isinstance(seasons, list)

    def test_get_versions_returns_data(self, opgg, mock_aiohttp, fixture_versions):
        """Test get_versions returns version data."""
        mock_aiohttp.get(VERSIONS_URL_PATTERN, payload=fixture_versions)

        versions = opgg.get_versions()

        assert versions is not None

    def test_get_keywords_returns_list(self, opgg, mock_aiohttp, fixture_keywords):
        """Test get_keywords returns keyword metadata."""
        mock_aiohttp.get(KEYWORDS_URL_PATTERN, payload=fixture_keywords)

        keywords = opgg.get_keywords()

        assert isinstance(keywords, list)


class TestCacheManagement:
    """Test cache management functionality."""

    def test_get_cache_stats_returns_dict(self, opgg):
        """Test get_cache_stats returns dictionary with cache info."""
        stats = opgg.get_cache_stats()

        assert isinstance(stats, dict)

    def test_clear_cache_specific_type(self, opgg, mock_aiohttp, fixture_champions_all):
        """Test clear_cache removes specific cache type."""
        mock_aiohttp.get(CHAMPIONS_URL_PATTERN, payload=fixture_champions_all, repeat=True)

        # Populate cache
        opgg.get_all_champions()

        # Clear champions cache
        result = opgg.clear_cache(CacheType.CHAMPIONS)

        assert isinstance(result, dict)

    def test_champion_cache_ttl_getter(self, opgg):
        """Test champion_cache_ttl property getter returns int."""
        ttl = opgg.champion_cache_ttl

        assert isinstance(ttl, int)
        assert ttl > 0

    def test_champion_cache_ttl_setter(self, opgg):
        """Test champion_cache_ttl property setter works."""
        original = opgg.champion_cache_ttl

        opgg.champion_cache_ttl = 3600
        assert opgg.champion_cache_ttl == 3600

        # Reset
        opgg.champion_cache_ttl = original

    def test_champion_cache_ttl_rejects_negative(self, opgg):
        """Test champion_cache_ttl rejects negative values."""
        with pytest.raises(ValueError):
            opgg.champion_cache_ttl = -1

    def test_champion_cache_ttl_rejects_non_int(self, opgg):
        """Test champion_cache_ttl rejects non-integer values."""
        with pytest.raises(ValueError):
            opgg.champion_cache_ttl = "invalid"


class TestInputValidation:
    """Test input validation for various methods."""

    def test_search_with_empty_name(self, opgg, mock_aiohttp, fixture_search_empty):
        """Test search handles empty name input."""
        mock_aiohttp.get(SEARCH_URL_PATTERN, payload=fixture_search_empty)

        # Empty string should still make request (may return empty results)
        results = opgg.search("", Region.NA, SearchReturnType.SIMPLE)
        assert isinstance(results, list)

    def test_get_summoner_requires_identifier(self, opgg):
        """Test get_summoner raises error without proper identifier."""
        # Neither SearchResult nor summoner_id+region provided
        with pytest.raises((ValueError, TypeError)):
            opgg.get_summoner()
