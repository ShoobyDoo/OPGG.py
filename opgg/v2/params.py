from enum import Enum


class Region(Enum):
    """
    Enum for regions.

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
        `TR` - Turkey\n
        `ANY` - Any
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
    ANY = "ANY"

    def __str__(self):
        return self.value


class By(Enum):
    """
    Enum for search-by or match-by types.

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

    def __str__(self):
        return self.value


class Queue(Enum):
    """
    Enum for queue types.

    ### Options:
        `SOLO` - SoloQueue\n
        `FLEX` - FlexQueue\n
        `ARENA` - Arena
    """

    SOLO = "SOLORANKED"
    FLEX = "FLEXRANKED"
    ARENA = "ARENA"

    def __str__(self):
        return self.value
