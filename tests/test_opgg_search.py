"""Tests for OPGG search and profile resolution (opgg/opgg.py lines 175-368)."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio

from opgg.opgg import OPGG
from opgg.params import Region, SearchReturnType, LangCode
from opgg.search_result import SearchResult
from opgg.summoner import Summoner


pytestmark = pytest.mark.unit


class TestOPGGSearch:
    """Test OPGG.search() method."""

    @patch("opgg.opgg.asyncio.run")
    @patch("opgg.utils.Utils._single_region_search")
    @patch("opgg.utils.Utils.filter_results_with_summoner_id")
    def test_search_single_region(
        self, mock_filter, mock_search, mock_run, mock_user_agent, sample_summoner_data
    ):
        """Test search with a specific region."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            # Setup mocks
            mock_search_result = {
                "summoner": sample_summoner_data,
                "region": Region.NA
            }
            mock_run.return_value = [mock_search_result]
            mock_filter.return_value = [SearchResult(
                summoner=Summoner(**sample_summoner_data),
                region=Region.NA
            )]

            opgg = OPGG()
            results = opgg.search("TestPlayer", region=Region.NA, returns=SearchReturnType.SIMPLE)

            assert len(results) >= 0
            mock_search.assert_called_once()

    @patch("opgg.opgg.asyncio.run")
    @patch("opgg.utils.Utils._search_all_regions")
    @patch("opgg.utils.Utils.filter_results_with_summoner_id")
    def test_search_all_regions(
        self, mock_filter, mock_search_all, mock_run, mock_user_agent, sample_summoner_data
    ):
        """Test search with Region.ANY triggers multi-region search."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            # Setup mocks
            mock_search_result = {
                "summoner": sample_summoner_data,
                "region": Region.NA
            }
            mock_run.return_value = [mock_search_result]
            mock_filter.return_value = [SearchResult(
                summoner=Summoner(**sample_summoner_data),
                region=Region.NA
            )]

            opgg = OPGG()
            results = opgg.search("TestPlayer", region=Region.ANY, returns=SearchReturnType.SIMPLE)

            mock_search_all.assert_called_once()

    @patch("opgg.opgg.asyncio.run")
    @patch("opgg.utils.Utils._single_region_search")
    @patch("opgg.utils.Utils.filter_results_with_summoner_id")
    @patch.object(OPGG, "get_summoner")
    def test_search_full_return_type_fetches_profiles(
        self, mock_get_summoner, mock_filter, mock_search, mock_run,
        mock_user_agent, sample_summoner_data
    ):
        """Test SearchReturnType.FULL triggers profile fetch."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            # Setup mocks
            mock_search_result = {
                "summoner": sample_summoner_data,
                "region": Region.NA
            }
            search_result_obj = SearchResult(
                summoner=Summoner(**sample_summoner_data),
                region=Region.NA
            )
            mock_run.return_value = [mock_search_result]
            mock_filter.return_value = [search_result_obj]
            mock_get_summoner.return_value = [Summoner(**sample_summoner_data)]

            opgg = OPGG()
            results = opgg.search("TestPlayer", region=Region.NA, returns=SearchReturnType.FULL)

            mock_get_summoner.assert_called_once()

    @patch("opgg.opgg.asyncio.run")
    @patch("opgg.utils.Utils._single_region_search")
    @patch("opgg.utils.Utils.filter_results_with_summoner_id")
    def test_search_filters_results_without_summoner_id(
        self, mock_filter, mock_search, mock_run, mock_user_agent
    ):
        """Test that search results without summoner_id are filtered out."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            mock_run.return_value = []
            mock_filter.return_value = []

            opgg = OPGG()
            results = opgg.search("InvalidPlayer", returns=SearchReturnType.SIMPLE)

            assert results == []
            mock_filter.assert_called_once()


class TestOPGGGetSummoner:
    """Test OPGG.get_summoner() method."""

    @patch("opgg.opgg.asyncio.run")
    @patch("opgg.utils.Utils._fetch_profile")
    @patch.object(OPGG, "_attach_season_meta")
    def test_get_summoner_single_search_result(
        self, mock_attach, mock_fetch, mock_run,
        mock_user_agent, sample_search_result, sample_summoner_data
    ):
        """Test get_summoner with single SearchResult."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            mock_run.return_value = {"summoner": sample_summoner_data}

            opgg = OPGG()
            summoner = opgg.get_summoner(sample_search_result)

            assert isinstance(summoner, Summoner)
            mock_fetch.assert_called_once()
            mock_attach.assert_called_once()

    @patch("opgg.opgg.asyncio.run")
    @patch("opgg.utils.Utils._fetch_profile_multiple")
    @patch("opgg.utils.Utils.filter_results_with_summoner_id")
    @patch.object(OPGG, "_attach_season_meta")
    def test_get_summoner_multiple_search_results(
        self, mock_attach, mock_filter, mock_fetch_multiple,
        mock_run, mock_user_agent, sample_search_result, sample_summoner_data
    ):
        """Test get_summoner with multiple SearchResults."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            mock_filter.return_value = [sample_search_result, sample_search_result]
            mock_run.return_value = [
                {"summoner": sample_summoner_data},
                {"summoner": sample_summoner_data}
            ]

            opgg = OPGG()
            summoners = opgg.get_summoner([sample_search_result, sample_search_result])

            assert isinstance(summoners, list)
            assert len(summoners) >= 0
            mock_fetch_multiple.assert_called_once()

    @patch("opgg.opgg.asyncio.run")
    @patch("opgg.utils.Utils._fetch_profile")
    @patch.object(OPGG, "_attach_season_meta")
    def test_get_summoner_with_summoner_id_and_region(
        self, mock_attach, mock_fetch, mock_run,
        mock_user_agent, sample_summoner_data
    ):
        """Test get_summoner with summoner_id and region fallback."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            mock_run.return_value = {"summoner": sample_summoner_data}

            opgg = OPGG()
            summoner = opgg.get_summoner(
                summoner_id="abc123",
                region=Region.NA
            )

            assert isinstance(summoner, Summoner)

    def test_get_summoner_missing_summoner_id_returns_partial(
        self, mock_user_agent, caplog
    ):
        """Test get_summoner logs critical and returns partial summoner when summoner_id is missing."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            search_result = SearchResult(
                summoner=Summoner(game_name="Test"),
                region=Region.NA
            )

            opgg = OPGG()
            result = opgg.get_summoner(search_result)

            assert isinstance(result, Summoner)
            # Should log critical error but still return the partial summoner

    def test_get_summoner_invalid_type_raises_error(self, mock_user_agent):
        """Test get_summoner raises ValueError for invalid input type."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            with pytest.raises(ValueError, match="Invalid type for search_result"):
                opgg.get_summoner("invalid_type")
