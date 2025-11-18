from pydantic import BaseModel, Field, field_validator

from typing import Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger("OPGG.py")


class ChampionStats(BaseModel):
    id: Optional[int] = None
    play: Optional[int] = None
    win: Optional[int] = None
    lose: Optional[int] = None
    game_length_second: Optional[int] = None
    kill: Optional[int] = None
    death: Optional[int] = None
    assist: Optional[int] = None
    gold_earned: Optional[int] = None
    minion_kill: Optional[int] = None
    neutral_minion_kill: Optional[int] = None
    damage_taken: Optional[int] = None
    damage_dealt_to_champions: Optional[int] = None
    double_kill: Optional[int] = 0
    triple_kill: Optional[int] = 0
    quadra_kill: Optional[int] = 0
    penta_kill: Optional[int] = 0
    vision_wards_bought_in_game: Optional[int] = 0
    op_score: Optional[int] = None
    snowball_throws: Optional[int] = None
    snowball_hits: Optional[int] = None

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in ChampionStats model")
        return v

    @property
    def winrate(self) -> int:
        """`[Computed Property]` Returns the winrate percentage of the champion."""
        return round(self.win / self.play * 100) if self.play and self.win else 0


class MostChampions(BaseModel):
    game_type: Optional[str] = None
    season_id: Optional[int] = None
    year: Optional[int] = None
    play: Optional[int] = None
    win: Optional[int] = None
    lose: Optional[int] = None
    champion_stats: Optional[list[ChampionStats]] = Field(default_factory=list)

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in MostChampions model")
        return v


class Price(BaseModel):
    currency: Optional[str] = None
    cost: Optional[int] = None

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in Price model")
        return v


class Skin(BaseModel):
    id: Optional[int] = None
    champion_id: Optional[int] = None
    name: Optional[str] = None
    has_chromas: Optional[bool] = None
    splash_image: Optional[str] = None
    loading_image: Optional[str] = None
    tiles_image: Optional[str] = None
    centered_image: Optional[str] = None
    skin_video_url: Optional[str] = None
    prices: Optional[list[Price]] = None
    sales: Optional[Any] = None
    release_date: Optional[datetime] = None

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in Skin model")
        return v


class Info(BaseModel):
    attack: Optional[int] = None
    defense: Optional[int] = None
    magic: Optional[int] = None
    difficulty: Optional[int] = None

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in Info model")
        return v


class Stats(BaseModel):
    hp: Optional[float] = None
    hpperlevel: Optional[float] = None
    mp: Optional[float] = None
    mpperlevel: Optional[float] = None
    movespeed: Optional[float] = None
    armor: Optional[float] = None
    armorperlevel: Optional[float] = None
    spellblock: Optional[float] = None
    spellblockperlevel: Optional[float] = None
    attackrange: Optional[float] = None
    hpregen: Optional[float] = None
    hpregenperlevel: Optional[float] = None
    mpregen: Optional[float] = None
    mpregenperlevel: Optional[float] = None
    crit: Optional[float] = None
    critperlevel: Optional[float] = None
    attackdamage: Optional[float] = None
    attackdamageperlevel: Optional[float] = None
    attackspeed: Optional[float] = None
    attackspeedperlevel: Optional[float] = None

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in Stats model")
        return v


class Passive(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in Passive model")
        return v


class Spell(BaseModel):
    key: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    max_rank: Optional[int] = None
    range_burn: Optional[list[int]] = Field(default_factory=list)
    cooldown_burn: Optional[list[float]] = Field(default_factory=list)
    cooldown_burn_float: Optional[list[float]] = Field(default_factory=list)
    cost_burn: Optional[list[int]] = Field(default_factory=list)
    tooltip: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in Spell model")
        return v


class Evolve(BaseModel):
    key: Optional[str] = None
    name: Optional[str] = None
    image_url: Optional[str] = None

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in Evolve model")
        return v


class Champion(BaseModel):
    id: Optional[int] = None
    key: Optional[str] = None
    name: Optional[str] = None
    image_url: Optional[str] = None
    evolve: Optional[list[Evolve]] = None
    blurb: Optional[str] = None
    title: Optional[str] = None
    tags: Optional[list[str]] = Field(default_factory=list)
    lore: Optional[str] = None
    partype: Optional[str] = None
    info: Optional[Info] = None
    stats: Optional[Stats] = None
    enemy_tips: Optional[list[str]] = Field(default_factory=list)
    ally_tips: Optional[list[str]] = Field(default_factory=list)
    skins: Optional[list[Skin]] = Field(default_factory=list)
    passive: Optional[Passive] = None
    spells: Optional[list[Spell]] = Field(default_factory=list)

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in Champion model")
        return v
