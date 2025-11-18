"""Shared test fixtures and utilities for OPGG.py test suite."""

import pytest
import tempfile
import shutil
import logging
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch
from aioresponses import aioresponses

from opgg.params import Region, LangCode, GameType, Tier, By, SearchReturnType
from opgg.champion import Champion, ChampionStats, Info, Stats, Skin, Price
from opgg.summoner import Summoner
from opgg.game import Game, Participant, Team, GameStat, Stats as GameStats
from opgg.season import Season, SeasonMeta, League, TierInfo, QueueInfo, RankInfo
from opgg.keyword import Keyword
from opgg.search_result import SearchResult


# Suppress Pydantic logging warnings during tests
@pytest.fixture(autouse=True)
def suppress_pydantic_warnings(caplog):
    """Suppress Pydantic field validation warnings during tests."""
    caplog.set_level(logging.ERROR, logger="OPGG.py")


# Temporary directory fixtures
@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp, ignore_errors=True)


@pytest.fixture
def temp_cache_dir(temp_dir):
    """Create a temporary cache directory."""
    cache_dir = temp_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir


@pytest.fixture
def temp_db_path(temp_cache_dir):
    """Create a temporary database path."""
    return str(temp_cache_dir / "test_opgg.db")


# Mock UserAgent fixture
@pytest.fixture
def mock_user_agent():
    """Mock fake_useragent.UserAgent."""
    with patch("opgg.opgg.UserAgent") as mock_ua:
        mock_ua.return_value.random = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Test Agent"
        )
        yield mock_ua


# HTTP mocking fixture
@pytest.fixture
def mock_aiohttp():
    """Mock aiohttp responses."""
    with aioresponses() as m:
        yield m


# Sample data factories
@pytest.fixture
def sample_champion_data():
    """Generate sample champion data."""
    return {
        "id": 1,
        "key": "Annie",
        "name": "Annie",
        "image_url": "https://opgg-static.akamaized.net/meta/images/lol/latest/champion/Annie.png",
        "title": "the Dark Child",
        "tags": ["Mage"],
        "blurb": "Dangerous, yet disarmingly precocious...",
        "lore": "Wielding destruction with...",
        "partype": "Mana",
        "info": {"attack": 2, "defense": 3, "magic": 10, "difficulty": 6},
        "stats": {
            "hp": 560.0,
            "hpperlevel": 102.0,
            "mp": 418.0,
            "mpperlevel": 25.0,
            "movespeed": 335.0,
            "armor": 19.22,
            "armorperlevel": 4.7,
            "spellblock": 30.0,
            "spellblockperlevel": 1.3,
            "attackrange": 625.0,
            "hpregen": 5.5,
            "hpregenperlevel": 0.55,
            "mpregen": 8.0,
            "mpregenperlevel": 0.8,
            "crit": 0.0,
            "critperlevel": 0.0,
            "attackdamage": 50.0,
            "attackdamageperlevel": 2.625,
            "attackspeed": 0.579,
            "attackspeedperlevel": 1.36,
        },
        "skins": [
            {
                "id": 1000,
                "champion_id": 1,
                "name": "default",
                "has_chromas": False,
                "splash_image": "https://example.com/splash.jpg",
                "loading_image": "https://example.com/loading.jpg",
                "tiles_image": None,
                "centered_image": None,
                "skin_video_url": None,
                "prices": [{"currency": "BE", "cost": 450}],
                "sales": None,
                "release_date": "2009-02-21T00:00:00",
            }
        ],
    }


@pytest.fixture
def sample_summoner_data():
    """Generate sample summoner data."""
    return {
        "id": 12345,
        "summoner_id": "abc123",
        "acct_id": "def456",
        "puuid": "ghi789",
        "game_name": "TestPlayer",
        "tagline": "NA1",
        "name": "TestPlayer",
        "internal_name": "testplayer",
        "profile_image_url": "https://example.com/profile.png",
        "level": 150,
        "updated_at": "2025-01-15T12:00:00",
        "renewable_at": "2025-01-15T12:05:00",
        "revision_at": "2025-01-15T12:00:00",
        "solo_tier_info": {
            "tier": "GOLD",
            "division": 2,
            "lp": 45,
            "level": None,
            "tier_image_url": "https://example.com/gold.png",
            "border_image_url": "https://example.com/border.png",
        },
    }


@pytest.fixture
def sample_game_data():
    """Generate sample game data."""
    return {
        "id": "game123",
        "created_at": "2025-01-15T10:30:00",
        "game_map": "Summoner's Rift",
        "game_type": "SOLORANKED",
        "version": "14.1.1",
        "game_length_second": 1800,
        "is_remake": False,
        "is_opscore_active": True,
        "participants": [
            {
                "participant_id": 1,
                "champion_id": 1,
                "team_key": "BLUE",
                "position": "MID",
                "items": [3089, 3135, 3157],
                "spells": [4, 14],
                "stats": {
                    "kill": 10,
                    "death": 2,
                    "assist": 8,
                    "minion_kill": 180,
                    "gold_earned": 15000,
                    "result": "WIN",
                    "op_score": 8.5,
                },
            }
        ],
        "teams": [
            {
                "key": "BLUE",
                "game_stat": {
                    "is_win": True,
                    "champion_kill": 25,
                    "tower_kill": 9,
                    "dragon_kill": 3,
                    "baron_kill": 1,
                },
                "banned_champions": [157, 64, 38, 55, 555],
            }
        ],
    }


@pytest.fixture
def sample_season_meta():
    """Generate sample season metadata."""
    return {
        "id": 27,
        "season": 27,
        "value": 27,
        "display_value": "2025 Season 1",
        "split": None,
        "is_preseason": False,
    }


@pytest.fixture
def sample_keyword_data():
    """Generate sample keyword data."""
    return {
        "keyword": "leader",
        "label": "Leader",
        "description": "Dominated the game from start to finish",
        "arrows": [],
        "is_op": True,
        "context": "game_performance",
    }


@pytest.fixture
def sample_search_result(sample_summoner_data):
    """Generate sample SearchResult."""
    summoner = Summoner(**sample_summoner_data)
    return SearchResult(summoner=summoner, region=Region.NA)


# Mock API response factories
@pytest.fixture
def mock_search_response():
    """Mock search API response."""
    return {
        "data": [
            {
                "id": 12345,
                "summoner_id": "abc123",
                "game_name": "TestPlayer",
                "tagline": "NA1",
                "level": 150,
                "profile_image_url": "https://example.com/profile.png",
                "updated_at": "2025-01-15T12:00:00Z",
            }
        ]
    }


@pytest.fixture
def mock_profile_response(sample_summoner_data):
    """Mock profile API response with full data."""
    return {
        "data": {
            **sample_summoner_data,
            "previous_seasons": [
                {
                    "season_id": 26,
                    "tier_info": {
                        "tier": "GOLD",
                        "division": 1,
                        "lp": 0,
                    },
                }
            ],
            "league_stats": [
                {
                    "queue_info": {"game_type": "SOLORANKED"},
                    "tier_info": {"tier": "GOLD", "division": 2, "lp": 45},
                    "win": 120,
                    "lose": 100,
                }
            ],
        }
    }


@pytest.fixture
def mock_games_response(sample_game_data):
    """Mock games API response."""
    return {"data": [sample_game_data], "meta": {"first_game_created_at": "2025-01-15T10:30:00", "last_game_created_at": "2025-01-15T10:30:00"}}


@pytest.fixture
def mock_champions_response(sample_champion_data):
    """Mock champions API response."""
    return {"data": [sample_champion_data]}


@pytest.fixture
def mock_versions_response():
    """Mock versions API response."""
    return {"data": ["14.1.1", "14.1.0", "13.24.1"]}


@pytest.fixture
def mock_seasons_response(sample_season_meta):
    """Mock seasons API response."""
    return {"data": [sample_season_meta]}


@pytest.fixture
def mock_keywords_response(sample_keyword_data):
    """Mock keywords API response."""
    return {"data": [sample_keyword_data]}


# Helper functions
@pytest.fixture
def create_champion():
    """Factory function to create Champion instances."""

    def _create(champion_id=1, name="TestChampion", **kwargs):
        data = {
            "id": champion_id,
            "key": name,
            "name": name,
            "image_url": f"https://example.com/{name}.png",
            "title": f"the {name}",
            "tags": ["Fighter"],
            **kwargs,
        }
        return Champion(**data)

    return _create


@pytest.fixture
def create_summoner():
    """Factory function to create Summoner instances."""

    def _create(summoner_id="test123", game_name="TestPlayer", **kwargs):
        data = {
            "id": 12345,
            "summoner_id": summoner_id,
            "game_name": game_name,
            "tagline": "NA1",
            "level": 100,
            **kwargs,
        }
        return Summoner(**data)

    return _create


@pytest.fixture
def create_game():
    """Factory function to create Game instances."""

    def _create(game_id="game123", **kwargs):
        data = {
            "id": game_id,
            "created_at": datetime.now(),
            "game_type": "SOLORANKED",
            "game_length_second": 1800,
            **kwargs,
        }
        return Game(**data)

    return _create


# Environment variable fixtures
@pytest.fixture
def clean_env(monkeypatch):
    """Clean environment variables before each test."""
    monkeypatch.delenv("OPGG_CHAMPION_CACHE_TTL_HOURS", raising=False)
    monkeypatch.delenv("OPGG_CACHE_DIR", raising=False)


# Async helper fixtures
@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    import asyncio

    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
