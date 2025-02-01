import os
import sqlite3
import logging

from opgg.v2.champion import Champion
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

        self.logger.debug("Creating champions table if it doesn't exist...")
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tblChampions (
                champion_id PRIMARY KEY,
                name
            );
            """
        )

        self.conn.commit()
        self.conn.close()

    def get_champ_id_by_name(self, champ_name: str) -> int | None:
        """
        Get the ID of a champion by name.

        Args:
            `champ_name` (`str`): The name of the champion

        Returns:
            `int | None`: The ID of the champion, or None if not found
        """
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        self.cursor.execute(
            "SELECT * FROM tblChampions WHERE name LIKE ?",
            (f"%{champ_name}%",),
        )
        result = self.cursor.fetchone()

        self.conn.close()

        # if the result is a tuple, return the first element (-> champ_id, name), otherwise return None
        return result[0] if isinstance(result, tuple) else None

    def cache_champs(self, champs: list[Champion]) -> None:
        """
        Cache champions in the database.

        Args:
            `champs` (`list[Champion]`): List of champions to cache
        """
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        # use executemany to bulk insert
        self.logger.debug(
            f"Attempting to insert {len(champs)} champions into cache database..."
        )
        self.cursor.executemany(
            """
            INSERT OR IGNORE INTO tblChampions (champion_id, name)
            VALUES (?, ?);
            """,
            [(champ.id, champ.name) for champ in champs],
        )

        self.conn.commit()
        self.conn.close()

        if len(champs) == self.get_cached_champs_count():
            self.logger.debug(
                f"Successfully inserted {len(champs)} champions into cache database."
            )
        else:
            self.logger.warning(
                f"Failed to insert {len(champs) - self.get_cached_champs_count()} champions into cache database."
            )
            self.logger.debug("CHAMPS DUMP: ", champs)

    def get_cached_champs_count(self) -> int:
        """
        Get the count of cached champions.

        Returns:
            `int`: The count of cached champions.
        """
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        self.cursor.execute("SELECT COUNT(*) FROM tblChampions")
        count = self.cursor.fetchone()[0]

        self.conn.close()

        self.logger.debug(f"Found {count} cached champions.")

        return count

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
