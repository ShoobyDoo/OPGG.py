from pydantic import BaseModel, Field

from typing import Any
from datetime import datetime


class ChampionStats(BaseModel):
    id: int | None = None
    play: int | None = None
    win: int | None = None
    lose: int | None = None
    game_length_second: int | None = None
    kill: int | None = None
    death: int | None = None
    assist: int | None = None
    gold_earned: int | None = None
    minion_kill: int | None = None
    neutral_minion_kill: int | None = None
    damage_taken: int | None = None
    damage_dealt_to_champions: int | None = None
    double_kill: int = 0
    triple_kill: int = 0
    quadra_kill: int = 0
    penta_kill: int = 0
    vision_wards_bought_in_game: int = 0
    op_score: int | None = None
    snowball_throws: int | None = None
    snowball_hits: int | None = None

    @property
    def winrate(self) -> int:
        """`[Computed Property]` Returns the winrate percentage of the champion."""
        return round(self.win / self.play * 100) if self.play and self.win else 0


class MostChampions(BaseModel):
    game_type: str | None = None
    season_id: int | None = None
    year: int | None = None
    play: int | None = None
    win: int | None = None
    lose: int | None = None
    champion_stats: list[ChampionStats] | None = Field(default_factory=list)


class Price(BaseModel):
    currency: str | None = None
    cost: int | None = None


class Skin(BaseModel):
    id: int | None = None
    champion_id: int | None = None
    name: str | None = None
    has_chromas: bool | None = None
    splash_image: str | None = None
    loading_image: str | None = None
    tiles_image: str | None = None
    centered_image: str | None = None
    skin_video_url: str | None = None
    prices: list[Price] | None = None
    sales: Any | None = None
    release_date: datetime | None = None


class Info(BaseModel):
    attack: int | None = None
    defense: int | None = None
    magic: int | None = None
    difficulty: int | None = None


class Stats(BaseModel):
    hp: float | None = None
    hpperlevel: float | None = None
    mp: float | None = None
    mpperlevel: float | None = None
    movespeed: float | None = None
    armor: float | None = None
    armorperlevel: float | None = None
    spellblock: float | None = None
    spellblockperlevel: float | None = None
    attackrange: float | None = None
    hpregen: float | None = None
    hpregenperlevel: float | None = None
    mpregen: float | None = None
    mpregenperlevel: float | None = None
    crit: float | None = None
    critperlevel: float | None = None
    attackdamage: float | None = None
    attackdamageperlevel: float | None = None
    attackspeed: float | None = None
    attackspeedperlevel: float | None = None


class Passive(BaseModel):
    name: str | None = None
    description: str | None = None
    image_url: str | None = None
    video_url: str | None = None


class Spell(BaseModel):
    key: str | None = None
    name: str | None = None
    description: str | None = None
    max_rank: int | None = None
    range_burn: list[int] | None = Field(default_factory=list)
    cooldown_burn: list[float] | None = Field(default_factory=list)
    cooldown_burn_float: list[float] | None = Field(default_factory=list)
    cost_burn: list[int] | None = Field(default_factory=list)
    tooltip: str | None = None
    image_url: str | None = None
    video_url: str | None = None


class Evolve(BaseModel):
    key: str | None = None
    name: str | None = None
    image_url: str | None = None


class Champion(BaseModel):
    id: int | None = None
    key: str | None = None
    name: str | None = None
    image_url: str | None = None
    evolve: list[Evolve] | None = None
    blurb: str | None = None
    title: str | None = None
    tags: list[str] | None = Field(default_factory=list)
    lore: str | None = None
    partype: str | None = None
    info: Info | None = None
    stats: Stats | None = None
    enemy_tips: list[str] | None = Field(default_factory=list)
    ally_tips: list[str] | None = Field(default_factory=list)
    skins: list[Skin] | None = Field(default_factory=list)
    passive: Passive | None = None
    spells: list[Spell] | None = Field(default_factory=list)
