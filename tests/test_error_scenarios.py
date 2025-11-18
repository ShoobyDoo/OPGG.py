"""Tests for error handling and edge cases."""

import pytest
from unittest.mock import patch, Mock
import asyncio

from opgg.opgg import OPGG
from opgg.params import Region, SearchReturnType
from opgg.search_result import SearchResult
from opgg.summoner import Summoner


pytestmark = pytest.mark.unit


class TestSearchErrorHandling:
    """Test error handling in search operations."""

    @patch("opgg.opgg.asyncio.run")
    @patch("opgg.utils.Utils._single_region_search")
    def test_search_with_empty_query(
        self, mock_search, mock_run, mock_user_agent
    ):
        """Test search handles empty query string."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            mock_run.return_value = []

            opgg = OPGG()
            results = opgg.search("", region=Region.NA, returns=SearchReturnType.SIMPLE)

            # Should still call search with normalized (empty) query
            assert isinstance(results, list)

    @patch("opgg.opgg.asyncio.run")
    @patch("opgg.utils.Utils._single_region_search")
    @patch("opgg.utils.Utils.filter_results_with_summoner_id")
    def test_search_with_no_results(
        self, mock_filter, mock_search, mock_run, mock_user_agent
    ):
        """Test search returns empty list when no results found."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            mock_run.return_value = []
            mock_filter.return_value = []

            opgg = OPGG()
            results = opgg.search("NonexistentPlayer", returns=SearchReturnType.SIMPLE)

            assert results == []


class TestGetSummonerErrorHandling:
    """Test error handling in get_summoner operations."""

    def test_get_summoner_with_none_search_result(self, mock_user_agent):
        """Test get_summoner handles None search_result gracefully."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            with pytest.raises(ValueError):
                opgg.get_summoner(search_result=None)

    def test_get_summoner_mismatched_types(self, mock_user_agent):
        """Test get_summoner raises error for mismatched summoner_id/region types."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            with pytest.raises(ValueError, match="Mismatched types"):
                # String summoner_id with list region (mismatched)
                opgg.get_summoner(summoner_id="abc123", region=[Region.NA, Region.EUW])

    @patch("opgg.opgg.asyncio.run")
    @patch("opgg.utils.Utils.filter_results_with_summoner_id")
    def test_get_summoner_all_results_missing_ids(
        self, mock_filter, mock_run, mock_user_agent, sample_summoner_data
    ):
        """Test get_summoner handles case where all results missing summoner IDs."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            # Simulate all results being filtered out
            mock_filter.return_value = []

            search_results = [
                SearchResult(summoner=Summoner(game_name="Test1"), region=Region.NA),
                SearchResult(summoner=Summoner(game_name="Test2"), region=Region.NA),
            ]

            opgg = OPGG()
            result = opgg.get_summoner(search_results)

            assert result == []


class TestCacheTTLErrorHandling:
    """Test error handling for cache TTL configuration."""

    def test_champion_cache_ttl_setter_invalid_type(self, mock_user_agent):
        """Test champion_cache_ttl setter rejects invalid types."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            with pytest.raises(ValueError, match="must be an integer"):
                opgg.champion_cache_ttl = "not a number"

    def test_champion_cache_ttl_setter_none(self, mock_user_agent):
        """Test champion_cache_ttl setter rejects None."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            with pytest.raises(ValueError):
                opgg.champion_cache_ttl = None


class TestHeadersMutability:
    """Test headers can be modified after initialization."""

    def test_headers_are_mutable(self, mock_user_agent):
        """Test that headers can be modified after OPGG instantiation."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()
            original_headers = opgg.headers.copy()

            # Modify headers
            opgg.headers["X-Custom-Header"] = "CustomValue"

            assert "X-Custom-Header" in opgg.headers
            assert opgg.headers["X-Custom-Header"] == "CustomValue"
            assert len(opgg.headers) > len(original_headers)

    def test_headers_complete_replacement(self, mock_user_agent):
        """Test headers can be completely replaced."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            new_headers = {
                "User-Agent": "New Agent",
                "Authorization": "Bearer token123",
                "X-API-Key": "key456"
            }

            opgg.headers = new_headers

            assert opgg.headers == new_headers
            assert opgg.headers["Authorization"] == "Bearer token123"
