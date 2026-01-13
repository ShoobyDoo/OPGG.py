from enum import Enum
from typing import NotRequired, TypedDict


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


class LangCode(Enum):
    """
    Enum for language codes.

    Please note, some languages may not be supported by OPGG.

    ---

    ### Options:
        `ENGLISH` - en_US (United States)\n
        `SPANISH` - es_ES (Spain)\n
        `PORTUGUESE` - pt_BR (Brazil)\n
        `FRENCH` - fr_FR (France)\n
        `GERMAN` - de_DE (Germany)\n
        `ITALIAN` - it_IT (Italy)\n
        `RUSSIAN` - ru_RU (Russia)\n
        `TURKISH` - tr_TR (Turkey)\n
        `KOREAN` - ko_KR (Korea)\n
        `JAPANESE` - ja_JP (Japan)\n
        `CHINESE` - zh_CN (Simplified)\n
        `CHINESE_TRAD` - zh_TW (Traditional)
    """

    ENGLISH = "en_US"  # English (United States)
    SPANISH = "es_ES"  # Spanish (Spain)
    PORTUGUESE = "pt_BR"  # Portuguese (Brazil)
    FRENCH = "fr_FR"  # French (France)
    GERMAN = "de_DE"  # German (Germany)
    ITALIAN = "it_IT"  # Italian (Italy)
    RUSSIAN = "ru_RU"  # Russian (Russia)
    TURKISH = "tr_TR"  # Turkish (Turkey)
    KOREAN = "ko_KR"  # Korean (Korea)
    JAPANESE = "ja_JP"  # Japanese (Japan)
    CHINESE = "zh_CN"  # Chinese (Simplified)
    CHINESE_TRAD = "zh_TW"  # Chinese (Traditional)

    def __str__(self):
        return self.value

    @classmethod
    def normalize(cls, value: "LangCode | str") -> str:
        """
        Normalize a LangCode enum or string to a string value.

        Args:
            `value` (`LangCode | str`): A LangCode enum member or string

        Returns:
            `str`: The string value of the language code
        """
        return value.value if isinstance(value, cls) else str(value)


class CacheType(Enum):
    """
    Enum for cache types.

    ### Options:
        `CHAMPIONS` - Champion data cache\n
        `SEASONS` - Season data cache\n
        `VERSIONS` - Version data cache\n
        `KEYWORDS` - Keyword metadata cache\n
        `ALL` - All cache types
    """

    CHAMPIONS = "champions"
    SEASONS = "seasons"
    VERSIONS = "versions"
    KEYWORDS = "keywords"
    ALL = "all"

    def __str__(self):
        return self.value


class Tier(Enum):
    """
    Enum for rank tiers.

    ### Options:
        `ALL` - All ranks\n
        `IRON` - Iron tier\n
        `BRONZE` - Bronze tier\n
        `SILVER` - Silver tier\n
        `GOLD` - Gold tier\n
        `PLATINUM` - Platinum tier\n
        `EMERALD` - Emerald tier\n
        `DIAMOND` - Diamond tier\n
        `MASTER` - Master tier\n
        `GRANDMASTER` - Grandmaster tier\n
        `CHALLENGER` - Challenger tier\n
        `EMERALD_PLUS` - Emerald and above (aggregated)\n
        `DIAMOND_PLUS` - Diamond and above (aggregated)
    """

    ALL = "all"
    IRON = "iron"
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    EMERALD = "emerald"
    DIAMOND = "diamond"
    MASTER = "master"
    GRANDMASTER = "grandmaster"
    CHALLENGER = "challenger"
    EMERALD_PLUS = "emerald_plus"
    DIAMOND_PLUS = "diamond_plus"

    def __str__(self):
        return self.value


class GameType(Enum):
    """
    Enum for game types.

    ### Options:
        `TOTAL` - All game types\n
        `RANKED` - Ranked games only\n
        `NORMAL` - Normal games only
    """

    TOTAL = "total"
    RANKED = "ranked"
    NORMAL = "normal"

    def __str__(self):
        return self.value


class StatsRegion(Enum):
    """
    Enum for champion statistics regions.

    ### Options:
        `GLOBAL` - Worldwide statistics
    """

    GLOBAL = "global"

    def __str__(self):
        return self.value


class SearchReturnType(Enum):
    """
    Enum for search return types.

    ### Options:
        `SIMPLE` - Basic search results without full summoner profiles\n
        `FULL` - Complete search results with full summoner profiles
    """

    SIMPLE = "simple"
    FULL = "full"

    def __str__(self):
        return self.value


class GenericReqParams(TypedDict):
    """
    A generic request parameters type.

    Parameters:
        base_api_url: `str`: The base API URL for the request
        headers: `dict`: The headers to include in the request
        lang_code: `LangCode`, optional: Language code for localization when supported
    """

    base_api_url: str
    headers: dict
    lang_code: NotRequired[LangCode]
