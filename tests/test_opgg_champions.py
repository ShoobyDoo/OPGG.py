"""Tests for opgg champion methods - Champion catalog and retrieval."""

import pytest
import re
import time
from unittest.mock import patch, Mock
from aioresponses import aioresponses

from opgg.opgg import OPGG
from opgg.params import LangCode, By
from opgg.champion import Champion


pytestmark = pytest.mark.unit


class TestGetAllChampions:
    """Test get_all_champions() method."""

    def test_get_all_champions_first_fetch(
        self, mock_user_agent, mock_champions_response
    ):
        """Test fetching all champions for the first time (no cache)."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/champions.*"),
                    payload=mock_champions_response,
                    status=200,
                )

                champions = opgg.get_all_champions()

            assert isinstance(champions, list)
            assert len(champions) > 0
            assert all(isinstance(c, Champion) for c in champions)

    def test_get_all_champions_force_refresh(
        self, mock_user_agent, mock_champions_response
    ):
        """Test force_refresh bypasses cache."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            with aioresponses() as m:
                # First call
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/champions.*"),
                    payload=mock_champions_response,
                    status=200,
                )

                champions1 = opgg.get_all_champions()

            with aioresponses() as m:
                # Force refresh should hit API again
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/champions.*"),
                    payload=mock_champions_response,
                    status=200,
                )

                champions2 = opgg.get_all_champions(force_refresh=True)

            assert len(champions1) == len(champions2)


class TestGetChampionById:
    """Test get_champion_by(By.ID, ...) method."""

    def test_get_champion_by_id_first_fetch(
        self, mock_user_agent, sample_champion_data
    ):
        """Test fetching a champion by ID (no cache)."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/champions/1\?hl=.*"),
                    payload={"data": sample_champion_data},
                    status=200,
                )

                champion = opgg.get_champion_by(By.ID, 1)

            assert isinstance(champion, Champion)
            assert champion.id == 1
            assert champion.name == "Annie"

    def test_get_champion_by_id_force_refresh(
        self, mock_user_agent, sample_champion_data
    ):
        """Test force_refresh bypasses cache for champion by ID."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            with aioresponses() as m:
                # First call
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/champions/1\?hl=.*"),
                    payload={"data": sample_champion_data},
                    status=200,
                )

                champion1 = opgg.get_champion_by(By.ID, 1)

            with aioresponses() as m:
                # Force refresh - should hit API again
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/champions/1\?hl=.*"),
                    payload={"data": sample_champion_data},
                    status=200,
                )

                champion2 = opgg.get_champion_by(By.ID, 1, force_refresh=True)

            assert champion1.id == champion2.id

    def test_get_champion_by_id_with_language(
        self, mock_user_agent, sample_champion_data
    ):
        """Test fetching champion by ID with custom language."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            with aioresponses() as m:
                # URL should contain hl=ko_KR
                m.get(
                    re.compile(r".*hl=ko_KR.*"),
                    payload={"data": sample_champion_data},
                    status=200,
                )

                champion = opgg.get_champion_by(By.ID, 1, lang_code=LangCode.KOREAN)

            assert isinstance(champion, Champion)


class TestGetChampionByName:
    """Test get_champion_by(By.NAME, ...) method."""

    def test_get_champion_by_name_no_cache_fetches_all(
        self, mock_user_agent, sample_champion_data
    ):
        """Test that name search with no cache fetches all champions."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"), \
             patch("opgg.cacher.Cacher.get_cached_champions_by_name", return_value=None), \
             patch("opgg.cacher.Cacher.get_champ_id_by_name", return_value=None), \
             patch("opgg.cacher.Cacher.get_cached_champions", return_value=None), \
             patch("opgg.cacher.Cacher.cache_champs"), \
             patch("opgg.cacher.Cacher.get_cached_champs_count", return_value=0):

            opgg = OPGG()

            # Name search with empty cache should trigger get_all_champions
            with aioresponses() as m:
                # Should fetch all champions
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/champions.*"),
                    payload={"data": [sample_champion_data]},
                    status=200,
                )

                champion = opgg.get_champion_by(By.NAME, "Annie")

            assert isinstance(champion, Champion)

    def test_get_champion_by_id_nonexistent(
        self, mock_user_agent
    ):
        """Test fetching champion with non-existent ID."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            with aioresponses() as m:
                # API returns 404 or error for non-existent champion
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/meta/champions/99999\?hl=.*"),
                    status=404,
                )

                # This should raise an exception
                with pytest.raises(Exception):
                    opgg.get_champion_by(By.ID, 99999)


class TestGetChampionStats:
    """Test get_champion_stats() method."""

    def test_get_champion_stats_default_params(self, mock_user_agent):
        """Test fetching champion stats with default parameters."""
        mock_stats_response = {
            "data": {
                "champions": [
                    {
                        "id": 1,
                        "name": "Annie",
                        "tier": "1",
                        "rank": 1,
                        "win_rate": 52.5,
                        "pick_rate": 3.2,
                        "ban_rate": 1.1,
                        "games": 15000,
                    }
                ],
                "summary": {
                    "version": "14.1.1",
                    "tier": "emerald_plus",
                }
            }
        }

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/global/champions/ranked\?tier=emerald_plus.*"),
                    payload=mock_stats_response,
                    status=200,
                )

                from opgg.params import Tier, StatsRegion, Queue

                stats = opgg.get_champion_stats(tier=Tier.EMERALD_PLUS)

            assert isinstance(stats, dict)
            assert "champions" in stats
            assert stats["summary"]["tier"] == "emerald_plus"

    def test_get_champion_stats_with_all_params(self, mock_user_agent):
        """Test fetching champion stats with all parameters specified."""
        mock_stats_response = {
            "data": {
                "champions": [
                    {
                        "id": 266,
                        "name": "Aatrox",
                        "tier": "1",
                        "rank": 5,
                        "win_rate": 51.2,
                        "pick_rate": 5.8,
                        "ban_rate": 12.3,
                        "games": 25000,
                    }
                ],
                "summary": {
                    "version": "14.1.1",
                    "tier": "diamond_plus",
                    "region": "kr",
                    "queue": "SOLORANKED",
                    "season_id": 25,
                }
            }
        }

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            with aioresponses() as m:
                m.get(
                    re.compile(
                        r"https://lol-api-champion\.op\.gg/api/kr/champions/ranked\?tier=diamond_plus.*"
                        r"version=14\.1\.1.*queue_type=SOLORANKED.*season_id=25"
                    ),
                    payload=mock_stats_response,
                    status=200,
                )

                from opgg.params import Tier, StatsRegion, Queue

                stats = opgg.get_champion_stats(
                    tier=Tier.DIAMOND_PLUS,
                    version="14.1.1",
                    region=StatsRegion.KOREA,
                    queue_type=Queue.SOLO,
                    season_id=25,
                )

            assert isinstance(stats, dict)
            assert "champions" in stats
            assert stats["summary"]["season_id"] == 25

    def test_get_champion_stats_different_tiers(self, mock_user_agent):
        """Test fetching champion stats for different tiers."""
        mock_stats_response = {"data": {"champions": [], "summary": {}}}

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            from opgg.params import Tier, StatsRegion

            with aioresponses() as m:
                # Test multiple tiers
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/global/champions/ranked\?tier=platinum_plus.*"),
                    payload=mock_stats_response,
                    status=200,
                )
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/global/champions/ranked\?tier=master_plus.*"),
                    payload=mock_stats_response,
                    status=200,
                )

                plat_stats = opgg.get_champion_stats(tier=Tier.PLATINUM_PLUS)
                master_stats = opgg.get_champion_stats(tier=Tier.MASTER_PLUS)

            assert isinstance(plat_stats, dict)
            assert isinstance(master_stats, dict)

    def test_get_champion_stats_different_regions(self, mock_user_agent):
        """Test fetching champion stats for different regions."""
        mock_stats_response = {"data": {"champions": [], "summary": {}}}

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            from opgg.params import Tier, StatsRegion

            with aioresponses() as m:
                # Test multiple regions
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/global/champions/ranked.*"),
                    payload=mock_stats_response,
                    status=200,
                )
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/kr/champions/ranked.*"),
                    payload=mock_stats_response,
                    status=200,
                )
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/na/champions/ranked.*"),
                    payload=mock_stats_response,
                    status=200,
                )

                global_stats = opgg.get_champion_stats(
                    tier=Tier.EMERALD_PLUS, region=StatsRegion.GLOBAL
                )
                kr_stats = opgg.get_champion_stats(
                    tier=Tier.EMERALD_PLUS, region=StatsRegion.KOREA
                )
                na_stats = opgg.get_champion_stats(
                    tier=Tier.EMERALD_PLUS, region=StatsRegion.NORTH_AMERICA
                )

            assert isinstance(global_stats, dict)
            assert isinstance(kr_stats, dict)
            assert isinstance(na_stats, dict)

    def test_get_champion_stats_different_queues(self, mock_user_agent):
        """Test fetching champion stats for different queue types."""
        mock_stats_response = {"data": {"champions": [], "summary": {}}}

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            from opgg.params import Tier, Queue

            with aioresponses() as m:
                # Test multiple queue types
                m.get(
                    re.compile(r".*queue_type=SOLORANKED.*"),
                    payload=mock_stats_response,
                    status=200,
                )
                m.get(
                    re.compile(r".*queue_type=FLEXRANKED.*"),
                    payload=mock_stats_response,
                    status=200,
                )

                solo_stats = opgg.get_champion_stats(
                    tier=Tier.EMERALD_PLUS, queue_type=Queue.SOLO
                )
                flex_stats = opgg.get_champion_stats(
                    tier=Tier.EMERALD_PLUS, queue_type=Queue.FLEX
                )

            assert isinstance(solo_stats, dict)
            assert isinstance(flex_stats, dict)

    def test_get_champion_stats_with_version(self, mock_user_agent):
        """Test fetching champion stats for specific game version."""
        mock_stats_response = {
            "data": {
                "champions": [],
                "summary": {"version": "13.24.1"}
            }
        }

        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            from opgg.params import Tier

            with aioresponses() as m:
                m.get(
                    re.compile(r".*version=13\.24\.1.*"),
                    payload=mock_stats_response,
                    status=200,
                )

                stats = opgg.get_champion_stats(
                    tier=Tier.EMERALD_PLUS,
                    version="13.24.1"
                )

            assert isinstance(stats, dict)
            assert stats["summary"]["version"] == "13.24.1"

    def test_get_champion_stats_api_error(self, mock_user_agent):
        """Test handling API error when fetching champion stats."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            from opgg.params import Tier

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-champion\.op\.gg/api/.*"),
                    status=500,
                )

                # This should raise an exception
                with pytest.raises(Exception):
                    opgg.get_champion_stats(tier=Tier.EMERALD_PLUS)
