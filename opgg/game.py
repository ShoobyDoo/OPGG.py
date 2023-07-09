# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : Doomlad
# Date    : 2023-07-05
# Edit    : 2023-07-05
# License : BSD-3-Clause


from __init__ import datetime

class Game:
    def __init__(self,
                 game_id: str,
                 champion_id: int,
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
        self._champion_id = champion_id
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
        return self._game_id
    
    @game_id.setter
    def game_id(self, value: str) -> None:
        self._game_id = value
        
    @property
    def champion_id(self) -> int:
        return self._champion_id
    
    @champion_id.setter
    def champion_id(self, value: int) -> None:
        self._champion_id = value
        
    @property
    def kill(self) -> int:
        return self._kill
    
    @kill.setter
    def kill(self, value: int) -> None:
        self._kill = value
        
    @property
    def death(self) -> int:
        return self._death
    
    @death.setter
    def death(self, value: int) -> None:
        self._death = value
        
    @property
    def assist(self) -> int:
        return self._assist
    
    @assist.setter
    def assist(self, value: int) -> None:
        self._assist = value
        
    @property
    def position(self) -> str:
        return self._position
     
    @position.setter
    def position(self, value: str) -> None:
        self._position = value
        
    @property
    def is_win(self) -> bool:
        return self._is_win
    
    @is_win.setter
    def is_win(self, value: bool) -> None:
        self._is_win = value
        
    @property
    def is_remake(self) -> bool:
        return self._is_remake
    
    @is_remake.setter
    def is_remake(self, value: bool) -> None:
        self._is_remake = value
        
    @property
    def op_score(self) -> float:
        return self._op_score
    
    @op_score.setter
    def op_score(self, value: float) -> None:
        self._op_score = value
        
    @property
    def op_score_rank(self) -> int:
        return self._op_score_rank
    
    @op_score_rank.setter
    def op_score_rank(self, value: int) -> None:
        self._op_score_rank = value
        
    @property
    def is_opscore_max_in_team(self) -> bool:
        return self._is_opscore_max_in_team
    
    @is_opscore_max_in_team.setter
    def is_opscore_max_in_team(self, value: bool) -> None:
        self._is_opscore_max_in_team = value
         
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @created_at.setter
    def created_at(self, value: datetime) -> None:
        self._created_at = value