from typing import Any
from box import Box

from opgg.v2.season import TierInfo


class QueueInfo(Box):
    id: int
    queue_translate: str
    game_type: str


class League(Box):
    queue_info: QueueInfo
    game_type: str
    tier_info: TierInfo
    win: int
    lose: int
    is_hot_streak: bool
    is_fresh_blood: bool
    is_veteran: bool
    is_inactive: bool
    series: Any | None  # unsure of type...
    updated_at: str  # TODO: datetime object conversion?
