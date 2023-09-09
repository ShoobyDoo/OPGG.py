import sqlite3
import logging
import os

from opgg.champion import Champion, Spell


class Cacher:
    """
    Cacher class for caching summoners, champions, and seasons.
    
    ### Properties:
        `db_path` - Path to the database file.\n
        `logger` - Logger instance.
    """
    def __init__(self, db_path = "./cache/opgg.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("OPGG.py")
        self.logger.name = "OPGG.py->Cacher"
    
    
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
                champion_evolve_list
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
                skin_prices
            )
            """
        )
        
        self.conn.commit()
        self.conn.close()
        
    
    def insert_summoner(self, summoner_name: str, summoner_id: str, return_result: bool = False) -> None | str:
        """
        Inserts a summoner name and id into the database.
        
        ### Args:
            summoner_name : `str`
                Summoner name.
                
            summoner_id : `str`
                Summoner ID.
        
        ### Returns:
            `str, optional` : Returns a string with the amount of rows affected if requested.
        """
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        
        self.logger.debug(f"Attempting to insert {summoner_name} into cache database...")
        
        self.cursor.execute(
            """
            INSERT OR IGNORE INTO tblSummoners (summoner_name, summoner_id)
            VALUES (?, ?);
            """, 
            (summoner_name, summoner_id)
        )
        
        self.conn.commit()
        self.conn.close()
        
        return_msg = f"You have made changes to the database. Table: tblSummoners | Rows affected: {self.cursor.rowcount}"
        
        if return_result: 
            return return_msg
        else:
            self.logger.info(return_msg)
        
    
    def insert_all_champs(self, champions: list[Champion], return_result: bool = False) -> None | str:
        """
        Inserts a list of champions and their related attributes into the database.
        
        ### Args:
            champions : `list[Champion]`
                A list of Champion objects to be cached.
        
        ### Returns:
            `None | str, optional` : Returns a string with the amount of rows affected if requested.
        """
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        total_rc = 0 # total rowcount
        return_msg = "You've made changes to the database. Table: {table} | Rows affected: {count}"
        
        self.logger.debug(f"Attempting to insert {len(champions)} champions into cache database...")
        
        batch_champion_insert: list[tuple] = []
        batch_passives_insert: list[tuple] = []
        batch_spells_insert: list[tuple] = []
        batch_skins_insert: list[tuple] = []
        
        for champion in champions:
            # champion
            batch_champion_insert.append((
                champion.id,
                champion.key,
                champion.name,
                champion.image_url,
                ','.join([f"{_evolve}" for _evolve in champion.evolve])
            ))
            
            # passive (champ id to map passive to champion)
            batch_passives_insert.append((
                champion.id,
                champion.passive.name,
                champion.passive.description,
                champion.passive.image_url,
                champion.passive.video_url
            ))
            
            # spells (champ id to map spell to champion)
            for spell in champion.spells:
                batch_spells_insert.append((
                    champion.id,
                    spell.key,
                    spell.name,
                    spell.description,
                    spell.max_rank,
                    ','.join([f"{_range}" for _range in spell.range_burn]),
                    ','.join([f"{_cooldown}" for _cooldown in spell.cooldown_burn]),
                    ','.join([f"{_cost}" for _cost in spell.cost_burn]),
                    spell.tooltip,
                    spell.image_url,
                    spell.video_url
                ))
            
            # skins (champ id to map skin to champion)
            for skin in champion.skins:
                batch_skins_insert.append((
                    champion.id,
                    skin.id,
                    skin.name,
                    skin.centered_image,
                    skin.skin_video_url,
                    ','.join([f"{price.currency}: {price.cost}" for price in skin.prices]) if skin.prices else None
                ))
        
        # insert into champion table
        self.cursor.executemany(
            """
            INSERT OR IGNORE INTO tblChampions (champion_id, champion_key, champion_name, champion_image_url, champion_evolve_list)
            VALUES (:1, :2, :3, :4, :5)
            """,
            batch_champion_insert
        )
        
        total_rc += self.cursor.rowcount
        self.logger.debug(return_msg.format(table="tblChampions", count=self.cursor.rowcount))
        
        # insert into passives table
        self.cursor.executemany(
            """
            INSERT OR IGNORE INTO tblPassives (champion_id, passive_name, passive_description, passive_image_url, passive_video_url)
            VALUES (:1, :2, :3, :4, :5)
            """,
            batch_passives_insert
        )
        
        total_rc += self.cursor.rowcount
        self.logger.debug(return_msg.format(table="tblPassives", count=self.cursor.rowcount))
        
        # insert into skins table
        self.cursor.executemany(
            """
            INSERT OR IGNORE INTO tblSkins (champion_id, skin_id, skin_name, skin_centered_image, skin_video_url, skin_prices)
            VALUES (:1, :2, :3, :4, :5, :6)
            """,
            batch_skins_insert
        )
        
        total_rc += self.cursor.rowcount
        self.logger.debug(return_msg.format(table="tblSkins", count=self.cursor.rowcount))
        
        # insert into spells table
        self.cursor.executemany(
            """
            INSERT OR IGNORE INTO tblSpells (champion_id, spell_key, spell_name, spell_description, spell_max_rank, spell_range_burn_list, spell_cooldown_burn_list, spell_cost_burn_list, spell_tooltip, spell_image_url, spell_video_url)
            VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11)
            """,
            batch_spells_insert
        )
        
        total_rc += self.cursor.rowcount
        self.logger.debug(return_msg.format(table="tblSpells", count=self.cursor.rowcount))
        
        self.conn.commit()
        self.conn.close()
        
        return_msg = f"You've made several changes to the database. Total rows affected87541: {total_rc}"
        
        if return_result: 
            return return_msg
        else:
            self.logger.info(return_msg)
            
    
    def get_summoner_id(self, summoner_name: str) -> str | None:
        """
        Gets a summoner name from the cache database by a provided summoner name.
        
        ### Args:
            summoner_name : `str`
                Summoner name.
        
        ### Returns:
            `str | None` : Returns a `str` with the summoner id, if found. Otherwise returns `None`.
        """
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        
        self.logger.info(f"Getting {summoner_name}'s summoner id from cache database...")
        
        self.cursor.execute("""
            SELECT summoner_id
            FROM tblSummoners
            WHERE summoner_name = ?;
        """, (summoner_name,))
        
        result = self.cursor.fetchone()
        self.conn.close()
        
        if result is None:
            self.logger.info(f"{summoner_name}'s summoner_id not found in cache database.")
            return None
        
        self.logger.info(f"{summoner_name}'s summoner_id found in cache database. ({result[0]})")
        return result[0]
    
    
    def get_summoner_name(self, summoner_id: str) -> str | None:
        """
        Gets a summoner name from the cache database by a provided summoner id.
        
        ### Args:
            summoner_id : `str`
                Summoner ID.
        
        ### Returns:
            `str | None` : Returns a `str` with the summoner name, if found. Otherwise returns `None`.
        """
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        
        self.logger.info(f"Getting associated summoner name from summoner_id: {summoner_id}...")
        
        self.cursor.execute("""
            SELECT summoner_name
            FROM tblSummoners
            WHERE summoner_id = ?;
        """, (summoner_id,))
        
        result = self.cursor.fetchone()
        self.conn.close()
        
        if result is None:
            self.logger.info(f"Could not find an associated summoner_name for summoner_id: {summoner_id}")
            return None
        
        self.logger.info(f"Found associated summoner_name for summoner_id: {summoner_id} ({result[0]})")
        return result[0]
    
    
    def connect(self) -> sqlite3.Connection:
        """
        Connects to local database, if it doesn't exist, one will be created.
        
        ### Returns:
            `sqlite3.Connection` : Returns a connection object.
        """
        return sqlite3.connect(self.db_path)
    
