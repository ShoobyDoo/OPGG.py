# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : ShoobyDoo
# Date    : 2023-07-05
# License : BSD-3-Clause


from datetime import datetime
from opgg.champion import Champion


class Game:
    """
    Represents a game played by a summoner.
    
    ### Properties:
        `game_id` - Internal game id\n
        `champion` - Champion played\n
        `kill` - Number of kills\n
        `death` - Number of deaths\n
        `assist` - Number of assists\n
        `position` - Position played\n
        `is_win` - Whether the game was won\n
        `is_remake` - Whether the game was a remake\n
        `op_score` - OP.GG score\n
        `op_score_rank` - OP.GG score rank\n
        `is_opscore_max_in_team` - Whether the OP.GG score was the highest in the team\n
        `created_at` - When the game was played\n
    """
    def __init__(self,
                 game_id: str,
                 champion: Champion,
                 kill: int,
                 death: int,
                 assist: int,
                 position: str,
                 is_win: bool,
                 is_remake: bool,
                 op_score: float,
                 op_score_rank: int,
                 is_opscore_max_in_team: bool,
                 created_at: datetime) -> None:
        self._game_id = game_id
        self._champion = champion
        self._kill = kill
        self._death = death
        self._assist = assist
        self._position = position
        self._is_win = is_win
        self._is_remake = is_remake
        self._op_score = op_score
        self._op_score_rank = op_score_rank
        self._is_opscore_max_in_team = is_opscore_max_in_team
        self._created_at = created_at
        
    @property
    def game_id(self) -> str:
        """
        A `str` representing the Internal game id
        """
        return self._game_id
    
    @game_id.setter
    def game_id(self, value: str) -> None:
        self._game_id = value
        
    @property
    def champion(self) -> Champion:
        """
        A `Champion` object representing the champion played
        """
        return self._champion
    
    @champion.setter
    def champion(self, value: Champion) -> None:
        self._champion = value
        
    @property
    def kill(self) -> int:
        """
        An `int` representing the number of kills
        """
        return self._kill
    
    @kill.setter
    def kill(self, value: int) -> None:
        self._kill = value
        
    @property
    def death(self) -> int:
        """
        An `int` representing the number of deaths
        """
        return self._death
    
    @death.setter
    def death(self, value: int) -> None:
        self._death = value
        
    @property
    def assist(self) -> int:
        """
        An `int` representing the number of assists
        """
        return self._assist
    
    @assist.setter
    def assist(self, value: int) -> None:
        self._assist = value
        
    @property
    def position(self) -> str:
        """
        A `str` representing the position played
        """
        return self._position
     
    @position.setter
    def position(self, value: str) -> None:
        self._position = value
        
    @property
    def is_win(self) -> bool:
        """
        A `bool` representing whether the game was won
        """
        return self._is_win
    
    @is_win.setter
    def is_win(self, value: bool) -> None:
        self._is_win = value
        
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
    def op_score(self) -> float:
        """
        A `float` representing the OP.GG score
        """
        return self._op_score
    
    @op_score.setter
    def op_score(self, value: float) -> None:
        self._op_score = value
        
    @property
    def op_score_rank(self) -> int:
        """
        An `int` representing the OP.GG score rank
        """
        return self._op_score_rank
    
    @op_score_rank.setter
    def op_score_rank(self, value: int) -> None:
        self._op_score_rank = value
        
    @property
    def is_opscore_max_in_team(self) -> bool:
        """
        A `bool` representing whether the OP.GG score was the highest in the team (MVP)
        """
        return self._is_opscore_max_in_team
    
    @is_opscore_max_in_team.setter
    def is_opscore_max_in_team(self, value: bool) -> None:
        self._is_opscore_max_in_team = value
         
    @property
    def created_at(self) -> datetime:
        """
        A `datetime` object representing when the game was played
        """
        return self._created_at
    
    @created_at.setter
    def created_at(self, value: datetime) -> None:
        self._created_at = value
    
    def __repr__(self) -> str:
        return f"Game(champion={self._champion}, kill={self._kill}, death={self._death}, assist={self._assist}, position={self._position}, is_win={self._is_win})"