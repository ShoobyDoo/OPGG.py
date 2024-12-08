from pydantic import BaseModel

from typing import Any, Optional
from datetime import datetime


class ChampionStats(BaseModel):
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
    double_kill: int = 0
    triple_kill: int = 0
    quadra_kill: int = 0
    penta_kill: int = 0
    vision_wards_bought_in_game: int = 0
    op_score: int
    snowball_throws: Optional[int] = None
    snowball_hits: Optional[int] = None

    @property
    def winrate(self) -> int:
        """`[Computed Property]` Returns the winrate percentage of the champion."""
        return round(self.win / self.play * 100) if self.play != 0 else 0


class MostChampions(BaseModel):
    game_type: str
    season_id: int
    year: Optional[int] = None
    play: int
    win: int
    lose: int
    champion_stats: list[ChampionStats]


class Price(BaseModel):
    currency: str
    cost: int


class Skin(BaseModel):
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


class Info(BaseModel):
    attack: int
    defense: int
    magic: int
    difficulty: int


class Stats(BaseModel):
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


class Passive(BaseModel):
    name: str
    description: str
    image_url: str
    video_url: str


class Spell(BaseModel):
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


class Evolve(BaseModel):
    key: str
    name: str
    image_url: str


class Champion(BaseModel):
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
