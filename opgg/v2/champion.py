from typing import Any
from box import Box
from datetime import datetime


class ChampionStats(Box):
    id: int
    play: int
    win: int
    lose: int
    game_length_second: int
    kill: int
    death: int
    assist: int
    gold_earned: int
    minion_kill: int
    neutral_minion_kill: int
    damage_taken: int
    damage_dealt_to_champions: int
    double_kill: int
    triple_kill: int
    quadra_kill: int
    penta_kill: int
    vision_wards_bought_in_game: int
    op_score: int
    snowball_throws: int
    snowball_hits: int


class MostChampions(Box):
    game_type: str
    season_id: int
    year: int | None
    play: int
    win: int
    lose: int
    champion_stats: list[ChampionStats]


class Price(Box):
    currency: str
    cost: int


class Skin(Box):
    id: int
    champion_id: int
    name: str
    has_chromas: bool
    splash_image: str
    loading_image: str
    tiles_image: str
    centered_image: str
    skin_video_url: str | None
    prices: list[Price] | None
    sales: Any | None  # We don't have information about the structure of sales
    release_date: datetime | None


class Info(Box):
    attack: int
    defense: int
    magic: int
    difficulty: int


class Stats(Box):
    hp: float
    hpperlevel: float
    mp: float
    mpperlevel: float
    movespeed: float
    armor: float
    armorperlevel: float
    spellblock: float
    spellblockperlevel: float
    attackrange: float
    hpregen: float
    hpregenperlevel: float
    mpregen: float
    mpregenperlevel: float
    crit: float
    critperlevel: float
    attackdamage: float
    attackdamageperlevel: float
    attackspeed: float
    attackspeedperlevel: float


class Passive(Box):
    name: str
    description: str
    image_url: str
    video_url: str


class Spell(Box):
    key: str
    name: str
    description: str
    max_rank: int
    range_burn: list[int]
    cooldown_burn: list[float]
    cooldown_burn_float: list[float]
    cost_burn: list[int]
    tooltip: str
    image_url: str
    video_url: str


class Evolve(Box):
    key: str
    name: str
    image_url: str


class Champion(Box):
    id: int
    key: str
    name: str
    image_url: str
    evolve: list[Evolve] | None
    blurb: str
    title: str
    tags: list[str]
    lore: str
    partype: str
    info: Info
    stats: Stats
    enemy_tips: list[str]
    ally_tips: list[str]
    skins: list[Skin]
    passive: Passive
    spells: list[Spell]
