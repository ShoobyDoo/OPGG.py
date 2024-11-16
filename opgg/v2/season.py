from box import Box


class TierInfo(Box):
    tier: str
    division: int
    lp: int
    level: int | None
    tier_image_url: str
    border_image_url: str


class RankInfo(Box):
    tier: str
    division: int
    lp: int


class RankEntry(Box):
    game_type: str
    rank_info: RankInfo
    created_at: str  # TODO: datetime object conversion?


class Season(Box):
    season_id: int
    tier_info: TierInfo
    rank_entries: list[RankEntry]
    created_at: str  # TODO: datetime object conversion?
