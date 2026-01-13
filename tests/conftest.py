"""Pytest configuration and shared fixtures."""

import gc
import json
import os
import sqlite3
import tempfile
import time
from pathlib import Path

import pytest
from aioresponses import aioresponses

# Path to fixtures directory
FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict:
    """
    Load a JSON fixture file by name.

    Args:
        name: Relative path to fixture file (e.g., "summoner/search_single.json")

    Returns:
        Parsed JSON data as a dictionary

    Raises:
        FileNotFoundError: If fixture file does not exist
    """
    filepath = FIXTURES_DIR / name
    if not filepath.exists():
        raise FileNotFoundError(f"Fixture not found: {filepath}")
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def load_fixture_or_default(name: str, default: dict) -> dict:
    """
    Load a JSON fixture file, returning default if file doesn't exist.

    Args:
        name: Relative path to fixture file
        default: Default data to return if file doesn't exist

    Returns:
        Parsed JSON data or default dictionary
    """
    filepath = FIXTURES_DIR / name
    if filepath.exists():
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    return default


# =============================================================================
# Database Fixtures
# =============================================================================


@pytest.fixture
def temp_db():
    """Create a temporary SQLite database for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_opgg.db")

    yield db_path

    # Cleanup - Windows-compatible approach
    # Force garbage collection to close any lingering connections
    gc.collect()

    # Close all SQLite connections to this database
    try:
        # Try to connect and immediately close to force any pending operations
        conn = sqlite3.connect(db_path)
        conn.close()
    except Exception:
        pass

    # Small delay to allow Windows to release file locks
    time.sleep(0.1)

    # Retry removal with exponential backoff (Windows file locking workaround)
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if os.path.exists(db_path):
                os.remove(db_path)
            break
        except PermissionError:
            if attempt < max_retries - 1:
                time.sleep(0.1 * (2**attempt))  # Exponential backoff
            else:
                # Last attempt failed, but don't fail the test
                # Temp files will be cleaned up by OS eventually
                pass

    # Remove directory
    try:
        os.rmdir(temp_dir)
    except Exception:
        # Directory might not be empty or might have permissions issues
        # Don't fail the test for cleanup issues
        pass


# =============================================================================
# HTTP Mocking Fixtures
# =============================================================================


@pytest.fixture
def mock_aiohttp():
    """Mock aiohttp requests for testing."""
    with aioresponses() as m:
        yield m


# =============================================================================
# Summoner Fixtures (Real API Responses)
# =============================================================================


@pytest.fixture
def fixture_search_single():
    """Real search API response with single result (ColbyFaulkn1)."""
    return load_fixture_or_default(
        "summoner/search_single.json",
        {
            "data": [
                {
                    "summoner_id": "test-summoner-id-123",
                    "game_name": "ColbyFaulkn1",
                    "tagline": "NA1",
                    "level": 150,
                    "profile_image_url": "https://opgg-static.akamaized.net/...",
                }
            ]
        },
    )


@pytest.fixture
def fixture_search_empty():
    """Empty search API response (no results)."""
    return load_fixture_or_default("summoner/search_empty.json", {"data": []})


@pytest.fixture
def fixture_profile_full():
    """Real profile API response with full summoner data."""
    return load_fixture_or_default(
        "summoner/profile_full.json",
        {
            "data": {
                "summoner": {
                    "summoner_id": "test-summoner-id-123",
                    "game_name": "ColbyFaulkn1",
                    "tagline": "NA1",
                    "level": 150,
                    "previous_seasons": [],
                    "league_stats": [],
                    "most_champions": {"champion_stats": []},
                }
            }
        },
    )


# =============================================================================
# Games Fixtures (Real API Responses)
# =============================================================================


@pytest.fixture
def fixture_games_ranked():
    """Real games API response for ranked games."""
    return load_fixture_or_default(
        "games/games_ranked.json",
        {
            "data": [
                {
                    "id": "game-id-1",
                    "created_at": "2025-01-10T12:00:00+00:00",
                    "game_type": "ranked",
                    "game_length_second": 1800,
                    "participants": [],
                    "teams": [],
                }
            ]
        },
    )


@pytest.fixture
def fixture_games_total():
    """Real games API response for total games (20 games for pagination testing)."""
    return load_fixture_or_default(
        "games/games_total.json",
        {
            "data": [
                {"id": f"game-{i}", "created_at": f"2025-01-{10-i:02d}T12:00:00+00:00"}
                for i in range(20)
            ]
        },
    )


@pytest.fixture
def fixture_games_empty():
    """Empty games API response."""
    return load_fixture_or_default("games/games_empty.json", {"data": []})


# =============================================================================
# Champion Fixtures (Real API Responses)
# =============================================================================


@pytest.fixture
def fixture_champions_all():
    """Real champions API response with all champions."""
    return load_fixture_or_default(
        "champions/champions_all.json",
        {
            "data": [
                {"id": 266, "key": "Aatrox", "name": "Aatrox", "image_url": "https://..."},
                {"id": 103, "key": "Ahri", "name": "Ahri", "image_url": "https://..."},
                {"id": 84, "key": "Akali", "name": "Akali", "image_url": "https://..."},
            ]
        },
    )


@pytest.fixture
def fixture_champion_by_id():
    """Real champion by ID API response (Aatrox - 266)."""
    return load_fixture_or_default(
        "champions/champion_266.json",
        {
            "data": {
                "id": 266,
                "key": "Aatrox",
                "name": "Aatrox",
                "title": "the Darkin Blade",
                "blurb": "...",
                "spells": [],
                "passive": {},
                "skins": [],
            }
        },
    )


@pytest.fixture
def fixture_champion_stats():
    """Real champion stats API response."""
    return load_fixture_or_default(
        "champions/champion_stats.json",
        {
            "data": [
                {"id": 266, "play": 10000, "win": 5200, "positions": ["TOP"]},
                {"id": 103, "play": 8000, "win": 4100, "positions": ["MID"]},
            ]
        },
    )


# =============================================================================
# Metadata Fixtures (Real API Responses)
# =============================================================================


@pytest.fixture
def fixture_seasons():
    """Real seasons API response."""
    return load_fixture_or_default(
        "metadata/seasons.json",
        {
            "data": [
                {
                    "id": 27,
                    "value": 27,
                    "display_value": "2024 Split 3",
                    "season": 14,
                    "split": 3,
                },
                {
                    "id": 26,
                    "value": 26,
                    "display_value": "2024 Split 2",
                    "season": 14,
                    "split": 2,
                },
            ]
        },
    )


@pytest.fixture
def fixture_versions():
    """Real versions API response."""
    return load_fixture_or_default(
        "metadata/versions.json", {"data": ["15.1", "15.0", "14.24", "14.23"]}
    )


@pytest.fixture
def fixture_keywords():
    """Real keywords API response."""
    return load_fixture_or_default(
        "metadata/keywords.json",
        {
            "data": [
                {
                    "keyword": "leader",
                    "label": "Leader",
                    "description": "...",
                    "is_op": True,
                },
                {
                    "keyword": "struggle",
                    "label": "Struggle",
                    "description": "...",
                    "is_op": False,
                },
            ]
        },
    )


# =============================================================================
# Error Fixtures
# =============================================================================


@pytest.fixture
def fixture_404_not_found():
    """404 Not Found error response."""
    return load_fixture_or_default(
        "errors/404_not_found.json",
        {"_status": 404, "_body": {"message": "Not found"}},
    )


@pytest.fixture
def fixture_429_rate_limit():
    """429 Rate Limit error response."""
    return load_fixture_or_default(
        "errors/429_rate_limit.json",
        {"_status": 429, "message": "Too Many Requests", "retry_after": 60},
    )


# =============================================================================
# Legacy Sample Fixtures (for backward compatibility with existing tests)
# =============================================================================


@pytest.fixture
def sample_summoner_data():
    """Sample summoner API response data (legacy fixture)."""
    return {
        "data": {
            "summoner": {
                "summoner_id": "test123",
                "game_name": "Faker",
                "tagline": "KR1",
                "level": 500,
                "profile_image_url": "https://example.com/image.jpg",
                "region": "kr",
            }
        }
    }


@pytest.fixture
def sample_search_results():
    """Sample search API response data (legacy fixture)."""
    return [
        {
            "region": "na",
            "summoner": {
                "summoner_id": "abc123",
                "game_name": "TestPlayer",
                "tagline": "NA1",
                "level": 100,
            },
        }
    ]


@pytest.fixture
def sample_champions_data():
    """Sample champions API response data (legacy fixture)."""
    return {
        "data": [
            {
                "id": 1,
                "name": "Annie",
                "image_url": "https://example.com/annie.jpg",
            },
            {
                "id": 2,
                "name": "Olaf",
                "image_url": "https://example.com/olaf.jpg",
            },
        ]
    }


@pytest.fixture
def sample_games_data():
    """Sample games API response data (legacy fixture)."""
    return {
        "data": [
            {
                "game_id": "game1",
                "created_at": "2025-01-01T12:00:00Z",
                "game_type": "RANKED",
                "is_win": True,
                "champion_id": 1,
            },
            {
                "game_id": "game2",
                "created_at": "2025-01-01T11:00:00Z",
                "game_type": "NORMAL",
                "is_win": False,
                "champion_id": 2,
            },
        ]
    }
