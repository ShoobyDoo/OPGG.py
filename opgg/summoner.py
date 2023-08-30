# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : ShoobyDoo
# Date    : 2023-07-05
# License : BSD-3-Clause


from datetime import datetime
from opgg.params import Queue
from opgg.season import Season
from opgg.league_stats import LeagueStats, Tier
from opgg.champion import ChampionStats
from opgg.game import Game


# left/right just factor
LJF = 18
RJF = 14


class Summoner:
    """
    Represents a summoner.
    
    ### Properties:
        `id` - Summoner id\n
        `summoner_id` - Summoner id\n
        `acct_id` - Account id\n
        `puuid` - Puuid\n
        `name` - Summoner name\n
        `internal_name` - Internal name\n
        `profile_image_url` - Profile image url\n
        `level` - Summoner level\n
        `updated_at` - When the summoner was last updated\n
        `renewable_at` - When the summoner can be renewed\n
        `previous_seasons` - Previous seasons\n
        `league_stats` - League stats\n
        `most_champions` - Most champions\n
        `recent_game_stats` - Recent game stats
    """
    def __init__(self,
                 id: int,
                 summoner_id: str,
                 acct_id: str,
                 puuid: str,
                 name: str,
                 internal_name: str,
                 profile_image_url: str,
                 level: int,
                 updated_at: datetime,
                 renewable_at: datetime,
                 previous_seasons: Season | list[Season],
                 league_stats: LeagueStats | list[LeagueStats],
                 most_champions: list[ChampionStats], 
                 recent_game_stats: Game | list[Game]) -> None:
        self._id = id
        self._summoner_id = summoner_id
        self._acct_id = acct_id
        self._puuid = puuid
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
        
        return  f"[Summoner: {self.name}]\n{'-' * 80}\n" \
                f"{'Id'.ljust(LJF)} {'(int)'.rjust(RJF)} | {self.id}\n" \
                f"{'Summoner Id'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.summoner_id}\n" \
                f"{'Account Id'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.acct_id}\n" \
                f"{'Puuid'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.puuid}\n" \
                f"{'Name'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.name}\n" \
                f"{'Internal Name'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.internal_name}\n" \
                f"{'Profile Image Url'.ljust(LJF)} {'(str)'.rjust(RJF)} | {self.profile_image_url}\n" \
                f"{'Level'.ljust(LJF)} {'(int)'.rjust(RJF)} | {self.level}\n" \
                f"{'Updated At'.ljust(LJF)} {'(datetime)'.rjust(RJF)} | {self.updated_at}\n" \
                f"{'Renewable At'.ljust(LJF)} {'(datetime)'.rjust(RJF)} | {self.renewable_at}\n" \
                f"{'Previous Seasons'.ljust(LJF)} {'(SeasonInfo)'.rjust(RJF)} | [List ({len(self.previous_seasons)})] \n{previous_seasons_fmt}" \
                f"{'League Stats'.ljust(LJF)} {'(LeagueStats)'.rjust(RJF)} | [List ({len(self.league_stats)})] \n{league_stats_fmt}" \
                f"{'Most Champions'.ljust(LJF)} {'(ChampStats)'.rjust(RJF)} | [List ({len(self.most_champions)})] \n{champion_stats_fmt}" \
                f"{'Recent Game Stats'.ljust(LJF)} {'(Game)'.rjust(RJF)} | [List ({len(self.recent_game_stats)})] \n{game_fmt}"