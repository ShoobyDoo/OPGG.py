from datetime import datetime
from typing import Any, Optional, List
from pydantic import BaseModel, Field, field_validator
import logging

from opgg.v2.opscore import OPScore, OPScoreAnalysis
from opgg.v2.season import QueueInfo, TierInfo
from opgg.v2.summoner import Summoner

logger = logging.getLogger("OPGG.py")


class Stats(BaseModel):
    """Represents a player's stats in a game."""

    champion_level: Optional[int] = None
    """Current champion level reached in game."""

    damage_self_mitigated: Optional[int] = None
    """Damage prevented through armor, magic resist and other damage reduction."""

    damage_dealt_to_objectives: Optional[int] = None
    """Total damage dealt to neutral objectives (dragons, herald, baron)."""

    damage_dealt_to_turrets: Optional[int] = None
    """Total damage dealt to enemy turrets."""

    magic_damage_dealt_player: Optional[int] = None
    """Total magic damage dealt to all targets."""

    physical_damage_taken: Optional[int] = None
    """Physical damage taken from all sources."""

    physical_damage_dealt_to_champions: Optional[int] = None
    """Physical damage dealt to enemy champions."""

    total_damage_taken: Optional[int] = None
    """Total damage taken from all sources."""

    total_damage_dealt: Optional[int] = None
    """Total damage dealt to all targets."""

    total_damage_dealt_to_champions: Optional[int] = None
    """Total damage dealt to enemy champions."""

    largest_critical_strike: Optional[int] = None
    """Highest critical strike damage dealt."""

    time_ccing_others: Optional[int] = None
    """Time spent applying crowd control to enemies (in seconds)."""

    vision_score: Optional[int] = None
    """Vision score based on wards placed/destroyed."""

    vision_wards_bought_in_game: Optional[int] = None
    """Number of control wards purchased."""

    sight_wards_bought_in_game: Optional[int] = None
    """Number of stealth wards purchased."""

    ward_kill: Optional[int] = None
    """Number of enemy wards destroyed."""

    ward_place: Optional[int] = None
    """Number of wards placed."""

    turret_kill: Optional[int] = None
    """Number of turrets destroyed."""

    barrack_kill: Optional[int] = None
    """Number of inhibitors destroyed."""

    kill: Optional[int] = None
    """Number of enemy champions killed."""

    death: Optional[int] = None
    """Number of times died."""

    assist: Optional[int] = None
    """Number of assists on enemy champion kills."""

    largest_multi_kill: Optional[int] = None
    """Highest multi-kill achieved (double, triple etc)."""

    largest_killing_spree: Optional[int] = None
    """Highest number of kills without dying."""

    minion_kill: Optional[int] = None
    """Number of minions killed."""

    neutral_minion_kill_team_jungle: Optional[int] = None
    """Number of allied jungle monsters killed."""

    neutral_minion_kill_enemy_jungle: Optional[int] = None
    """Number of enemy jungle monsters killed."""

    neutral_minion_kill: Optional[int] = None
    """Total neutral monsters killed."""

    gold_earned: Optional[int] = None
    """Total gold earned this game."""

    total_heal: Optional[int] = None
    """Total amount healed (self and allies)."""

    result: Optional[str] = None
    """Game result (WIN/LOSS)."""

    op_score: Optional[float] = None
    """OP.GG performance score."""

    op_score_rank: Optional[int] = None
    """Performance ranking within team."""

    is_opscore_max_in_team: Optional[bool] = None
    """Whether this player had highest OP score in team."""

    lane_score: Optional[int] = None
    """Lane phase performance score."""

    op_score_timeline: Optional[list[OPScore]] = Field(default_factory=list)
    """OP score timeline."""

    op_score_timeline_analysis: Optional[OPScoreAnalysis] = None
    """OP score timeline analysis."""

    keyword: Optional[str] = None
    """Keyword for OP score analysis. (Leader, Average, Struggle, etc.)"""

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in Stats model")
        return v


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

    summoner: Optional[Summoner] = None
    """The summoner (player) information."""

    participant_id: Optional[int] = None
    """Unique identifier for this participant in the game."""

    champion_id: Optional[int] = None
    """ID of the champion played."""

    team_key: Optional[str] = None
    """Team identifier (e.g. 'BLUE', 'RED')."""

    position: Optional[str] = None
    """Lane position played (e.g. 'TOP', 'JUNGLE')."""

    role: Optional[str] = None
    """Role played in team composition."""

    items: Optional[list[int]] = Field(default_factory=list)
    """List of item IDs in inventory."""

    trinket_item: Optional[int] = None
    """ID of equipped trinket item."""

    rune: Optional[Rune] = None
    """Rune configuration used."""

    spells: Optional[list[int]] = Field(default_factory=list)
    """List of summoner spell IDs."""

    stats: Optional[Stats] = None
    """In-game performance statistics."""

    tier_info: Optional[TierInfo] = None
    """Player's ranked tier information."""

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in Participant model")
        return v


class GameStat(BaseModel):
    """Represents team-wide game statistics."""

    is_win: Optional[bool] = None
    """Whether the team won the game."""

    champion_kill: Optional[int] = None
    """Total champion kills by team."""

    champion_first: Optional[bool] = None
    """Whether team got first champion kill."""

    inhibitor_kill: Optional[int] = None
    """Number of inhibitors destroyed."""

    inhibitor_first: Optional[bool] = None
    """Whether team destroyed first inhibitor."""

    rift_herald_kill: Optional[int] = None
    """Number of Rift Heralds killed."""

    rift_herald_first: Optional[bool] = None
    """Whether team killed first Rift Herald."""

    dragon_kill: Optional[int] = None
    """Number of dragons killed."""

    dragon_first: Optional[bool] = None
    """Whether team killed first dragon."""

    baron_kill: Optional[int] = None
    """Number of Baron Nashors killed."""

    baron_first: Optional[bool] = None
    """Whether team killed first Baron."""

    tower_kill: Optional[int] = None
    """Number of towers destroyed."""

    tower_first: Optional[bool] = None
    """Whether team destroyed first tower."""

    horde_kill: Optional[int] = None
    """Number of void monsters killed."""

    horde_first: Optional[bool] = None
    """Whether team killed first void monster."""

    is_remake: Optional[bool] = None
    """Whether the game was remade."""

    death: Optional[int] = None
    """Total team deaths."""

    assist: Optional[int] = None
    """Total team assists."""

    gold_earned: Optional[int] = None
    """Total team gold earned."""

    kill: Optional[int] = None
    """Total team kills."""

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in GameStat model")
        return v


class Team(BaseModel):
    """Represents a team in the game."""

    key: Optional[str] = None
    """Team identifier (e.g. 'BLUE', 'RED')."""

    game_stat: Optional[GameStat] = None
    """Team's game statistics."""

    banned_champions: Optional[list[int | None]] = Field(default_factory=list)
    """List of champion IDs banned by team."""

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in Team model")
        return v


class Meta(BaseModel):
    """Metadata about a collection of games."""

    first_game_created_at: Optional[datetime] = None
    """Timestamp of the earliest game in the collection."""

    last_game_created_at: Optional[datetime] = None
    """Timestamp of the most recent game in the collection."""

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in Meta model")
        return v

    class Config:
        """Pydantic model configuration."""

        json_encoders = {datetime: lambda v: v.isoformat()}


class LiveGameParticipant(BaseModel):
    """Represents a participant in a live game."""

    summoner: Optional[Summoner] = None
    """The summoner (player) information."""

    participant_id: Optional[int] = None
    """Unique identifier for this participant in the game."""

    champion_id: Optional[int] = None
    """ID of the champion being played."""

    position: Optional[str] = None
    """Lane position (e.g. 'TOP', 'JUNGLE')."""

    role: Optional[str] = None
    """Role in team composition."""

    team_key: Optional[str] = None
    """Team identifier (e.g. 'BLUE', 'RED')."""

    items: Optional[List[int]] = Field(default_factory=list)
    """List of item IDs in inventory."""

    trinket_item: Optional[int] = None
    """ID of equipped trinket item."""

    rune: Optional[Rune] = None
    """Rune configuration used."""

    spells: Optional[List[int]] = Field(default_factory=list)
    """List of summoner spell IDs."""

    stats: Optional[Stats] = None
    """In-game performance statistics."""

    tier_info: Optional[TierInfo] = None
    """Player's ranked tier information."""


class LiveGameTeam(BaseModel):
    """Represents a team in a live game."""

    key: str
    """Team identifier (e.g. 'BLUE', 'RED')."""

    game_stat: Optional[GameStat] = None
    """Team's game statistics."""

    banned_champions: Optional[List[int]] = Field(default_factory=list)
    """List of champion IDs banned by team."""

    average_tier_info: Optional[TierInfo] = None
    """Average rank of team players."""


class LiveGame(BaseModel):
    """Represents a live game."""

    participants: List[LiveGameParticipant]
    """List of all players in the game."""

    teams: List[LiveGameTeam]
    """List of both teams and their statistics."""

    game_id: Optional[str] = None
    """Unique identifier for this game."""

    game_type: Optional[str] = None
    """Type of game (e.g. ranked, normal)."""

    game_start_time: Optional[datetime] = None
    """When the game started."""

    platform_id: Optional[str] = None
    """Server/platform identifier."""

    observer_key: Optional[str] = None
    """Spectator mode encryption key."""

    queue_info: Optional[QueueInfo] = None
    """Queue type information."""

    class Config:
        """Pydantic model configuration."""

        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class Game(BaseModel):
    id: Optional[str] = None
    """The unique game identifier."""

    created_at: Optional[datetime] = None
    """When the game was played."""

    game_map: Optional[str] = None
    """The map the game was played on (e.g. Summoner's Rift)."""

    game_type: Optional[str] = None
    """The type of game (e.g. ranked, normal, aram)."""

    version: Optional[str] = None
    """Game client version."""

    meta_version: Optional[str] = None
    """OPGG metadata version."""

    game_length_second: Optional[int] = None
    """Total game duration in seconds."""

    is_remake: Optional[bool] = None
    """Whether the game was remade."""

    is_opscore_active: Optional[bool] = None
    """Whether OP scores were calculated for this game."""

    is_recorded: Optional[bool] = False
    """Whether the game was recorded."""

    record_info: Optional[Any] = None
    """Recording information if available."""

    average_tier_info: Optional[TierInfo] = None
    """Average rank of all players in the game."""

    participants: Optional[list[Participant]] = Field(default_factory=list)
    """List of all players in the game."""

    teams: Optional[list[Team]] = Field(default_factory=list)
    """List of both teams and their statistics."""

    memo: Optional[Any] = None
    """Internal OPGG memo field."""

    myData: Optional[Participant] = None
    """The queried player's game data."""

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if (
            v is None and info.field_name != "is_recorded"
        ):  # Skip is_recorded since it has a default value
            logger.warning(f"Field '{info.field_name}' is None in Game model")
        return v

    class Config:
        """Pydantic model configuration."""

        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat()}
