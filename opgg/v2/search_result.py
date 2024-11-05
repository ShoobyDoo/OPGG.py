from box import Box
from typing import Any


class SearchResult(Box):
    id: int
    summoner_id: str
    acct_id: str
    puuid: str
    game_name: str
    tagline: str
    name: str
    internal_name: str
    profile_image_url: str
    level: int
    updated_at: str # TODO: datetime object conversion?
    renewable_at: str # TODO: datetime object conversion?
    revision_at: str # TODO: datetime object conversion?
    solo_tier_info: Any # unsure of type...
    team_info: Any
