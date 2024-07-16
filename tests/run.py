import os
import sys

# Add module to path to reference opgg subdir from here.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from opgg.game import GameStats, Stats, Team
from opgg.opgg import OPGG

from opgg.champion import Champion, Passive, Spell, Price, Skin, ChampionStats
from opgg.summoner import Game, Participant, Summoner
from opgg.league_stats import LeagueStats, Tier, QueueInfo
from opgg.season import Season, SeasonInfo
from opgg.utils import Utils

from opggtests import OPGGTests


def main():    
    # Doublelift summoner id just to have an active user
    opgg = OPGG("AVCaop7DsXMxYghWRgonI__cn6cKD9EssfdNn-A8NhKvW2U")
    
    page_props = Utils.get_page_props("Doublelift")
    
    # Call page props once so it doesnt have to be called each time 
    summoner = opgg.get_summoner(return_content_only=True)

    # Get a game object
    game = opgg.get_recent_games(results=1, return_content_only=True)
    
    objects_to_test = [
        # champion.py
        Champion, 
        Passive,
        Spell,
        Price,
        Skin,
        ChampionStats,
        
        # game.py
        Stats,
        GameStats,
        Team,
        
        # league_stats.py
        LeagueStats,
        Tier,
        QueueInfo,
        
        # season.py
        Season, 
        SeasonInfo,
        
        # summoner.py
        Summoner,
        Participant,
        Game,
    ]
    
    opgg_response_data = [
        page_props['championsById']['1'],                               # Champion (1 = Annie)
        page_props['championsById']['1']['passive'],                    # Passive
        page_props['championsById']['1']['spells'][0],                  # Spell (0 index is Q)
        page_props['championsById']['1']['skins'][2]['prices'][0],      # Price (2 index is skin with price)
        page_props['championsById']['1']['skins'][0],                   # Skin (0 index is first skin, default)
        summoner['summoner']['most_champions']['champion_stats'][0],    # ChampionStats
        
        game[0]["participants"][0]["stats"],                            # Stats
        game[0]["teams"][0]["game_stat"],                               # GameStats
        game[0]["teams"][0],                                            # Team
        
        summoner["summoner"]["league_stats"][0],                        # LeagueStats
        summoner["summoner"]["previous_seasons"][0]["tier_info"],       # Tier
        summoner["summoner"]["league_stats"][0]["queue_info"],          # QueueInfo
        
        summoner["summoner"]["previous_seasons"][0],                    # Season
        page_props['seasons'][0],                                       # SeasonInfo
        
        summoner["summoner"],                                           # Summoner
        game[0]["participants"][0],                                     # Participant
        game[0],                                                        # Game
    ]
    
    results = OPGGTests.verify_objects(objects_to_test, opgg_response_data)
    
    test_count = len(results)
    passed_count = sum(results)
    failed_count = test_count - passed_count
    
    print("========================= SUMMARY =========================")
    if not all(results):
        print("\nThe following objects require attention:\n")
        [print(f"-> {obj.__name__}") for obj, result in zip(objects_to_test, results) if not result]

    print(f"\n{passed_count} of {test_count} total tests passed. {failed_count} tests failed.\n\n========================= SUMMARY =========================\n\n")
    

if __name__ == "__main__":
    main()
