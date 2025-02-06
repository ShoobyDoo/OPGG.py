from datetime import datetime
from typing import Any, Optional, List
from pydantic import BaseModel, Field, field_validator

from opgg.v2.opscore import OPScore, OPScoreAnalysis
from opgg.v2.season import QueueInfo, TierInfo
from opgg.v2.summoner import Summoner


class Stats(BaseModel):
    """Represents a player's stats in a game."""

    champion_level: int
    """Current champion level reached in game."""

    damage_self_mitigated: int
    """Damage prevented through armor, magic resist and other damage reduction."""

    damage_dealt_to_objectives: int
    """Total damage dealt to neutral objectives (dragons, herald, baron)."""

    damage_dealt_to_turrets: int
    """Total damage dealt to enemy turrets."""

    magic_damage_dealt_player: int
    """Total magic damage dealt to all targets."""

    physical_damage_taken: int
    """Physical damage taken from all sources."""

    physical_damage_dealt_to_champions: int
    """Physical damage dealt to enemy champions."""

    total_damage_taken: int
    """Total damage taken from all sources."""

    total_damage_dealt: int
    """Total damage dealt to all targets."""

    total_damage_dealt_to_champions: int
    """Total damage dealt to enemy champions."""

    largest_critical_strike: int
    """Highest critical strike damage dealt."""

    time_ccing_others: int
    """Time spent applying crowd control to enemies (in seconds)."""

    vision_score: int
    """Vision score based on wards placed/destroyed."""

    vision_wards_bought_in_game: int
    """Number of control wards purchased."""

    sight_wards_bought_in_game: int
    """Number of stealth wards purchased."""

    ward_kill: int
    """Number of enemy wards destroyed."""

    ward_place: int
    """Number of wards placed."""

    turret_kill: int
    """Number of turrets destroyed."""

    barrack_kill: int
    """Number of inhibitors destroyed."""

    kill: int
    """Number of enemy champions killed."""

    death: int
    """Number of times died."""

    assist: int
    """Number of assists on enemy champion kills."""

    largest_multi_kill: int
    """Highest multi-kill achieved (double, triple etc)."""

    largest_killing_spree: int
    """Highest number of kills without dying."""

    minion_kill: int
    """Number of minions killed."""

    neutral_minion_kill_team_jungle: Optional[int] = None
    """Number of allied jungle monsters killed."""

    neutral_minion_kill_enemy_jungle: Optional[int] = None
    """Number of enemy jungle monsters killed."""

    neutral_minion_kill: int
    """Total neutral monsters killed."""

    gold_earned: int
    """Total gold earned this game."""

    total_heal: int
    """Total amount healed (self and allies)."""

    result: str
    """Game result (WIN/LOSS)."""

    op_score: float
    """OP.GG performance score."""

    op_score_rank: int
    """Performance ranking within team."""

    is_opscore_max_in_team: bool
    """Whether this player had highest OP score in team."""

    # lane score can be None when the game is a remake it seems...
    lane_score: int | None
    """Lane phase performance score."""

    op_score_timeline: list[OPScore]
    """OP score timeline."""

    op_score_timeline_analysis: OPScoreAnalysis | None
    """OP score timeline analysis."""

    keyword: str | None
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

    summoner: Summoner
    """The summoner (player) information."""

    participant_id: int
    """Unique identifier for this participant in the game."""

    champion_id: int
    """ID of the champion played."""

    team_key: str
    """Team identifier (e.g. 'BLUE', 'RED')."""

    position: str
    """Lane position played (e.g. 'TOP', 'JUNGLE')."""

    role: str | None
    """Role played in team composition."""

    items: list[int]
    """List of item IDs in inventory."""

    trinket_item: int
    """ID of equipped trinket item."""

    rune: Rune
    """Rune configuration used."""

    spells: list[int]
    """List of summoner spell IDs."""

    stats: Stats
    """In-game performance statistics."""

    tier_info: TierInfo
    """Player's ranked tier information."""


class GameStat(BaseModel):
    """Represents team-wide game statistics."""

    is_win: bool
    """Whether the team won the game."""

    champion_kill: int
    """Total champion kills by team."""

    champion_first: bool
    """Whether team got first champion kill."""

    inhibitor_kill: int
    """Number of inhibitors destroyed."""

    inhibitor_first: bool
    """Whether team destroyed first inhibitor."""

    rift_herald_kill: int
    """Number of Rift Heralds killed."""

    rift_herald_first: bool
    """Whether team killed first Rift Herald."""

    dragon_kill: int
    """Number of dragons killed."""

    dragon_first: bool
    """Whether team killed first dragon."""

    baron_kill: int
    """Number of Baron Nashors killed."""

    baron_first: bool
    """Whether team killed first Baron."""

    tower_kill: int
    """Number of towers destroyed."""

    tower_first: bool
    """Whether team destroyed first tower."""

    horde_kill: int
    """Number of void monsters killed."""

    horde_first: bool
    """Whether team killed first void monster."""

    is_remake: bool
    """Whether the game was remade."""

    death: int
    """Total team deaths."""

    assist: int
    """Total team assists."""

    gold_earned: int
    """Total team gold earned."""

    kill: int
    """Total team kills."""


class Team(BaseModel):
    """Represents a team in the game."""

    key: str
    """Team identifier (e.g. 'BLUE', 'RED')."""

    game_stat: GameStat
    """Team's game statistics."""

    banned_champions: list[int | None]
    """List of champion IDs banned by team."""


class Meta(BaseModel):
    """Metadata about a collection of games."""

    first_game_created_at: datetime
    """Timestamp of the earliest game in the collection."""

    last_game_created_at: datetime
    """Timestamp of the most recent game in the collection."""

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
    id: str
    """The unique game identifier."""

    created_at: datetime
    """When the game was played."""

    game_map: str
    """The map the game was played on (e.g. Summoner's Rift)."""

    game_type: str
    """The type of game (e.g. ranked, normal, aram)."""

    version: str
    """Game client version."""

    meta_version: str
    """OPGG metadata version."""

    game_length_second: int
    """Total game duration in seconds."""

    is_remake: bool
    """Whether the game was remade."""

    is_opscore_active: bool
    """Whether OP scores were calculated for this game."""

    is_recorded: bool = False
    """Whether the game was recorded."""

    @field_validator('is_recorded', mode='before')
    def set_is_recorded(cls, v):
        return v if v is not None else False

    record_info: Any = None
    """Recording information if available."""

    average_tier_info: TierInfo
    """Average rank of all players in the game."""

    participants: list[Participant]
    """List of all players in the game."""

    teams: list[Team]
    """List of both teams and their statistics."""

    memo: Any = None
    """Internal OPGG memo field."""

    myData: Participant
    """The queried player's game data."""

    class Config:
        """Pydantic model configuration."""

        arbitrary_types_allowed = True
        json_encoders = {datetime: lambda v: v.isoformat()}
