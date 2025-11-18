"""Tests for params module enums and types (opgg/params.py)."""

import pytest
from opgg.params import (
    Region, By, Queue, LangCode, CacheType, Tier, GameType,
    StatsRegion, SearchReturnType, GenericReqParams
)


pytestmark = pytest.mark.unit


class TestRegionEnum:
    """Test Region enum."""

    def test_region_values(self):
        """Test Region enum has all expected values."""
        assert Region.NA.value == "NA"
        assert Region.EUW.value == "EUW"
        assert Region.EUNE.value == "EUNE"
        assert Region.KR.value == "KR"
        assert Region.JP.value == "JP"
        assert Region.BR.value == "BR"
        assert Region.LAN.value == "LAN"
        assert Region.LAS.value == "LAS"
        assert Region.OCE.value == "OCE"
        assert Region.RU.value == "RU"
        assert Region.TR.value == "TR"
        assert Region.ANY.value == "ANY"

    def test_region_str_conversion(self):
        """Test Region __str__ returns value."""
        assert str(Region.NA) == "NA"
        assert str(Region.KR) == "KR"
        assert str(Region.ANY) == "ANY"


class TestByEnum:
    """Test By enum."""

    def test_by_values(self):
        """Test By enum values."""
        assert By.ID.value == "id"
        assert By.NAME.value == "name"
        assert By.COST.value == "cost"
        assert By.BLUE_ESSENCE.value == "BE"
        assert By.RIOT_POINTS.value == "RP"

    def test_by_str_conversion(self):
        """Test By __str__ returns value."""
        assert str(By.ID) == "id"
        assert str(By.NAME) == "name"


class TestQueueEnum:
    """Test Queue enum."""

    def test_queue_values(self):
        """Test Queue enum values."""
        assert Queue.SOLO.value == "SOLORANKED"
        assert Queue.FLEX.value == "FLEXRANKED"
        assert Queue.ARENA.value == "ARENA"

    def test_queue_str_conversion(self):
        """Test Queue __str__ returns value."""
        assert str(Queue.SOLO) == "SOLORANKED"


class TestLangCodeEnum:
    """Test LangCode enum."""

    def test_langcode_values(self):
        """Test LangCode enum values."""
        assert LangCode.ENGLISH.value == "en_US"
        assert LangCode.KOREAN.value == "ko_KR"
        assert LangCode.JAPANESE.value == "ja_JP"
        assert LangCode.CHINESE.value == "zh_CN"

    def test_langcode_str_conversion(self):
        """Test LangCode __str__ returns value."""
        assert str(LangCode.ENGLISH) == "en_US"
        assert str(LangCode.KOREAN) == "ko_KR"


class TestCacheTypeEnum:
    """Test CacheType enum."""

    def test_cachetype_values(self):
        """Test CacheType enum values."""
        assert CacheType.CHAMPIONS.value == "champions"
        assert CacheType.SEASONS.value == "seasons"
        assert CacheType.VERSIONS.value == "versions"
        assert CacheType.KEYWORDS.value == "keywords"
        assert CacheType.ALL.value == "all"


class TestTierEnum:
    """Test Tier enum."""

    def test_tier_values(self):
        """Test Tier enum values."""
        assert Tier.ALL.value == "all"
        assert Tier.IRON.value == "iron"
        assert Tier.BRONZE.value == "bronze"
        assert Tier.SILVER.value == "silver"
        assert Tier.GOLD.value == "gold"
        assert Tier.PLATINUM.value == "platinum"
        assert Tier.EMERALD.value == "emerald"
        assert Tier.DIAMOND.value == "diamond"
        assert Tier.MASTER.value == "master"
        assert Tier.GRANDMASTER.value == "grandmaster"
        assert Tier.CHALLENGER.value == "challenger"
        assert Tier.EMERALD_PLUS.value == "emerald_plus"
        assert Tier.DIAMOND_PLUS.value == "diamond_plus"


class TestGameTypeEnum:
    """Test GameType enum."""

    def test_gametype_values(self):
        """Test GameType enum values."""
        assert GameType.TOTAL.value == "total"
        assert GameType.RANKED.value == "ranked"
        assert GameType.NORMAL.value == "normal"


class TestStatsRegionEnum:
    """Test StatsRegion enum."""

    def test_statsregion_values(self):
        """Test StatsRegion enum values."""
        assert StatsRegion.GLOBAL.value == "global"


class TestSearchReturnTypeEnum:
    """Test SearchReturnType enum."""

    def test_searchreturntype_values(self):
        """Test SearchReturnType enum values."""
        assert SearchReturnType.SIMPLE.value == "simple"
        assert SearchReturnType.FULL.value == "full"


class TestGenericReqParams:
    """Test GenericReqParams TypedDict."""

    def test_generic_req_params_structure(self):
        """Test GenericReqParams can be instantiated with correct fields."""
        params: GenericReqParams = {
            "base_api_url": "https://api.example.com",
            "headers": {"User-Agent": "Test"},
        }

        assert params["base_api_url"] == "https://api.example.com"
        assert params["headers"]["User-Agent"] == "Test"

    def test_generic_req_params_with_lang_code(self):
        """Test GenericReqParams with optional lang_code field."""
        params: GenericReqParams = {
            "base_api_url": "https://api.example.com",
            "headers": {"User-Agent": "Test"},
            "lang_code": LangCode.ENGLISH,
        }

        assert params["lang_code"] == LangCode.ENGLISH
