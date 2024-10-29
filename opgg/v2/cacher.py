import sqlite3
import logging
import os
import glob
from datetime import datetime


class Cacher:
    """
    Cacher class for caching summoners, champions, and seasons.

    ### Properties:
        `db_path` - Path to the database file.\n
        `logger` - Logger instance.
    """
    def __init__(self, db_path = f'./cache/opgg-{datetime.now().strftime("%Y-%m-%d")}.db'):
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

        self.conn = self.connect()
        self.cursor = self.conn.cursor()

        # Create summoner table if it doesn't exist
        self.logger.debug("Creating summoner table if it doesn't exist...")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS tblSummoners (summoner_name PRIMARY KEY, summoner_id);""")

        # Create champions table if it doesn't exist
        self.logger.debug("Creating champions table if it doesn't exist...")
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tblChampions (
                champion_id PRIMARY KEY,
                champion_key,
                champion_name,
                champion_image_url,
                champion_evolve_list,
                champion_partype
            );
            """
        )

        # Create seasons table if it doesn't exist
        self.logger.debug("Creating seasons table if it doesn't exist...")
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tblSeasonInfo (
                season_id PRIMARY KEY,
                season_value,
                season_display_name,
                season_split,
                season_is_preseason
            );
            """
        )

        # Create passives table if it doesn't exist
        self.logger.debug("Creating passives table if it doesn't exist...")
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tblPassives (
                champion_id PRIMARY KEY,
                passive_name,
                passive_description,
                passive_image_url,
                passive_video_url
            );
            """
        )

        # Create spells table if it doesn't exist
        self.logger.debug("Creating spells table if it doesn't exist...")
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tblSpells (
                champion_id,
                spell_key,
                spell_name PRIMARY KEY,
                spell_description,
                spell_max_rank,
                spell_range_burn_list,
                spell_cooldown_burn_list,
                spell_cooldown_burn_float_list,
                spell_cost_burn_list,
                spell_tooltip,
                spell_image_url,
                spell_video_url
            );
            """
        )

        # Create skins table if it doesn't exist
        self.logger.debug("Creating skins table if it doesn't exist...")
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tblSkins (
                champion_id,
                skin_id PRIMARY KEY,
                skin_name,
                skin_centered_image,
                skin_video_url,
                skin_prices,
                skin_sales,
                skin_release_date
            )
            """
        )

        self.conn.commit()
        self.conn.close()