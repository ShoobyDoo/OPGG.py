import sqlite3
import logging
import os


class Cacher:
    """
    Cacher class for caching summoner ids.
    
    ### Properties:
        `db_path` - Path to the database file.\n
        `logger` - Logger instance.
    """
    def __init__(self, db_path = "./cache/opgg.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("OPGG.py")
    
    
    def setup(self) -> None:
        """
        Sets up the cache database. 
        
        This will run at OPGG object creation.
        """
        if not os.path.exists('./cache'):
            self.logger.info("Creating cache directory...")
            os.mkdir('./cache')
            self.logger.info("Setting up cache database...")
        
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        
        self.logger.info("Creating summoner table if it doesn't exist...")
        
        # Create summoner table if it doesn't exist
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS tblSummoners (summoner_name PRIMARY KEY, summoner_id);""")
        self.conn.close()
        
    
    def insert(self, summoner_name: str, summoner_id: str, return_result: bool = False) -> None | str:
        """
        Inserts a summoner into the cache database.
        
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
        
        self.logger.info(f"Inserting {summoner_name} into cache database...")
        
        self.cursor.execute("""
            INSERT INTO tblSummoners (summoner_name, summoner_id)
            VALUES (?, ?);
        """, (summoner_name, summoner_id))
        
        self.conn.commit()
        self.conn.close()
        
        return_msg = f"You have made changes to the database. Rows affected: {self.cursor.rowcount}"
        
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
    
