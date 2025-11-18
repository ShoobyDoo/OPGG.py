"""Tests for OPGG cache management methods - force_refresh_cache, get_cache_stats, clear_cache."""

import pytest
import re
from unittest.mock import patch, Mock, call
from aioresponses import aioresponses

from opgg.opgg import OPGG
from opgg.params import CacheType, LangCode
from opgg.champion import Champion
from opgg.keyword import Keyword
from opgg.season import SeasonMeta


pytestmark = pytest.mark.unit


class TestForceRefreshCache:
    """Test force_refresh_cache() method."""

    def test_force_refresh_all_default(
        self, mock_user_agent, mock_champions_response, mock_seasons_response,
        mock_versions_response, mock_keywords_response
    ):
        """Test force refresh all cache types with default parameters (English)."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_champions", return_value=None), \
             patch("opgg.cacher.Cacher.get_cached_seasons", return_value=None), \
             patch("opgg.cacher.Cacher.get_cached_versions", return_value=None), \
             patch("opgg.cacher.Cacher.get_cached_keywords", return_value=None):

            opgg = OPGG()

            with aioresponses() as m:
                # Mock all API endpoints
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/champions.*"),
                    payload=mock_champions_response,
                    status=200,
                )
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/meta/seasons.*"),
                    payload=mock_seasons_response,
                    status=200,
                )
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/versions.*"),
                    payload=mock_versions_response,
                    status=200,
                )
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/meta/keywords.*"),
                    payload=mock_keywords_response,
                    status=200,
                )

                stats = opgg.force_refresh_cache()

            # Verify stats structure
            assert "champions" in stats
            assert "seasons" in stats
            assert "versions" in stats
            assert "keywords" in stats

            # Verify English was refreshed
            assert "en_US" in stats["champions"]["languages"]
            assert "en_US" in stats["seasons"]["languages"]
            assert "en_US" in stats["versions"]["languages"]
            assert "en_US" in stats["keywords"]["languages"]

            # Verify counts
            assert stats["champions"]["count"] > 0
            assert stats["keywords"]["count"] > 0

    def test_force_refresh_single_cache_type(
        self, mock_user_agent, mock_champions_response
    ):
        """Test force refresh single cache type (champions only)."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_champions", return_value=None):

            opgg = OPGG()

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/champions.*"),
                    payload=mock_champions_response,
                    status=200,
                )

                stats = opgg.force_refresh_cache(cache_types=CacheType.CHAMPIONS)

            # Verify only champions were refreshed
            assert stats["champions"]["count"] > 0
            assert len(stats["champions"]["languages"]) > 0

            # Others should be empty
            assert stats["seasons"]["count"] == 0
            assert stats["versions"]["count"] == 0
            assert stats["keywords"]["count"] == 0

    def test_force_refresh_multiple_cache_types(
        self, mock_user_agent, mock_champions_response, mock_keywords_response
    ):
        """Test force refresh multiple specific cache types."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_champions", return_value=None), \
             patch("opgg.cacher.Cacher.get_cached_keywords", return_value=None):

            opgg = OPGG()

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/champions.*"),
                    payload=mock_champions_response,
                    status=200,
                )
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/meta/keywords.*"),
                    payload=mock_keywords_response,
                    status=200,
                )

                stats = opgg.force_refresh_cache(
                    cache_types=[CacheType.CHAMPIONS, CacheType.KEYWORDS]
                )

            # Verify only specified types were refreshed
            assert stats["champions"]["count"] > 0
            assert stats["keywords"]["count"] > 0
            assert stats["seasons"]["count"] == 0
            assert stats["versions"]["count"] == 0

    def test_force_refresh_specific_language(
        self, mock_user_agent, mock_champions_response
    ):
        """Test force refresh for specific language."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_champions", return_value=None):

            opgg = OPGG()

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/champions.*hl=ko_KR"),
                    payload=mock_champions_response,
                    status=200,
                )

                stats = opgg.force_refresh_cache(
                    cache_types=CacheType.CHAMPIONS,
                    lang_code=LangCode.KOREAN
                )

            # Verify Korean was refreshed
            assert "ko_KR" in stats["champions"]["languages"]
            assert "en_US" not in stats["champions"]["languages"]

    def test_force_refresh_all_languages(
        self, mock_user_agent, mock_champions_response
    ):
        """Test force refresh for all cached languages."""
        # Mock cache stats showing multiple languages cached
        cache_stats = {
            "champions": {
                "languages": ["en_US", "ko_KR", "ja_JP"],
                "total_count": 150,
            },
            "seasons": {"languages": [], "total_count": 0},
            "versions": {"languages": [], "total_count": 0},
            "keywords": {"languages": [], "total_count": 0},
        }

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cache_stats", return_value=cache_stats), \
             patch("opgg.cacher.Cacher.get_cached_champions", return_value=None):

            opgg = OPGG()

            with aioresponses() as m:
                # Mock all three languages
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/champions.*hl=en_US"),
                    payload=mock_champions_response,
                    status=200,
                )
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/champions.*hl=ko_KR"),
                    payload=mock_champions_response,
                    status=200,
                )
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/champions.*hl=ja_JP"),
                    payload=mock_champions_response,
                    status=200,
                )

                stats = opgg.force_refresh_cache(
                    cache_types=CacheType.CHAMPIONS,
                    all_languages=True
                )

            # Verify all three languages were refreshed
            assert "en_US" in stats["champions"]["languages"]
            assert "ko_KR" in stats["champions"]["languages"]
            assert "ja_JP" in stats["champions"]["languages"]
            assert len(stats["champions"]["languages"]) == 3

    def test_force_refresh_all_languages_no_cached_langs(
        self, mock_user_agent, mock_champions_response
    ):
        """Test force refresh all languages when no languages cached yet (defaults to English)."""
        cache_stats = {
            "champions": {"languages": [], "total_count": 0},
            "seasons": {"languages": [], "total_count": 0},
            "versions": {"languages": [], "total_count": 0},
            "keywords": {"languages": [], "total_count": 0},
        }

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cache_stats", return_value=cache_stats), \
             patch("opgg.cacher.Cacher.get_cached_champions", return_value=None):

            opgg = OPGG()

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/champions.*"),
                    payload=mock_champions_response,
                    status=200,
                )

                stats = opgg.force_refresh_cache(
                    cache_types=CacheType.CHAMPIONS,
                    all_languages=True
                )

            # Should default to English
            assert "en_US" in stats["champions"]["languages"]

    def test_force_refresh_handles_api_error(self, mock_user_agent):
        """Test force refresh handles API errors gracefully."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_champions", return_value=None):

            opgg = OPGG()

            with aioresponses() as m:
                # Mock API error
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/champions.*"),
                    status=500,
                )

                stats = opgg.force_refresh_cache(cache_types=CacheType.CHAMPIONS)

            # Should return empty stats for failed refresh
            assert stats["champions"]["count"] == 0
            assert len(stats["champions"]["languages"]) == 0


class TestGetCacheStats:
    """Test get_cache_stats() method."""

    def test_get_cache_stats_empty_cache(self, mock_user_agent):
        """Test getting stats from empty cache."""
        empty_stats = {
            "champions": {"languages": [], "total_count": 0},
            "seasons": {"languages": [], "total_count": 0},
            "versions": {"languages": [], "total_count": 0},
            "keywords": {"languages": [], "total_count": 0},
        }

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cache_stats", return_value=empty_stats):

            opgg = OPGG()
            stats = opgg.get_cache_stats()

            assert stats == empty_stats
            assert stats["champions"]["total_count"] == 0

    def test_get_cache_stats_populated_cache(self, mock_user_agent):
        """Test getting stats from populated cache."""
        populated_stats = {
            "champions": {
                "languages": ["en_US", "ko_KR"],
                "total_count": 166,
                "by_language": {"en_US": 83, "ko_KR": 83},
            },
            "seasons": {
                "languages": ["en_US"],
                "total_count": 15,
            },
            "versions": {
                "languages": ["en_US"],
                "total_count": 1,
            },
            "keywords": {
                "languages": ["en_US"],
                "total_count": 20,
            },
        }

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cache_stats", return_value=populated_stats):

            opgg = OPGG()
            stats = opgg.get_cache_stats()

            assert stats == populated_stats
            assert stats["champions"]["total_count"] == 166
            assert "en_US" in stats["champions"]["languages"]
            assert "ko_KR" in stats["champions"]["languages"]

    def test_get_cache_stats_structure(self, mock_user_agent):
        """Test cache stats has correct structure."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cache_stats") as mock_stats:

            opgg = OPGG()
            stats = opgg.get_cache_stats()

            # Verify cacher method was called
            mock_stats.assert_called_once()


class TestClearCache:
    """Test clear_cache() method."""

    def test_clear_all_cache_default(self, mock_user_agent):
        """Test clearing all cache with default parameters."""
        cleared_stats = {
            "champions": 166,
            "seasons": 15,
            "versions": 1,
            "keywords": 20,
            "total": 202,
        }

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.clear_cache", return_value=cleared_stats) as mock_clear:

            opgg = OPGG()
            result = opgg.clear_cache()

            # Verify cacher method was called with correct params
            mock_clear.assert_called_once_with(
                cache_type=CacheType.ALL,
                lang_code=None
            )
            assert result == cleared_stats
            assert result["total"] == 202

    def test_clear_specific_cache_type(self, mock_user_agent):
        """Test clearing specific cache type."""
        cleared_stats = {
            "champions": 166,
            "seasons": 0,
            "versions": 0,
            "keywords": 0,
            "total": 166,
        }

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.clear_cache", return_value=cleared_stats) as mock_clear:

            opgg = OPGG()
            result = opgg.clear_cache(cache_type=CacheType.CHAMPIONS)

            mock_clear.assert_called_once_with(
                cache_type=CacheType.CHAMPIONS,
                lang_code=None
            )
            assert result["champions"] == 166
            assert result["seasons"] == 0

    def test_clear_cache_specific_language(self, mock_user_agent):
        """Test clearing cache for specific language."""
        cleared_stats = {
            "champions": 83,
            "seasons": 0,
            "versions": 0,
            "keywords": 0,
            "total": 83,
        }

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.clear_cache", return_value=cleared_stats) as mock_clear:

            opgg = OPGG()
            result = opgg.clear_cache(
                cache_type=CacheType.CHAMPIONS,
                lang_code=LangCode.KOREAN
            )

            mock_clear.assert_called_once_with(
                cache_type=CacheType.CHAMPIONS,
                lang_code=LangCode.KOREAN
            )
            assert result["total"] == 83

    def test_clear_cache_seasons_only(self, mock_user_agent):
        """Test clearing seasons cache only."""
        cleared_stats = {
            "champions": 0,
            "seasons": 15,
            "versions": 0,
            "keywords": 0,
            "total": 15,
        }

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.clear_cache", return_value=cleared_stats) as mock_clear:

            opgg = OPGG()
            result = opgg.clear_cache(cache_type=CacheType.SEASONS)

            mock_clear.assert_called_once_with(
                cache_type=CacheType.SEASONS,
                lang_code=None
            )
            assert result["seasons"] == 15

    def test_clear_cache_versions_only(self, mock_user_agent):
        """Test clearing versions cache only."""
        cleared_stats = {
            "champions": 0,
            "seasons": 0,
            "versions": 1,
            "keywords": 0,
            "total": 1,
        }

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.clear_cache", return_value=cleared_stats) as mock_clear:

            opgg = OPGG()
            result = opgg.clear_cache(cache_type=CacheType.VERSIONS)

            mock_clear.assert_called_once_with(
                cache_type=CacheType.VERSIONS,
                lang_code=None
            )
            assert result["versions"] == 1

    def test_clear_cache_keywords_only(self, mock_user_agent):
        """Test clearing keywords cache only."""
        cleared_stats = {
            "champions": 0,
            "seasons": 0,
            "versions": 0,
            "keywords": 20,
            "total": 20,
        }

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.clear_cache", return_value=cleared_stats) as mock_clear:

            opgg = OPGG()
            result = opgg.clear_cache(cache_type=CacheType.KEYWORDS)

            mock_clear.assert_called_once_with(
                cache_type=CacheType.KEYWORDS,
                lang_code=None
            )
            assert result["keywords"] == 20

    def test_clear_cache_empty_cache(self, mock_user_agent):
        """Test clearing already empty cache."""
        cleared_stats = {
            "champions": 0,
            "seasons": 0,
            "versions": 0,
            "keywords": 0,
            "total": 0,
        }

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.clear_cache", return_value=cleared_stats):

            opgg = OPGG()
            result = opgg.clear_cache()

            assert result["total"] == 0
