"""Tests for Pydantic data models."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from opgg.champion import Champion, ChampionStats, Info, Stats, Skin, Price, MostChampions
from opgg.summoner import Summoner
from opgg.game import Game, Participant, Team, GameStat, Stats as GameStats
from opgg.season import Season, SeasonMeta, League, TierInfo
from opgg.keyword import Keyword
from opgg.search_result import SearchResult
from opgg.params import Region


pytestmark = pytest.mark.unit


class TestChampionModel:
    """Test Champion model validation."""

    def test_champion_valid_data(self, sample_champion_data):
        """Test Champion model with valid data."""
        champion = Champion(**sample_champion_data)

        assert champion.id == 1
        assert champion.name == "Annie"
        assert champion.key == "Annie"
        assert champion.title == "the Dark Child"
        assert "Mage" in champion.tags

    def test_champion_optional_fields_none(self):
        """Test Champion model handles None in optional fields."""
        champion = Champion(id=1, name="Test")

        assert champion.id == 1
        assert champion.name == "Test"
        assert champion.key is None
        assert champion.lore is None

    def test_champion_with_stats(self, sample_champion_data):
        """Test Champion model with stats nested object."""
        champion = Champion(**sample_champion_data)

        assert champion.stats is not None
        assert champion.stats.hp == 560.0
        assert champion.stats.movespeed == 335.0

    def test_champion_with_skins(self, sample_champion_data):
        """Test Champion model with skins list."""
        champion = Champion(**sample_champion_data)

        assert len(champion.skins) > 0
        assert champion.skins[0].champion_id == 1


class TestChampionStatsModel:
    """Test ChampionStats model."""

    def test_championstats_valid_data(self):
        """Test ChampionStats with valid data."""
        stats = ChampionStats(
            id=1,
            play=100,
            win=55,
            lose=45,
            kill=500,
            death=300,
            assist=700
        )

        assert stats.play == 100
        assert stats.win == 55
        assert stats.lose == 45

    def test_championstats_winrate_property(self):
        """Test ChampionStats winrate computed property."""
        stats = ChampionStats(play=100, win=60, lose=40)

        assert stats.winrate == 60

    def test_championstats_winrate_zero_games(self):
        """Test ChampionStats winrate returns 0 when no games played."""
        stats = ChampionStats(play=None, win=None)

        assert stats.winrate == 0


class TestSummonerModel:
    """Test Summoner model validation."""

    def test_summoner_valid_data(self, sample_summoner_data):
        """Test Summoner with valid data."""
        summoner = Summoner(**sample_summoner_data)

        assert summoner.id == 12345
        assert summoner.game_name == "TestPlayer"
        assert summoner.tagline == "NA1"
        assert summoner.level == 150

    def test_summoner_is_full_profile_false(self):
        """Test is_full_profile returns False when profile data is missing."""
        summoner = Summoner(id=1, game_name="Test")

        assert summoner.is_full_profile is False

    def test_summoner_is_full_profile_true(self, sample_summoner_data):
        """Test is_full_profile returns True when all profile data exists."""
        data = {
            **sample_summoner_data,
            "previous_seasons": [{"season_id": 26}],
            "league_stats": [{"win": 10, "lose": 5}],
            "most_champions": {"play": 50}
        }
        summoner = Summoner(**data)

        assert summoner.is_full_profile is True

    def test_summoner_datetime_fields(self):
        """Test Summoner datetime fields are properly parsed."""
        summoner = Summoner(
            id=1,
            updated_at="2025-01-15T12:00:00",
            renewable_at="2025-01-15T12:05:00"
        )

        assert isinstance(summoner.updated_at, datetime)
        assert isinstance(summoner.renewable_at, datetime)


class TestGameModel:
    """Test Game model validation."""

    def test_game_valid_data(self, sample_game_data):
        """Test Game with valid data."""
        game = Game(**sample_game_data)

        assert game.id == "game123"
        assert game.game_type == "SOLORANKED"
        assert game.game_length_second == 1800
        assert game.is_remake is False

    def test_game_with_participants(self, sample_game_data):
        """Test Game with participants list."""
        game = Game(**sample_game_data)

        assert len(game.participants) > 0
        assert game.participants[0].champion_id == 1

    def test_game_with_teams(self, sample_game_data):
        """Test Game with teams list."""
        game = Game(**sample_game_data)

        assert len(game.teams) > 0
        assert game.teams[0].key == "BLUE"

    def test_game_datetime_parsing(self):
        """Test Game datetime field parsing."""
        game = Game(id="test", created_at="2025-01-15T10:30:00")

        assert isinstance(game.created_at, datetime)


class TestParticipantModel:
    """Test Participant model."""

    def test_participant_valid_data(self):
        """Test Participant with valid data."""
        participant = Participant(
            participant_id=1,
            champion_id=1,
            team_key="BLUE",
            position="MID"
        )

        assert participant.participant_id == 1
        assert participant.champion_id == 1
        assert participant.team_key == "BLUE"

    def test_participant_with_stats(self):
        """Test Participant with stats nested object."""
        participant = Participant(
            participant_id=1,
            stats=GameStats(kill=10, death=2, assist=8)
        )

        assert participant.stats.kill == 10
        assert participant.stats.death == 2


class TestSeasonModels:
    """Test Season-related models."""

    def test_season_meta_valid_data(self, sample_season_meta):
        """Test SeasonMeta with valid data."""
        season = SeasonMeta(**sample_season_meta)

        assert season.id == 27
        assert season.season == 27
        assert season.display_value == "2025 Season 1"
        assert season.is_preseason is False

    def test_tier_info_model(self):
        """Test TierInfo model."""
        tier_info = TierInfo(
            tier="GOLD",
            division=2,
            lp=45,
            tier_image_url="https://example.com/gold.png"
        )

        assert tier_info.tier == "GOLD"
        assert tier_info.division == 2
        assert tier_info.lp == 45


class TestKeywordModel:
    """Test Keyword model."""

    def test_keyword_valid_data(self, sample_keyword_data):
        """Test Keyword with valid data."""
        keyword = Keyword(**sample_keyword_data)

        assert keyword.keyword == "leader"
        assert keyword.label == "Leader"
        assert "Dominated" in keyword.description
        assert keyword.is_op is True


class TestSearchResultModel:
    """Test SearchResult model."""

    def test_search_result_valid_data(self, sample_summoner_data):
        """Test SearchResult with valid data."""
        summoner = Summoner(**sample_summoner_data)
        search_result = SearchResult(summoner=summoner, region=Region.NA)

        assert search_result.summoner == summoner
        assert search_result.region == Region.NA

    def test_search_result_str_representation(self, sample_summoner_data):
        """Test SearchResult string representation."""
        summoner = Summoner(**sample_summoner_data)
        search_result = SearchResult(summoner=summoner, region=Region.NA)

        str_repr = str(search_result)
        assert "TestPlayer" in str_repr or "NA" in str_repr


class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_champion_model_dump(self, sample_champion_data):
        """Test Champion model_dump()."""
        champion = Champion(**sample_champion_data)
        dumped = champion.model_dump()

        assert isinstance(dumped, dict)
        assert dumped["id"] == 1
        assert dumped["name"] == "Annie"

    def test_summoner_model_dump(self, sample_summoner_data):
        """Test Summoner model_dump()."""
        summoner = Summoner(**sample_summoner_data)
        dumped = summoner.model_dump()

        assert isinstance(dumped, dict)
        assert dumped["game_name"] == "TestPlayer"

    def test_game_model_dump(self, sample_game_data):
        """Test Game model_dump()."""
        game = Game(**sample_game_data)
        dumped = game.model_dump()

        assert isinstance(dumped, dict)
        assert dumped["id"] == "game123"
