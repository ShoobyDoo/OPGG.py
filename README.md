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


def main():    
    opgg = OPGG()
    
    summoner: Summoner
    for summoner in opgg.search(["ColbyFaulkn1"]):
        print(summoner)
        
    
if __name__ == "__main__":
    main()
```

### Output
**Important Note:** The information returned below is a summary view with the most important parts of each object shown "at a glance". 
Many of the objects have several additional properties that can be accessed by referencing the object in code.
```
[Summoner: ColbyFaulkn1]
--------------------------------------------------------------------------------
Id                          (int) | 113462497
Summoner Id                 (str) | h7UNeo4aQz9Rnc0FKlKvgrEgEFEoJxHMLN7oMAGvrsFI2l9Mk0-eWe1yKg
Account Id                  (str) | Qw7zgbaE-iIsC_n4VhtWXY83u0f21TQL2e6xi2Z-bYAm8KiQIFafhPfb
Puuid                       (str) | k-CwhMDDAwLZYjLMcehGbvFoNsPm4HyvWqWHmkyrgX91vZtUbUDvTPaCkiPoVpPx_SjRVW8RU8Hx0g
Name                        (str) | ColbyFaulkn1
Internal Name               (str) | colbyfaulkn1
Profile Image Url           (str) | https://opgg-static.akamaized.net/meta/images/profile_icons/profileIcon907.jpg
Level                       (int) | 45
Updated At             (datetime) | 2023-08-20T07:26:15+09:00
Renewable At           (datetime) | 2023-08-20T07:28:15+09:00
Previous Seasons     (SeasonInfo) | [List (1)]
                                  | Season(season=SeasonInfo(display_value=2023, is_preseason=False), tier_info=Tier(tier=SILVER, division=1, lp=1))
League Stats        (LeagueStats) | [List (3)]
                                  | LeagueStats(queue_info=QueueInfo(game_type=SOLORANKED), tier_info=Tier(tier=SILVER, division=2, lp=64), win=3, lose=3)
                                  | LeagueStats(queue_info=QueueInfo(game_type=FLEXRANKED), tier_info=Tier(tier=None, division=None, lp=None), win=1, lose=1)
                                  | LeagueStats(queue_info=QueueInfo(game_type=ARENA), tier_info=Tier(tier=None, division=None, lp=None), win=None, lose=None)
Most Champions       (ChampStats) | [List (5)]
                                  | ChampionStats(champion=Champion(name=Pyke), win=1 / lose=2 (winrate: 33.33%), kda=1.62)
                                  | ChampionStats(champion=Champion(name=Morgana), win=1 / lose=1 (winrate: 50.0%), kda=3.85)
                                  | ChampionStats(champion=Champion(name=Blitzcrank), win=1 / lose=0 (winrate: 100.0%), kda=4.25)
                                  | ChampionStats(champion=Champion(name=Zed), win=1 / lose=0 (winrate: 100.0%), kda=10.5)
                                  | ChampionStats(champion=Champion(name=Gangplank), win=0 / lose=1 (winrate: 0.0%), kda=1.67)
Recent Game Stats          (Game) | [List (10)]
                                  | Game(champion=Champion(name=Gangplank), kill=5, death=3, assist=0, position=MID, is_win=False)
                                  | Game(champion=Champion(name=Zed), kill=14, death=2, assist=7, position=MID, is_win=True)
                                  | Game(champion=Champion(name=Morgana), kill=7, death=10, assist=24, position=SUPPORT, is_win=False)
                                  | Game(champion=Champion(name=Pyke), kill=4, death=6, assist=4, position=SUPPORT, is_win=False)
                                  | Game(champion=Champion(name=Blitzcrank), kill=2, death=4, assist=15, position=SUPPORT, is_win=True)
                                  | Game(champion=Champion(name=Morgana), kill=3, death=3, assist=16, position=SUPPORT, is_win=True)
                                  | Game(champion=Champion(name=Zed), kill=8, death=0, assist=5, position=MID, is_win=True)
                                  | Game(champion=Champion(name=Pyke), kill=5, death=9, assist=7, position=SUPPORT, is_win=False)
                                  | Game(champion=Champion(name=Zed), kill=13, death=5, assist=5, position=MID, is_win=False)
                                  | Game(champion=Champion(name=Pyke), kill=10, death=4, assist=12, position=SUPPORT, is_win=True)
```

## Join the Discussion
Here's a link to the [Support Discord](https://discord.gg/fzRK2Sb)
