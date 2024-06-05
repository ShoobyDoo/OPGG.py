[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FShoobyDoo%2FOPGG.py&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23DDDDDD&title=visits&edge_flat=false)](https://hits.seeyoufarm.com)

# OPGG.py
An unofficial Python library for accessing OPGG data.
#### You can view the current active developments on the [OPGG.py Project](https://github.com/users/ShoobyDoo/projects/2) page

## Prerequisites

* [Python 3.11](https://www.python.org/downloads/) 
    
    *Note: Will likely work on versions slightly older or newer*

## Installation

### Automatic

This library is available as a [pip package](https://pypi.org/project/opgg.py/) and can be installed via the following command:
```
py -m pip install opgg.py
```

### Manual

#### Dependencies
* [requests](https://pypi.org/project/requests/)
* [beautifulsoup4](https://pypi.org/project/beautifulsoup4/)

Alternatively, you can use the provided requirements.txt to install the required libraries by running the following command: <br>
```
py -m pip install -r requirements.txt
```

## Usage / Basic Example

### Importing the library
```python
from opgg.opgg import OPGG
from opgg.summoner import Summoner
from opgg.params import Region


def main():    
    opgg_obj = OPGG()

    summoner: Summoner = opgg_obj.search("Stefty#EUW", Region.EUW)
    print(summoner)


if __name__ == "__main__":
    main()
```

### Output
**Important Note:** The information returned below is a summary view with the most important parts of each object shown "at a glance". 
Many of the objects have several additional properties that can be accessed by referencing the object in code.
```
[Summoner: Stefty]
--------------------------------------------------------------------------------
Id                          (int) | 33091204
Summoner Id                 (str) | 3ki-WOsTh1hB-UBfvHUxgPp1sD5bBP4YOLNEhD9XV0GI3jc
Account Id                  (str) | k1NgnQp8jIex9pYBIAZBhjwQbQfH4tejH2OOpzjbBA8U5A
Puuid                       (str) | DpLDhMgenwpV0MpV-yPor3rDoeNk3JoyZZ6_Mj1ezDuMPg0Zvcxm07Vyf8GlWPVhLTgAI_KgFgVcPw
Game Name                   (str) | Stefty
Tagline                     (str) | EUW
Name                        (str) | Stefty
Internal Name               (str) | stefty
Profile Image Url           (str) | https://opgg-static.akamaized.net/meta/images/profile_icons/profileIcon6295.jpg
Level                       (int) | 535
Updated At             (datetime) | 2024-05-31T10:30:28+09:00
Renewable At           (datetime) | 2024-05-31T10:32:28+09:00
Previous Seasons         (Season) | [List (12)]
                                  | Season(season=SeasonInfo(display_value=2024, is_preseason=0), tier_info=Tier(tier=EMERALD, division=2, lp=37))
                                  | Season(season=SeasonInfo(display_value=2023, is_preseason=0), tier_info=Tier(tier=EMERALD, division=4, lp=0))
                                  | Season(season=SeasonInfo(display_value=2023, is_preseason=0), tier_info=Tier(tier=PLATINUM, division=3, lp=0))
                                  | Season(season=SeasonInfo(display_value=2022, is_preseason=0), tier_info=Tier(tier=PLATINUM, division=4, lp=32))
                                  | Season(season=SeasonInfo(display_value=2021, is_preseason=0), tier_info=Tier(tier=PLATINUM, division=4, lp=0))
                                  | Season(season=SeasonInfo(display_value=2020, is_preseason=0), tier_info=Tier(tier=PLATINUM, division=3, lp=57))
                                  | Season(season=SeasonInfo(display_value=9, is_preseason=0), tier_info=Tier(tier=PLATINUM, division=4, lp=53))
                                  | Season(season=SeasonInfo(display_value=8, is_preseason=0), tier_info=Tier(tier=PLATINUM, division=5, lp=14))
                                  | Season(season=SeasonInfo(display_value=7, is_preseason=0), tier_info=Tier(tier=GOLD, division=5, lp=45))
                                  | Season(season=SeasonInfo(display_value=6, is_preseason=0), tier_info=Tier(tier=GOLD, division=5, lp=19))
                                  | Season(season=SeasonInfo(display_value=5, is_preseason=0), tier_info=Tier(tier=SILVER, division=2, lp=98))
                                  | Season(season=SeasonInfo(display_value=4, is_preseason=0), tier_info=Tier(tier=SILVER, division=4, lp=0))
League Stats        (LeagueStats) | [List (3)]
                                  | LeagueStats(queue_info=QueueInfo(game_type=SOLORANKED), tier_info=Tier(tier=EMERALD, division=4, lp=19), win=9 / lose=14 (winrate: 39.13%))
                                  | LeagueStats(queue_info=QueueInfo(game_type=FLEXRANKED), tier_info=Tier(tier=EMERALD, division=4, lp=0), win=6 / lose=10 (winrate: 37.5%))
                                  | LeagueStats(queue_info=QueueInfo(game_type=ARENA), tier_info=Tier(tier=UNRANKED, division=0, lp=0), win=0 / lose=0 (winrate: 0%))
Most Champions       (ChampStats) | [List (10)]
                                  | ChampionStats(champion=Champion(name=Sylas), win=4 / lose=7 (winrate: 36.36%), kda=2.41)
                                  | ChampionStats(champion=Champion(name=Jhin), win=4 / lose=5 (winrate: 44.44%), kda=3.37)
                                  | ChampionStats(champion=Champion(name=Garen), win=2 / lose=0 (winrate: 100.0%), kda=1.71)
                                  | ChampionStats(champion=Champion(name=Jarvan IV), win=1 / lose=1 (winrate: 50.0%), kda=6.75)
                                  | ChampionStats(champion=Champion(name=Nilah), win=1 / lose=1 (winrate: 50.0%), kda=2.18)
                                  | ChampionStats(champion=Champion(name=Viego), win=0 / lose=2 (winrate: 0.0%), kda=2.0)
                                  | ChampionStats(champion=Champion(name=Kai'Sa), win=0 / lose=2 (winrate: 0.0%), kda=2.5)
                                  | ChampionStats(champion=Champion(name=Nidalee), win=0 / lose=2 (winrate: 0.0%), kda=2.64)
                                  | ChampionStats(champion=Champion(name=Jinx), win=1 / lose=0 (winrate: 100.0%), kda=22.0)
                                  | ChampionStats(champion=Champion(name=Veigar), win=1 / lose=0 (winrate: 100.0%), kda=2.71)
Recent Game Stats          (Game) | [List (10)]
                                  | Game(champion=Champion(name=Veigar), kill=3, death=9, assist=7, position=ADC, is_win=False)
                                  | Game(champion=Champion(name=Jinx), kill=9, death=11, assist=12, position=ADC, is_win=False)
                                  | Game(champion=Champion(name=Ekko), kill=3, death=1, assist=4, position=JUNGLE, is_win=True)
                                  | Game(champion=Champion(name=Ekko), kill=14, death=8, assist=2, position=JUNGLE, is_win=False)
                                  | Game(champion=Champion(name=Jhin), kill=8, death=7, assist=3, position=ADC, is_win=False)
                                  | Game(champion=Champion(name=Sylas), kill=15, death=6, assist=7, position=JUNGLE, is_win=True)
                                  | Game(champion=Champion(name=Jhin), kill=10, death=7, assist=9, position=ADC, is_win=False)
                                  | Game(champion=Champion(name=Caitlyn), kill=5, death=10, assist=8, position=ADC, is_win=False)
                                  | Game(champion=Champion(name=Viego), kill=4, death=5, assist=3, position=JUNGLE, is_win=False)
                                  | Game(champion=Champion(name=Sylas), kill=8, death=7, assist=3, position=JUNGLE, is_win=False)
```

## Join the Discussion
Here's a link to the [Support Discord](https://discord.gg/fzRK2Sb)
