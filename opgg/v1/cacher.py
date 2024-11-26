import sqlite3
import logging
import os
import glob
from datetime import datetime

from opgg.v1.champion import Champion, Passive, Skin, Spell
from opgg.v1.season import SeasonInfo


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
        
        # Do all this cleanup and verification in the connect function to minimize work required
        # to enforce this. Anytime a function needs to connect to the database, this check should
        # be performed and the data base structure should be verified. 
        # 
        # It should also then query out to pull the necessary data as if this is called on a 
        # get_<whatever> type function the database will have no data following a cache rebuild.
        cache_db = glob.glob("./cache/opgg*.db")
        
        if (len(cache_db) > 0 and "-" in cache_db[0]):
            old_path = cache_db[0]
            cache_last_updated = datetime.strptime(old_path.split("-", 1)[-1].replace(".db", ""), "%Y-%m-%d")
            
            self.logger.info(f"Cache found! Was last built: {cache_last_updated}")
            
            if (datetime.now() - cache_last_updated).days >= 7:
                self.logger.info("Cache is older than 1 week, rebuilding...")
                
                # set db_path to the old cache for a second
                new_path = self.db_path
                
                self.logger.info("Deleting old cache data...")
                os.remove(old_path)
                
                self.logger.info(f"Updating filename with current date {old_path} -> {new_path}")
                self.db_path = new_path
                
                self.logger.info("Cache has been removed! The immediate request following a cache rebuild might take slightly longer as new data is fetched and the cache is updated.")
                
        elif (len(cache_db) > 0):
            os.remove(cache_db[0])
        
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
        
        
    def get_summoner_id(self, summoner_name: str) -> str | None:
        """
        Gets a summoner id from the cache database by a provided summoner name.
        
        `Note: I'm now realizing there are quite a few limitations to this method.`\n
        `There is currently no way to specify region in the search, different regions could have the same summoner name.`
        `This method's search logic will need to be reworked.`
        
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
    
    
    def insert_all_champs(self, champions: list[Champion], return_result: bool = False) -> None | str:
        """
        Inserts a list of champions and their related attributes into the database.
        
        ### Args:
            champions : `list[Champion]`
                A list of Champion objects to be cached.
        
        ### Returns:
            `None` | `str, optional` : Returns a string with the amount of rows affected if requested.
        """
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        total_rc = 0 # total rowcount
        return_msg = "You've made changes to the database. Table: {table} | Rows affected: {count}"
        
        self.logger.debug(f"Attempting to insert {len(champions)} champions into cache database...")
        
        batch_champion_insert:  list[tuple] = []
        batch_passives_insert:  list[tuple] = []
        batch_spells_insert:    list[tuple] = []
        batch_skins_insert:     list[tuple] = []
        
        for champion in champions:
            # champion
            batch_champion_insert.append((
                champion.id,
                champion.key,
                champion.name,
                champion.image_url,
                ','.join([f"{_evolve}" for _evolve in champion.evolve]),
                champion.partype
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
                    ','.join([f"{_cooldown_float}" for _cooldown_float in spell.cooldown_burn_float]),
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
                    ','.join([f"{price.currency}: {price.cost}" for price in skin.prices]) if skin.prices else None,
                    skin.release_date,
                    ','.join([f"{_price}" for _price in skin.prices]) if skin.prices else str(skin.prices)
                ))
        
        # insert into champion table
        self.cursor.executemany(
            """
            INSERT OR IGNORE INTO tblChampions (champion_id, champion_key, champion_name, champion_image_url, champion_evolve_list, champion_partype)
            VALUES (:1, :2, :3, :4, :5, :6)
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
            INSERT OR IGNORE INTO tblSkins (champion_id, skin_id, skin_name, skin_centered_image, skin_video_url, skin_prices, skin_release_date, skin_sales)
            VALUES (:1, :2, :3, :4, :5, :6, :7, :8)
            """,
            batch_skins_insert
        )
        
        total_rc += self.cursor.rowcount
        self.logger.debug(return_msg.format(table="tblSkins", count=self.cursor.rowcount))
        
        # insert into spells table
        self.cursor.executemany(
            """
            INSERT OR IGNORE INTO tblSpells (champion_id, spell_key, spell_name, spell_description, spell_max_rank, spell_range_burn_list, spell_cooldown_burn_list, spell_cooldown_burn_float_list, spell_cost_burn_list, spell_tooltip, spell_image_url, spell_video_url)
            VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12)
            """,
            batch_spells_insert
        )
        
        total_rc += self.cursor.rowcount
        self.logger.debug(return_msg.format(table="tblSpells", count=self.cursor.rowcount))
        
        self.conn.commit()
        self.conn.close()
        
        return_msg = f"You've made several changes to the database. Total rows affected: {total_rc}"
        
        if return_result: 
            return return_msg
        else:
            self.logger.info(return_msg)
            
            
    def get_all_champs(self) -> list[Champion] | None:
        """
        Gets all champions from the cache database and returns a list of Champion objects.

        ### Returns:
            `list[Champion]` | `None` : Returns a list of Champion objects if found. Otherwise returns `None`.
        """
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        all_champs = []
        
        self.logger.info("Getting all champions from cache database...")
        self.cursor.execute("SELECT * FROM tblChampions;")
        result = self.cursor.fetchall()
        
        if result is None:
            self.logger.error("No champions found in cache database.")
            raise Exception("Multiple levels of data fetching have failed to result in this event.\n \
                            1. There were no champions returned in the request to opgg (?) See debug logs...\n \
                            2. There were no champions found in the cache database.")
        else:
            self.logger.info(f"Found {len(result)} champions in cache database.")
            cached_champ: tuple[str, str, str, str, str]
            for i, cached_champ in enumerate(result):
                # In order to restore a champion object, we need the following:
                # PASSIVE FROM PASSIVES TABLE
                # SPELLS FROM SPELLS TABLE
                # SKINS FROM SKINS TABLE
                champ_passive = self.get_passive(cached_champ[0])
                champ_spells = self.get_spells(cached_champ[0])
                champ_skins = self.get_skins(cached_champ[0])
                
                champ_obj = Champion(
                    id=cached_champ[0],
                    key=cached_champ[1],
                    name=cached_champ[2],
                    image_url=cached_champ[3],
                    evolve=cached_champ[4].split(',') if cached_champ[4] else None,
                    partype=cached_champ[5],
                    passive=champ_passive,
                    spells=champ_spells,
                    skins=champ_skins
                )
                all_champs.append(champ_obj)
                self.logger.info(f"Successfully rebuilt the \"{champ_obj.name}\" champion object from cache. ({i+1}/{len(result)})")
                
            return all_champs
                
            
    def get_passive(self, champion_id: int) -> Passive | None:
        """
        Gets a champion's passive from the cache database.
        
        ### Args:
            champion_id : `int`
                Champion ID.
        
        ### Returns:
            `Passive | None` : Returns a `Passive` object if found. Otherwise returns `None`.
        """
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        
        self.logger.debug(f"Getting passive for champion_id: {champion_id}...")
        
        self.cursor.execute(
            """
            SELECT *
            FROM tblPassives
            WHERE champion_id = ?;
            """, (champion_id,)
        )
        
        result = self.cursor.fetchone()
        self.conn.close()
        
        if result is None:
            self.logger.debug(f"Passive not found for champion_id: {champion_id}.")
            return None
        
        self.logger.debug(f"Passive \"{result[1]}\" found for champion_id: {champion_id}.")
        return Passive(
            name=result[1],
            description=result[2],
            image_url=result[3],
            video_url=result[4]
        )    
         
            
    def get_spells(self, champion_id: int) -> list[Spell] | None:
        """
        Gets a champion's spells from the cache database.
        
        ### Args:
            champion_id : `int`
                Champion ID.
        
        ### Returns:
            `list[Spell] | None` : Returns a list of `Spell` objects if found. Otherwise returns `None`.
        """
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        
        self.logger.debug(f"Getting spells for champion_id: {champion_id}...")
        
        self.cursor.execute(
            """
            SELECT *
            FROM tblSpells
            WHERE champion_id = ?;
            """, (champion_id,)
        )
        
        result = self.cursor.fetchall()
        self.conn.close()
        
        if result is None:
            self.logger.debug(f"No spells found for champion_id: {champion_id}.")
            return None
        
        self.logger.debug(f"Found spells for champion_id: {champion_id}.")
        return [Spell(
            key=spell[1],
            name=spell[2],
            description=spell[3],
            max_rank=spell[4],
            range_burn=spell[5].split(',') if spell[5] else None,
            cooldown_burn=spell[6].split(',') if spell[6] else None,
            cooldown_burn_float=spell[7].split(',') if spell[7] else None,
            cost_burn=spell[8].split(',') if spell[8] else None,
            tooltip=spell[9],
            image_url=spell[10],
            video_url=spell[11]
        ) for spell in result]
    
    
    def get_skins(self, champion_id: int) -> list[Skin] | None:
        """
        Gets a champion's skins from the cache database.
        
        ### Args:
            champion_id : `int`
                Champion ID.
        
        ### Returns:
            `list[Skin] | None` : Returns a list of `Skin` objects if found. Otherwise returns `None`.
        """
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        
        self.logger.debug(f"Getting skins for champion_id: {champion_id}...")
        
        self.cursor.execute(
            """
            SELECT *
            FROM tblSkins
            WHERE champion_id = ?;
            """, (champion_id,)
        )
        
        result = self.cursor.fetchall()
        self.conn.close()
        
        if result is None:
            self.logger.debug(f"No skins found for champion_id: {champion_id}.")
            return None
        
        self.logger.debug(f"Found skins for champion_id: {champion_id}.")
        return [Skin(
            champion_id=skin[0],
            id=skin[1],
            name=skin[2],
            centered_image=skin[3],
            skin_video_url=skin[4],
            prices=skin[5].split(',') if skin[5] else None,
            release_date=skin[6]
        ) for skin in result] 
    
    
    def insert_all_seasons(self, seasons: list[SeasonInfo], return_result: bool = False) -> None | str:
        """
        Inserts a list of seasons and their related attributes into the database.
        
        ### Args:
            seasons : `list[SeasonInfo]`
                A list of SeasonInfo objects to be cached.
        
        ### Returns:
            `None` | `str, optional` : Returns a string with the amount of rows affected if requested.
        """
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        total_rc = 0
        return_msg = "You've made changes to the database. Table: {table} | Rows affected: {count}"
        
        self.logger.debug(f"Attempting to insert {len(seasons)} seasons into cache database...")
        
        batch_seasons_insert: list[tuple] = []
        
        for season_info in seasons:
            batch_seasons_insert.append((
                season_info.id,
                season_info.value,
                season_info.display_value,
                season_info.split,
                season_info.is_preseason
            ))
        
        self.cursor.executemany(
            """
            INSERT OR IGNORE INTO tblSeasonInfo (season_id, season_value, season_display_name, season_split, season_is_preseason)
            VALUES (:1, :2, :3, :4, :5)
            """,
            batch_seasons_insert
        )
        
        total_rc += self.cursor.rowcount
        self.logger.debug(return_msg.format(table="tblSeasonInfo", count=self.cursor.rowcount))
        
        self.conn.commit()
        self.conn.close()
        
        return_msg = f"You've made several changes to the database. Total rows affected: {total_rc}"
        
        if return_result:
            return return_msg
        else:
            self.logger.info(return_msg)
        
    
    def get_all_seasons(self) -> list[SeasonInfo] | None:
        """
        Gets all seasons from the cache database and returns a list of SeasonInfo objects.
        
        ### Returns:
            `list[SeasonInfo]` | `None` : Returns a list of SeasonInfo objects if found. Otherwise returns `None`.
        """
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        all_seasons = []
        
        self.logger.info("Getting all seasons from cache database...")
        self.cursor.execute("SELECT * FROM tblSeasonInfo;")
        result = self.cursor.fetchall()
        
        if result is None:
            self.logger.info("No seasons found in cache database.")
            return None
        else:
            self.logger.info(f"Found {len(result)} seasons in cache database.")
            for i, season in enumerate(result):
                season_obj = SeasonInfo(
                    id=season[0],
                    value=season[1],
                    display_value=season[2],
                    split=season[3],
                    is_preseason=season[4] == 1 # boolean values are saved as 0 (false) or 1 (true)
                )
                all_seasons.append(season_obj)
                self.logger.debug(f"Successfully rebuilt the \"{season_obj.display_value}\" season object from cache. ({i+1}/{len(result)})")
                
            return all_seasons
    
    
    def drop_tables(self, tables: list[str]) -> None:
        """
        Drops all specified tables.
        
        ### Args:
            tables : `str`
                A list of table names to be deleted/dropped
        """
        self.conn = self.connect()
        self.cursor = self.conn.cursor()
        
        for table in tables:
            self.logger.debug(f"Dropping table \"{table}\" ...")
            self.cursor.execute(f"DROP TABLE IF EXISTS {table}")
        
        self.conn.commit()
        self.conn.close()
        
    
    def connect(self) -> sqlite3.Connection:
        """
        Connects to local database, if it doesn't exist, one will be created.
        
        ### Returns:
            `sqlite3.Connection` : Returns a connection object.
        """
        return sqlite3.connect(self.db_path)
