import os
import sys

# Add module to path to reference opgg subdir from here.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from opgg.opgg import OPGG

from opgg.champion import Champion, Passive, Spell, Price, Skin, ChampionStats
from opgg.summoner import Game
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
    
    # DIFFERENTIATE BETWEEN MINOR AND MAJOR CATESTROPHIC ERRORS
    # IF MY OBJECT HAS ATTRIBUTES THAT ARE NO LONGER RETURNED BY PAGE PROPS, THIS IS MAJOR.
    # THIS WILL RESULT IN AN ERROR CONSTRUCTING THE OBJECT, AS IT WILL ERROR OUT WHEN IT 
    # TRIES TO SET THE ATTRIBUTE AND BRICK THE WHOLE OBJECT CREATION.
    objects_to_test = [
        Champion, 
        Passive,
        Spell,
        Price,
        Skin,
        ChampionStats,
         
        Game,
         
        #  LeagueStats,
        #  Tier,
        #  QueueInfo,
         
        #  Season, 
        #  SeasonInfo,
         
        #  Summoner
    ]
    
    results = OPGGTests.verify_objects(
        objects_to_test,
        
        # Champions by Id (1 = Annie)
        [
            page_props['championsById']['1'],                              # Champion
            page_props['championsById']['1']['passive'],                   # Passive
            page_props['championsById']['1']['spells'][0],                 # Spell (0 index is Q)
            page_props['championsById']['1']['skins'][2]['prices'][0],     # Price (2 index is skin with price)
            page_props['championsById']['1']['skins'][0],                  # Skin (0 index is first skin, default)
            summoner['summoner']['most_champions']['champion_stats'][0],   # ChampionStats
            game[0],                                                       # Game
            # page_props['seasonsById']
        ]
    )
    
    test_count = len(results)
    passed_count = sum(results)
    failed_count = test_count - passed_count
    
    print("========================= SUMMARY =========================\n")
    print("The following objects require attention:\n")
    [print(f"-> {obj.__name__}") for obj, result in zip(objects_to_test, results) if not result]

    print(f"\n{passed_count} of {test_count} total tests passed. {failed_count} tests failed.\n\n========================= SUMMARY =========================\n\n")
    

if __name__ == "__main__":
    main()
