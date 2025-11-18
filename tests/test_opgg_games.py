"""Tests for opgg.get_recent_games() - Match History functionality."""

import pytest
import re
from unittest.mock import patch
from aioresponses import aioresponses

from opgg.opgg import OPGG
from opgg.params import Region, LangCode, GameType
from opgg.search_result import SearchResult
from opgg.summoner import Summoner
from opgg.game import Game


pytestmark = pytest.mark.unit


class TestGetRecentGamesSingle:
    """Test get_recent_games() for a single summoner."""

    def test_get_recent_games_with_search_result(
        self, mock_user_agent, mock_games_response
    ):
        """Test fetching recent games with a single SearchResult."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            search_result = SearchResult(
                summoner=Summoner(summoner_id="test123", game_name="Player1", level=100),
                region=Region.NA,
            )

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/.*/summoners/test123/games.*"),
                    payload=mock_games_response,
                    status=200,
                )

                games = opgg.get_recent_games(search_result=search_result)

            assert isinstance(games, list)
            assert len(games) > 0
            assert all(isinstance(g, Game) for g in games)

    def test_get_recent_games_with_results_limit(
        self, mock_user_agent, mock_games_response
    ):
        """Test fetching recent games with custom results limit."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            search_result = SearchResult(
                summoner=Summoner(summoner_id="test123", game_name="Player1", level=100),
                region=Region.EUW,
            )

            with aioresponses() as m:
                # The URL should contain limit=25
                m.get(
                    re.compile(r".*limit=25.*"),
                    payload=mock_games_response,
                    status=200,
                )

                games = opgg.get_recent_games(search_result=search_result, results=25)

            assert isinstance(games, list)

    def test_get_recent_games_with_game_type(
        self, mock_user_agent, mock_games_response
    ):
        """Test fetching games with specific GameType."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            search_result = SearchResult(
                summoner=Summoner(summoner_id="test123", game_name="Player1", level=100),
                region=Region.KR,
            )

            with aioresponses() as m:
                # The URL should contain game_type=ranked
                m.get(
                    re.compile(r".*ranked.*"),
                    payload=mock_games_response,
                    status=200,
                )

                games = opgg.get_recent_games(
                    search_result=search_result, game_type=GameType.RANKED
                )

            assert isinstance(games, list)

    def test_get_recent_games_game_type_coercion(
        self, mock_user_agent, mock_games_response
    ):
        """Test that GameType enum is properly coerced to string value."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            search_result = SearchResult(
                summoner=Summoner(summoner_id="test123", game_name="Player1", level=100),
                region=Region.NA,
            )

            with aioresponses() as m:
                # Verify the GameType.TOTAL value is used in URL
                m.get(
                    re.compile(r".*game_type=total.*"),
                    payload=mock_games_response,
                    status=200,
                )

                games = opgg.get_recent_games(
                    search_result=search_result, game_type=GameType.TOTAL
                )

            assert isinstance(games, list)

    def test_get_recent_games_with_lang_code(
        self, mock_user_agent, mock_games_response
    ):
        """Test fetching games with custom language code."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            search_result = SearchResult(
                summoner=Summoner(summoner_id="test123", game_name="Player1", level=100),
                region=Region.KR,
            )

            with aioresponses() as m:
                # URL should contain hl=ko_KR
                m.get(
                    re.compile(r".*hl=ko_KR.*"),
                    payload=mock_games_response,
                    status=200,
                )

                games = opgg.get_recent_games(
                    search_result=search_result, lang_code=LangCode.KOREAN
                )

            assert isinstance(games, list)

    def test_get_recent_games_empty_response(
        self, mock_user_agent
    ):
        """Test fetching games when none exist."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            search_result = SearchResult(
                summoner=Summoner(summoner_id="test123", game_name="Player1", level=100),
                region=Region.NA,
            )

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/.*/summoners/test123/games.*"),
                    payload={"data": []},
                    status=200,
                )

                games = opgg.get_recent_games(search_result=search_result)

            assert games == []


class TestGetRecentGamesMultiple:
    """Test get_recent_games() for multiple summoners."""

    def test_get_recent_games_with_multiple_search_results(
        self, mock_user_agent, mock_games_response
    ):
        """Test fetching games for multiple summoners."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            search_results = [
                SearchResult(
                    summoner=Summoner(summoner_id="id1", game_name="Player1", level=100),
                    region=Region.NA,
                ),
                SearchResult(
                    summoner=Summoner(summoner_id="id2", game_name="Player2", level=100),
                    region=Region.EUW,
                ),
            ]

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/.*/summoners/id1/games.*"),
                    payload=mock_games_response,
                    status=200,
                )
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/.*/summoners/id2/games.*"),
                    payload=mock_games_response,
                    status=200,
                )

                games_list = opgg.get_recent_games(search_result=search_results)

            assert isinstance(games_list, list)
            assert len(games_list) == 2
            # Each element should be a list of games
            assert all(isinstance(games, list) for games in games_list)
            assert all(isinstance(g, Game) for games in games_list for g in games)

    def test_get_recent_games_multiple_with_game_type(
        self, mock_user_agent, mock_games_response
    ):
        """Test fetching ranked games for multiple summoners."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            search_results = [
                SearchResult(
                    summoner=Summoner(summoner_id="id1", game_name="Player1", level=100),
                    region=Region.NA,
                ),
                SearchResult(
                    summoner=Summoner(summoner_id="id2", game_name="Player2", level=100),
                    region=Region.KR,
                ),
            ]

            with aioresponses() as m:
                # Both should have game_type=ranked
                m.get(
                    re.compile(r".*game_type=ranked.*"),
                    payload=mock_games_response,
                    status=200,
                    repeat=True,
                )

                games_list = opgg.get_recent_games(
                    search_result=search_results, game_type=GameType.RANKED
                )

            assert len(games_list) == 2


class TestGetRecentGamesFallback:
    """Test get_recent_games() with summoner_id and region fallback."""

    def test_get_recent_games_with_summoner_id_region_single(
        self, mock_user_agent, mock_games_response
    ):
        """Test fetching games with summoner_id and region parameters."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/.*/summoners/fallback123/games.*"),
                    payload=mock_games_response,
                    status=200,
                )

                games = opgg.get_recent_games(
                    summoner_id="fallback123", region=Region.NA
                )

            assert isinstance(games, list)
            assert len(games) > 0

    def test_get_recent_games_with_summoner_id_region_multiple(
        self, mock_user_agent, mock_games_response
    ):
        """Test fetching games with lists of summoner_ids and regions."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/.*/summoners/sid1/games.*"),
                    payload=mock_games_response,
                    status=200,
                )
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/.*/summoners/sid2/games.*"),
                    payload=mock_games_response,
                    status=200,
                )

                games_list = opgg.get_recent_games(
                    summoner_id=["sid1", "sid2"], region=[Region.NA, Region.EUW]
                )

            assert isinstance(games_list, list)
            assert len(games_list) == 2
            assert all(isinstance(games, list) for games in games_list)

    def test_get_recent_games_fallback_with_game_type(
        self, mock_user_agent, mock_games_response
    ):
        """Test summoner_id/region fallback with specific game type."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            with aioresponses() as m:
                m.get(
                    re.compile(r".*game_type=ranked.*"),
                    payload=mock_games_response,
                    status=200,
                )

                games = opgg.get_recent_games(
                    summoner_id="test", region=Region.NA, game_type=GameType.RANKED
                )

            assert isinstance(games, list)


class TestGetRecentGamesErrorHandling:
    """Test error handling for get_recent_games()."""

    def test_get_recent_games_mismatched_summoner_id_region_types(
        self, mock_user_agent
    ):
        """Test error when summoner_id and region types don't match."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            # String summoner_id with list of regions should raise ValueError
            with pytest.raises(ValueError, match="Mismatched types"):
                opgg.get_recent_games(summoner_id="test", region=[Region.NA, Region.EUW])

            # List of summoner_ids with single region should raise ValueError
            with pytest.raises(ValueError, match="Mismatched types"):
                opgg.get_recent_games(summoner_id=["id1", "id2"], region=Region.NA)

    def test_get_recent_games_invalid_search_result_type(
        self, mock_user_agent
    ):
        """Test error when search_result is invalid type."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            # Invalid type should raise ValueError
            with pytest.raises(ValueError, match="Invalid type for search_result"):
                opgg.get_recent_games(search_result="invalid")

            with pytest.raises(ValueError, match="Invalid type for search_result"):
                opgg.get_recent_games(search_result=12345)

    def test_get_recent_games_none_search_result_missing_fallback(
        self, mock_user_agent
    ):
        """Test behavior when search_result is None but no fallback provided."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            # None search_result with no summoner_id/region should raise error
            with pytest.raises(ValueError, match="Invalid type for search_result"):
                opgg.get_recent_games(search_result=None)


class TestGetRecentGamesIntegration:
    """Integration tests for get_recent_games() with full response data."""

    def test_get_recent_games_game_data_structure(
        self, mock_user_agent, sample_game_data
    ):
        """Test that returned Game objects have correct structure."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            search_result = SearchResult(
                summoner=Summoner(summoner_id="test123", game_name="Player1", level=100),
                region=Region.NA,
            )

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/.*/summoners/test123/games.*"),
                    payload={"data": [sample_game_data]},
                    status=200,
                )

                games = opgg.get_recent_games(search_result=search_result)

            assert len(games) == 1
            game = games[0]

            # Verify Game object structure
            assert game.id == "game123"
            assert game.game_type == "SOLORANKED"
            assert game.game_length_second == 1800
            assert game.participants is not None
            assert len(game.participants) > 0
            assert game.teams is not None

    def test_get_recent_games_participant_data_retention(
        self, mock_user_agent, sample_game_data
    ):
        """Test that Participant objects retain all data including keywords."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            search_result = SearchResult(
                summoner=Summoner(summoner_id="test123", game_name="Player1", level=100),
                region=Region.NA,
            )

            with aioresponses() as m:
                m.get(
                    re.compile(r"https://lol-api-summoner\.op\.gg/api/.*/summoners/test123/games.*"),
                    payload={"data": [sample_game_data]},
                    status=200,
                )

                games = opgg.get_recent_games(search_result=search_result)

            participant = games[0].participants[0]

            # Verify Participant data
            assert participant.champion_id == 1
            assert participant.team_key == "BLUE"
            assert participant.position == "MID"
            assert participant.stats is not None
            assert participant.stats.kill == 10
            assert participant.stats.death == 2

    def test_get_recent_games_string_game_type_value(
        self, mock_user_agent, mock_games_response
    ):
        """Test that string game_type values are handled correctly."""
        with patch("opgg.opgg.os.path.exists", return_value=False), \
             patch("opgg.opgg.os.mkdir"), \
             patch("opgg.cacher.Cacher.setup"):

            opgg = OPGG()

            search_result = SearchResult(
                summoner=Summoner(summoner_id="test123", game_name="Player1", level=100),
                region=Region.NA,
            )

            with aioresponses() as m:
                # Pass string instead of GameType enum
                m.get(
                    re.compile(r".*game_type=ranked.*"),
                    payload=mock_games_response,
                    status=200,
                )

                games = opgg.get_recent_games(
                    search_result=search_result, game_type="ranked"
                )

            assert isinstance(games, list)
