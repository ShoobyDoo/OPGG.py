# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : Doomlad
# Date    : 2023-07-05
# Edit    : 2023-07-05
# License : BSD-3-Clause


class ChampionStats:
    def __init__(self,
                 id,
                 play,
                 win,
                 lose,
                 kill,
                 death,
                 assist,
                 gold_earned,
                 minion_kill,
                 turret_kill,
                 neutral_minion_kill,
                 damage_dealt,
                 damage_taken,
                 physical_damage_dealt,
                 magic_damage_dealt,
                 most_kill,
                 max_kill,
                 max_death,
                 double_kill,
                 triple_kill,
                 quadra_kill,
                 penta_kill,
                 game_length_second) -> None:
        self._id = id
        self._play = play
        self._win = win
        self._lose = lose
        self._kill = kill
        self._death = death
        self._assist = assist
        self._gold_earned = gold_earned
        self._minion_kill = minion_kill 
        self._turret_kill = turret_kill 
        self._neutral_minion_kill = neutral_minion_kill 
        self._damage_dealt = damage_dealt 
        self._damage_taken = damage_taken 
        self._physical_damage_dealt = physical_damage_dealt 
        self._magic_damage_dealt = magic_damage_dealt 
        self._most_kill = most_kill 
        self._max_kill = max_kill 
        self._max_death = max_death 
        self._double_kill = double_kill 
        self._triple_kill = triple_kill 
        self._quadra_kill = quadra_kill 
        self._penta_kill = penta_kill 
        self._game_length_second = game_length_second
        
    @property
    def id(self) -> int:
        return self._id
    
    @property
    def play(self) -> int:
        return self._play

    @property
    def win(self) -> int:
        return self._win

    @property
    def lose(self) -> int:
        return self._lose

    @property
    def kill(self) -> int:
        return self._kill

    @property
    def death(self) -> int:
        return self._death

    @property
    def assist(self) -> int:
        return self._assist

    @property
    def gold_earned(self) -> int:
        return self._gold_earned

    @property
    def minion_kill(self) -> int:
        return self._minion_kill
 
    @property
    def turret_kill(self) -> int:
        return self._turret_kill

    @property
    def neutral_minion_kill(self) -> int:
        return self._neutral_minion_kill

    @property
    def damage_dealt(self) -> int:
        return self._damage_dealt
        
    @property
    def damage_taken(self) -> int:
        return self._damage_taken
        
    @property
    def physical_damage_dealt(self) -> int:
        return self._physical_damage_dealt
        
    @property
    def magic_damage_dealt(self) -> int:
        return self._magic_damage_dealt

    @property
    def most_kill(self) -> int:
        return self._most_kill
    
    @property
    def max_kill(self) -> int:
        return self._max_kill
    
    @property
    def max_death(self) -> int:
        return self._max_death
    
    @property
    def double_kill(self) -> int:
        return self._double_kill
    
    @property
    def triple_kill(self) -> int:
        return self._triple_kill
    
    @property
    def quadra_kill(self) -> int:
        return self._quadra_kill
    
    @property
    def penta_kill(self) -> int:
        return self._penta_kill
    
    @property
    def game_length_second(self) -> int:
        return self._game_length_second
    
    @property
    def kda(self) -> float:
        return (self._kill + self._assist) / self._death if self._death != 0 else 0

    def __repr__(self) -> str:
        return  f"ChampionStats(ID={self.id}, Win={self.win}, Lose={self.lose}, KDA={round(self.kda, 2)})"