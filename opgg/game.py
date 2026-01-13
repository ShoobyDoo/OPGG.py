from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from opgg.opscore import OPScore, OPScoreAnalysis
from opgg.season import QueueInfo, TierInfo
from opgg.summoner import Summoner


class Stats(BaseModel):
    """Represents a player's stats in a game."""

    champion_level: int | None = None
    """Current champion level reached in game."""

    damage_self_mitigated: int | None = None
    """Damage prevented through armor, magic resist and other damage reduction."""

    damage_dealt_to_objectives: int | None = None
    """Total damage dealt to neutral objectives (dragons, herald, baron)."""

    damage_dealt_to_turrets: int | None = None
    """Total damage dealt to enemy turrets."""

    magic_damage_dealt_player: int | None = None
    """Total magic damage dealt to all targets."""

    physical_damage_taken: int | None = None
    """Physical damage taken from all sources."""

    physical_damage_dealt_to_champions: int | None = None
    """Physical damage dealt to enemy champions."""

    total_damage_taken: int | None = None
    """Total damage taken from all sources."""

    total_damage_dealt: int | None = None
    """Total damage dealt to all targets."""

    total_damage_dealt_to_champions: int | None = None
    """Total damage dealt to enemy champions."""

    largest_critical_strike: int | None = None
    """Highest critical strike damage dealt."""

    time_ccing_others: int | None = None
    """Time spent applying crowd control to enemies (in seconds)."""

    vision_score: int | None = None
    """Vision score based on wards placed/destroyed."""

    vision_wards_bought_in_game: int | None = None
    """Number of control wards purchased."""

    sight_wards_bought_in_game: int | None = None
    """Number of stealth wards purchased."""

    ward_kill: int | None = None
    """Number of enemy wards destroyed."""

    ward_place: int | None = None
    """Number of wards placed."""

    turret_kill: int | None = None
    """Number of turrets destroyed."""

    barrack_kill: int | None = None
    """Number of inhibitors destroyed."""

    kill: int | None = None
    """Number of enemy champions killed."""

    death: int | None = None
    """Number of times died."""

    assist: int | None = None
    """Number of assists on enemy champion kills."""

    largest_multi_kill: int | None = None
    """Highest multi-kill achieved (double, triple etc)."""

    largest_killing_spree: int | None = None
    """Highest number of kills without dying."""

    minion_kill: int | None = None
    """Number of minions killed."""

    neutral_minion_kill_team_jungle: int | None = None
    """Number of allied jungle monsters killed."""

    neutral_minion_kill_enemy_jungle: int | None = None
    """Number of enemy jungle monsters killed."""

    neutral_minion_kill: int | None = None
    """Total neutral monsters killed."""

    gold_earned: int | None = None
    """Total gold earned this game."""

    total_heal: int | None = None
    """Total amount healed (self and allies)."""

    result: str | None = None
    """Game result (WIN/LOSS)."""

    op_score: float | None = None
    """OP.GG performance score."""

    op_score_rank: int | None = None
    """Performance ranking within team."""

    is_opscore_max_in_team: bool | None = None
    """Whether this player had highest OP score in team."""

    lane_score: int | None = None
    """Lane phase performance score."""

    op_score_timeline: list[OPScore] | None = Field(default_factory=list)
    """OP score timeline."""

    op_score_timeline_analysis: OPScoreAnalysis | None = None
    """OP score timeline analysis."""

    keyword: str | None = None
    """Keyword for OP score analysis. (Leader, Average, Struggle, etc.)"""


class Rune(BaseModel):
    """Represents a player's rune configuration."""

    primary_page_id: int
    """ID of the primary rune page."""

    primary_rune_id: int
    """ID of the primary keystone rune."""

    secondary_page_id: int
    """ID of the secondary rune page."""


class Participant(BaseModel):
    """Represents a participant in a game."""

    summoner: Summoner | None = None
    """The summoner (player) information."""

    participant_id: int | None = None
    """Unique identifier for this participant in the game."""

    champion_id: int | None = None
    """ID of the champion played."""

    team_key: str | None = None
    """Team identifier (e.g. 'BLUE', 'RED')."""

    position: str | None = None
    """Lane position played (e.g. 'TOP', 'JUNGLE')."""

    role: str | None = None
    """Role played in team composition."""

    items: list[int] | None = Field(default_factory=list)
    """List of item IDs in inventory."""

    trinket_item: int | None = None
    """ID of equipped trinket item."""

    rune: Rune | None = None
    """Rune configuration used."""

    spells: list[int] | None = Field(default_factory=list)
    """List of summoner spell IDs."""

    stats: Stats | None = None
    """In-game performance statistics."""

    tier_info: TierInfo | None = None
    """Player's ranked tier information."""


class GameStat(BaseModel):
    """Represents team-wide game statistics."""

    is_win: bool | None = None
    """Whether the team won the game."""

    champion_kill: int | None = None
    """Total champion kills by team."""

    champion_first: bool | None = None
    """Whether team got first champion kill."""

    inhibitor_kill: int | None = None
    """Number of inhibitors destroyed."""

    inhibitor_first: bool | None = None
    """Whether team destroyed first inhibitor."""

    rift_herald_kill: int | None = None
    """Number of Rift Heralds killed."""

    rift_herald_first: bool | None = None
    """Whether team killed first Rift Herald."""

    dragon_kill: int | None = None
    """Number of dragons killed."""

    dragon_first: bool | None = None
    """Whether team killed first dragon."""

    baron_kill: int | None = None
    """Number of Baron Nashors killed."""

    baron_first: bool | None = None
    """Whether team killed first Baron."""

    tower_kill: int | None = None
    """Number of towers destroyed."""

    tower_first: bool | None = None
    """Whether team destroyed first tower."""

    horde_kill: int | None = None
    """Number of void monsters killed."""

    horde_first: bool | None = None
    """Whether team killed first void monster."""

    is_remake: bool | None = None
    """Whether the game was remade."""

    death: int | None = None
    """Total team deaths."""

    assist: int | None = None
    """Total team assists."""

    gold_earned: int | None = None
    """Total team gold earned."""

    kill: int | None = None
    """Total team kills."""


class Team(BaseModel):
    """Represents a team in the game."""

    key: str | None = None
    """Team identifier (e.g. 'BLUE', 'RED')."""

    game_stat: GameStat | None = None
    """Team's game statistics."""

    banned_champions: list[int | None] | None = Field(default_factory=list)
    """List of champion IDs banned by team."""


class Meta(BaseModel):
    """Metadata about a collection of games."""

    first_game_created_at: datetime | None = None
    """Timestamp of the earliest game in the collection."""

    last_game_created_at: datetime | None = None
    """Timestamp of the most recent game in the collection."""

    model_config = ConfigDict()

    @field_serializer("first_game_created_at", "last_game_created_at")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        return value.isoformat() if value else None


class LiveGameParticipant(BaseModel):
    """Represents a participant in a live game."""

    summoner: Summoner | None = None
    """The summoner (player) information."""

    participant_id: int | None = None
    """Unique identifier for this participant in the game."""

    champion_id: int | None = None
    """ID of the champion being played."""

    position: str | None = None
    """Lane position (e.g. 'TOP', 'JUNGLE')."""

    role: str | None = None
    """Role in team composition."""

    team_key: str | None = None
    """Team identifier (e.g. 'BLUE', 'RED')."""

    items: list[int] | None = Field(default_factory=list)
    """List of item IDs in inventory."""

    trinket_item: int | None = None
    """ID of equipped trinket item."""

    rune: Rune | None = None
    """Rune configuration used."""

    spells: list[int] | None = Field(default_factory=list)
    """List of summoner spell IDs."""

    stats: Stats | None = None
    """In-game performance statistics."""

    tier_info: TierInfo | None = None
    """Player's ranked tier information."""


class LiveGameTeam(BaseModel):
    """Represents a team in a live game."""

    key: str
    """Team identifier (e.g. 'BLUE', 'RED')."""

    game_stat: GameStat | None = None
    """Team's game statistics."""

    banned_champions: list[int] | None = Field(default_factory=list)
    """List of champion IDs banned by team."""

    average_tier_info: TierInfo | None = None
    """Average rank of team players."""


class LiveGame(BaseModel):
    """Represents a live game."""

    participants: list[LiveGameParticipant]
    """List of all players in the game."""

    teams: list[LiveGameTeam]
    """List of both teams and their statistics."""

    game_id: str | None = None
    """Unique identifier for this game."""

    game_type: str | None = None
    """Type of game (e.g. ranked, normal)."""

    game_start_time: datetime | None = None
    """When the game started."""

    platform_id: str | None = None
    """Server/platform identifier."""

    observer_key: str | None = None
    """Spectator mode encryption key."""

    queue_info: QueueInfo | None = None
    """Queue type information."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_serializer("game_start_time")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        return value.isoformat() if value else None


class Game(BaseModel):
    id: str | None = None
    """The unique game identifier."""

    created_at: datetime | None = None
    """When the game was played."""

    game_map: str | None = None
    """The map the game was played on (e.g. Summoner's Rift)."""

    game_type: str | None = None
    """The type of game (e.g. ranked, normal, aram)."""

    version: str | None = None
    """Game client version."""

    meta_version: str | None = None
    """OPGG metadata version."""

    game_length_second: int | None = None
    """Total game duration in seconds."""

    is_remake: bool | None = None
    """Whether the game was remade."""

    is_opscore_active: bool | None = None
    """Whether OP scores were calculated for this game."""

    is_recorded: bool | None = False
    """Whether the game was recorded."""

    record_info: Any | None = None
    """Recording information if available."""

    average_tier_info: TierInfo | None = None
    """Average rank of all players in the game."""

    participants: list[Participant] | None = Field(default_factory=list)
    """List of all players in the game."""

    teams: list[Team] | None = Field(default_factory=list)
    """List of both teams and their statistics."""

    memo: Any | None = None
    """Internal OPGG memo field."""

    my_data: Participant | None = None
    """The queried player's game data."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_serializer("created_at")
    def serialize_datetime(self, value: datetime | None) -> str | None:
        return value.isoformat() if value else None
