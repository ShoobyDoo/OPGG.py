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

    def __init__(self, db_path=f"./cache/opgg.py.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("OPGG.py")

    def setup(self) -> None:
        """
        Sets up the cache database and table(s).

        Runs at OPGG object creation.
        """
        if not os.path.exists("./cache"):
            self.logger.info("Creating cache directory...")
            os.mkdir("./cache")
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

    def cache_search_results(self, search_results: list[SearchResult]) -> None:
        """
        Cache search results in the database.

        Args:
            `search_results` (`list[SearchResult]`): List of search results to cache
        """
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        try:
            for result in search_results:
                summoner = result.summoner
                self.logger.debug(
                    f"Processing summoner for caching: {summoner.game_name}#{summoner.tagline}"
                )

                # Check if summoner exists
                self.cursor.execute(
                    """
                    SELECT summoner_id FROM tblSummoners 
                    WHERE summoner_id = ?
                    """,
                    (summoner.summoner_id,),
                )

                exists = self.cursor.fetchone()

                if exists:
                    # Update existing summoner if game_name or tagline changed
                    self.cursor.execute(
                        """
                        UPDATE tblSummoners 
                        SET game_name = ?, tagline = ?
                        WHERE summoner_id = ? 
                        AND (game_name != ? OR tagline != ?)
                        """,
                        (
                            summoner.game_name,
                            summoner.tagline,
                            summoner.summoner_id,
                            summoner.game_name,
                            summoner.tagline,
                        ),
                    )
                else:
                    # Insert new summoner
                    self.cursor.execute(
                        """
                        INSERT INTO tblSummoners (summoner_id, game_name, tagline)
                        VALUES (?, ?, ?)
                        """,
                        (summoner.summoner_id, summoner.game_name, summoner.tagline),
                    )

            self.conn.commit()
            self.logger.info(
                f"Successfully cached {len(search_results)} search results"
            )

        except Exception as e:
            self.logger.error(f"Error caching search results: {str(e)}")
            self.conn.rollback()
        finally:
            self.conn.close()

    def is_search_result_cached(
        self, game_name: str, tagline: str = ""
    ) -> tuple[bool, str | None]:
        """
        Check if a search result exists in the cache.

        Args:
            `game_name` (`str`): The summoner's game name
            `tagline` (`str`, optional): The summoner's tagline. Defaults to empty string.

        Returns:
            `tuple[bool, str | None]`: Tuple containing:
                - `bool`: Whether the summoner is cached
                - `str | None`: The summoner_id if cached, None if not
        """
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        try:
            if tagline:
                # Search with both game_name and tagline
                self.cursor.execute(
                    """
                    SELECT summoner_id FROM tblSummoners 
                    WHERE game_name = ? AND tagline = ?
                    """,
                    (game_name, tagline),
                )
            else:
                # Search with just game_name
                self.cursor.execute(
                    """
                    SELECT summoner_id FROM tblSummoners 
                    WHERE game_name = ?
                    """,
                    (game_name,),
                )

            result = self.cursor.fetchone()
            return (True, result[0]) if result else (False, None)

        except Exception as e:
            self.logger.error(f"Error checking cache: {str(e)}")
            return False, None
        finally:
            self.conn.close()
