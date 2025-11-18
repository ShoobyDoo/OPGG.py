"""Tests for opgg/utils.py - HTTP layer and utility functions."""

import pytest
import json
import logging
import re
from pathlib import Path
from unittest.mock import Mock
from aioresponses import aioresponses

from opgg.utils import Utils
from opgg.params import Region, LangCode, GenericReqParams
from opgg.search_result import SearchResult
from opgg.summoner import Summoner


class TestReadLocalJson:
    """Test the read_local_json static method."""

    def test_read_valid_json(self, tmp_path):
        """Test reading a valid JSON file."""
        test_file = tmp_path / "test.json"
        test_data = {"key": "value", "number": 42, "nested": {"data": "here"}}
        test_file.write_text(json.dumps(test_data))

        result = Utils.read_local_json(str(test_file))

        assert result == test_data
        assert result["key"] == "value"
        assert result["number"] == 42

    def test_read_empty_json(self, tmp_path):
        """Test reading an empty JSON object."""
        test_file = tmp_path / "empty.json"
        test_file.write_text("{}")

        result = Utils.read_local_json(str(test_file))

        assert result == {}

    def test_read_json_array(self, tmp_path):
        """Test reading a JSON array."""
        test_file = tmp_path / "array.json"
        test_data = [1, 2, 3, {"key": "value"}]
        test_file.write_text(json.dumps(test_data))

        result = Utils.read_local_json(str(test_file))

        assert result == test_data
        assert len(result) == 4


class TestSafeGet:
    """Test the safe_get static method for attribute access."""

    def test_safe_get_single_attr(self):
        """Test getting a single existing attribute."""

        class TestObj:
            attr = "value"

        obj = TestObj()
        result = Utils.safe_get(obj, "attr")

        assert result == "value"

    def test_safe_get_nested_attrs(self):
        """Test getting nested attributes."""

        class Level2:
            value = "deep_value"

        class Level1:
            level2 = Level2()

        class TestObj:
            level1 = Level1()

        obj = TestObj()
        result = Utils.safe_get(obj, "level1", "level2", "value")

        assert result == "deep_value"

    def test_safe_get_missing_attr(self):
        """Test getting a non-existent attribute returns None."""

        class TestObj:
            pass

        obj = TestObj()
        result = Utils.safe_get(obj, "nonexistent")

        assert result is None

    def test_safe_get_partial_path(self):
        """Test getting attribute where path breaks midway."""

        class Level1:
            pass

        class TestObj:
            level1 = Level1()

        obj = TestObj()
        # level1.level2 doesn't exist
        result = Utils.safe_get(obj, "level1", "level2", "value")

        assert result is None


class TestFilterResultsWithSummonerId:
    """Test the filter_results_with_summoner_id method."""

    def test_filter_empty_list(self):
        """Test filtering an empty list returns empty list."""
        result = Utils.filter_results_with_summoner_id([])

        assert result == []

    def test_filter_all_valid_results(self):
        """Test filtering when all results have summoner_id."""
        results = [
            SearchResult(
                summoner=Summoner(summoner_id="id1", game_name="Player1", level=100),
                region=Region.NA,
            ),
            SearchResult(
                summoner=Summoner(summoner_id="id2", game_name="Player2", level=100),
                region=Region.EUW,
            ),
        ]

        filtered = Utils.filter_results_with_summoner_id(results)

        assert len(filtered) == 2
        assert filtered == results

    def test_filter_removes_missing_summoner_id(self, caplog):
        """Test filtering removes results without summoner_id."""
        valid_result = SearchResult(
            summoner=Summoner(summoner_id="valid_id", game_name="Valid", level=100),
            region=Region.NA,
        )
        invalid_result = SearchResult(
            summoner=Summoner(game_name="Invalid", tagline="NA1", level=50),
            region=Region.EUW,
        )

        with caplog.at_level(logging.CRITICAL):
            filtered = Utils.filter_results_with_summoner_id([valid_result, invalid_result])

        assert len(filtered) == 1
        assert filtered[0].summoner.summoner_id == "valid_id"
        assert "missing a summoner_id" in caplog.text

    def test_filter_with_custom_logger(self):
        """Test filtering with a custom logger object."""
        mock_logger = Mock(spec=logging.Logger)
        invalid_result = SearchResult(
            summoner=Summoner(game_name="Player", tagline="NA1", level=100),
            region=Region.NA,
        )

        filtered = Utils.filter_results_with_summoner_id([invalid_result], mock_logger)

        assert len(filtered) == 0
        mock_logger.critical.assert_called_once()


class TestSearchRegion:
    """Test the _search_region async method."""

    @pytest.mark.asyncio
    async def test_search_region_success(self, mock_search_response):
        """Test successful region search."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-summoner.op.gg/api/summoners/{region}/search?keyword={riot_id}&hl={hl}",
            "headers": {"User-Agent": "Test"},
            "lang_code": LangCode.ENGLISH,
        }

        with aioresponses() as m:
            m.get(
                re.compile(r"https://lol-api-summoner\.op\.gg/api/summoners/[Nn][Aa]/search.*", re.IGNORECASE),
                payload=mock_search_response,
                status=200,
            )

            import aiohttp
            async with aiohttp.ClientSession() as session:
                region, data = await Utils._search_region(
                    session, "TestPlayer", Region.NA, params
                )

        assert region == Region.NA
        assert len(data) == 1
        assert data[0]["summoner_id"] == "abc123"

    @pytest.mark.asyncio
    async def test_search_region_with_tagline(self, mock_search_response):
        """Test region search with tagline in query."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-summoner.op.gg/api/summoners/{region}/search?keyword={riot_id}&hl={hl}",
            "headers": {"User-Agent": "Test"},
            "lang_code": LangCode.ENGLISH,
        }

        with aioresponses() as m:
            # The # should be encoded as %23
            m.get(
                re.compile(r"https://lol-api-summoner\.op\.gg/api/summoners/[Nn][Aa]/search.*", re.IGNORECASE),
                payload=mock_search_response,
                status=200,
            )

            import aiohttp
            async with aiohttp.ClientSession() as session:
                region, data = await Utils._search_region(
                    session, "TestPlayer#NA1", Region.NA, params
                )

        assert region == Region.NA
        assert len(data) == 1

    @pytest.mark.asyncio
    async def test_search_region_not_found(self):
        """Test region search when summoner not found."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-summoner.op.gg/api/summoners/{region}/search?keyword={riot_id}&hl={hl}",
            "headers": {"User-Agent": "Test"},
            "lang_code": LangCode.ENGLISH,
        }

        with aioresponses() as m:
            m.get(
                re.compile(r"https://lol-api-summoner\.op\.gg/api/summoners/na/search.*"),
                payload={"data": []},
                status=200,
            )

            import aiohttp
            async with aiohttp.ClientSession() as session:
                region, data = await Utils._search_region(
                    session, "Unknown", Region.NA, params
                )

        assert region == Region.NA
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_search_region_error_handling(self):
        """Test region search handles errors gracefully."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-summoner.op.gg/api/summoners/{region}/search?keyword={riot_id}&hl={hl}",
            "headers": {"User-Agent": "Test"},
            "lang_code": LangCode.ENGLISH,
        }

        with aioresponses() as m:
            m.get(
                re.compile(r"https://lol-api-summoner\.op\.gg/api/summoners/na/search.*"),
                status=500,
            )

            import aiohttp
            async with aiohttp.ClientSession() as session:
                region, data = await Utils._search_region(
                    session, "Error", Region.NA, params
                )

        assert region == Region.NA
        assert data == []


class TestSearchAllRegions:
    """Test the _search_all_regions async method."""

    @pytest.mark.asyncio
    async def test_search_all_regions_success(self):
        """Test successful multi-region search."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-summoner.op.gg/api/summoners/{region}/search?keyword={riot_id}&hl={hl}",
            "headers": {"User-Agent": "Test"},
            "lang_code": LangCode.ENGLISH,
        }

        with aioresponses() as m:
            # Mock responses for all regions using regex
            m.get(
                re.compile(r"https://lol-api-summoner\.op\.gg/api/summoners/.*/search.*"),
                payload={
                    "data": [
                        {
                            "summoner_id": "test_id",
                            "game_name": "TestPlayer",
                            "level": 100,
                        }
                    ]
                },
                status=200,
                repeat=True,
            )

            results = await Utils._search_all_regions("TestPlayer", params)

        # Should get results from all regions except ANY
        assert len(results) > 0
        assert all("region" in r and "summoner" in r for r in results)

    @pytest.mark.asyncio
    async def test_search_all_regions_deduplication(self):
        """Test that duplicate summoner_ids are removed."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-summoner.op.gg/api/summoners/{region}/search?keyword={riot_id}&hl={hl}",
            "headers": {"User-Agent": "Test"},
            "lang_code": LangCode.ENGLISH,
        }

        with aioresponses() as m:
            # Mock same summoner_id from multiple regions
            m.get(
                re.compile(r"https://lol-api-summoner\.op\.gg/api/summoners/.*/search.*"),
                payload={
                    "data": [
                        {
                            "summoner_id": "duplicate_id",  # Same ID
                            "game_name": "TestPlayer",
                            "level": 100,
                        }
                    ]
                },
                status=200,
                repeat=True,
            )

            results = await Utils._search_all_regions("TestPlayer", params)

        # Should only get one result despite multiple regions
        assert len(results) == 1
        assert results[0]["summoner"]["summoner_id"] == "duplicate_id"

    @pytest.mark.asyncio
    async def test_search_all_regions_no_results(self):
        """Test search when no summoner found in any region."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-summoner.op.gg/api/summoners/{region}/search?keyword={riot_id}&hl={hl}",
            "headers": {"User-Agent": "Test"},
            "lang_code": LangCode.ENGLISH,
        }

        with aioresponses() as m:
            m.get(
                re.compile(r"https://lol-api-summoner\.op\.gg/api/summoners/.*/search.*"),
                payload={"data": []},
                status=200,
                repeat=True,
            )

            results = await Utils._search_all_regions("NotFound", params)

        assert len(results) == 0


class TestSingleRegionSearch:
    """Test the _single_region_search async method."""

    @pytest.mark.asyncio
    async def test_single_region_search_success(self, mock_search_response):
        """Test successful single region search."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-summoner.op.gg/api/summoners/{region}/search?keyword={riot_id}&hl={hl}",
            "headers": {"User-Agent": "Test"},
            "lang_code": LangCode.ENGLISH,
        }

        with aioresponses() as m:
            m.get(
                re.compile(r"https://lol-api-summoner\.op\.gg/api/summoners/[Ee][Uu][Ww]/search.*", re.IGNORECASE),
                payload=mock_search_response,
                status=200,
            )

            results = await Utils._single_region_search("TestPlayer", Region.EUW, params)

        assert len(results) == 1
        # Region is returned as string from Region enum
        assert results[0]["region"].lower() == "euw"
        assert results[0]["summoner"]["summoner_id"] == "abc123"


class TestFetchProfile:
    """Test the _fetch_profile async method."""

    @pytest.mark.asyncio
    async def test_fetch_profile_success(self, mock_profile_response):
        """Test successful profile fetch."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-summoner.op.gg/api/summoners/na/abc123/summary",
            "headers": {"User-Agent": "Test"},
        }

        with aioresponses() as m:
            m.get(
                "https://lol-api-summoner.op.gg/api/summoners/na/abc123/summary",
                payload=mock_profile_response,
                status=200,
            )

            result = await Utils._fetch_profile("abc123", params)

        assert result is not None
        assert result["summoner_id"] == "abc123"
        assert "previous_seasons" in result

    @pytest.mark.asyncio
    async def test_fetch_profile_not_found(self):
        """Test profile fetch when summoner not found."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-summoner.op.gg/api/summoners/na/invalid/summary",
            "headers": {"User-Agent": "Test"},
        }

        with aioresponses() as m:
            m.get(
                "https://lol-api-summoner.op.gg/api/summoners/na/invalid/summary",
                status=404,
            )

            with pytest.raises(Exception):
                await Utils._fetch_profile("invalid", params)


class TestFetchProfileMultiple:
    """Test the _fetch_profile_multiple async method."""

    @pytest.mark.asyncio
    async def test_fetch_multiple_with_search_results(self, mock_profile_response):
        """Test fetching multiple profiles using search results."""
        search_results = [
            SearchResult(
                **{
                    "summoner": Summoner(summoner_id="id1", game_name="Player1", level=100),
                    "region": Region.NA,
                }
            ),
            SearchResult(
                **{
                    "summoner": Summoner(summoner_id="id2", game_name="Player2", level=100),
                    "region": Region.EUW,
                }
            ),
        ]

        params: GenericReqParams = {
            "base_api_url": "https://lol-api-summoner.op.gg/api/summoners/{region}/{summoner_id}/summary?hl={hl}",
            "headers": {"User-Agent": "Test"},
            "lang_code": LangCode.ENGLISH,
        }

        with aioresponses() as m:
            m.get(
                re.compile(r"https://lol-api-summoner\.op\.gg/api/summoners/.*/id1/summary.*"),
                payload=mock_profile_response,
                status=200,
            )
            m.get(
                re.compile(r"https://lol-api-summoner\.op\.gg/api/summoners/.*/id2/summary.*"),
                payload=mock_profile_response,
                status=200,
            )

            results = await Utils._fetch_profile_multiple(params, search_results=search_results)

        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_fetch_multiple_with_summoner_ids_and_regions(self, mock_profile_response):
        """Test fetching multiple profiles using summoner_ids and regions."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-summoner.op.gg/api/summoners/{region}/{summoner_id}/summary?hl={hl}",
            "headers": {"User-Agent": "Test"},
            "lang_code": LangCode.ENGLISH,
        }

        with aioresponses() as m:
            m.get(
                re.compile(r"https://lol-api-summoner\.op\.gg/api/summoners/.*/id1/summary.*"),
                payload=mock_profile_response,
                status=200,
            )
            m.get(
                re.compile(r"https://lol-api-summoner\.op\.gg/api/summoners/.*/id2/summary.*"),
                payload=mock_profile_response,
                status=200,
            )

            results = await Utils._fetch_profile_multiple(
                params,
                summoner_ids=["id1", "id2"],
                regions=[Region.NA, Region.KR],
            )

        assert len(results) == 2


class TestFetchRecentGames:
    """Test the _fetch_recent_games async method."""

    @pytest.mark.asyncio
    async def test_fetch_recent_games_success(self, mock_games_response):
        """Test successful recent games fetch."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-summoner.op.gg/api/summoners/na/abc123/games",
            "headers": {"User-Agent": "Test"},
        }

        with aioresponses() as m:
            m.get(
                "https://lol-api-summoner.op.gg/api/summoners/na/abc123/games",
                payload=mock_games_response,
                status=200,
            )

            result = await Utils._fetch_recent_games(params)

        assert result is not None
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_fetch_recent_games_empty(self):
        """Test fetching games when none exist."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-summoner.op.gg/api/summoners/na/abc123/games",
            "headers": {"User-Agent": "Test"},
        }

        with aioresponses() as m:
            m.get(
                "https://lol-api-summoner.op.gg/api/summoners/na/abc123/games",
                payload={"data": []},
                status=200,
            )

            result = await Utils._fetch_recent_games(params)

        assert result == []


class TestFetchRecentGamesMultiple:
    """Test the _fetch_recent_games_multiple async method."""

    @pytest.mark.asyncio
    async def test_fetch_games_multiple(self, mock_games_response):
        """Test fetching games for multiple summoners."""
        params_list = [
            {
                "base_api_url": "https://lol-api-summoner.op.gg/api/summoners/na/id1/games",
                "headers": {"User-Agent": "Test"},
            },
            {
                "base_api_url": "https://lol-api-summoner.op.gg/api/summoners/euw/id2/games",
                "headers": {"User-Agent": "Test"},
            },
        ]

        with aioresponses() as m:
            m.get(
                "https://lol-api-summoner.op.gg/api/summoners/na/id1/games",
                payload=mock_games_response,
                status=200,
            )
            m.get(
                "https://lol-api-summoner.op.gg/api/summoners/euw/id2/games",
                payload=mock_games_response,
                status=200,
            )

            results = await Utils._fetch_recent_games_multiple(params_list)

        assert len(results) == 2


class TestUpdate:
    """Test the _update async method."""

    @pytest.mark.asyncio
    async def test_update_success(self):
        """Test successful profile update."""
        search_result = SearchResult(
            **{
                "summoner": Summoner(summoner_id="abc123", game_name="Player", level=100),
                "region": Region.NA,
            }
        )

        params: GenericReqParams = {
            "base_api_url": "https://lol-api-summoner.op.gg/api/summoners/{region}/{summoner_id}/renewal",
            "headers": {"User-Agent": "Test"},
        }

        with aioresponses() as m:
            m.post(
                re.compile(r"https://lol-api-summoner\.op\.gg/api/summoners/.*/abc123/renewal"),
                payload={"message": "Profile updated successfully"},
                status=200,
            )

            result = await Utils._update(search_result, params)

        assert result is not None
        assert "message" in result

    @pytest.mark.asyncio
    async def test_update_accepted(self):
        """Test update with 202 Accepted status."""
        search_result = SearchResult(
            **{
                "summoner": Summoner(summoner_id="abc123", game_name="Player", level=100),
                "region": Region.NA,
            }
        )

        params: GenericReqParams = {
            "base_api_url": "https://lol-api-summoner.op.gg/api/summoners/{region}/{summoner_id}/renewal",
            "headers": {"User-Agent": "Test"},
        }

        with aioresponses() as m:
            m.post(
                re.compile(r"https://lol-api-summoner\.op\.gg/api/summoners/.*/abc123/renewal"),
                payload={"message": "Update queued"},
                status=202,
            )

            result = await Utils._update(search_result, params)

        assert result is not None


class TestFetchAllChampions:
    """Test the _fetch_all_champions async method."""

    @pytest.mark.asyncio
    async def test_fetch_all_champions_success(self, mock_champions_response):
        """Test successful champions fetch."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-champion.op.gg/api/champions",
            "headers": {"User-Agent": "Test"},
        }

        with aioresponses() as m:
            m.get(
                "https://lol-api-champion.op.gg/api/champions",
                payload=mock_champions_response,
                status=200,
            )

            result = await Utils._fetch_all_champions(params)

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1


class TestFetchChampionById:
    """Test the _fetch_champion_by_id async method."""

    @pytest.mark.asyncio
    async def test_fetch_champion_by_id_success(self, sample_champion_data):
        """Test successful champion fetch by ID."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-champion.op.gg/api/champions/{champion_id}?hl={hl}",
            "headers": {"User-Agent": "Test"},
        }

        with aioresponses() as m:
            m.get(
                "https://lol-api-champion.op.gg/api/champions/1?hl=en_US",
                payload={"data": sample_champion_data},
                status=200,
            )

            result = await Utils._fetch_champion_by_id(1, params, LangCode.ENGLISH)

        assert result is not None
        assert result["id"] == 1


class TestFetchChampionStats:
    """Test the _fetch_champion_stats async method."""

    @pytest.mark.asyncio
    async def test_fetch_champion_stats_success(self):
        """Test successful champion stats fetch."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-champion.op.gg/api/champions/ranked",
            "headers": {"User-Agent": "Test"},
        }

        mock_stats = {
            "data": [
                {
                    "id": 1,
                    "name": "Annie",
                    "win_rate": 52.5,
                    "pick_rate": 3.2,
                    "ban_rate": 1.1,
                }
            ]
        }

        with aioresponses() as m:
            m.get(
                "https://lol-api-champion.op.gg/api/champions/ranked",
                payload=mock_stats,
                status=200,
            )

            result = await Utils._fetch_champion_stats(params)

        assert result is not None
        assert len(result) == 1


class TestFetchVersions:
    """Test the _fetch_versions async method."""

    @pytest.mark.asyncio
    async def test_fetch_versions_success(self, mock_versions_response):
        """Test successful versions fetch."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-champion.op.gg/api/meta/versions",
            "headers": {"User-Agent": "Test"},
        }

        with aioresponses() as m:
            m.get(
                "https://lol-api-champion.op.gg/api/meta/versions",
                payload=mock_versions_response,
                status=200,
            )

            result = await Utils._fetch_versions(params)

        assert result is not None
        assert isinstance(result, list)
        assert "14.1.1" in result


class TestFetchSeasons:
    """Test the _fetch_seasons async method."""

    @pytest.mark.asyncio
    async def test_fetch_seasons_success(self, mock_seasons_response):
        """Test successful seasons fetch."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-summoner.op.gg/api/meta/seasons",
            "headers": {"User-Agent": "Test"},
        }

        with aioresponses() as m:
            m.get(
                "https://lol-api-summoner.op.gg/api/meta/seasons",
                payload=mock_seasons_response,
                status=200,
            )

            result = await Utils._fetch_seasons(params)

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1


class TestFetchKeywords:
    """Test the _fetch_keywords async method."""

    @pytest.mark.asyncio
    async def test_fetch_keywords_success(self, mock_keywords_response):
        """Test successful keywords fetch."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-summoner.op.gg/api/meta/keywords",
            "headers": {"User-Agent": "Test"},
        }

        with aioresponses() as m:
            m.get(
                "https://lol-api-summoner.op.gg/api/meta/keywords",
                payload=mock_keywords_response,
                status=200,
            )

            result = await Utils._fetch_keywords(params)

        assert result is not None
        assert isinstance(result, list)
        assert len(result) == 1


class TestFetchLiveGame:
    """Test the _fetch_live_game async method."""

    @pytest.mark.asyncio
    async def test_fetch_live_game_success(self):
        """Test successful live game fetch."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-summoner.op.gg/api/summoners/na/abc123/spectate",
            "headers": {"User-Agent": "Test"},
        }

        live_game_data = {
            "data": {
                "game_id": "123456",
                "participants": [],
            },
            "message": "Success",
        }

        with aioresponses() as m:
            m.get(
                "https://lol-api-summoner.op.gg/api/summoners/na/abc123/spectate",
                payload=live_game_data,
                status=200,
            )

            result = await Utils._fetch_live_game(params)

        assert result is not None
        assert result["status"] == 200
        assert "data" in result
        assert result["message"] == "Success"

    @pytest.mark.asyncio
    async def test_fetch_live_game_not_in_game(self):
        """Test fetching live game when summoner is not in a game."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-summoner.op.gg/api/summoners/na/abc123/spectate",
            "headers": {"User-Agent": "Test"},
        }

        error_response = {
            "code": 404,
            "message": "Not found",
            "detail": {"detailMessage": "Summoner not in live game"},
        }

        with aioresponses() as m:
            m.get(
                "https://lol-api-summoner.op.gg/api/summoners/na/abc123/spectate",
                payload=error_response,
                status=404,
            )

            result = await Utils._fetch_live_game(params)

        assert result is not None
        assert result["status"] == 404
        assert "detail" in result
        # The detail message should match what was provided in the response
        assert result["detail"] == "Summoner not in live game"

    @pytest.mark.asyncio
    async def test_fetch_live_game_404_with_empty_detail(self):
        """Test fetching live game with 404 and empty detail message."""
        params: GenericReqParams = {
            "base_api_url": "https://lol-api-summoner.op.gg/api/summoners/na/abc123/spectate",
            "headers": {"User-Agent": "Test"},
        }

        error_response = {
            "code": 404,
            "message": "Not found",
            "detail": {"detailMessage": ""},
        }

        with aioresponses() as m:
            m.get(
                "https://lol-api-summoner.op.gg/api/summoners/na/abc123/spectate",
                payload=error_response,
                status=404,
            )

            result = await Utils._fetch_live_game(params)

        assert result["status"] == 404
        assert "Provided summoner is not in a live game!" in result["detail"]
