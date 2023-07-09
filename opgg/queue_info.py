# Quick and simple scraper to pull some data from OPGG using multisearch

# Author  : Doomlad
# Date    : 2023-07-05
# Edit    : 2023-07-05
# License : BSD-3-Clause


class QueueInfo:
    def __init__(self,
                 id: int,
                 queue_translate: str,
                 game_type: str) -> None:
        self._id = id
        self._queue_translate = queue_translate
        self._game_type = game_type
        
    @property
    def id(self) -> int:
        return self._id
     
    @id.setter
    def id(self, value: int) -> None:
        self._id = value
        
    @property
    def queue_translate(self) -> str:
        return self._queue_translate
    
    @queue_translate.setter
    def queue_translate(self, value: str) -> None:
        self._queue_translate = value
        
    @property
    def game_type(self) -> str:
        return self._game_type
    
    @game_type.setter
    def game_type(self, value: str) -> None:
        self._game_type = value