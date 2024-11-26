# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : ShoobyDoo
# Date    : 2023-07-05
# License : BSD-3-Clause


from datetime import datetime
from opgg.v1.params import By


class Passive:
    """
    Represents a champion's passive ability.\n
    
    ### Properties:
        `name: str` - Name of the passive\n
        `description: str` - Description of the passive\n
        `image_url: str` - URL to the passive image\n
        `video_url: str` - URL to the passive video\n
    """
    def __init__(self,
                 name: str,
                 description: str,
                 image_url: str,
                 video_url: str) -> None:
        self._name = name
        self._description = description 
        self._image_url = image_url
        self._video_url = video_url

    @property
    def name(self) -> str:
        """
        A `str` representing the name of the passive ability.
        """
        return self._name
    
    @property
    def description(self) -> str:
        """
        A `str` representing the description of the passive ability.
        """
        return self._description
    
    @property
    def image_url(self) -> str:
        """
        A `str` representing the URL to the passive image.
        """
        return self._image_url
    
    @property
    def video_url(self) -> str:
        """
        A `str` representing the URL to the passive video.
        """
        return self._video_url
    

class Spell:
    """
    Represents a champion's spell.\n
    
    ### Properties:
        `key: str` - Key of the spell\n
        `name: str` - Name of the spell\n
        `description: str` - Description of the spell\n
        `max_rank: int` - Max rank of the spell\n
        `range_burn: list` - Range of the spell\n
        `cooldown_burn: list` - Cooldowns of the spell\n
        `cooldown_burn_float: list[float]` - Cooldowns of the spell as floats\n
        `cost_burn: list` - Cost of the spell\n
        `tooltip: str` - Tooltip of the spell\n
        `image_url: str` - URL to the spell image\n
        `video_url: str` - URL to the spell video\n
    """
    def __init__(self,
                 key: str,
                 name: str,
                 description: str,
                 max_rank: int,
                 range_burn: list,
                 cooldown_burn: list,
                 cooldown_burn_float: list[float],
                 cost_burn: list,
                 tooltip: str,
                 image_url: str,
                 video_url: str) -> None:
        self._key = key
        self._name = name
        self._description = description
        self._max_rank = max_rank
        self._range_burn = range_burn
        self._cooldown_burn = cooldown_burn
        self._cooldown_burn_float = cooldown_burn_float
        self._cost_burn = cost_burn
        self._tooltip = tooltip
        self._image_url = image_url
        self._video_url = video_url

    @property
    def key(self) -> str:
        """
        A `str` representing the keybind of the spell. (Q, W, E, R)
        """
        return self._key
    
    @property
    def name(self) -> str:
        """
        A `str` representing the name of the spell.
        """
        return self._name
    
    @property
    def description(self) -> str:
        """
        A `str` representing the description of the spell.
        """
        return self._description
    
    @property
    def max_rank(self) -> int:
        """
        An `int` representing the max rank of the spell.
        """
        return self._max_rank
    
    @property
    def range_burn(self) -> list:
        """
        A `list[int]` representing the range(s) of the spell at each rank.
        """
        return self._range_burn
    
    @property
    def cooldown_burn(self) -> list:
        """
        A `list[int]` representing the cooldown(s) of the spell at each rank.
        """
        return self._cooldown_burn
    
    @property
    def cooldown_burn_float(self) -> list[float]:
        """
        A `list[float]` representing the cooldown(s) of the spell at each rank in floating point numbers. (More precise)
        """
        return self._cooldown_burn
    
    @property
    def cost_burn(self) -> list:
        """
        A `list[int]` representing the cost(s) of the spell at each rank.
        """
        return self._cost_burn
    
    @property
    def tooltip(self) -> str:
        """
        A `str` representing the tooltip of the spell.
        """
        return self._tooltip
    
    @property
    def image_url(self) -> str:
        """
        A `str` representing the URL to the spell's image.
        """
        return self._image_url
    
    @property
    def video_url(self) -> str:
        """
        A `str` representing the URL to a video of the spell in use.
        """
        return self._video_url
    
    def __repr__(self) -> str:
        return f"Skill({self.key}: {self.name})"


class Price:
    """
    Represents a price.\n
    
    ### Properties:
        `currency: str` - Currency of the price\n
        `cost: int` - Cost of the price\n
    """
    def __init__(self,
                 currency: str,
                 cost: int) -> None:
        self._currency = currency
        self._cost = cost
    
    @property
    def currency(self) -> str:
        """
        A `str` representing the currency of the price. (BE, RP)
        """
        return self._currency
    
    @property
    def cost(self) -> int:
        """
        An `int` representing the cost of the price.
        """
        return self._cost
    
    def __repr__(self) -> str:
        return f"Price({self.currency}: {self.cost})"


class Skin:
    """
    Represents a skin for a champion.\n
    
    ### Properties:
        `id: int` - ID of the skin\n
        `champion_id: int` - ID of the champion the skin belongs to\n
        `name: str` - Name of the skin\n
        `centered_image: str` - URL to the centered image of the skin\n
        `skin_video_url: str` - URL to the skin video\n
        `prices: list[Price]` - List of prices for the skin\n
        `sales: list` - List of sales for the skin. Defaults to None.\n
        `release_date: datetime` - Release date of the skin\n
    """
    def __init__(self,
                 id: int,
                 champion_id: int,
                 name: str,
                 centered_image: str,
                 skin_video_url: str, 
                 prices: list[Price],
                 release_date: datetime,
                 sales = None) -> None:
        self._id = id
        self._champion_id = champion_id
        self._name = name
        self._centered_image = centered_image 
        self._skin_video_url = skin_video_url 
        self._prices = prices 
        self._sales = sales
        self._release_date = release_date
    
    @property
    def id(self) -> int:
        """
        An `int` representing the ID of the skin.
        """
        return self._id
     
    @property
    def champion_id(self) -> int:
        """
        An `int` representing the ID of the champion the skin belongs to.
        """
        return self._champion_id
     
    @property
    def name(self) -> str:
        """
        A `str` representing the name of the skin.
        """
        return self._name
    
    @property
    def centered_image(self) -> str:
        """
        A `str` representing the URL to the centered image of the skin.
        """
        return self._centered_image
     
    @property
    def skin_video_url(self) -> str:
        """
        A `str` representing the URL to the skin video.
        """
        return self._skin_video_url
    
    @property
    def prices(self) -> list[Price]:
        """
        A `list[Price]` objects representing the prices of the skin.
        """
        return self._prices
    
    @property
    def sales(self) -> list:
        """
        A `list` representing the sales of the skin. Defaults to None.\n
        
        Note: This gets returned by the API, but all values I tested returned were null/none
        """
        return self._sales         
    
    @property
    def release_date(self) -> datetime:
        """
        A `datetime` object representing the release date of the skin
        """
        return self._release_date
    
    def __repr__(self) -> str:
        return f"Skin({self.name})"


class Champion:
    """
    Represents a champion.\n
    
    ### Properties:
        `id: int` - ID of the champion\n
        `key: str` - Key of the champion\n
        `name: str` - Name of the champion\n
        `image_url: str` - URL to the champion image\n
        `evolve: list` - List of evolutions for the champion\n
        `partype: str` - Resource used by champion to cast spells\n
        `passive: Passive` - Passive object for the champion\n
        `spells: list[Spell]` - List of Spell objects for the champion\n
        `skins: list[Skin]` - List of Skin objects for the champion\n
    """
    def __init__(self,
                 id: int,
                 key: str,
                 name: str,
                 image_url: str,
                 evolve: list,
                 partype: str,
                 passive: Passive,
                 spells: list[Spell],
                 skins: list[Skin]) -> None:
        self._id = id
        self._key = key
        self._name = name
        self._image_url = image_url
        self._evolve = evolve
        self._partype = partype
        self._passive = passive
        self._spells = spells
        self._skins = skins
        
    @property
    def id(self) -> int:
        """
        An `int` representing the ID of the champion.
        """
        return self._id
     
    @property
    def key(self) -> str:
        """
        A `str` representing the key of the champion.
        """
        return self._key
    
    @property
    def name(self) -> str:
        """
        A `str` representing the name of the champion.
        """
        return self._name
    
    @property
    def image_url(self) -> str:
        """
        A `str` representing the URL to the champion image.
        """
        return self._image_url
    
    @property
    def evolve(self) -> list:
        """
        A `list` representing the evolutions of the champion.
        
        Note: 99% of the time this is an empty list.
        """
        return self._evolve
    
    @property
    def partype(self) -> str:
        """
        A `str` representing the resource type the champion uses to cast spells. (Mana, Energy, etc.)
        """
        return self._partype
    
    @property
    def passive(self) -> Passive:
        """
        A `Passive` object representing the passive ability of the champion.
        """
        return self._passive
    
    @property
    def spells(self) -> list[Spell]:
        """
        A list[Spell] objects representing the spells of the champion.
        """
        return self._spells
    
    @property
    def skins(self) -> list[Skin]:
        """
        A `list[Skin]` objects representing the skins of the champion.
        """
        return self._skins


    def get_cost_by(self, by: By = By.BLUE_ESSENCE) -> int | None:
        """
        Get the cost of the champion.
        
        ### Args:
            by : `By`
                The currency to get the cost in. Defaults to `By.BLUE_ESSENCE`.
        """
        # Get the cost of the champion in either blue essence or riot points
        by = "IP" if by == By.BLUE_ESSENCE else by.upper()
        
        for skin in self.skins:
            if skin.prices is not None:
                for price in skin.prices:
                    if price.currency == by:
                        return price.cost
            else:
                return None
        
        
    def __repr__(self) -> str:
        return f"Champion(name={self.name})"


class ChampionStats:
    """
    Represents the stats of the user on a given champion.\n
    
    ### Properties:
        `champion: Champion` - Champion object\n
        `id: int` - Unique identifier for the stats\n
        `play: int` - Number of games played\n
        `win: int` - Number of games won\n
        `lose: int` - Number of games lost\n
        `kill: int` - Number of kills\n
        `death: int` - Number of deaths\n
        `assist: int` - Number of assists\n
        `gold_earned: int` - Amount of gold earned\n
        `minion_kill: int` - Number of minions killed\n
        `turret_kill: int` - Number of turrets killed\n
        `neutral_minion_kill: int` - Number of neutral minions killed\n
        `damage_dealt: int` - Amount of damage dealt\n
        `damage_taken: int` - Amount of damage taken\n
        `physical_damage_dealt: int` - Amount of physical damage dealt\n
        `magic_damage_dealt: int` - Amount of magic damage dealt\n
        `most_kill: int` - Most kills in a game\n
        `max_kill: int` - Max kills in a game\n
        `max_death: int` - Max deaths in a game\n
        `double_kill: int` - Number of double kills\n
        `triple_kill: int` - Number of triple kills\n
        `quadra_kill: int` - Number of quadra kills\n
        `penta_kill: int` - Number of penta kills\n
        `game_length_second: int` - Total game length in seconds\n
        `inhibitor_kills: int` - Number of inhibitor kills\n
        `sight_wards_bought_in_game: int` - Number of sight wards bought in game\n
        `vision_wards_bought_in_game: int` - Number of vision wards bought in game\n
        `vision_score: int` - Vision score\n
        `wards_placed: int` - Number of wards placed\n
        `wards_killed: int` - Number of wards killed\n
        `heal: int` - Amount of healing done\n
        `time_ccing_others: int` - Time spent crowd-controlling others\n
        `op_score: int` - Overall performance score\n
        `is_max_in_team_op_score: int` - Indicator if the max score in team is OP\n
        `physical_damage_taken: int` - Amount of physical damage taken\n
        `damage_dealt_to_champions: int` - Total damage dealt to champions\n
        `physical_damage_dealt_to_champions: int` - Physical damage dealt to champions\n
        `magic_damage_dealt_to_champions: int` - Magic damage dealt to champions\n
        `damage_dealt_to_objectives: int` - Damage dealt to objectives\n
        `damage_dealt_to_turrets: int` - Damage dealt to turrets\n
        `damage_self_mitigated: int` - Amount of damage self-mitigated\n
        `max_largest_multi_kill: int` - Maximum largest multi-kill\n
        `max_largest_critical_strike: int` - Maximum largest critical strike\n
        `max_largest_killing_spree: int` - Maximum largest killing spree\n
        `snowball_throws: int` - Number of snowball throws\n
        `snowball_hits: int` - Number of snowball hits\n
    """
    def __init__(self,
                 champion: Champion,
                 id: int,
                 play: int,
                 win: int,
                 lose: int,
                 kill: int,
                 death: int,
                 assist: int,
                 gold_earned: int,
                 minion_kill: int,
                 turret_kill: int,
                 neutral_minion_kill: int,
                 damage_dealt: int,
                 damage_taken: int,
                 physical_damage_dealt: int,
                 magic_damage_dealt: int,
                 most_kill: int,
                 max_kill: int,
                 max_death: int,
                 double_kill: int,
                 triple_kill: int,
                 quadra_kill: int,
                 penta_kill: int,
                 game_length_second: int,
                 inhibitor_kills: int,
                 sight_wards_bought_in_game: int,
                 vision_wards_bought_in_game: int,
                 vision_score: int,
                 wards_placed: int,
                 wards_killed: int,
                 heal: int,
                 time_ccing_others: int,
                 op_score: int,
                 is_max_in_team_op_score: int,
                 physical_damage_taken: int,
                 damage_dealt_to_champions: int,
                 physical_damage_dealt_to_champions: int,
                 magic_damage_dealt_to_champions: int,
                 damage_dealt_to_objectives: int,
                 damage_dealt_to_turrets: int,
                 damage_self_mitigated: int,
                 max_largest_multi_kill: int,
                 max_largest_critical_strike: int,
                 max_largest_killing_spree: int,
                 snowball_throws: int,
                 snowball_hits: int) -> None:
        self._champion = champion
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
        
        self._inhibitor_kills = inhibitor_kills
        self._sight_wards_bought_in_game = sight_wards_bought_in_game
        self._vision_wards_bought_in_game = vision_wards_bought_in_game
        self._vision_score = vision_score
        self._wards_placed = wards_placed
        self._wards_killed = wards_killed
        self._heal = heal
        self._time_ccing_others = time_ccing_others
        self._op_score = op_score
        self._is_max_in_team_op_score = is_max_in_team_op_score
        self._physical_damage_taken = physical_damage_taken
        self._damage_dealt_to_champions = damage_dealt_to_champions
        self._physical_damage_dealt_to_champions = physical_damage_dealt_to_champions
        self._magic_damage_dealt_to_champions = magic_damage_dealt_to_champions
        self._damage_dealt_to_objectives = damage_dealt_to_objectives
        self._damage_dealt_to_turrets = damage_dealt_to_turrets
        self._damage_self_mitigated = damage_self_mitigated
        self._max_largest_multi_kill = max_largest_multi_kill
        self._max_largest_critical_strike = max_largest_critical_strike
        self._max_largest_killing_spree = max_largest_killing_spree
        self._snowball_throws = snowball_throws
        self._snowball_hits = snowball_hits        
        
    @property
    def champion(self) -> Champion:
        """
        A `Champion` object representing the champion.
        """
        return self._champion
    
    @property
    def id(self) -> int:
        """
        An `int` representing the champion id
        """
        return self._id
    
    @property
    def play(self) -> int:
        """
        An `int` representing the number of games played.
        """
        return self._play

    @property
    def win(self) -> int:
        """
        An `int` representing the number of games won.
        """
        return self._win

    @property
    def lose(self) -> int:
        """
        An `int` representing the number of games lost.
        """
        return self._lose

    @property
    def kill(self) -> int:
        """
        An `int` representing the number of kills.
        """
        return self._kill

    @property
    def death(self) -> int:
        """
        An `int` representing the number of deaths.
        """
        return self._death

    @property
    def assist(self) -> int:
        """
        An `int` representing the number of assists.
        """
        return self._assist

    @property
    def gold_earned(self) -> int:
        """
        An `int` representing the amount of gold earned.
        """
        return self._gold_earned

    @property
    def minion_kill(self) -> int:
        """
        An `int` representing the number of minions killed.
        """
        return self._minion_kill
 
    @property
    def turret_kill(self) -> int:
        """
        An `int` representing the number of turrets killed.
        """
        return self._turret_kill

    @property
    def neutral_minion_kill(self) -> int:
        """
        An `int` representing the number of neutral minions killed.
        """
        return self._neutral_minion_kill

    @property
    def damage_dealt(self) -> int:
        """
        An `int` representing the amount of damage dealt.
        """
        return self._damage_dealt
        
    @property
    def damage_taken(self) -> int:
        """
        An `int` representing the amount of damage taken.
        """
        return self._damage_taken
        
    @property
    def physical_damage_dealt(self) -> int:
        """
        An `int` representing the amount of physical damage dealt.
        """
        return self._physical_damage_dealt
        
    @property
    def magic_damage_dealt(self) -> int:
        """
        An `int` representing the amount of magic damage dealt.
        """
        return self._magic_damage_dealt

    @property
    def most_kill(self) -> int:
        """
        An `int` representing the most kills in a game.
        """
        return self._most_kill
    
    @property
    def max_kill(self) -> int:
        """
        An `int` representing the max kills in a game.
        """
        return self._max_kill
    
    @property
    def max_death(self) -> int:
        """
        An `int` representing the max deaths in a game.
        """
        return self._max_death
    
    @property
    def double_kill(self) -> int:
        """
        An `int` representing the number of double kills.
        """
        return self._double_kill
    
    @property
    def triple_kill(self) -> int:
        """
        An `int` representing the number of triple kills.
        """
        return self._triple_kill
    
    @property
    def quadra_kill(self) -> int:
        """
        An `int` representing the number of quadra kills.
        """
        return self._quadra_kill
    
    @property
    def penta_kill(self) -> int:
        """
        An `int` representing the number of penta kills.
        """
        return self._penta_kill
    
    @property
    def game_length_second(self) -> int:
        """
        An `int` representing the total game length in seconds.
        """
        return self._game_length_second
    
    @property
    def kda(self) -> float:
        """
        A `float` representing the KDA of the champion.
        """
        return (self._kill + self._assist) / self._death if self._death != 0 else 0

    @property
    def win_rate(self) -> float:
        """
        A `float` representing the win rate of the champion.
        """
        return round(float((self._win / self._play) * 100), 2) if self._play != 0 else 0

    @property
    def inhibitor_kills(self) -> int:
        """
        An `int` representing the number of inhibitor kills.
        """
        return self._inhibitor_kills

    @property
    def sight_wards_bought_in_game(self) -> int:
        """
        An `int` representing the number of sight wards bought in game.
        """
        return self._sight_wards_bought_in_game

    @property
    def vision_wards_bought_in_game(self) -> int:
        """
        An `int` representing the number of vision wards bought in game.
        """
        return self._vision_wards_bought_in_game

    @property
    def vision_score(self) -> int:
        """
        An `int` representing the vision score.
        """
        return self._vision_score

    @property
    def wards_placed(self) -> int:
        """
        An `int` representing the number of wards placed.
        """
        return self._wards_placed

    @property
    def wards_killed(self) -> int:
        """
        An `int` representing the number of wards killed.
        """
        return self._wards_killed

    @property
    def heal(self) -> int:
        """
        An `int` representing the amount of healing done.
        """
        return self._heal

    @property
    def time_ccing_others(self) -> int:
        """
        An `int` representing the time spent crowd-controlling others.
        """
        return self._time_ccing_others

    @property
    def op_score(self) -> int:
        """
        An `int` representing the OP score.
        """
        return self._op_score

    @property
    def is_max_in_team_op_score(self) -> bool:
        """
        A `bool` indicating if the player has the maximum OP score in the team.
        """
        return self._is_max_in_team_op_score

    @property
    def physical_damage_taken(self) -> int:
        """
        An `int` representing the physical damage taken.
        """
        return self._physical_damage_taken

    @property
    def damage_dealt_to_champions(self) -> int:
        """
        An `int` representing the total damage dealt to champions.
        """
        return self._damage_dealt_to_champions

    @property
    def physical_damage_dealt_to_champions(self) -> int:
        """
        An `int` representing the physical damage dealt to champions.
        """
        return self._physical_damage_dealt_to_champions

    @property
    def magic_damage_dealt_to_champions(self) -> int:
        """
        An `int` representing the magic damage dealt to champions.
        """
        return self._magic_damage_dealt_to_champions

    @property
    def damage_dealt_to_objectives(self) -> int:
        """
        An `int` representing the damage dealt to objectives.
        """
        return self._damage_dealt_to_objectives

    @property
    def damage_dealt_to_turrets(self) -> int:
        """
        An `int` representing the damage dealt to turrets.
        """
        return self._damage_dealt_to_turrets

    @property
    def damage_self_mitigated(self) -> int:
        """
        An `int` representing the damage self mitigated.
        """
        return self._damage_self_mitigated

    @property
    def max_largest_multi_kill(self) -> int:
        """
        An `int` representing the maximum largest multi-kill.
        """
        return self._max_largest_multi_kill

    @property
    def max_largest_critical_strike(self) -> int:
        """
        An `int` representing the maximum largest critical strike.
        """
        return self._max_largest_critical_strike

    @property
    def max_largest_killing_spree(self) -> int:
        """
        An `int` representing the maximum largest killing spree.
        """
        return self._max_largest_killing_spree

    @property
    def snowball_throws(self) -> int:
        """
        An `int` representing the number of snowball throws.
        """
        return self._snowball_throws

    @property
    def snowball_hits(self) -> int:
        """
        An `int` representing the number of snowball hits.
        """
        return self._snowball_hits


    def __repr__(self) -> str:
        return  f"ChampionStats(champion={self.champion}, win={self.win} / lose={self.lose} (winrate: {self.win_rate}%), kda={round(self.kda, 2)})"