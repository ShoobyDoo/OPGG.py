# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : ShoobyDoo
# Date    : 2023-07-05
# License : BSD-3-Clause


class Stats:
    """
    Represents a player's performance in a game.\n
    
    ### Properties:
        `champion_level: int` - Level of the champion in the game\n
        `damage_self_mitigated: int` - Total damage mitigated by the player\n
        `damage_dealt_to_objectives: int` - Damage dealt to game objectives\n
        `damage_dealt_to_turrets: int` - Damage dealt to turrets\n
        `magic_damage_dealt_player: int` - Magic damage dealt to players\n
        `physical_damage_taken: int` - Physical damage taken by the player\n
        `physical_damage_dealt_to_champions: int` - Physical damage dealt to champions\n
        `total_damage_taken: int` - Total damage taken by the player\n
        `total_damage_dealt: int` - Total damage dealt by the player\n
        `total_damage_dealt_to_champions: int` - Total damage dealt to champions\n
        `largest_critical_strike: int` - Largest critical strike damage\n
        `time_ccing_others: int` - Time spent crowd controlling other players\n
        `vision_score: int` - Vision score of the player\n
        `vision_wards_bought_in_game: int` - Vision wards bought during the game\n
        `sight_wards_bought_in_game: int` - Sight wards bought during the game\n
        `ward_kill: int` - Number of wards killed\n
        `ward_place: int` - Number of wards placed\n
        `turret_kill: int` - Number of turrets killed\n
        `barrack_kill: int` - Number of barracks killed\n
        `kill: int` - Number of kills\n
        `death: int` - Number of deaths\n
        `assist: int` - Number of assists\n
        `largest_multi_kill: int` - Largest multi-kill achieved\n
        `largest_killing_spree: int` - Largest killing spree achieved\n
        `minion_kill: int` - Number of minions killed\n
        `neutral_minion_kill_team_jungle: int` - Neutral minions killed in the team jungle\n
        `neutral_minion_kill_enemy_jungle: int` - Neutral minions killed in the enemy jungle\n
        `neutral_minion_kill: int` - Total neutral minions killed\n
        `gold_earned: int` - Total gold earned by the player\n
        `total_heal: int` - Total amount of healing done by the player\n
        `result: str` - Result of the game (e.g., win, loss)\n
        `op_score: int` - Overall performance score\n
        `op_score_rank: int` - Rank based on overall performance score\n
        `is_opscore_max_in_team: bool` - Whether the player's op score is the highest in the team\n
        `lane_score: int` - Lane performance score\n
        `op_score_timeline: list[dict]` - Timeline of op scores\n
        `op_score_timeline_analysis: dict` - Analysis of op score timeline\n
    """
    def __init__(self,
                 champion_level: int,
                 damage_self_mitigated: int,
                 damage_dealt_to_objectives: int,
                 damage_dealt_to_turrets: int,
                 magic_damage_dealt_player: int,
                 physical_damage_taken: int,
                 physical_damage_dealt_to_champions: int,
                 total_damage_taken: int,
                 total_damage_dealt: int,
                 total_damage_dealt_to_champions: int,
                 largest_critical_strike: int,
                 time_ccing_others: int,
                 vision_score: int,
                 vision_wards_bought_in_game: int,
                 sight_wards_bought_in_game: int,
                 ward_kill: int,
                 ward_place: int,
                 turret_kill: int,
                 barrack_kill: int,
                 kill: int,
                 death: int,
                 assist: int,
                 largest_multi_kill: int,
                 largest_killing_spree: int,
                 minion_kill: int,
                 neutral_minion_kill_team_jungle: int,
                 neutral_minion_kill_enemy_jungle: int,
                 neutral_minion_kill: int,
                 gold_earned: int,
                 total_heal: int,
                 result: str,
                 op_score: int,
                 op_score_rank: int,
                 is_opscore_max_in_team: bool,
                 lane_score: int,
                 op_score_timeline: list[dict],
                 op_score_timeline_analysis: dict) -> None:
        self._champion_level = champion_level
        self._damage_self_mitigated = damage_self_mitigated
        self._damage_dealt_to_objectives = damage_dealt_to_objectives
        self._damage_dealt_to_turrets = damage_dealt_to_turrets
        self._magic_damage_dealt_player = magic_damage_dealt_player
        self._physical_damage_taken = physical_damage_taken
        self._physical_damage_dealt_to_champions = physical_damage_dealt_to_champions
        self._total_damage_taken = total_damage_taken
        self._total_damage_dealt = total_damage_dealt
        self._total_damage_dealt_to_champions = total_damage_dealt_to_champions
        self._largest_critical_strike = largest_critical_strike
        self._time_ccing_others = time_ccing_others
        self._vision_score = vision_score
        self._vision_wards_bought_in_game = vision_wards_bought_in_game
        self._sight_wards_bought_in_game = sight_wards_bought_in_game
        self._ward_kill = ward_kill
        self._ward_place = ward_place
        self._turret_kill = turret_kill
        self._barrack_kill = barrack_kill
        self._kill = kill
        self._death = death
        self._assist = assist
        self._largest_multi_kill = largest_multi_kill
        self._largest_killing_spree = largest_killing_spree
        self._minion_kill = minion_kill
        self._neutral_minion_kill_team_jungle = neutral_minion_kill_team_jungle
        self._neutral_minion_kill_enemy_jungle = neutral_minion_kill_enemy_jungle
        self._neutral_minion_kill = neutral_minion_kill
        self._gold_earned = gold_earned
        self._total_heal = total_heal
        self._result = result
        self._op_score = op_score
        self._op_score_rank = op_score_rank
        self._is_opscore_max_in_team = is_opscore_max_in_team
        self._lane_score = lane_score
        self._op_score_timeline = op_score_timeline
        self._op_score_timeline_analysis = op_score_timeline_analysis

    @property
    def champion_level(self) -> int:
        """
        A `int` representing the champions level
        """
        return self._champion_level
    
    @champion_level.setter
    def champion_level(self, value: int) -> None:
        self._champion_level = value

    @property
    def damage_self_mitigated(self) -> int:
        """
        An `int` representing the amount of damage mitigated on self
        """
        return self._damage_self_mitigated
    
    @damage_self_mitigated.setter
    def damage_self_mitigated(self, value: int) -> None:
        self._damage_self_mitigated = value
        
    @property
    def damage_dealt_to_objectives(self) -> int:
        """
        A `int` representing the amount of damage dealt to objectives overall
        """
        return self._damage_dealt_to_objectives
    
    @damage_dealt_to_objectives.setter
    def damage_dealt_to_objectives(self, value: int) -> None:
        self._damage_dealt_to_objectives = value
    
    @property
    def damage_dealt_to_turrets(self) -> int:
        """
        An `int` representing the amount of damage dealt to turrets specifically
        """
        return self._damage_dealt_to_turrets
    
    @damage_dealt_to_turrets.setter
    def damage_dealt_to_turrets(self, value: int) -> None:
        self._damage_dealt_to_turrets = value
    
    @property
    def magic_damage_dealt_player(self) -> int:
        """
        A `int` representing the amount of magic damage dealt to other players
        """
        return self._magic_damage_dealt_player
    
    @magic_damage_dealt_player.setter
    def magic_damage_dealt_player(self, value: int) -> None:
        self._magic_damage_dealt_player = value
    
    @property
    def physical_damage_taken(self) -> int:
        """
        An `int` representing the amount of physical damage taken
        """
        return self._physical_damage_taken
    
    @physical_damage_taken.setter
    def physical_damage_taken(self, value: int) -> None:
        self._physical_damage_taken = value
    
    @property
    def physical_damage_dealt_to_champions(self) -> int:
        """
        A `int` representing the amount of physical damage dealt to other players
        """
        return self._physical_damage_dealt_to_champions
    
    @physical_damage_dealt_to_champions.setter
    def physical_damage_dealt_to_champions(self, value: int) -> None:
        self._physical_damage_dealt_to_champions = value
    
    @property
    def total_damage_taken(self) -> int:
        """
        An `int` representing the amount of damage taken in total
        """
        return self._total_damage_taken
    
    @total_damage_taken.setter
    def total_damage_taken(self, value: int) -> None:
        self._total_damage_taken = value
        
    @property
    def total_damage_dealt(self) -> int:
        """
        A `int` representing the amount of damage dealt in total
        """
        return self._total_damage_dealt
    
    @total_damage_dealt.setter
    def total_damage_dealt(self, value: int) -> None:
        self._total_damage_dealt = value
        
    @property
    def total_damage_dealt_to_champions(self) -> int:
        """
        An `int` representing the amount of damage dealt to other champions in total
        """
        return self._total_damage_dealt_to_champions
    
    @total_damage_dealt_to_champions.setter
    def total_damage_dealt_to_champions(self, value: int) -> None:
        self._total_damage_dealt_to_champions = value
        
    @property
    def largest_critical_strike(self) -> int:
        """
        A `int` representing the largest critical strike
        """
        return self._largest_critical_strike
    
    @largest_critical_strike.setter
    def largest_critical_strike(self, value: int) -> None:
        self._largest_critical_strike = value
        
    @property
    def time_ccing_others(self) -> int:
        """
        An `int` representing the amount of time cc'ing (crowd controlling) others
        """
        return self._time_ccing_others
    
    @time_ccing_others.setter
    def time_ccing_others(self, value: int) -> None:
        self._time_ccing_others = value
        
    @property
    def vision_score(self) -> int:
        """
        A `int` representing the vision score
        """
        return self._vision_score
    
    @vision_score.setter
    def vision_score(self, value: int) -> None:
        self._vision_score = value
        
    @property
    def vision_wards_bought_in_game(self) -> int:
        """
        An `int` representing the amount of vision wards bought in the game
        """
        return self._vision_wards_bought_in_game
    
    @vision_wards_bought_in_game.setter
    def vision_wards_bought_in_game(self, value: int) -> None:
        self._vision_wards_bought_in_game = value
        
    @property
    def sight_wards_bought_in_game(self) -> int:
        """
        A `int` representing the amount of sight wards bought in the game
        """
        return self._sight_wards_bought_in_game
    
    @sight_wards_bought_in_game.setter
    def sight_wards_bought_in_game(self, value: int) -> None:
        self._sight_wards_bought_in_game = value
        
    @property
    def ward_kill(self) -> int:
        """
        A `int` representing the number of wards killed
        """
        return self._ward_kill
    
    @ward_kill.setter
    def ward_kill(self, value: int) -> None:
        self._ward_kill = value
        
    @property
    def ward_place(self) -> int:
        """
        An `int` representing the number of wards placed
        """
        return self._ward_place
    
    @ward_place.setter
    def ward_place(self, value: int) -> None:
        self._ward_place = value
        
    @property
    def turret_kill(self) -> int:
        """
        An `int` representing the amount of turrets killed
        """
        return self._turret_kill
    
    @turret_kill.setter
    def turret_kill(self, value: int) -> None:
        self._turret_kill = value    
    
    @property
    def barrack_kill(self) -> int:
        """
        An `int` representing the amount of inhibitor kills
        """
        return self._barrack_kill
    
    @barrack_kill.setter
    def barrack_kill(self, value: int) -> None:
        self._barrack_kill = value
    
    @property
    def kill(self) -> int:
        """
        An `int` representing the amount of kills
        """
        return self._kill
    
    @kill.setter
    def kill(self, value: int) -> None:
        self._kill = value
    
    @property
    def death(self) -> int:
        """
        An `int` representing the amount of death
        """
        return self._death
    
    @death.setter
    def death(self, value: int) -> None:
        self._death = value
    
    @property
    def assist(self) -> int:
        """
        An `int` representing the amount of assist
        """
        return self._assist
    
    @assist.setter
    def assist(self, value: int) -> None:
        self._assist = value
    
    @property
    def largest_multi_kill(self) -> int:
        """
        An `int` representing the largest amount of multi-kills
        """
        return self._largest_multi_kill
    
    @largest_multi_kill.setter
    def largest_multi_kill(self, value: int) -> None:
        self._largest_multi_kill = value
    
    @property
    def largest_killing_spree(self) -> int:
        """
        An `int` representing the largest killing spree
        """
        return self._largest_killing_spree
    
    @largest_killing_spree.setter
    def largest_killing_spree(self, value: int) -> None:
        self._largest_killing_spree = value
    
    @property
    def minion_kill(self) -> int:
        """
        An `int` representing the amount of minions killed
        """
        return self._minion_kill
    
    @minion_kill.setter
    def minion_kill(self, value: int) -> None:
        self._minion_kill = value
    
    @property
    def neutral_minion_kill_team_jungle(self) -> int:
        """
        An `int` representing the amount of neutral jungle mobs killed in team jungle
        """
        return self._neutral_minion_kill_team_jungle
    
    @neutral_minion_kill_team_jungle.setter
    def neutral_minion_kill_team_jungle(self, value: int) -> None:
        self._neutral_minion_kill_team_jungle = value
    
    @property
    def neutral_minion_kill_enemy_jungle(self) -> int:
        """
        An `int` representing the amount of neutral jungle mobs killed in enemy jungle
        """
        return self._neutral_minion_kill_enemy_jungle
    
    @neutral_minion_kill_enemy_jungle.setter
    def neutral_minion_kill_enemy_jungle(self, value: int) -> None:
        self._neutral_minion_kill_enemy_jungle = value
    
    @property
    def neutral_minion_kill(self) -> int:
        """
        An `int` representing the amount of neutral minion kills
        """
        return self._neutral_minion_kill
    
    @neutral_minion_kill.setter
    def neutral_minion_kill(self, value: int) -> None:
        self._neutral_minion_kill = value
    
    @property
    def gold_earned(self) -> int:
        """
        An `int` representing the amount of gold earned
        """
        return self._gold_earned
    
    @gold_earned.setter
    def gold_earned(self, value: int) -> None:
        self._gold_earned = value
    
    @property
    def total_heal(self) -> int:
        """
        An `int` representing the total amount healed
        """
        return self._total_heal
    
    @total_heal.setter
    def total_heal(self, value: int) -> None:
        self._total_heal = value
    
    @property
    def result(self) -> str:
        """
        An `str` representing the result of the match (WIN / LOSE)
        """
        return self._result
    
    @result.setter
    def result(self, value: str) -> None:
        self._result = value
    
    @property
    def op_score(self) -> int:
        """
        An `int` representing your op score
        """
        return self._op_score
    
    @op_score.setter
    def op_score(self, value: int) -> None:
        self._op_score = value
    
    @property
    def op_score_rank(self) -> int:
        """
        An `int` representing how your op score stacked up amongst your team (1-10)
        """
        return self._op_score_rank
    
    @op_score_rank.setter
    def op_score_rank(self, value: int) -> None:
        self._op_score_rank = value
    
    @property
    def is_opscore_max_in_team(self) -> bool:
        """
        An `bool` representing whether or not you had the highest op score amongst your team
        """
        return self._is_opscore_max_in_team
    
    @is_opscore_max_in_team.setter
    def is_opscore_max_in_team(self, value: bool) -> None:
        self._is_opscore_max_in_team = value
    
    @property
    def lane_score(self) -> int:
        """
        An `int` representing your lane score
        """
        return self._lane_score
    
    @lane_score.setter
    def lane_score(self, value: int) -> None:
        self._lane_score = value
    
    @property
    def op_score_timeline(self) -> list[dict[str, float]]:
        """
        An `list[dict[str, float]]` representing your op score as the game progresses. Data points are provided every 60 seconds.
        """
        return self._op_score_timeline
    
    @op_score_timeline.setter
    def op_score_timeline(self, value: list[dict[str, float]]) -> None:
        self._op_score_timeline = value
    
    @property
    def op_score_timeline_analysis(self) -> dict[str, str]:
        """
        An `dict[str, str]` representing the timeline analysis
        """
        return self._op_score_timeline_analysis
    
    @op_score_timeline_analysis.setter
    def op_score_timeline_analysis(self, value: dict[str, str]) -> None:
        self._op_score_timeline_analysis = value
    

class GameStats:
    """
    Represents a player's game performance metrics.\n
    
    ### Properties:
        `is_win: bool` - Whether the game was won\n
        `champion_kill: int` - Number of champion kills\n
        `champion_first: bool` - Whether the first champion kill was achieved\n
        `inhibitor_kill: int` - Number of inhibitor kills\n
        `inhibitor_first: bool` - Whether the first inhibitor kill was achieved\n
        `rift_herald_kill: int` - Number of Rift Herald kills\n
        `rift_herald_first: bool` - Whether the first Rift Herald kill was achieved\n
        `dragon_kill: int` - Number of dragon kills\n
        `dragon_first: bool` - Whether the first dragon kill was achieved\n
        `baron_kill: int` - Number of Baron kills\n
        `baron_first: bool` - Whether the first Baron kill was achieved\n
        `tower_kill: int` - Number of tower kills\n
        `tower_first: bool` - Whether the first tower kill was achieved\n
        `horde_kill: int` - Number of horde kills\n
        `horde_first: bool` - Whether the first horde kill was achieved\n
        `is_remake: bool` - Whether the game was a remake\n
        `death: int` - Number of deaths\n
        `assist: int` - Number of assists\n
        `gold_earned: int` - Total gold earned\n
        `kill: int` - Number of kills\n
    """
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
    """
    Represents a game's summary including key statistics and banned champions.\n
    
    ### Properties:
        `key: str` - Unique identifier for the game\n
        `game_stat: GameStats` - Detailed statistics of the game\n
        `banned_champions: list` - List of banned champions in the game\n
    """
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
