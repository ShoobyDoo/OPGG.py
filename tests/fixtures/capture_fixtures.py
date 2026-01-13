"""
Script to capture real OPGG API responses for test fixtures.

Usage:
    python tests/fixtures/capture_fixtures.py

This script will:
1. Make real API calls to OPGG endpoints
2. Save JSON responses to fixture files
3. Handle errors gracefully and report which endpoints failed

Environment Variables:
    TEST_SUMMONER_NAME: Riot ID to use for testing (default: ColbyFaulkn1)
    TEST_REGION: Region to use (default: na)
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import aiohttp
from fake_useragent import UserAgent

# Configuration
TEST_SUMMONER_NAME = os.getenv("TEST_SUMMONER_NAME", "ColbyFaulkn1")
TEST_REGION = os.getenv("TEST_REGION", "na")
FIXTURES_DIR = Path(__file__).parent

# API URLs (mirrored from opgg/opgg.py)
SUMMONER_API_URL = "https://lol-api-summoner.op.gg/api"
CHAMPION_API_URL = "https://lol-api-champion.op.gg/api"


async def fetch_json(session: aiohttp.ClientSession, url: str) -> dict | None:
    """Fetch JSON from a URL, returning None on error."""
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            elif response.status == 404:
                # Return the 404 response body for error fixtures
                try:
                    return {"_status": 404, "_body": await response.json()}
                except Exception:
                    return {"_status": 404, "_body": await response.text()}
            else:
                print(f"  HTTP {response.status}: {url}")
                return None
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


async def capture_search(session: aiohttp.ClientSession, summoner_name: str, region: str) -> dict | None:
    """Capture search endpoint response."""
    # Encode the summoner name for URL (replace # with %23)
    encoded_name = quote(summoner_name, safe="")
    url = f"{SUMMONER_API_URL}/v3/{region}/summoners?riot_id={encoded_name}&hl=en_US"
    return await fetch_json(session, url)


async def capture_profile(session: aiohttp.ClientSession, summoner_id: str, region: str) -> dict | None:
    """Capture profile/summary endpoint response."""
    url = f"{SUMMONER_API_URL}/{region}/summoners/{summoner_id}/summary?hl=en_US"
    return await fetch_json(session, url)


async def capture_games(
    session: aiohttp.ClientSession,
    summoner_id: str,
    region: str,
    limit: int = 15,
    game_type: str = "total",
) -> dict | None:
    """Capture games endpoint response."""
    url = (
        f"{SUMMONER_API_URL}/{region}/summoners/{summoner_id}/games?"
        f"limit={limit}&game_type={game_type}&hl=en_US&ended_at="
    )
    return await fetch_json(session, url)


async def capture_all_champions(session: aiohttp.ClientSession) -> dict | None:
    """Capture all champions metadata endpoint response."""
    url = f"{CHAMPION_API_URL}/meta/champions?hl=en_US"
    return await fetch_json(session, url)


async def capture_champion_by_id(session: aiohttp.ClientSession, champion_id: int) -> dict | None:
    """Capture single champion by ID endpoint response."""
    url = f"{CHAMPION_API_URL}/meta/champions/{champion_id}?hl=en_US"
    return await fetch_json(session, url)


async def capture_champion_stats(session: aiohttp.ClientSession, tier: str = "emerald_plus") -> dict | None:
    """Capture champion stats endpoint response."""
    url = f"{CHAMPION_API_URL}/global/champions/ranked?tier={tier}"
    return await fetch_json(session, url)


async def capture_seasons(session: aiohttp.ClientSession) -> dict | None:
    """Capture seasons metadata endpoint response."""
    url = f"{SUMMONER_API_URL}/meta/seasons?hl=en_US"
    return await fetch_json(session, url)


async def capture_versions(session: aiohttp.ClientSession) -> dict | None:
    """Capture versions metadata endpoint response."""
    url = f"{CHAMPION_API_URL}/meta/versions?hl=en_US"
    return await fetch_json(session, url)


async def capture_keywords(session: aiohttp.ClientSession) -> dict | None:
    """Capture keywords metadata endpoint response."""
    url = f"{SUMMONER_API_URL}/meta/keywords?hl=en_US"
    return await fetch_json(session, url)


async def capture_live_game(session: aiohttp.ClientSession, summoner_id: str, region: str) -> dict | None:
    """Capture live game/spectate endpoint response (usually 404 when not in game)."""
    url = f"{SUMMONER_API_URL}/{region}/summoners/{summoner_id}/spectate?hl=en_US"
    return await fetch_json(session, url)


def save_fixture(name: str, data: dict) -> bool:
    """Save fixture data to a JSON file."""
    filepath = FIXTURES_DIR / name
    filepath.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"  Failed to save {name}: {e}")
        return False


async def main() -> int:
    """Main fixture capture routine."""
    print("=" * 60)
    print("OPGG.py Test Fixture Capture")
    print("=" * 60)
    print(f"Test Summoner: {TEST_SUMMONER_NAME}")
    print(f"Test Region:   {TEST_REGION}")
    print(f"Fixtures Dir:  {FIXTURES_DIR}")
    print(f"Timestamp:     {datetime.now().isoformat()}")
    print("=" * 60)

    headers = {"User-Agent": UserAgent().random}
    success_count = 0
    fail_count = 0
    summoner_id = None

    async with aiohttp.ClientSession(headers=headers) as session:
        # Phase 1: Search to get summoner_id
        print("\n[1/11] Capturing search response...")
        search_data = await capture_search(session, TEST_SUMMONER_NAME, TEST_REGION)

        if search_data:
            if save_fixture("summoner/search_single.json", search_data):
                print("  OK: summoner/search_single.json")
                success_count += 1

                # Extract summoner_id for subsequent calls
                data_list = search_data.get("data", [])
                if data_list and len(data_list) > 0:
                    summoner_id = data_list[0].get("summoner_id")
                    print(f"  Found summoner_id: {summoner_id}")
        else:
            print("  FAIL: Could not capture search response")
            fail_count += 1

        # Create empty search fixture
        print("\n[2/11] Creating empty search fixture...")
        empty_search = {"data": []}
        if save_fixture("summoner/search_empty.json", empty_search):
            print("  OK: summoner/search_empty.json")
            success_count += 1

        if not summoner_id:
            print("\nERROR: Could not find summoner_id. Subsequent captures will fail.")
            print("Make sure the summoner name is correct and exists in the region.")
            return 1

        # Phase 2: Profile
        print("\n[3/11] Capturing profile response...")
        profile_data = await capture_profile(session, summoner_id, TEST_REGION)
        if profile_data:
            if save_fixture("summoner/profile_full.json", profile_data):
                print("  OK: summoner/profile_full.json")
                success_count += 1
        else:
            print("  FAIL: Could not capture profile response")
            fail_count += 1

        # Phase 3: Games (ranked)
        print("\n[4/11] Capturing ranked games response...")
        games_ranked = await capture_games(session, summoner_id, TEST_REGION, limit=15, game_type="ranked")
        if games_ranked:
            if save_fixture("games/games_ranked.json", games_ranked):
                print("  OK: games/games_ranked.json")
                success_count += 1
        else:
            print("  FAIL: Could not capture ranked games response")
            fail_count += 1

        # Phase 4: Games (total - for pagination testing)
        print("\n[5/11] Capturing total games response...")
        games_total = await capture_games(session, summoner_id, TEST_REGION, limit=20, game_type="total")
        if games_total:
            if save_fixture("games/games_total.json", games_total):
                print("  OK: games/games_total.json")
                success_count += 1
        else:
            print("  FAIL: Could not capture total games response")
            fail_count += 1

        # Create empty games fixture
        print("\n[6/11] Creating empty games fixture...")
        empty_games = {"data": []}
        if save_fixture("games/games_empty.json", empty_games):
            print("  OK: games/games_empty.json")
            success_count += 1

        # Phase 5: All Champions
        print("\n[7/11] Capturing all champions response...")
        champions_all = await capture_all_champions(session)
        if champions_all:
            if save_fixture("champions/champions_all.json", champions_all):
                print("  OK: champions/champions_all.json")
                success_count += 1
        else:
            print("  FAIL: Could not capture champions response")
            fail_count += 1

        # Phase 6: Champion by ID (Aatrox = 266)
        print("\n[8/11] Capturing champion by ID response (Aatrox=266)...")
        champion_266 = await capture_champion_by_id(session, 266)
        if champion_266:
            if save_fixture("champions/champion_266.json", champion_266):
                print("  OK: champions/champion_266.json")
                success_count += 1
        else:
            print("  FAIL: Could not capture champion by ID response")
            fail_count += 1

        # Phase 7: Champion Stats
        print("\n[9/11] Capturing champion stats response...")
        champion_stats = await capture_champion_stats(session, "emerald_plus")
        if champion_stats:
            if save_fixture("champions/champion_stats.json", champion_stats):
                print("  OK: champions/champion_stats.json")
                success_count += 1
        else:
            print("  FAIL: Could not capture champion stats response")
            fail_count += 1

        # Phase 8: Seasons
        print("\n[10/11] Capturing metadata responses...")
        seasons = await capture_seasons(session)
        if seasons:
            if save_fixture("metadata/seasons.json", seasons):
                print("  OK: metadata/seasons.json")
                success_count += 1
        else:
            print("  FAIL: Could not capture seasons response")
            fail_count += 1

        # Versions
        versions = await capture_versions(session)
        if versions:
            if save_fixture("metadata/versions.json", versions):
                print("  OK: metadata/versions.json")
                success_count += 1
        else:
            print("  FAIL: Could not capture versions response")
            fail_count += 1

        # Keywords
        keywords = await capture_keywords(session)
        if keywords:
            if save_fixture("metadata/keywords.json", keywords):
                print("  OK: metadata/keywords.json")
                success_count += 1
        else:
            print("  FAIL: Could not capture keywords response")
            fail_count += 1

        # Phase 9: Live game (will likely be 404)
        print("\n[11/11] Capturing live game response...")
        live_game = await capture_live_game(session, summoner_id, TEST_REGION)
        if live_game:
            # Check if it's a 404 response (player not in game)
            if live_game.get("_status") == 404:
                if save_fixture("errors/404_not_found.json", live_game):
                    print("  OK: errors/404_not_found.json (player not in game)")
                    success_count += 1
            else:
                # Player is actually in a game
                if save_fixture("summoner/live_game.json", live_game):
                    print("  OK: summoner/live_game.json (player in game!)")
                    success_count += 1
        else:
            print("  FAIL: Could not capture live game response")
            fail_count += 1

        # Create 429 rate limit fixture (simulated structure)
        print("\nCreating simulated error fixtures...")
        rate_limit = {
            "_status": 429,
            "message": "Too Many Requests",
            "retry_after": 60,
        }
        if save_fixture("errors/429_rate_limit.json", rate_limit):
            print("  OK: errors/429_rate_limit.json (simulated)")
            success_count += 1

    # Summary
    print("\n" + "=" * 60)
    print("CAPTURE COMPLETE")
    print("=" * 60)
    print(f"Success: {success_count}")
    print(f"Failed:  {fail_count}")
    print("=" * 60)

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
