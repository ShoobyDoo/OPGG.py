# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : ShoobyDoo
# Date    : 2023-07-05
# License : BSD-3-Clause


from datetime import datetime
from typing import Any
from opgg.champion import Champion
from opgg.league_stats import QueueInfo, Tier


class Stats:
    def __init__(self,
                 champion_level: int,
                 damage_self_mitigated: int,
                 damage_dealt_to_objectives: int,
                 inhibitor_kill: int,
                 inhibitor_first: int,
                 rift_herald_kill: int,
                 rift_herald_first: int,
                 dragon_kill: int,
                 dragon_first: int, 
                 baron_kill: int,
                 baron_first: int, 
                 tower_kill: int,
                 tower_first: int, 
                 horde_kill: int,
                 horde_first: int, 
                 is_remake: bool,
                 death: int,
                 assist: int,
                 gold_earned: int,
                 kill: int) -> None:
        self._champion_level = champion_level
        self._damage_self_mitigated = damage_self_mitigated
        self._damage_dealt_to_objectives = damage_dealt_to_objectives
        self._inhibitor_kill = inhibitor_kill
        self._inhibitor_first = inhibitor_first
        self._rift_herald_kill = rift_herald_kill
        self._rift_herald_first = rift_herald_first
        self._dragon_kill = dragon_kill
        self._dragon_first = dragon_first
        self._baron_kill = baron_kill
        self._baron_first = baron_first
        self._tower_kill = tower_kill
        self._tower_first = tower_first
        self._horde_kill = horde_kill
        self._horde_first = horde_first
        self._is_remake = is_remake
        self._death = death
        self._assist = assist
        self._gold_earned = gold_earned
        self._kill = kill

    @property
    def champion_level(self) -> bool:
        """
        A `bool` representing the game result
        """
        return self._champion_level
    
    @champion_level.setter
    def champion_level(self, value: bool) -> None:
        self._champion_level = value

    @property
    def damage_self_mitigated(self) -> int:
        """
        An `int` representing the number of champions killed
        """
        return self._damage_self_mitigated
    
    @damage_self_mitigated.setter
    def damage_self_mitigated(self, value: int) -> None:
        self._damage_self_mitigated = value
        
    @property
    def damage_dealt_to_objectives(self) -> int:
        """
        A `int` representing if team got first champion kill
        """
        return self._damage_dealt_to_objectives
    
    @damage_dealt_to_objectives.setter
    def damage_dealt_to_objectives(self, value: int) -> None:
        self._damage_dealt_to_objectives = value
    
    @property
    def damage_dealt_to_turrets(self) -> int:
        """
        An `int` representing the number of inhibitors killed
        """
        return self._damage_dealt_to_turrets
    
    @damage_dealt_to_turrets.setter
    def damage_dealt_to_turrets(self, value: int) -> None:
        self._damage_dealt_to_turrets = value
    
    @property
    def magic_damage_dealt_player(self) -> int:
        """
        A `int` representing if team got first inhibitor kill
        """
        return self._magic_damage_dealt_player
    
    @magic_damage_dealt_player.setter
    def magic_damage_dealt_player(self, value: int) -> None:
        self._magic_damage_dealt_player = value
    
    @property
    def physical_damage_taken(self) -> int:
        """
        An `int` representing the number of rift herald kills
        """
        return self._physical_damage_taken
    
    @physical_damage_taken.setter
    def physical_damage_taken(self, value: int) -> None:
        self._physical_damage_taken = value
    
    @property
    def physical_damage_dealt_to_champions(self) -> int:
        """
        A `int` representing if team got first rift herald kill
        """
        return self._physical_damage_dealt_to_champions
    
    @physical_damage_dealt_to_champions.setter
    def physical_damage_dealt_to_champions(self, value: int) -> None:
        self._physical_damage_dealt_to_champions = value
    
    @property
    def total_damage_taken(self) -> int:
        """
        An `int` representing the number of dragon kills
        """
        return self._total_damage_taken
    
    @total_damage_taken.setter
    def total_damage_taken(self, value: int) -> None:
        self._total_damage_taken = value
        
    @property
    def total_damage_dealt(self) -> int:
        """
        A `int` representing if team got first dragon
        """
        return self._total_damage_dealt
    
    @total_damage_dealt.setter
    def total_damage_dealt(self, value: int) -> None:
        self._total_damage_dealt = value
        
    @property
    def total_damage_dealt_to_champions(self) -> int:
        """
        An `int` representing the number of baron kills
        """
        return self._total_damage_dealt_to_champions
    
    @total_damage_dealt_to_champions.setter
    def total_damage_dealt_to_champions(self, value: int) -> None:
        self._total_damage_dealt_to_champions = value
        
    @property
    def largest_critical_strike(self) -> int:
        """
        A `int` representing if team got first baron kill
        """
        return self._largest_critical_strike
    
    @largest_critical_strike.setter
    def largest_critical_strike(self, value: int) -> None:
        self._largest_critical_strike = value
        
    @property
    def time_ccing_others(self) -> int:
        """
        An `int` representing the number of tower kills
        """
        return self._time_ccing_others
    
    @time_ccing_others.setter
    def time_ccing_others(self, value: int) -> None:
        self._time_ccing_others = value
        
    @property
    def vision_score(self) -> int:
        """
        A `int` representing if team got first tower kill
        """
        return self._vision_score
    
    @vision_score.setter
    def vision_score(self, value: int) -> None:
        self._vision_score = value
        
    @property
    def vision_wards_bought_in_game(self) -> int:
        """
        An `int` representing the number of void grub kills
        """
        return self._vision_wards_bought_in_game
    
    @vision_wards_bought_in_game.setter
    def vision_wards_bought_in_game(self, value: int) -> None:
        self._vision_wards_bought_in_game = value
        
    @property
    def sight_wards_bought_in_game(self) -> int:
        """
        A `int` representing if team got first void grub kill
        """
        return self._sight_wards_bought_in_game
    
    @sight_wards_bought_in_game.setter
    def sight_wards_bought_in_game(self, value: int) -> None:
        self._sight_wards_bought_in_game = value
        
    @property
    def ward_kill(self) -> int:
        """
        A `int` representing if game was a remake
        """
        return self._ward_kill
    
    @ward_kill.setter
    def ward_kill(self, value: int) -> None:
        self._ward_kill = value
        
    @property
    def ward_place(self) -> int:
        """
        An `int` representing the total amount of ward_places for the team
        """
        return self._ward_place
    
    @ward_place.setter
    def ward_place(self, value: int) -> None:
        self._ward_place = value
        
    @property
    def turret_kill(self) -> int:
        """
        An `int` representing the total amount of turret_kills for the team
        """
        return self._turret_kill
    
    @turret_kill.setter
    def turret_kill(self, value: int) -> None:
        self._turret_kill = value    
    
    @property
    def barrack_kill(self) -> int:
        """
        An `int` representing the total amount of gold earned for the team
        """
        return self._barrack_kill
    
    @barrack_kill.setter
    def barrack_kill(self, value: int) -> None:
        self._barrack_kill = value
    
    @property
    def kill(self) -> int:
        """
        An `int` representing the total amount of kills for the team
        """
        return self._kill
    
    @kill.setter
    def kill(self, value: int) -> None:
        self._kill = value
    
    @property
    def death(self) -> int:
        """
        An `int` representing the total amount of deaths for the team
        """
        return self._death
    
    @death.setter
    def death(self, value: int) -> None:
        self._death = value
    
    @property
    def assist(self) -> int:
        """
        An `int` representing the total amount of assists for the team
        """
        return self._assist
    
    @assist.setter
    def assist(self, value: int) -> None:
        self._assist = value
    
    @property
    def largest_multi_kill(self) -> int:
        """
        An `int` representing the total amount of largest_multi_kills for the team
        """
        return self._largest_multi_kill
    
    @largest_multi_kill.setter
    def largest_multi_kill(self, value: int) -> None:
        self._largest_multi_kill = value
    
    @property
    def largest_killing_spree(self) -> int:
        """
        An `int` representing the total amount of largest_killing_sprees for the team
        """
        return self._largest_killing_spree
    
    @largest_killing_spree.setter
    def largest_killing_spree(self, value: int) -> None:
        self._largest_killing_spree = value
    
    @property
    def minion_kill(self) -> int:
        """
        An `int` representing the total amount of minion_kills for the team
        """
        return self._minion_kill
    
    @minion_kill.setter
    def minion_kill(self, value: int) -> None:
        self._minion_kill = value
    
    @property
    def neutral_minion_kill_team_jungle(self) -> int:
        """
        An `int` representing the total amount of neutral_minion_kill_team_jungles for the team
        """
        return self._neutral_minion_kill_team_jungle
    
    @neutral_minion_kill_team_jungle.setter
    def neutral_minion_kill_team_jungle(self, value: int) -> None:
        self._neutral_minion_kill_team_jungle = value
    
    @property
    def neutral_minion_kill_enemy_jungle(self) -> int:
        """
        An `int` representing the total amount of neutral_minion_kill_enemy_jungles for the team
        """
        return self._neutral_minion_kill_enemy_jungle
    
    @neutral_minion_kill_enemy_jungle.setter
    def neutral_minion_kill_enemy_jungle(self, value: int) -> None:
        self._neutral_minion_kill_enemy_jungle = value
    
    @property
    def neutral_minion_kill(self) -> int:
        """
        An `int` representing the total amount of neutral_minion_kills for the team
        """
        return self._neutral_minion_kill
    
    @neutral_minion_kill.setter
    def neutral_minion_kill(self, value: int) -> None:
        self._neutral_minion_kill = value
    
    @property
    def gold_earned(self) -> int:
        """
        An `int` representing the total amount of gold_earneds for the team
        """
        return self._gold_earned
    
    @gold_earned.setter
    def gold_earned(self, value: int) -> None:
        self._gold_earned = value
    
    @property
    def total_heal(self) -> int:
        """
        An `int` representing the total amount of total_heals for the team
        """
        return self._total_heal
    
    @total_heal.setter
    def total_heal(self, value: int) -> None:
        self._total_heal = value
    
    @property
    def result(self) -> int:
        """
        An `int` representing the total amount of results for the team
        """
        return self._result
    
    @result.setter
    def result(self, value: int) -> None:
        self._result = value
    
    @property
    def op_score(self) -> int:
        """
        An `int` representing the total amount of op_scores for the team
        """
        return self._op_score
    
    @op_score.setter
    def op_score(self, value: int) -> None:
        self._op_score = value
    
    @property
    def op_score_rank(self) -> int:
        """
        An `int` representing the total amount of op_score_ranks for the team
        """
        return self._op_score_rank
    
    @op_score_rank.setter
    def op_score_rank(self, value: int) -> None:
        self._op_score_rank = value
    
    @property
    def is_opscore_max_in_team(self) -> int:
        """
        An `int` representing the total amount of is_opscore_max_in_teams for the team
        """
        return self._is_opscore_max_in_team
    
    @is_opscore_max_in_team.setter
    def is_opscore_max_in_team(self, value: int) -> None:
        self._is_opscore_max_in_team = value
    
    @property
    def lane_score(self) -> int:
        """
        An `int` representing the total amount of lane_scores for the team
        """
        return self._lane_score
    
    @lane_score.setter
    def lane_score(self, value: int) -> None:
        self._lane_score = value
    
    @property
    def op_score_timeline(self) -> list[dict[str, float]]:
        """
        An `list[dict[str, float]]` representing the total amount of op_score_timelines for the team
        """
        return self._op_score_timeline
    
    @op_score_timeline.setter
    def op_score_timeline(self, value: list[dict[str, float]]) -> None:
        self._op_score_timeline = value
    
    @property
    def op_score_timeline_analysis(self) -> dict[str, str]:
        """
        An `dict[str, str]` representing the total amount of op_score_timeline_analysiss for the team
        """
        return self._op_score_timeline_analysis
    
    @op_score_timeline_analysis.setter
    def op_score_timeline_analysis(self, value: dict[str, str]) -> None:
        self._op_score_timeline_analysis = value
    

class GameStats:
    def __init__(self,
                 is_win: bool,
                 champion_kill: int,
                 champion_first: bool,
                 inhibitor_kill: int,
                 inhibitor_first: bool,
                 rift_herald_kill: int,
                 rift_herald_first: bool,
                 dragon_kill: int,
                 dragon_first: bool, 
                 baron_kill: int,
                 baron_first: bool, 
                 tower_kill: int,
                 tower_first: bool, 
                 horde_kill: int,
                 horde_first: bool, 
                 is_remake: bool,
                 death: int,
                 assist: int,
                 gold_earned: int,
                 kill: int) -> None:
        self._is_win = is_win
        self._champion_kill = champion_kill
        self._champion_first = champion_first
        self._inhibitor_kill = inhibitor_kill
        self._inhibitor_first = inhibitor_first
        self._rift_herald_kill = rift_herald_kill
        self._rift_herald_first = rift_herald_first
        self._dragon_kill = dragon_kill
        self._dragon_first = dragon_first
        self._baron_kill = baron_kill
        self._baron_first = baron_first
        self._tower_kill = tower_kill
        self._tower_first = tower_first
        self._horde_kill = horde_kill
        self._horde_first = horde_first
        self._is_remake = is_remake
        self._death = death
        self._assist = assist
        self._gold_earned = gold_earned
        self._kill = kill

    @property
    def is_win(self) -> bool:
        """
        A `bool` representing the game result
        """
        return self._is_win
    
    @is_win.setter
    def is_win(self, value: bool) -> None:
        self._is_win = value

    @property
    def champion_kill(self) -> int:
        """
        An `int` representing the number of champions killed
        """
        return self._champion_kill
    
    @champion_kill.setter
    def champion_kill(self, value: int) -> None:
        self._champion_kill = value
        
    @property
    def champion_first(self) -> bool:
        """
        A `bool` representing if team got first champion kill
        """
        return self._champion_first
    
    @champion_first.setter
    def champion_first(self, value: bool) -> None:
        self._champion_first = value
    
    @property
    def inhibitor_kill(self) -> int:
        """
        An `int` representing the number of inhibitors killed
        """
        return self._inhibitor_kill
    
    @inhibitor_kill.setter
    def inhibitor_kill(self, value: int) -> None:
        self._inhibitor_kill = value
    
    @property
    def inhibitor_first(self) -> bool:
        """
        A `bool` representing if team got first inhibitor kill
        """
        return self._inhibitor_first
    
    @inhibitor_first.setter
    def inhibitor_first(self, value: bool) -> None:
        self._inhibitor_first = value
    
    @property
    def rift_herald_kill(self) -> int:
        """
        An `int` representing the number of rift herald kills
        """
        return self._rift_herald_kill
    
    @rift_herald_kill.setter
    def rift_herald_kill(self, value: int) -> None:
        self._rift_herald_kill = value
    
    @property
    def rift_herald_first(self) -> bool:
        """
        A `bool` representing if team got first rift herald kill
        """
        return self._rift_herald_first
    
    @rift_herald_first.setter
    def rift_herald_first(self, value: bool) -> None:
        self._rift_herald_first = value
    
    @property
    def dragon_kill(self) -> int:
        """
        An `int` representing the number of dragon kills
        """
        return self._dragon_kill
    
    @dragon_kill.setter
    def dragon_kill(self, value: int) -> None:
        self._dragon_kill = value
        
    @property
    def dragon_first(self) -> bool:
        """
        A `bool` representing if team got first dragon
        """
        return self._dragon_first
    
    @dragon_first.setter
    def dragon_first(self, value: bool) -> None:
        self._dragon_first = value
        
    @property
    def baron_kill(self) -> int:
        """
        An `int` representing the number of baron kills
        """
        return self._baron_kill
    
    @baron_kill.setter
    def baron_kill(self, value: int) -> None:
        self._baron_kill = value
        
    @property
    def baron_first(self) -> bool:
        """
        A `bool` representing if team got first baron kill
        """
        return self._baron_first
    
    @baron_first.setter
    def baron_first(self, value: bool) -> None:
        self._baron_first = value
        
    @property
    def tower_kill(self) -> int:
        """
        An `int` representing the number of tower kills
        """
        return self._tower_kill
    
    @tower_kill.setter
    def tower_kill(self, value: int) -> None:
        self._tower_kill = value
        
    @property
    def tower_first(self) -> bool:
        """
        A `bool` representing if team got first tower kill
        """
        return self._tower_first
    
    @tower_first.setter
    def tower_first(self, value: bool) -> None:
        self._tower_first = value
        
    @property
    def horde_kill(self) -> int:
        """
        An `int` representing the number of void grub kills
        """
        return self._horde_kill
    
    @horde_kill.setter
    def horde_kill(self, value: int) -> None:
        self._horde_kill = value
        
    @property
    def horde_first(self) -> bool:
        """
        A `bool` representing if team got first void grub kill
        """
        return self._horde_first
    
    @horde_first.setter
    def horde_first(self, value: bool) -> None:
        self._horde_first = value
        
    @property
    def is_remake(self) -> bool:
        """
        A `bool` representing if game was a remake
        """
        return self._is_remake
    
    @is_remake.setter
    def is_remake(self, value: bool) -> None:
        self._is_remake = value
        
    @property
    def death(self) -> int:
        """
        An `int` representing the total amount of deaths for the team
        """
        return self._death
    
    @death.setter
    def death(self, value: int) -> None:
        self._death = value
        
    @property
    def assist(self) -> int:
        """
        An `int` representing the total amount of assists for the team
        """
        return self._assist
    
    @assist.setter
    def assist(self, value: int) -> None:
        self._assist = value    
    
    @property
    def gold_earned(self) -> int:
        """
        An `int` representing the total amount of gold earned for the team
        """
        return self._gold_earned
    
    @gold_earned.setter
    def gold_earned(self, value: int) -> None:
        self._gold_earned = value
    
    @property
    def kill(self) -> int:
        """
        An `int` representing the total amount of kills for the team
        """
        return self._kill
    
    @kill.setter
    def kill(self, value: int) -> None:
        self._kill = value
    

class Team:
    def __init__(self,
                 key: str,
                 game_stat: GameStats,
                 banned_champions: list) -> None:
        self._key = key
        self._game_stat = game_stat
        self._banned_champions = banned_champions

    @property
    def key(self) -> str:
        """
        A `str` representing the team key (BLUE, RED, etc.)
        """
        return self._key
    
    @key.setter
    def key(self, value: str) -> None:
        self._key = value
    
    @property
    def game_stat(self) -> GameStats:
        """
        A `GameStats` object representing all game specific stats
        """
        return self._game_stat
    
    @game_stat.setter
    def game_stat(self, value: GameStats) -> None:
        self._game_stat = value
    
    @property
    def banned_champions(self) -> list:
        """
        A `list` of champion ids that were banned
        """
        return self._banned_champions
    
    @banned_champions.setter
    def banned_champions(self, value: list) -> None:
        self._banned_champions = value


class Team:
    def __init__(self,
                 key: str,
                 game_stat: GameStats,
                 banned_champions: list) -> None:
        self._key = key
        self._game_stat = game_stat
        self._banned_champions = banned_champions

    @property
    def key(self) -> str:
        """
        A `str` representing the team key (BLUE, RED, etc.)
        """
        return self._key
    
    @key.setter
    def key(self, value: str) -> None:
        self._key = value
    
    @property
    def game_stat(self) -> GameStats:
        """
        A `GameStats` object representing all game specific stats
        """
        return self._game_stat
    
    @game_stat.setter
    def game_stat(self, value: GameStats) -> None:
        self._game_stat = value
    
    @property
    def banned_champions(self) -> list:
        """
        A `list` of champion ids that were banned
        """
        return self._banned_champions
    
    @banned_champions.setter
    def banned_champions(self, value: list) -> None:
        self._banned_champions = value


