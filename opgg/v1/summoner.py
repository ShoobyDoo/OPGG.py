# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : ShoobyDoo
# Date    : 2023-07-05
# License : BSD-3-Clause


from datetime import datetime
from typing import Any
from opgg.v1.game import Stats, Team
from opgg.v1.params import By, Queue
from opgg.v1.season import Season
from opgg.v1.league_stats import LeagueStats, QueueInfo, Tier
from opgg.v1.champion import Champion, ChampionStats
from opgg.v1.utils import Utils

# left/right just factor
LJF = 18
RJF = 14


class Participant:
    """
    Represents a participant in the game with detailed information about their performance and loadout.\n
    
    ### Properties:
        `summoner: Summoner` - The summoner associated with this participant\n
        `participant_id: int` - Unique identifier for the participant\n
        `champion_id: int` - Identifier for the champion used by the participant\n
        `team_key: str` - Key representing the participant's team\n
        `position: str` - Position played by the participant (e.g., Top, Mid, Bot)\n
        `role: str` - Role played by the participant (e.g., Carry, Support)\n
        `items: list` - List of items acquired by the participant\n
        `trinket_item: int` - Identifier for the trinket item used by the participant\n
        `rune: dict[str, int]` - Dictionary of runes used by the participant with their respective values\n
        `spells: list` - List of spells used by the participant\n
        `stats: Stats` - Performance statistics of the participant\n
        `tier_info: Tier` - Tier information of the participant\n
    """
    def __init__(self,
                 summoner: 'Summoner',
                 participant_id: int,
                 champion_id: int,
                 team_key: str,
                 position: str,
                 role: str,
                 items: list,
                 trinket_item: int,
                 rune: dict[str, int], # temp. need to see if a Rune object is necessary
                 spells: list,
                 stats: Stats,
                 tier_info: Tier) -> None:
        self._summoner = summoner
        self._participant_id = participant_id
        self._champion_id = champion_id
        self._team_key = team_key
        self._position = position
        self._role = role
        self._items = items
        self._trinket_item = trinket_item
        self._rune = rune
        self._spells = spells
        self._stats = stats
        self._tier_info = tier_info
    
    @property
    def summoner(self) -> 'Summoner':
        """
        A `Summoner` object representing a summoner
        """
        return self._summoner
    
    @summoner.setter
    def summoner(self, value: 'Summoner') -> None:
        self._summoner = value
    
    @property
    def participant_id(self) -> int:
        """
        An `int` representing the participant id
        """
        return self._participant_id
    
    @participant_id.setter
    def participant_id(self, value: int) -> None:
        self._participant_id = value
        
    @property
    def champion_id(self) -> int:
        """
        An `int` representing the champion id
        """
        return self._champion_id
    
    @champion_id.setter
    def champion_id(self, value: int) -> None:
        self._champion_id = value
    
    @property
    def team_key(self) -> str:
        """
        A `str` representing the team (BLUE, RED)
        """
        return self._team_key
    
    @team_key.setter
    def team_key(self, value: str) -> None:
        self._team_key = value
    
    @property
    def position(self) -> str:
        """
        A `str` representing the position the participant was playing
        """
        return self._position
    
    @position.setter
    def position(self, value: str) -> None:
        self._position = value
    
    @property
    def role(self) -> str:
        """
        A `str` representing the role the participant was playing
        """
        return self._role
    
    @role.setter
    def role(self, value: str) -> None:
        self._role = value
    
    @property
    def items(self) -> list[int]:
        """
        A `list[int]` representing the participants items
        """
        return self._items
    
    @items.setter
    def items(self, value: list[int]) -> None:
        self._items = value
    
    @property
    def trinket_item(self) -> int:
        """
        An `int` representing the trinket item
        """
        return self._trinket_item
    
    @trinket_item.setter
    def trinket_item(self, value: int) -> None:
        self._trinket_item = value
    
    @property
    def rune(self) -> dict[str, int]:
        """
        A `dict[str, int]` representing the rune configuration of the participant
        """
        return self._rune
    
    @rune.setter
    def rune(self, value: dict[str, int]) -> None:
        self._rune = value
    
    @property
    def spells(self) -> list:
        """
        A `list` representing the spell configuration of the participant
        """
        return self._spells
    
    @spells.setter
    def spells(self, value: list) -> None:
        self._spells = value
    
    @property
    def stats(self) -> Stats:
        """
        A `Stats` object representing the participants game stats
        """
        return self._stats
    
    @stats.setter
    def stats(self, value: Stats) -> None:
        self._stats = value
    
    @property
    def tier_info(self) -> Tier:
        """
        A `Tier` object representing the participants league tier
        """
        return self._tier_info
    
    @tier_info.setter
    def tier_info(self, value: Tier) -> None:
        self._tier_info = value
    

class Game:
    """
    Represents a game played by a summoner.\n
    
    ### Properties:
        `id: str` - Internal game id\n
        `created_at: datetime` - Date & Time of game\n
        `game_map: GameMap` - Game map (Summoners Rift, Howling Abyss, etc.)\n
        `queue_info: QueueInfo` - Queue info\n
        `version: str` - Game version\n
        `game_length_second: int` - Length of game in seconds\n
        `is_remake: bool` - Whether or not the game was a remake\n
        `is_opscore_active: bool` - Whether or not the opscore was active\n
        `is_recorded: bool` - Whether or not the game was recorded\n
        `record_info: Any` - Unknown return value and type\n
        `average_tier_info: Tier` - Average Tier of the game\n
        `participants: list[Participant]` - A list of all participant in the game\n
        `teams: list[Team]` - A list of teams in the game\n
        `memo: Any` - Unknown return value and type\n
        `myData: Participant` - User specific participant data
    """
    def __init__(self,
                 id: str,
                 created_at: datetime,
                 game_map: str,
                 queue_info: QueueInfo,
                 version: str,
                 game_length_second: int,
                 is_remake: bool,
                 is_opscore_active: bool,
                 is_recorded: bool,
                 record_info: Any,
                 average_tier_info: Tier,
                 participants: list[Participant],
                 teams: list[Team],
                 memo: Any,
                 myData: Participant) -> None:
        self._id = id
        self._created_at = created_at
        self._game_map = game_map
        self._queue_info = queue_info
        self._version = version
        self._game_length_second = game_length_second
        self._is_remake = is_remake
        self._is_opscore_active = is_opscore_active
        self._is_recorded = is_recorded
        self._record_info = record_info
        self._average_tier_info = average_tier_info
        self._participants = participants
        self._teams = teams
        self._memo = memo
        self._myData = myData
        
    @property
    def id(self) -> str:
        """
        A `str` representing the Internal game id
        """
        return self._id
    
    @id.setter
    def id(self, value: str) -> None:
        self._id = value
        
    @property
    def created_at(self) -> datetime:
        """
        A `datetime` object representing the Date & Time of game played
        """
        return self._created_at
    
    @created_at.setter
    def created_at(self, value: datetime) -> None:
        self._created_at = value
        
    @property
    def game_map(self) -> str:
        """
        A `str` representing the game map (Summoners Rift, Howling Abyss, etc.)
        """
        return self._game_map
    
    @game_map.setter
    def game_map(self, value: str) -> None:
        self._game_map = value
        
    @property
    def queue_info(self) -> QueueInfo:
        """
        A `QueueInfo` object representing queue information
        """
        return self._queue_info
    
    @queue_info.setter
    def queue_info(self, value: QueueInfo) -> None:
        self._queue_info = value
        
    @property
    def version(self) -> str:
        """
        A `str` representing the game version
        """
        return self._version
    
    @version.setter
    def version(self, value: str) -> None:
        self._version = value
        
    @property
    def game_length_second(self) -> int:
        """
        An `int` representing the length of the game in seconds
        """
        return self._game_length_second
     
    @game_length_second.setter
    def game_length_second(self, value: int) -> None:
        self._game_length_second = value
        
    @property
    def is_remake(self) -> bool:
        """
        A `bool` representing whether the game was a remake
        """
        return self._is_remake
    
    @is_remake.setter
    def is_remake(self, value: bool) -> None:
        self._is_remake = value
        
    @property
    def is_opscore_active(self) -> bool:
        """
        A `bool` representing whether the opscore was active
        """
        return self._is_opscore_active
    
    @is_opscore_active.setter
    def is_opscore_active(self, value: bool) -> None:
        self._is_opscore_active = value
        
        
    @property
    def is_recorded(self) -> bool:
        """
        A `bool` representing whether the game was recorded
        """
        return self._is_recorded
    
    @is_recorded.setter
    def is_recorded(self, value: bool) -> None:
        self._is_recorded = value
        
    @property
    def record_info(self) -> Any:
        """
        An `Any` object with unknown return value and type
        """
        return self._record_info
    
    @record_info.setter
    def record_info(self, value: Any) -> None:
        self._record_info = value
        
    @property
    def average_tier_info(self) -> Tier:
        """
        A `Tier` object representing the average league tier
        """
        return self._average_tier_info
    
    @average_tier_info.setter
    def average_tier_info(self, value: Tier) -> None:
        self._average_tier_info = value
         
    @property
    def participants(self) -> list[Participant]:
        """
        A `list[Participant]` object(s) representing all participants of a game
        """
        return self._participants
    
    @participants.setter
    def participants(self, value: list[Participant]) -> None:
        self._participants = value
    
    @property
    def teams(self) -> list[Team]:
        """
        A `list[Team]` object(s) representing all teams of a game
        """
        return self._teams
    
    @teams.setter
    def teams(self, value: list[Team]) -> None:
        self._teams = value
        
    @property
    def memo(self) -> Any:
        """
        An `Any` object with unknown return value and type
        """
        return self._memo
    
    @memo.setter
    def memo(self, value: Any) -> None:
        self._memo = value
        
    @property
    def myData(self) -> Participant:
        """
        A `Participant` object representing personal participant record
        """
        return self._myData
    
    @myData.setter
    def myData(self, value: Participant) -> None:
        self._myData = value
    
    def __repr__(self) -> str:
        return f"Game(champion_id={self.myData.champion_id}, kill={self.myData.stats.kill}, death={self.myData.stats.death}, assist={self.myData.stats.assist}, position={self.myData.position}, result={self.myData.stats.result})"


class Summoner:
    """
    Represents a summoner.\n
    
    ### Properties:
        `id: int` - Summoner id\n
        `summoner_id: str` - Summoner id\n
        `acct_id: str` - Account id\n
        `puuid: str` - Puuid\n
        `game_name: str` - In-game username\n
        `tagline: str` - Regional identifier\n
        `name: str` - Summoner name\n
        `internal_name: str` - Internal name\n
        `profile_image_url: str` - Profile image URL\n
        `level: int` - Summoner level\n
        `updated_at: datetime` - When the summoner was last updated\n
        `renewable_at: datetime` - When the summoner can be renewed\n
        `previous_seasons: Season | list[Season]` - Previous seasons\n
        `league_stats: LeagueStats | list[LeagueStats]` - League stats\n
        `most_champions: list[ChampionStats]` - Most champions\n
        `recent_game_stats: Game | list[Game]` - Recent game stats\n
    """
    def __init__(self,
                 id: int,
                 summoner_id: str,
                 acct_id: str,
                 puuid: str,
                 game_name: str,
                 tagline: str,
                 name: str,
                 internal_name: str,
                 profile_image_url: str,
                 level: int,
                 updated_at: datetime,
                 renewable_at: datetime,
                 previous_seasons: Season | list[Season] = None,
                 league_stats: LeagueStats | list[LeagueStats] = None,
                 most_champions: list[ChampionStats] = None, 
                 recent_game_stats: Game | list[Game] = None) -> None:
        self._id = id
        self._summoner_id = summoner_id
        self._acct_id = acct_id
        self._puuid = puuid
        self._game_name = game_name
        self._tagline = tagline
        self._name = name
        self._internal_name = internal_name
        self._profile_image_url = profile_image_url
        self._level = level
        self._updated_at = updated_at
        self._renewable_at = renewable_at
        self._previous_seasons = previous_seasons
        self._league_stats = league_stats
        self._most_champions = most_champions  
        self._recent_game_stats = recent_game_stats
        
    @property
    def id(self) -> int:
        """
        An `int` representing the id (opgg specific)
        """
        return self._id
    
    @id.setter
    def id(self, value: int) -> None:
        self._id = value
        
    @property
    def summoner_id(self) -> str:
        """
        A `str` representing the summoner id (riot api)
        """
        return self._summoner_id
    
    @summoner_id.setter
    def summoner_id(self, value: str) -> None:
        self._summoner_id = value
        
    @property
    def acct_id(self) -> str:
        """
        A `str` representing the account id (riot api)
        """
        return self._acct_id
    
    @acct_id.setter
    def acct_id(self, value: str) -> None:
        self._acct_id = value
        
    @property
    def puuid(self) -> str:
        """
        A `str` representing the puuid (riot api)
        """
        return self._puuid
    
    @puuid.setter
    def puuid(self, value: str) -> None:
        self._puuid = value
    
    @property
    def game_name(self) -> str:
        """
        A `str` representing the in-game username
        """
        return self._game_name
    
    @game_name.setter
    def game_name(self, value: str) -> None:
        self._game_name = value
    
    @property
    def tagline(self) -> str:
        """
        A `str` representing the tagline
        """
        return self._tagline
    
    @tagline.setter
    def tagline(self, value: str) -> None:
        self._tagline = value
    
    @property
    def name(self) -> str:
        """
        A `str` representing the summoner name
        """
        return self._name
    
    @name.setter
    def name(self, value: str) -> None:
        self._name = value
        
    @property
    def internal_name(self) -> str:
        """
        A `str` representing the internal name
        """
        return self._internal_name
    
    @internal_name.setter
    def internal_name(self, value: str) -> None:
        self._internal_name = value
        
    @property
    def profile_image_url(self) -> str:
        """
        A `str` representing the profile image url
        """
        return self._profile_image_url
    
    @profile_image_url.setter
    def profile_image_url(self, value: str) -> None:
        self._profile_image_url = value
        
    @property
    def level(self) -> int:
        """
        An `int` representing the summoner level
        """
        return self._level
    
    @level.setter
    def level(self, value: int) -> None:
        self._level = value
        
    @property
    def updated_at(self) -> datetime:
        """
        A `datetime` object representing when the summoner was last updated
        """
        return self._updated_at
    
    @updated_at.setter
    def updated_at(self, value: datetime) -> None:
        self._updated_at = value
        
    @property
    def renewable_at(self) -> datetime:
        """
        A `datetime` object representing when the summoner can be renewed
        """
        return self._renewable_at
    
    @renewable_at.setter
    def renewable_at(self, value: datetime) -> None:
        self._renewable_at = value
        
    @property
    def previous_seasons(self) -> Season | list[Season]:
        """
        A `Season | list[Season]` object(s) representing the previously played seasons
        """
        return self._previous_seasons
      
    @previous_seasons.setter
    def previous_seasons(self, value: Season | list[Season]) -> None:
        self._previous_seasons = value
        
    @property
    def league_stats(self) -> LeagueStats | list[LeagueStats]:
        """
        A `LeagueStats | list[LeagueStats]` object(s) representing all applicable league stats
        """
        return self._league_stats
    
    @league_stats.setter
    def league_stats(self, value: LeagueStats | list[LeagueStats]) -> None:
        self._league_stats = value
        
    @property
    def most_champions(self) -> list[ChampionStats]:
        """
        A `list[ChampionStats]` objects representing the most played champions
        """
        return self._most_champions
    
    @most_champions.setter
    def most_champions(self, value: list[ChampionStats]) -> None:
        self._most_champions = value
        
    @property
    def recent_game_stats(self) -> Game | list[Game]:
        """
        A `Game | list[Game]` object(s) representing the most recent games
        """
        return self._recent_game_stats
    
    @recent_game_stats.setter
    def recent_game_stats(self, value: Game | list[Game]) -> None:
        self._recent_game_stats = value

    def get_tier_from_queue(self, queue: Queue = Queue.SOLO) -> Tier:
        """
        A method to get the summoners current tier in a given queue type.
        
        ### Args:
            queue : `Queue`
                The queue type to get the tier from. Defaults to `Queue.SOLO`.
        
        ### Returns:
            `Tier` : The tier object which contains the rank, division, and lp.
        """
        
        league_stat: LeagueStats
        for league_stat in self.league_stats:
            if league_stat.queue_info.game_type == queue:
                return league_stat.tier_info
        else:
            return None
    
    def get_top_champ(self) -> ChampionStats:
        return self.most_champions[0]
        
    
    def __repr__(self) -> str:
        previous_seasons_fmt, league_stats_fmt, champion_stats_fmt, game_fmt = "", "", "", ""
        
        for season in self.previous_seasons: previous_seasons_fmt += f"{''.ljust(LJF+RJF)}  | {season}\n"
        for league_stat in self.league_stats: league_stats_fmt += f"{''.ljust(LJF+RJF)}  | {league_stat}\n"
        for champ_stat in self.most_champions: champion_stats_fmt += f"{''.ljust(LJF+RJF)}  | {champ_stat}\n"
        for game in self.recent_game_stats: game_fmt += f"{''.ljust(LJF+RJF)}  | {game}\n"
        
        return  f"[Summoner: {self.game_name}]\n{'-' * 80}\n" \
                f"{'Id'.ljust(LJF)} {'(int)'.rjust(RJF)} | {self.id}\n" \
                f"{'Summoner Id'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.summoner_id}\n" \
                f"{'Account Id'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.acct_id}\n" \
                f"{'Puuid'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.puuid}\n" \
                f"{'Game Name'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.game_name}\n" \
                f"{'Tagline'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.tagline}\n" \
                f"{'Name'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.name}\n" \
                f"{'Internal Name'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.internal_name}\n" \
                f"{'Profile Image Url'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.profile_image_url}\n" \
                f"{'Level'.ljust(LJF)} {'(int)'.rjust(RJF)} | {self.level}\n" \
                f"{'Updated At'.ljust(LJF)} {'(datetime)'.rjust(RJF)} | {self.updated_at}\n" \
                f"{'Renewable At'.ljust(LJF)} {'(datetime)'.rjust(RJF)} | {self.renewable_at}\n" \
                f"{'Previous Seasons'.ljust(LJF)} {'(Season)'.rjust(RJF)} | [List ({len(self.previous_seasons)})] \n{previous_seasons_fmt}" \
                f"{'League Stats'.ljust(LJF)} {'(LeagueStats)'.rjust(RJF)} | [List ({len(self.league_stats)})] \n{league_stats_fmt}" \
                f"{'Most Champions'.ljust(LJF)} {'(ChampStats)'.rjust(RJF)} | [List ({len(self.most_champions)})] \n{champion_stats_fmt}" \
                f"{'Recent Game Stats'.ljust(LJF)} {'(Game)'.rjust(RJF)} | [List ({len(self.recent_game_stats)})] \n{game_fmt}"