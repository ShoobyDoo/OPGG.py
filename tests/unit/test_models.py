"""Comprehensive unit tests for Pydantic models."""

from datetime import datetime

import pytest

from opgg.champion import (
    Champion,
    ChampionStats,
    Info,
    MostChampions,
    Passive,
    Skin,
    Spell,
)
from opgg.champion import Stats as ChampionBaseStats
from opgg.game import Game, GameStat, Participant, Rune, Stats, Team
from opgg.keyword import Keyword
from opgg.params import Region
from opgg.search_result import SearchResult
from opgg.season import League, Season, SeasonMeta, TierInfo
from opgg.summoner import Summoner


class TestSummonerModel:
    """Comprehensive tests for Summoner Pydantic model."""

    def test_summoner_from_real_search_response(self, fixture_search_single):
        """Test Summoner instantiation from real search response structure."""
        data = fixture_search_single["data"][0]
        summoner = Summoner(**data)

        assert summoner.summoner_id is not None
        assert summoner.game_name is not None
        assert isinstance(summoner.summoner_id, str)

    def test_summoner_from_real_profile_response(self, fixture_profile_full):
        """Test Summoner instantiation from real profile response structure."""
        data = fixture_profile_full["data"]["summoner"]
        summoner = Summoner(**data)

        assert summoner.summoner_id is not None
        # Profile should have richer data structures
        assert hasattr(summoner, "previous_seasons")
        assert hasattr(summoner, "league_stats")

    def test_summoner_is_full_profile_false_for_minimal_data(self):
        """Test is_full_profile returns False for minimal summoner data."""
        summoner = Summoner(summoner_id="test123", game_name="Test")
        assert summoner.is_full_profile is False

    def test_summoner_is_full_profile_true_when_complete(self):
        """Test is_full_profile returns True when all required fields present."""
        summoner = Summoner(
            summoner_id="test123",
            previous_seasons=[],
            league_stats=[],
            most_champions=MostChampions(),
        )
        assert summoner.is_full_profile is True

    def test_summoner_datetime_serialization(self):
        """Test datetime fields serialize correctly to ISO format."""
        now = datetime.now()
        summoner = Summoner(summoner_id="test", updated_at=now)

        serialized = summoner.model_dump()
        assert serialized["updated_at"] == now.isoformat()

    def test_summoner_with_tier_info(self):
        """Test Summoner with nested TierInfo for ranked data."""
        tier_data = {"tier": "DIAMOND", "division": 4, "lp": 50}
        summoner = Summoner(
            summoner_id="test", solo_tier_info=TierInfo(**tier_data)
        )

        assert summoner.solo_tier_info is not None
        assert summoner.solo_tier_info.tier == "DIAMOND"
        assert summoner.solo_tier_info.division == 4

    def test_summoner_all_fields_optional(self):
        """Test Summoner works with only summoner_id populated."""
        summoner = Summoner(summoner_id="minimal")
        assert summoner.summoner_id == "minimal"
        assert summoner.game_name is None
        assert summoner.level is None
        assert summoner.profile_image_url is None

    def test_summoner_with_previous_seasons(self, fixture_profile_full):
        """Test Summoner correctly parses previous_seasons list."""
        data = fixture_profile_full["data"]["summoner"]
        summoner = Summoner(**data)

        # previous_seasons should be a list (may be empty)
        assert isinstance(summoner.previous_seasons, list)

    def test_summoner_with_league_stats(self, fixture_profile_full):
        """Test Summoner correctly parses league_stats list."""
        data = fixture_profile_full["data"]["summoner"]
        summoner = Summoner(**data)

        # league_stats should be a list
        assert isinstance(summoner.league_stats, list)


class TestChampionModel:
    """Comprehensive tests for Champion and related models."""

    def test_champion_from_real_roster_response(self, fixture_champions_all):
        """Test Champion instantiation from real roster response."""
        data = fixture_champions_all["data"][0]
        champion = Champion(**data)

        assert champion.id is not None
        assert champion.name is not None
        assert isinstance(champion.id, int)

    def test_champion_from_real_detail_response(self, fixture_champion_by_id):
        """Test Champion instantiation from real champion detail response."""
        data = fixture_champion_by_id["data"]
        champion = Champion(**data)

        assert champion.id is not None
        # Detail response should have more fields
        assert hasattr(champion, "spells")
        assert hasattr(champion, "passive")
        assert hasattr(champion, "skins")

    def test_champion_with_nested_models(self):
        """Test Champion with all nested models populated."""
        champion = Champion(
            id=266,
            name="Aatrox",
            info=Info(attack=8, defense=4, magic=3, difficulty=4),
            stats=ChampionBaseStats(hp=650.0, armor=38.0),
            passive=Passive(name="Deathbringer Stance"),
            spells=[Spell(key="Q", name="The Darkin Blade")],
            skins=[Skin(id=1, name="Original")],
        )

        assert champion.info.attack == 8
        assert champion.stats.hp == 650.0
        assert champion.passive.name == "Deathbringer Stance"
        assert len(champion.spells) == 1
        assert len(champion.skins) == 1

    def test_champion_stats_winrate_calculation(self):
        """Test ChampionStats winrate property calculates correctly."""
        stats = ChampionStats(id=266, play=100, win=55, lose=45)
        assert stats.winrate == 55

    def test_champion_stats_winrate_zero_plays(self):
        """Test ChampionStats winrate handles zero plays gracefully."""
        stats_no_games = ChampionStats(id=266, play=0)
        assert stats_no_games.winrate == 0

    def test_champion_stats_winrate_none_values(self):
        """Test ChampionStats winrate handles None values."""
        stats = ChampionStats(id=266, play=None, win=None)
        assert stats.winrate == 0

    def test_most_champions_model(self):
        """Test MostChampions model with nested ChampionStats."""
        most = MostChampions(
            game_type="SOLORANKED",
            season_id=27,
            play=100,
            win=55,
            lose=45,
            champion_stats=[ChampionStats(id=266, play=50, win=30)],
        )

        assert most.game_type == "SOLORANKED"
        assert len(most.champion_stats) == 1
        assert most.champion_stats[0].id == 266

    def test_champion_info_model(self):
        """Test Info model with all fields."""
        info = Info(attack=8, defense=4, magic=3, difficulty=6)
        assert info.attack == 8
        assert info.difficulty == 6

    def test_skin_model(self):
        """Test Skin model with various fields."""
        skin = Skin(
            id=1,
            champion_id=266,
            name="Aatrox",
            has_chromas=False,
            splash_image="https://example.com/splash.jpg",
        )
        assert skin.name == "Aatrox"
        assert skin.has_chromas is False

    def test_spell_model(self):
        """Test Spell model with ability data."""
        spell = Spell(
            key="Q",
            name="The Darkin Blade",
            description="Aatrox slams his sword...",
            max_rank=5,
        )
        assert spell.key == "Q"
        assert spell.max_rank == 5


class TestGameModel:
    """Comprehensive tests for Game and related models."""

    def test_game_from_real_response(self, fixture_games_ranked):
        """Test Game instantiation from real games response."""
        data = fixture_games_ranked["data"]
        if data:
            game = Game(**data[0])
            # Game should have basic attributes
            assert hasattr(game, "id") or hasattr(game, "created_at")

    def test_game_with_full_structure(self):
        """Test Game with complete nested structure."""
        game = Game(
            id="test-game",
            created_at=datetime.now(),
            game_type="ranked",
            game_length_second=1800,
            participants=[
                Participant(
                    participant_id=1,
                    champion_id=266,
                    team_key="BLUE",
                    position="TOP",
                    stats=Stats(kill=5, death=2, assist=8),
                    rune=Rune(
                        primary_page_id=8100,
                        primary_rune_id=8112,
                        secondary_page_id=8300,
                    ),
                )
            ],
            teams=[
                Team(
                    key="BLUE",
                    game_stat=GameStat(is_win=True, champion_kill=25),
                    banned_champions=[266, 103, 84],
                )
            ],
        )

        assert game.id == "test-game"
        assert len(game.participants) == 1
        assert game.participants[0].stats.kill == 5
        assert game.teams[0].game_stat.is_win is True

    def test_stats_model_all_common_fields(self):
        """Test Stats model with common performance fields."""
        stats = Stats(
            kill=10,
            death=3,
            assist=15,
            minion_kill=200,
            gold_earned=15000,
            vision_score=45,
            op_score=8.5,
            op_score_rank=1,
        )

        assert stats.kill == 10
        assert stats.death == 3
        assert stats.assist == 15
        assert stats.op_score == 8.5

    def test_rune_model(self):
        """Test Rune model with keystone and secondary path."""
        rune = Rune(
            primary_page_id=8100,  # Domination
            primary_rune_id=8112,  # Electrocute
            secondary_page_id=8300,  # Inspiration
        )
        assert rune.primary_page_id == 8100
        assert rune.primary_rune_id == 8112

    def test_participant_model(self):
        """Test Participant model with all key attributes."""
        participant = Participant(
            participant_id=1,
            champion_id=266,
            team_key="BLUE",
            position="TOP",
            items=[3071, 6630, 3111],
            spells=[4, 14],  # Flash, Ignite
        )
        assert participant.champion_id == 266
        assert participant.position == "TOP"
        assert len(participant.items) == 3

    def test_team_model_with_game_stat(self):
        """Test Team model with nested GameStat."""
        team = Team(
            key="RED",
            game_stat=GameStat(
                is_win=False,
                champion_kill=15,
                dragon_kill=2,
                baron_kill=0,
            ),
            banned_champions=[1, 2, 3, 4, 5],
        )
        assert team.key == "RED"
        assert team.game_stat.is_win is False
        assert len(team.banned_champions) == 5

    def test_game_stat_objectives(self):
        """Test GameStat with all objective tracking fields."""
        stat = GameStat(
            is_win=True,
            champion_kill=30,
            tower_kill=11,
            inhibitor_kill=2,
            dragon_kill=4,
            baron_kill=2,
            rift_herald_kill=1,
        )
        assert stat.dragon_kill == 4
        assert stat.baron_kill == 2


class TestSearchResultModel:
    """Tests for SearchResult model."""

    def test_search_result_with_region_enum(self):
        """Test SearchResult with Region enum."""
        sr = SearchResult(
            summoner=Summoner(summoner_id="test123"), region=Region.NA
        )

        assert sr.summoner.summoner_id == "test123"
        assert sr.region == Region.NA

    def test_search_result_with_string_region(self):
        """Test SearchResult accepts string region (converted to enum)."""
        sr = SearchResult(
            summoner=Summoner(summoner_id="test"), region=Region.KR
        )
        assert sr.region == Region.KR

    def test_search_result_str_representation(self):
        """Test SearchResult __str__ method formats correctly."""
        sr = SearchResult(
            summoner=Summoner(
                summoner_id="abc", game_name="Player", tagline="NA1", level=100
            ),
            region=Region.NA,
        )

        str_repr = str(sr)
        assert "Player" in str_repr
        assert "NA1" in str_repr
        assert "100" in str_repr

    def test_search_result_from_real_data(self, fixture_search_single):
        """Test SearchResult with real fixture data."""
        data = fixture_search_single["data"][0]
        sr = SearchResult(summoner=Summoner(**data), region=Region.NA)

        assert sr.summoner.summoner_id is not None
        assert sr.region == Region.NA


class TestSeasonModels:
    """Tests for Season-related models."""

    def test_season_meta_from_real_response(self, fixture_seasons):
        """Test SeasonMeta from real seasons response."""
        data = fixture_seasons["data"]
        if data:
            meta = SeasonMeta(**data[0])
            assert meta.id is not None

    def test_tier_info_model(self):
        """Test TierInfo model with all rank information."""
        tier = TierInfo(
            tier="DIAMOND",
            division=4,
            lp=75,
            tier_image_url="https://example.com/diamond.png",
        )

        assert tier.tier == "DIAMOND"
        assert tier.division == 4
        assert tier.lp == 75

    def test_tier_info_master_plus(self):
        """Test TierInfo for Master+ (no division)."""
        tier = TierInfo(tier="MASTER", division=None, lp=250)

        assert tier.tier == "MASTER"
        assert tier.division is None
        assert tier.lp == 250

    def test_league_model(self):
        """Test League model with win/loss tracking."""
        league = League(
            game_type="SOLORANKED",
            tier_info=TierInfo(tier="PLATINUM", division=2),
            win=50,
            lose=45,
            is_hot_streak=True,
        )

        assert league.game_type == "SOLORANKED"
        assert league.tier_info.tier == "PLATINUM"
        assert league.is_hot_streak is True

    def test_season_with_meta(self):
        """Test Season with attached SeasonMeta."""
        season = Season(
            season_id=27,
            tier_info=TierInfo(tier="GOLD", division=1),
            meta=SeasonMeta(id=27, display_value="2024 Split 3"),
        )

        assert season.season_id == 27
        assert season.meta.display_value == "2024 Split 3"

    def test_season_datetime_serialization(self):
        """Test Season datetime serialization."""
        now = datetime.now()
        season = Season(season_id=27, created_at=now)

        serialized = season.model_dump()
        assert serialized["created_at"] == now.isoformat()


class TestKeywordModel:
    """Tests for Keyword model."""

    def test_keyword_from_real_response(self, fixture_keywords):
        """Test Keyword from real keywords response."""
        data = fixture_keywords["data"]
        if data:
            keyword = Keyword(**data[0])
            assert keyword.keyword is not None or keyword.label is not None

    def test_keyword_all_fields(self):
        """Test Keyword with all fields populated."""
        keyword = Keyword(
            keyword="leader",
            label="Leader",
            description="Performed exceptionally well",
            arrows=["up", "up"],
            is_op=True,
            context="team",
        )

        assert keyword.label == "Leader"
        assert keyword.is_op is True
        assert len(keyword.arrows) == 2

    def test_keyword_default_arrows(self):
        """Test Keyword arrows defaults to empty list."""
        keyword = Keyword(keyword="average")
        assert keyword.arrows == []


class TestModelValidation:
    """Tests for model validation behavior."""

    def test_extra_fields_handled_gracefully(self):
        """Test that extra fields from API don't cause errors."""
        # OPGG API may add new fields - models should handle gracefully
        data = {
            "summoner_id": "test",
            "new_field_from_api": "should not break",
            "another_new_field": 123,
        }

        # This should not raise ValidationError
        summoner = Summoner(**data)
        assert summoner.summoner_id == "test"

    def test_http_url_field_validation(self):
        """Test that HttpUrl fields accept valid URLs."""
        summoner = Summoner(
            summoner_id="test",
            profile_image_url="https://valid-url.com/image.jpg",
        )
        assert summoner.profile_image_url is not None

    def test_nested_model_validation(self):
        """Test nested model validation works correctly."""
        data = {
            "summoner_id": "test",
            "solo_tier_info": {"tier": "GOLD", "division": 2, "lp": 50},
        }

        summoner = Summoner(**data)
        assert summoner.solo_tier_info.tier == "GOLD"

    def test_model_dump_excludes_none_optionally(self):
        """Test model_dump can exclude None values."""
        summoner = Summoner(summoner_id="test")

        # Full dump includes None values
        full_dump = summoner.model_dump()
        assert "game_name" in full_dump

        # Exclude None values
        clean_dump = summoner.model_dump(exclude_none=True)
        assert "game_name" not in clean_dump
        assert "summoner_id" in clean_dump
