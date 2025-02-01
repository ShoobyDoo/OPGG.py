# Simple scraper to pull some data from OPGG using multisearch

# Author  : ShoobyDoo
# Date    : 2023-07-05
# License : BSD-3-Clause


class Region:
    """
    Struct for regions.
    
    ### Options:
        `NA` - North America\n
        `EUW` - Europe West\n
        `EUNE` - Europe Nordic & East\n
        `KR` - Korea\n
        `JP` - Japan\n
        `BR` - Brazil\n
        `LAN` - Latin America North\n
        `LAS` - Latin America South\n
        `OCE` - Oceania\n
        `RU` - Russia\n
        `TR` - Turkey
    """
    
    NA = "NA"
    EUW = "EUW"
    EUNE = "EUNE"
    KR = "KR"
    JP = "JP"
    BR = "BR"
    LAN = "LAN"
    LAS = "LAS"
    OCE = "OCE"
    RU = "RU"
    TR = "TR"


class By:
    """
    Struct for search-by or match-by types.
    
    ### Options:
        `ID` - Generic ID\n
        `KEY` - Generic Key\n
        `NAME` - Generic Name\n
        `COST` - Generic Cost\n
        `BLUE_ESSENCE` - Specific Cost (Blue Essence)\n
        `RIOT_POINTS` - Specific Cost (Riot Points)
    """
        
    ID = "id"
    KEY = "key"
    NAME = "name"
    COST = "cost"
    BLUE_ESSENCE = "BE"
    RIOT_POINTS = "RP"
    

class Queue:
    """
    Struct for queue types.
    
    ### Options:
        `SOLO` - SoloQueue\n
        `FLEX` - FlexQueue\n
        `ARENA` - Arena
    """
    
    SOLO = "SOLORANKED"
    FLEX = "FLEXRANKED"
    ARENA = "ARENA"
    