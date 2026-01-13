"""Unit tests for cacher.py - SQLite caching system."""

import time
from opgg.cacher import Cacher
from opgg.champion import Champion
from opgg.params import LangCode, CacheType


class TestCacher:
    """Test the Cacher class functionality."""

    def test_cacher_init(self, temp_db):
        """Test Cacher initialization with custom db path."""
        cacher = Cacher(db_path=temp_db)
        assert cacher.db_path == temp_db

    def test_setup_creates_tables(self, temp_db):
        """Test that setup() creates all required tables."""
        cacher = Cacher(db_path=temp_db)
        cacher.setup()

        # Verify tables exist
        with cacher._connect() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = [row[0] for row in cursor.fetchall()]

        expected_tables = ["tblChampions", "tblKeywords", "tblSeasons", "tblVersions"]
        for table in expected_tables:
            assert table in tables, f"Table {table} should exist"

    def test_cache_champion(self, temp_db):
        """Test caching a champion."""
        cacher = Cacher(db_path=temp_db)
        cacher.setup()

        test_champion = Champion(
            id=1,
            name="Annie",
            image_url="https://example.com/annie.jpg",
        )

        cacher.cache_champs([test_champion], LangCode.ENGLISH)

        # Verify champion was cached
        cached = cacher.get_cached_champions(LangCode.ENGLISH)
        assert len(cached) == 1
        assert cached[0].id == 1
        assert cached[0].name == "Annie"

    def test_cache_ttl_expiry(self, temp_db):
        """Test that cached items respect TTL."""
        cacher = Cacher(db_path=temp_db)
        cacher.setup()

        test_champion = Champion(
            id=1,
            name="Annie",
            image_url="https://example.com/annie.jpg",
        )

        # Cache with very short TTL
        cacher.cache_champs([test_champion], LangCode.ENGLISH)

        # Check immediately with long TTL - should exist
        cached = cacher.get_cached_champions(LangCode.ENGLISH, ttl_seconds=10)
        assert len(cached) == 1

        # Wait briefly and check with very short TTL - should be considered stale after waiting
        time.sleep(0.2)
        # Use direct staleness check instead since get_cached_champions behavior changed
        is_stale = cacher.is_champion_cache_stale(LangCode.ENGLISH, ttl_seconds=0.1)
        assert is_stale is True

    def test_get_champ_id_by_name(self, temp_db):
        """Test retrieving champion ID by name."""
        cacher = Cacher(db_path=temp_db)
        cacher.setup()

        test_champion = Champion(id=1, name="Annie")
        cacher.cache_champs([test_champion], LangCode.ENGLISH)

        champ_id = cacher.get_champ_id_by_name("Annie")
        assert champ_id == 1

        champ_id_case_insensitive = cacher.get_champ_id_by_name("annie")
        assert champ_id_case_insensitive == 1

        champ_id_not_found = cacher.get_champ_id_by_name("DoesNotExist")
        assert champ_id_not_found is None

    def test_clear_cache_all(self, temp_db):
        """Test clearing all cache types."""
        cacher = Cacher(db_path=temp_db)
        cacher.setup()

        # Add data to cache
        cacher.cache_champs([Champion(id=1, name="Annie")], LangCode.ENGLISH)

        # Verify data exists
        cached = cacher.get_cached_champions(LangCode.ENGLISH)
        assert len(cached) == 1

        # Clear all cache
        cacher.clear_cache(CacheType.ALL)

        # Verify cache is empty
        cached_after = cacher.get_cached_champions(LangCode.ENGLISH)
        assert len(cached_after) == 0

    def test_cache_multiple_languages(self, temp_db):
        """Test that cache handles multiple languages separately."""
        cacher = Cacher(db_path=temp_db)
        cacher.setup()

        english_champ = Champion(id=1, name="Annie")
        korean_champ = Champion(id=2, name="애니")

        cacher.cache_champs([english_champ], LangCode.ENGLISH)
        cacher.cache_champs([korean_champ], LangCode.KOREAN)

        en_cached = cacher.get_cached_champions(LangCode.ENGLISH)
        kr_cached = cacher.get_cached_champions(LangCode.KOREAN)

        assert len(en_cached) == 1
        assert len(kr_cached) == 1
        assert en_cached[0].name == "Annie"
        assert kr_cached[0].name == "애니"

    def test_get_cache_stats(self, temp_db):
        """Test cache statistics retrieval."""
        cacher = Cacher(db_path=temp_db)
        cacher.setup()

        # Add some data
        cacher.cache_champs([Champion(id=1, name="Annie")], LangCode.ENGLISH)
        cacher.cache_champs([Champion(id=2, name="Olaf")], LangCode.ENGLISH)

        stats = cacher.get_cache_stats()

        assert "champions" in stats
        assert stats["champions"]["total_count"] >= 2
