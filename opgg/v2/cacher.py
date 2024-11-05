import sqlite3
import logging
import os
import glob


from datetime import datetime
from typing import Literal

from opgg.v2.search_result import SearchResult


class Cacher:
    """
    Cacher class for caching summoners, champions, and seasons.

    ### Properties:
        `db_path` - Path to the database file.\n
        `logger` - Logger instance.
    """
    def __init__(self, db_path = f'./cache/opgg.py.db'):
        self.db_path = db_path
        self.logger = logging.getLogger("OPGG.py")

    def setup(self) -> None:
        """
        Sets up the cache database and table(s).

        Runs at OPGG object creation.
        """
        if not os.path.exists('./cache'):
            self.logger.info("Creating cache directory...")
            os.mkdir('./cache')
            self.logger.info("Setting up cache database...")

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # Create summoner table if it doesn't exist
        self.logger.debug("Creating summoner table if it doesn't exist...")
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tblSummoners (
                summoner_id PRIMARY KEY,
                game_name,
                tagline
            );
            """
        )

        # Create index on game_name
        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_game_name ON tblSummoners (game_name);
            """
        )

        # Create composite index on game_name and tagline
        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_game_name_tagline ON tblSummoners (game_name, tagline);
            """
        )

        self.conn.commit()
        self.conn.close()


    def is_search_result_cached(self, search_result: SearchResult) -> bool:
        search_result.game_name


        self.cursor.execute("")


    def cache_search_results(self, search_results: list[SearchResult]) -> None:
        # General flow of caching:
        # Take a given array of search results, and
        # 1. Check if summoner_id exists in cache table
        # 2. If it does, verify the game_name and taglines match and update them if they dont (update existing WITH changes)
        # 3. If it doesn't, simply cache it in place. Cache everything that comes through the program to speed up subsequent requests.
        # 4. The summoner_id is the bread and butter of the other endpoints, so really thats what we want.

        for result in search_results:
            self.logger.debug(f"Processing SearchResult object: {result}")
