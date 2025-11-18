"""Tests for OPGG metadata methods - Versions, Keywords, and Seasons."""

import pytest
import re
from unittest.mock import patch, Mock
from aioresponses import aioresponses

from opgg.opgg import OPGG
from opgg.params import LangCode
from opgg.keyword import Keyword
from opgg.season import SeasonMeta


pytestmark = pytest.mark.unit


class TestGetVersions:
    """Test get_versions() method."""

    def test_get_versions_first_fetch(self, mock_user_agent, mock_versions_response):
        """Test fetching versions for the first time (no cache)."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_versions", return_value=None), \
             patch("opgg.cacher.Cacher.cache_versions") as mock_cache:

            opgg = OPGG()

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/versions.*"),
                    payload=mock_versions_response,
                    status=200,
                )

                versions = opgg.get_versions()

            # Verify API returned data (should be just the list extracted from 'data' field)
            assert versions == mock_versions_response["data"]
            # Verify data was cached
            mock_cache.assert_called_once()

    def test_get_versions_from_cache(self, mock_user_agent, mock_versions_response):
        """Test returning versions from cache."""
        cached_data = mock_versions_response["data"]

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_versions", return_value=cached_data):

            opgg = OPGG()

            with aioresponses() as m:
                # API should NOT be called
                versions = opgg.get_versions()

            # Should return cached data
            assert versions == cached_data
            # Verify no API calls were made
            assert len(m.requests) == 0

    def test_get_versions_force_refresh(self, mock_user_agent, mock_versions_response):
        """Test force_refresh bypasses cache."""
        cached_data = ["13.0.0"]
        fresh_data = mock_versions_response["data"]

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_versions", return_value=cached_data), \
             patch("opgg.cacher.Cacher.cache_versions") as mock_cache:

            opgg = OPGG()

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/versions.*"),
                    payload=mock_versions_response,
                    status=200,
                )

                versions = opgg.get_versions(force_refresh=True)

            # Should return fresh data, not cached
            assert versions == fresh_data
            assert versions != cached_data
            # Verify new data was cached
            mock_cache.assert_called_once()

    def test_get_versions_different_languages(self, mock_user_agent, mock_versions_response):
        """Test fetching versions with different language codes."""
        expected_data = mock_versions_response["data"]

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_versions", return_value=None):

            opgg = OPGG()

            with aioresponses() as m:
                # Mock for Korean
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/versions.*hl=ko_KR"),
                    payload=mock_versions_response,
                    status=200,
                )
                # Mock for Japanese
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/versions.*hl=ja_JP"),
                    payload=mock_versions_response,
                    status=200,
                )

                kr_versions = opgg.get_versions(lang_code=LangCode.KOREAN)
                jp_versions = opgg.get_versions(lang_code=LangCode.JAPANESE)

            # Both should succeed
            assert kr_versions == expected_data
            assert jp_versions == expected_data


class TestGetKeywords:
    """Test get_keywords() method."""

    def test_get_keywords_first_fetch(self, mock_user_agent, mock_keywords_response):
        """Test fetching keywords for the first time (no cache)."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_keywords", return_value=None), \
             patch("opgg.cacher.Cacher.cache_keywords") as mock_cache:

            opgg = OPGG()

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/meta/keywords.*"),
                    payload=mock_keywords_response,
                    status=200,
                )

                keywords = opgg.get_keywords()

            # Verify returned Keyword objects
            assert isinstance(keywords, list)
            assert len(keywords) > 0
            assert all(isinstance(k, Keyword) for k in keywords)
            # Verify data was cached
            mock_cache.assert_called_once()

    def test_get_keywords_from_cache(self, mock_user_agent, sample_keyword_data):
        """Test returning keywords from cache."""
        cached_data = [sample_keyword_data]

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_keywords", return_value=cached_data):

            opgg = OPGG()

            with aioresponses() as m:
                # API should NOT be called
                keywords = opgg.get_keywords()

            # Should return cached data as Keyword objects
            assert isinstance(keywords, list)
            assert len(keywords) == 1
            assert isinstance(keywords[0], Keyword)
            assert keywords[0].keyword == "leader"
            # Verify no API calls were made
            assert len(m.requests) == 0

    def test_get_keywords_force_refresh(self, mock_user_agent, mock_keywords_response, sample_keyword_data):
        """Test force_refresh bypasses cache."""
        cached_data = [sample_keyword_data]

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_keywords", return_value=cached_data), \
             patch("opgg.cacher.Cacher.cache_keywords") as mock_cache:

            opgg = OPGG()

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/meta/keywords.*"),
                    payload=mock_keywords_response,
                    status=200,
                )

                keywords = opgg.get_keywords(force_refresh=True)

            # Should return fresh data
            assert isinstance(keywords, list)
            assert all(isinstance(k, Keyword) for k in keywords)
            # Verify new data was cached
            mock_cache.assert_called_once()

    def test_get_keywords_handles_dict_response(self, mock_user_agent):
        """Test handling keywords wrapped in data field."""
        response_with_data = {
            "data": [
                {
                    "keyword": "leader",
                    "label": "Leader",
                    "description": "Dominated the game",
                    "arrows": [],
                    "is_op": True,
                    "context": "game_performance",
                }
            ]
        }

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_keywords", return_value=None), \
             patch("opgg.cacher.Cacher.cache_keywords"):

            opgg = OPGG()

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/meta/keywords.*"),
                    payload=response_with_data,
                    status=200,
                )

                keywords = opgg.get_keywords()

            assert len(keywords) == 1
            assert isinstance(keywords[0], Keyword)
            assert keywords[0].keyword == "leader"

    def test_get_keywords_handles_keywords_field(self, mock_user_agent):
        """Test handling keywords wrapped in keywords field (alternative structure)."""
        response_with_keywords = {
            "keywords": [
                {
                    "keyword": "struggle",
                    "label": "Struggle",
                    "description": "Had a tough game",
                    "arrows": [],
                    "is_op": False,
                    "context": "game_performance",
                }
            ]
        }

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_keywords", return_value=None):

            opgg = OPGG()

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/meta/keywords.*"),
                    payload=response_with_keywords,
                    status=200,
                )

                keywords = opgg.get_keywords()

            assert len(keywords) == 1
            assert keywords[0].keyword == "struggle"

    def test_get_keywords_handles_list_response(self, mock_user_agent, sample_keyword_data):
        """Test handling keywords as direct list (no wrapper)."""
        response_as_list = [sample_keyword_data]

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_keywords", return_value=None):

            opgg = OPGG()

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/meta/keywords.*"),
                    payload=response_as_list,
                    status=200,
                )

                keywords = opgg.get_keywords()

            assert len(keywords) == 1
            assert isinstance(keywords[0], Keyword)

    def test_get_keywords_empty_response(self, mock_user_agent):
        """Test handling empty keywords response."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_keywords", return_value=None):

            opgg = OPGG()

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/meta/keywords.*"),
                    payload={"data": []},
                    status=200,
                )

                keywords = opgg.get_keywords()

            assert isinstance(keywords, list)
            assert len(keywords) == 0

    def test_get_keywords_different_languages(self, mock_user_agent, mock_keywords_response):
        """Test fetching keywords with different language codes."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_keywords", return_value=None):

            opgg = OPGG()

            with aioresponses() as m:
                # Mock for Korean
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/meta/keywords.*hl=ko_KR"),
                    payload=mock_keywords_response,
                    status=200,
                )
                # Mock for French
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/meta/keywords.*hl=fr_FR"),
                    payload=mock_keywords_response,
                    status=200,
                )

                kr_keywords = opgg.get_keywords(lang_code=LangCode.KOREAN)
                fr_keywords = opgg.get_keywords(lang_code=LangCode.FRENCH)

            # Both should succeed
            assert all(isinstance(k, Keyword) for k in kr_keywords)
            assert all(isinstance(k, Keyword) for k in fr_keywords)


class TestGetAllSeasons:
    """Test get_all_seasons() method."""

    def test_get_all_seasons_first_fetch(self, mock_user_agent, mock_seasons_response):
        """Test fetching seasons for the first time (no cache)."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_seasons", return_value=None), \
             patch("opgg.cacher.Cacher.cache_seasons") as mock_cache:

            opgg = OPGG()

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/meta/seasons.*"),
                    payload=mock_seasons_response,
                    status=200,
                )

                seasons = opgg.get_all_seasons()

            # Verify returned SeasonMeta objects
            assert isinstance(seasons, list)
            assert len(seasons) > 0
            assert all(isinstance(s, SeasonMeta) for s in seasons)
            # Verify data was cached
            mock_cache.assert_called_once()

    def test_get_all_seasons_from_in_memory_cache(self, mock_user_agent, sample_season_meta):
        """Test returning seasons from in-memory cache."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            # Manually populate in-memory cache
            season = SeasonMeta(**sample_season_meta)
            opgg._season_meta_cache["en_US"] = {27: season}

            with aioresponses() as m:
                # API should NOT be called
                seasons = opgg.get_all_seasons()

            # Should return in-memory cached data
            assert len(seasons) == 1
            assert isinstance(seasons[0], SeasonMeta)
            assert seasons[0].season == 27
            # Verify no API calls were made
            assert len(m.requests) == 0

    def test_get_all_seasons_from_db_cache(self, mock_user_agent, sample_season_meta):
        """Test returning seasons from database cache."""
        cached_data = [sample_season_meta]

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_seasons", return_value=cached_data):

            opgg = OPGG()

            with aioresponses() as m:
                # API should NOT be called
                seasons = opgg.get_all_seasons()

            # Should return cached data as SeasonMeta objects
            assert len(seasons) == 1
            assert isinstance(seasons[0], SeasonMeta)
            assert seasons[0].season == 27
            # Verify in-memory cache was populated
            assert "en_US" in opgg._season_meta_cache
            assert 27 in opgg._season_meta_cache["en_US"]
            # Verify no API calls were made
            assert len(m.requests) == 0

    def test_get_all_seasons_force_refresh(self, mock_user_agent, mock_seasons_response, sample_season_meta):
        """Test force_refresh bypasses cache."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_seasons", return_value=[sample_season_meta]), \
             patch("opgg.cacher.Cacher.cache_seasons") as mock_cache:

            opgg = OPGG()
            # Set in-memory cache
            opgg._season_meta_cache["en_US"] = {27: SeasonMeta(**sample_season_meta)}

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/meta/seasons.*"),
                    payload=mock_seasons_response,
                    status=200,
                )

                seasons = opgg.get_all_seasons(force_refresh=True)

            # Should return fresh data
            assert isinstance(seasons, list)
            assert all(isinstance(s, SeasonMeta) for s in seasons)
            # Verify new data was cached
            mock_cache.assert_called_once()

    def test_get_all_seasons_different_languages(self, mock_user_agent, mock_seasons_response):
        """Test fetching seasons with different language codes."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_seasons", return_value=None):

            opgg = OPGG()

            with aioresponses() as m:
                # Mock for Korean
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/meta/seasons.*hl=ko_KR"),
                    payload=mock_seasons_response,
                    status=200,
                )
                # Mock for German
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/meta/seasons.*hl=de_DE"),
                    payload=mock_seasons_response,
                    status=200,
                )

                kr_seasons = opgg.get_all_seasons(lang_code=LangCode.KOREAN)
                de_seasons = opgg.get_all_seasons(lang_code=LangCode.GERMAN)

            # Both should succeed
            assert all(isinstance(s, SeasonMeta) for s in kr_seasons)
            assert all(isinstance(s, SeasonMeta) for s in de_seasons)
            # Verify separate cache entries
            assert "ko_KR" in opgg._season_meta_cache
            assert "de_DE" in opgg._season_meta_cache


class TestNormalizeSeasonPayload:
    """Test _normalize_seasons_payload() internal method."""

    def test_normalize_empty_payload(self, mock_user_agent):
        """Test normalizing empty/None payload."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            assert opgg._normalize_seasons_payload(None) == []
            assert opgg._normalize_seasons_payload([]) == []
            assert opgg._normalize_seasons_payload({}) == []

    def test_normalize_list_payload(self, mock_user_agent, sample_season_meta):
        """Test normalizing list of season dictionaries."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            payload = [sample_season_meta, {"id": 26, "season": 26}]
            result = opgg._normalize_seasons_payload(payload)

            assert len(result) == 2
            assert all(isinstance(s, dict) for s in result)

    def test_normalize_dict_with_seasons_key(self, mock_user_agent, sample_season_meta):
        """Test normalizing dict with 'seasons' key."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            payload = {"seasons": [sample_season_meta]}
            result = opgg._normalize_seasons_payload(payload)

            assert len(result) == 1
            assert result[0]["season"] == 27

    def test_normalize_single_dict_payload(self, mock_user_agent, sample_season_meta):
        """Test normalizing single season dict."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            result = opgg._normalize_seasons_payload(sample_season_meta)

            assert len(result) == 1
            assert result[0]["season"] == 27

    def test_normalize_filters_non_dict_items(self, mock_user_agent):
        """Test filtering out non-dict items from list."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            payload = [{"season": 1}, "invalid", None, {"season": 2}, 123]
            result = opgg._normalize_seasons_payload(payload)

            assert len(result) == 2
            assert all(isinstance(s, dict) for s in result)


class TestHydrateSeasonMeta:
    """Test _hydrate_season_meta() internal method."""

    def test_hydrate_empty_payload(self, mock_user_agent):
        """Test hydrating empty payload."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            result = opgg._hydrate_season_meta([], "en_US")

            assert result == []
            assert "en_US" not in opgg._season_meta_cache

    def test_hydrate_valid_payload(self, mock_user_agent, sample_season_meta):
        """Test hydrating valid season data."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            payload = [sample_season_meta]
            result = opgg._hydrate_season_meta(payload, "en_US")

            assert len(result) == 1
            assert isinstance(result[0], SeasonMeta)
            assert result[0].season == 27
            # Verify in-memory cache was populated
            assert "en_US" in opgg._season_meta_cache
            assert 27 in opgg._season_meta_cache["en_US"]

    def test_hydrate_multiple_seasons(self, mock_user_agent):
        """Test hydrating multiple seasons."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            payload = [
                {"id": 27, "season": 27, "display_value": "2025 S1"},
                {"id": 26, "season": 26, "display_value": "2024 S2"},
            ]
            result = opgg._hydrate_season_meta(payload, "en_US")

            assert len(result) == 2
            assert all(isinstance(s, SeasonMeta) for s in result)
            # Verify both seasons are in cache
            assert 27 in opgg._season_meta_cache["en_US"]
            assert 26 in opgg._season_meta_cache["en_US"]

    def test_hydrate_updates_existing_cache(self, mock_user_agent, sample_season_meta):
        """Test hydrating updates existing in-memory cache."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            # Populate initial cache
            old_season = SeasonMeta(id=26, season=26, display_value="Old")
            opgg._season_meta_cache["en_US"] = {26: old_season}

            # Hydrate with new data
            payload = [sample_season_meta]
            result = opgg._hydrate_season_meta(payload, "en_US")

            # Old cache should be replaced
            assert 26 not in opgg._season_meta_cache["en_US"]
            assert 27 in opgg._season_meta_cache["en_US"]
