# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : Doomlad
# Date    : 2023-07-05
# Edit    : 2023-07-05
# License : BSD-3-Clause


class SeasonInfo:
    def __init__(self,
                 id: int,
                 value: int,
                 display_value: int,
                 is_preseason: bool) -> None:
        self._id = id
        self._value = value
        self._display_value = display_value
        self._is_preseason = is_preseason
