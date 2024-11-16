from box import Box


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
    
    @property
    def winrate(self) -> float:
        """
        `[Computed Property]` Calculate the winrate as a percentage.

        Returns:
            `float`: Winrate percentage (0-100), or 0 if no games played
        """
        return round((self.win / self.play) * 100, 2) if self.play > 0 else 0.0