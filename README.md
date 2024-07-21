[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2FShoobyDoo%2FOPGG.py&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23DDDDDD&title=visits&edge_flat=false)](https://hits.seeyoufarm.com)

# OPGG.py
An unofficial Python library for accessing OPGG data.
#### You can view the current active developments on the [OPGG.py Project](https://github.com/users/ShoobyDoo/projects/2) page

## Prerequisites

* [Python 3.11+](https://www.python.org/downloads/) 
    
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
* [fake-useragent](https://pypi.org/project/fake-useragent/)

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

    summoner: Summoner = opgg_obj.search("Doublelift#NA1")
    print(summoner)


if __name__ == "__main__":
    main()
```

### Output
**Important Note:** The information returned below is a summary view with the most important parts of each object shown "at a glance". 
Many of the objects have several additional properties that can be accessed by referencing the object in code.
```
[Summoner: Doublelift]
--------------------------------------------------------------------------------
Id                          (int) | 20132258
Summoner Id                 (str) | AVCaop7DsXMxYghWRgonI__cn6cKD9EssfdNn-A8NhKvW2U
Account Id                  (str) | I7kr1mRrzLbLiQc_Id3zCWiNlj-Pi3bvEB2O5LD8oMlO0w
Puuid                       (str) | u8t2CfocyGKreqYaW9xHwk1qE3L82aCYrOeacNyNhg_mBC4LEhHKhy0-JygUI8gTKZzz6KlgNOM44g
Game Name                   (str) | Doublelift
Tagline                     (str) | NA1
Name                        (str) | Doublelift
Internal Name               (str) | doublelift
Profile Image Url           (str) | https://opgg-static.akamaized.net/meta/images/profile_icons/profileIcon6637.jpg
Level                       (int) | 544
Updated At             (datetime) | 2024-07-21T12:08:56+09:00
Renewable At           (datetime) | 2024-07-21T12:10:56+09:00
Previous Seasons         (Season) | [List (12)]
                                  | Season(season=SeasonInfo(display_value=2024, is_preseason=False), tier_info=Tier(tier=CHALLENGER, division=1, lp=1044))
                                  | Season(season=SeasonInfo(display_value=2023, is_preseason=False), tier_info=Tier(tier=GRANDMASTER, division=1, lp=693))
                                  | Season(season=SeasonInfo(display_value=2023, is_preseason=False), tier_info=Tier(tier=MASTER, division=1, lp=42))
                                  | Season(season=SeasonInfo(display_value=2022, is_preseason=False), tier_info=Tier(tier=DIAMOND, division=1, lp=100))
                                  | Season(season=SeasonInfo(display_value=2021, is_preseason=False), tier_info=Tier(tier=CHALLENGER, division=1, lp=987))
                                  | Season(season=SeasonInfo(display_value=2020, is_preseason=False), tier_info=Tier(tier=DIAMOND, division=2, lp=33))
                                  | Season(season=SeasonInfo(display_value=9, is_preseason=False), tier_info=Tier(tier=DIAMOND, division=3, lp=76))
                                  | Season(season=SeasonInfo(display_value=8, is_preseason=False), tier_info=Tier(tier=MASTER, division=1, lp=52))
                                  | Season(season=SeasonInfo(display_value=7, is_preseason=False), tier_info=Tier(tier=MASTER, division=1, lp=142))
                                  | Season(season=SeasonInfo(display_value=6, is_preseason=False), tier_info=Tier(tier=MASTER, division=1, lp=239))
                                  | Season(season=SeasonInfo(display_value=5, is_preseason=False), tier_info=Tier(tier=DIAMOND, division=2, lp=21))
                                  | Season(season=SeasonInfo(display_value=4, is_preseason=False), tier_info=Tier(tier=CHALLENGER, division=1, lp=0))
League Stats        (LeagueStats) | [List (3)]
                                  | LeagueStats(queue_info=QueueInfo(game_type=SOLORANKED), tier_info=Tier(tier=CHALLENGER, division=1, lp=1182), win=284 / lose=242 (winrate: 53.99%))
                                  | LeagueStats(queue_info=QueueInfo(game_type=FLEXRANKED), tier_info=Tier(tier=UNRANKED, division=0, lp=0), win=0 / lose=0 (winrate: 0%))
                                  | LeagueStats(queue_info=QueueInfo(game_type=ARENA), tier_info=Tier(tier=UNRANKED, division=0, lp=0), win=2 / lose=1 (winrate: 66.67%))
Most Champions       (ChampStats) | [List (10)]
                                  | ChampionStats(champion=Champion(name=Jinx), win=109 / lose=70 (winrate: 60.89%), kda=3.81)
                                  | ChampionStats(champion=Champion(name=Jhin), win=54 / lose=38 (winrate: 58.7%), kda=3.96)
                                  | ChampionStats(champion=Champion(name=Ashe), win=21 / lose=19 (winrate: 52.5%), kda=3.92)
                                  | ChampionStats(champion=Champion(name=Zeri), win=17 / lose=15 (winrate: 53.12%), kda=3.42)
                                  | ChampionStats(champion=Champion(name=Kai'Sa), win=14 / lose=11 (winrate: 56.0%), kda=3.46)
                                  | ChampionStats(champion=Champion(name=Caitlyn), win=10 / lose=6 (winrate: 62.5%), kda=2.85)
                                  | ChampionStats(champion=Champion(name=Lucian), win=7 / lose=9 (winrate: 43.75%), kda=3.55)
                                  | ChampionStats(champion=Champion(name=Senna), win=6 / lose=6 (winrate: 50.0%), kda=3.63)
                                  | ChampionStats(champion=Champion(name=Tristana), win=4 / lose=7 (winrate: 36.36%), kda=2.07)
                                  | ChampionStats(champion=Champion(name=Janna), win=7 / lose=3 (winrate: 70.0%), kda=5.36)
Recent Game Stats          (Game) | [List (10)]
                                  | Game(champion_id=63, kill=1, death=4, assist=6, position=JUNGLE, result=LOSE)
                                  | Game(champion_id=202, kill=21, death=3, assist=11, position=ADC, result=WIN)
                                  | Game(champion_id=222, kill=2, death=3, assist=12, position=ADC, result=WIN)
                                  | Game(champion_id=222, kill=6, death=6, assist=4, position=ADC, result=LOSE)
                                  | Game(champion_id=221, kill=2, death=2, assist=1, position=ADC, result=LOSE)
                                  | Game(champion_id=202, kill=2, death=2, assist=5, position=ADC, result=WIN)
                                  | Game(champion_id=22, kill=12, death=12, assist=13, position=ADC, result=LOSE)
                                  | Game(champion_id=222, kill=9, death=7, assist=4, position=ADC, result=WIN)
                                  | Game(champion_id=22, kill=14, death=4, assist=8, position=ADC, result=WIN)
                                  | Game(champion_id=202, kill=9, death=0, assist=5, position=ADC, result=WIN)
```

## Join the Discussion
Here's a link to the [Support Discord](https://discord.gg/fzRK2Sb)
