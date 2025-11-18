import os
import sqlite3
import logging
import json
import time

from opgg.champion import Champion
from opgg.params import LangCode, CacheType


class Cacher:
    """
    Cacher class for caching long-lived metadata (champions, seasons, etc.).

    ### Properties:
        `db_path` - Path to the database file.\n
        `logger` - Logger instance.
    """

    def __init__(self, db_path="./cache/opgg.py.db"):
        self.db_path = db_path
        self.logger = logging.getLogger("OPGG.py")

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _ensure_column(self, table: str, column: str, definition: str) -> None:
        """
        Ensure a column exists on the specified table, adding it if missing.
        """
        self.cursor.execute(f"PRAGMA table_info({table})")
        existing_columns = {info[1] for info in self.cursor.fetchall()}

        if column not in existing_columns:
            self.logger.info(f"Adding missing column '{column}' to table '{table}'")
            self.cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def setup(self) -> None:
        """
        Sets up the cache database and table(s).

        Runs at OPGG object creation.
        """
        if not os.path.exists("./cache"):
            self.logger.info("Creating cache directory...")
            os.mkdir("./cache")
            self.logger.info("Setting up cache database...")

        self.conn = self._connect()
        self.cursor = self.conn.cursor()

        # === CHAMPIONS TABLE ===
        self.logger.debug("Creating champions table if it doesn't exist...")
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tblChampions (
                champion_id PRIMARY KEY,
                name,
                lang_code,
                data,
                cached_at REAL
            );
            """
        )
        self._ensure_column("tblChampions", "lang_code", "TEXT")
        self._ensure_column("tblChampions", "data", "TEXT")
        self._ensure_column("tblChampions", "cached_at", "REAL")

        # Create indexes for tblChampions
        self.logger.debug("Creating indexes for tblChampions...")
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_champions_lang ON tblChampions(lang_code)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_champions_name ON tblChampions(name COLLATE NOCASE)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_champions_cached_at ON tblChampions(cached_at)"
        )

        # === SEASONS TABLE ===
        self.logger.debug("Creating seasons table if it doesn't exist...")
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tblSeasons (
                season_id INTEGER,
                lang_code TEXT,
                data TEXT,
                cached_at REAL,
                PRIMARY KEY (season_id, lang_code)
            );
            """
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_seasons_lang ON tblSeasons(lang_code)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_seasons_cached_at ON tblSeasons(cached_at)"
        )

        # === VERSIONS TABLE ===
        self.logger.debug("Creating versions table if it doesn't exist...")
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tblVersions (
                version TEXT,
                lang_code TEXT,
                data TEXT,
                cached_at REAL,
                PRIMARY KEY (version, lang_code)
            );
            """
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_versions_lang ON tblVersions(lang_code)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_versions_cached_at ON tblVersions(cached_at)"
        )

        # === KEYWORDS TABLE ===
        self.logger.debug("Creating keywords table if it doesn't exist...")
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tblKeywords (
                keyword TEXT,
                lang_code TEXT,
                data TEXT,
                cached_at REAL,
                PRIMARY KEY (keyword, lang_code)
            );
            """
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_keywords_lang ON tblKeywords(lang_code)"
        )
        self.cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_keywords_cached_at ON tblKeywords(cached_at)"
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
        champ_name = champ_name.lower()

        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT champion_id FROM tblChampions WHERE LOWER(name) LIKE ?",
                (f"%{champ_name}%",),
            )
            result = cursor.fetchone()

        if result is None:
            return None

        if isinstance(result, sqlite3.Row):
            return result["champion_id"]

        return result[0] if isinstance(result, tuple) else None

    def cache_champs(self, champs: list[Champion], lang_code: LangCode) -> None:
        """
        Cache champions in the database.

        Args:
            `champs` (`list[Champion]`): List of champions to cache
        """
        if not champs:
            return

        lang_value = (
            lang_code.value if isinstance(lang_code, LangCode) else str(lang_code)
        )
        payloads: list[tuple[int, str | None, str, str, float]] = []
        cached_at = time.time()

        for champ in champs:
            if champ.id is None:
                continue
            payloads.append(
                (
                    champ.id,
                    champ.name,
                    lang_value,
                    champ.model_dump_json(),
                    cached_at,
                )
            )

        if not payloads:
            self.logger.warning(
                "No champions with valid IDs were provided for caching."
            )
            return

        self.logger.debug(
            f"Attempting to upsert {len(payloads)} champions into cache database (lang={lang_value})..."
        )

        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO tblChampions (champion_id, name, lang_code, data, cached_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(champion_id) DO UPDATE SET
                    name = excluded.name,
                    lang_code = excluded.lang_code,
                    data = excluded.data,
                    cached_at = excluded.cached_at;
                """,
                payloads,
            )
            conn.commit()

        self.logger.debug(
            f"Successfully cached {len(payloads)} champions for lang={lang_value}."
        )

    def get_cached_champs_count(self, lang_code: LangCode | None = None) -> int:
        """
        Get the count of cached champions.

        Returns:
            `int`: The count of cached champions.
        """
        query = "SELECT COUNT(*) FROM tblChampions"
        params: list[str] = []

        if lang_code:
            query += " WHERE lang_code = ?"
            params.append(
                lang_code.value if isinstance(lang_code, LangCode) else str(lang_code)
            )

        with self._connect() as conn:
            cursor = conn.execute(query, params)
            result = cursor.fetchone()
            count = result[0] if result else 0

        self.logger.debug(
            f"Found {count} cached champions"
            + (f" for lang={lang_code}" if lang_code else "")
            + "."
        )

        return count

    def get_cached_champions(
        self, lang_code: LangCode, ttl_seconds: int | None = None
    ) -> list[Champion]:
        """
        Return all cached champions for the requested language, if available.
        """
        if ttl_seconds and self.is_champion_cache_stale(lang_code, ttl_seconds):
            self.logger.info(
                "Champion cache expired for lang=%s. Skipping cached data.", lang_code
            )
            return []

        lang_value = (
            lang_code.value if isinstance(lang_code, LangCode) else str(lang_code)
        )

        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT data FROM tblChampions
                WHERE lang_code = ? AND data IS NOT NULL
                """,
                (lang_value,),
            ).fetchall()

        champions: list[Champion] = []

        for row in rows:
            data = row[0] if not isinstance(row, sqlite3.Row) else row["data"]
            if not data:
                continue
            try:
                champions.append(Champion(**json.loads(data)))
            except Exception as exc:
                self.logger.error(f"Failed to rebuild Champion from cache: {exc}")

        return champions

    def get_cached_champion_by_id(
        self, champion_id: int, lang_code: LangCode, ttl_seconds: int | None = None
    ) -> Champion | None:
        """
        Return a cached champion entry by ID if the payload exists.
        """
        if ttl_seconds and self.is_champion_cache_stale(lang_code, ttl_seconds):
            return None

        lang_value = (
            lang_code.value if isinstance(lang_code, LangCode) else str(lang_code)
        )

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT data FROM tblChampions
                WHERE champion_id = ? AND lang_code = ? AND data IS NOT NULL
                """,
                (champion_id, lang_value),
            ).fetchone()

        if not row:
            return None

        data = row[0] if not isinstance(row, sqlite3.Row) else row["data"]
        if not data:
            return None

        try:
            return Champion(**json.loads(data))
        except Exception as exc:
            self.logger.error(
                f"Failed to rebuild Champion({champion_id}) from cache: {exc}"
            )
            return None

    def get_cached_champions_by_name(
        self,
        champ_name: str,
        lang_code: LangCode,
        ttl_seconds: int | None = None,
    ) -> list[Champion]:
        """
        Return cached champions that match the provided name fragment.
        """
        if ttl_seconds and self.is_champion_cache_stale(lang_code, ttl_seconds):
            return []

        lang_value = (
            lang_code.value if isinstance(lang_code, LangCode) else str(lang_code)
        )
        matcher = f"%{champ_name.lower()}%"

        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT data FROM tblChampions
                WHERE lang_code = ? AND data IS NOT NULL AND LOWER(name) LIKE ?
                """,
                (lang_value, matcher),
            ).fetchall()

        champions: list[Champion] = []

        for row in rows:
            data = row[0] if not isinstance(row, sqlite3.Row) else row["data"]
            if not data:
                continue
            try:
                champions.append(Champion(**json.loads(data)))
            except Exception as exc:
                self.logger.error(f"Failed to rebuild cached champion: {exc}")

        return champions

    def get_champion_cache_timestamp(
        self, lang_code: LangCode | None = None
    ) -> float | None:
        """
        Return the latest cached_at timestamp for champions, optionally scoped by language.
        """
        query = "SELECT MAX(cached_at) FROM tblChampions"
        params: list[str] = []

        if lang_code:
            query += " WHERE lang_code = ?"
            params.append(
                lang_code.value if isinstance(lang_code, LangCode) else str(lang_code)
            )

        with self._connect() as conn:
            row = conn.execute(query, params).fetchone()

        if not row:
            return None

        timestamp = row[0]
        return float(timestamp) if timestamp is not None else None

    def is_champion_cache_stale(
        self, lang_code: LangCode, ttl_seconds: int | None
    ) -> bool:
        if not ttl_seconds:
            return False

        last_cached = self.get_champion_cache_timestamp(lang_code)
        if last_cached is None:
            return True

        return (time.time() - last_cached) > ttl_seconds

    # === SEASONS CACHING ===

    def cache_seasons(self, seasons_data: dict, lang_code: LangCode) -> None:
        """
        Cache seasons data in the database.

        Args:
            `seasons_data` (`dict`): Dictionary containing season information
            `lang_code` (`LangCode`): Language code for the data
        """
        if not seasons_data:
            return

        lang_value = (
            lang_code.value if isinstance(lang_code, LangCode) else str(lang_code)
        )
        cached_at = time.time()

        # seasons_data is expected to be a dict with season info
        # We'll store the entire dict as JSON
        payloads: list[tuple[int, str, str, float]] = []

        # If seasons_data has a 'seasons' list, iterate over it
        if isinstance(seasons_data, dict) and "seasons" in seasons_data:
            for season in seasons_data.get("seasons", []):
                season_id = season.get("id")
                if season_id is not None:
                    payloads.append(
                        (season_id, lang_value, json.dumps(season), cached_at)
                    )
        elif isinstance(seasons_data, list):
            # If it's a list of seasons directly
            for season in seasons_data:
                season_id = season.get("id")
                if season_id is not None:
                    payloads.append(
                        (season_id, lang_value, json.dumps(season), cached_at)
                    )

        if not payloads:
            self.logger.warning("No valid season data provided for caching.")
            return

        self.logger.debug(
            f"Attempting to upsert {len(payloads)} seasons into cache database (lang={lang_value})..."
        )

        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO tblSeasons (season_id, lang_code, data, cached_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(season_id, lang_code) DO UPDATE SET
                    data = excluded.data,
                    cached_at = excluded.cached_at;
                """,
                payloads,
            )
            conn.commit()

        self.logger.debug(
            f"Successfully cached {len(payloads)} seasons for lang={lang_value}."
        )

    def get_cached_seasons(
        self, lang_code: LangCode, ttl_seconds: int | None = None
    ) -> list[dict] | None:
        """
        Return cached seasons for the requested language, if available.

        Args:
            `lang_code` (`LangCode`): Language code
            `ttl_seconds` (`int | None`): Time-to-live in seconds

        Returns:
            `list[dict] | None`: Cached seasons data or None
        """
        if ttl_seconds and self.is_seasons_cache_stale(lang_code, ttl_seconds):
            self.logger.info(
                "Seasons cache expired for lang=%s. Skipping cached data.", lang_code
            )
            return None

        lang_value = (
            lang_code.value if isinstance(lang_code, LangCode) else str(lang_code)
        )

        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT data FROM tblSeasons
                WHERE lang_code = ? AND data IS NOT NULL
                """,
                (lang_value,),
            ).fetchall()

        if not rows:
            return None

        seasons = []
        for row in rows:
            data = row[0] if not isinstance(row, sqlite3.Row) else row["data"]
            if data:
                try:
                    seasons.append(json.loads(data))
                except Exception as exc:
                    self.logger.error(f"Failed to parse season data from cache: {exc}")

        return seasons or None

    def get_seasons_cache_timestamp(
        self, lang_code: LangCode | None = None
    ) -> float | None:
        """
        Return the latest cached_at timestamp for seasons, optionally scoped by language.

        Args:
            `lang_code` (`LangCode | None`): Optional language code

        Returns:
            `float | None`: Timestamp or None
        """
        query = "SELECT MAX(cached_at) FROM tblSeasons"
        params: list[str] = []

        if lang_code:
            query += " WHERE lang_code = ?"
            params.append(
                lang_code.value if isinstance(lang_code, LangCode) else str(lang_code)
            )

        with self._connect() as conn:
            row = conn.execute(query, params).fetchone()

        if not row:
            return None

        timestamp = row[0]
        return float(timestamp) if timestamp is not None else None

    def is_seasons_cache_stale(
        self, lang_code: LangCode, ttl_seconds: int | None
    ) -> bool:
        """
        Check if seasons cache is stale for given language.

        Args:
            `lang_code` (`LangCode`): Language code
            `ttl_seconds` (`int | None`): Time-to-live in seconds

        Returns:
            `bool`: True if stale, False otherwise
        """
        if not ttl_seconds:
            return False

        last_cached = self.get_seasons_cache_timestamp(lang_code)
        if last_cached is None:
            return True

        return (time.time() - last_cached) > ttl_seconds

    # === KEYWORDS CACHING ===

    def cache_keywords(
        self, keywords_data: list[dict] | dict, lang_code: LangCode
    ) -> None:
        """
        Cache keyword metadata in the database.

        Args:
            `keywords_data` (`list[dict] | dict`): Keyword entries to store
            `lang_code` (`LangCode`): Language code for the data
        """
        if not keywords_data:
            return

        if isinstance(keywords_data, dict):
            if isinstance(keywords_data.get("data"), list):
                keywords_list = keywords_data.get("data", [])
            elif isinstance(keywords_data.get("keywords"), list):
                keywords_list = keywords_data.get("keywords", [])
            else:
                keywords_list = []
        else:
            keywords_list = keywords_data

        if not isinstance(keywords_list, list):
            self.logger.warning("Keyword payload is not a list; skipping cache update.")
            return

        lang_value = (
            lang_code.value if isinstance(lang_code, LangCode) else str(lang_code)
        )
        cached_at = time.time()

        payloads: list[tuple[str, str, str, float]] = []
        for keyword in keywords_list:
            keyword_key = keyword.get("keyword")
            if not keyword_key:
                continue
            payloads.append((keyword_key, lang_value, json.dumps(keyword), cached_at))

        if not payloads:
            self.logger.warning("No valid keyword entries provided for caching.")
            return

        self.logger.debug(
            "Upserting %d keywords into cache database (lang=%s)...",
            len(payloads),
            lang_value,
        )

        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO tblKeywords (keyword, lang_code, data, cached_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(keyword, lang_code) DO UPDATE SET
                    data = excluded.data,
                    cached_at = excluded.cached_at;
                """,
                payloads,
            )
            conn.commit()

        self.logger.debug(
            "Successfully cached %d keyword entries for lang=%s.",
            len(payloads),
            lang_value,
        )

    def get_cached_keywords(
        self, lang_code: LangCode, ttl_seconds: int | None = None
    ) -> list[dict] | None:
        """
        Return cached keywords for the requested language, if available.

        Args:
            `lang_code` (`LangCode`): Language code
            `ttl_seconds` (`int | None`): TTL in seconds

        Returns:
            `list[dict] | None`: Keyword entries or None
        """
        if ttl_seconds and self.is_keywords_cache_stale(lang_code, ttl_seconds):
            self.logger.info(
                "Keyword cache expired for lang=%s. Skipping cached data.", lang_code
            )
            return None

        lang_value = (
            lang_code.value if isinstance(lang_code, LangCode) else str(lang_code)
        )

        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT data FROM tblKeywords
                WHERE lang_code = ? AND data IS NOT NULL
                """,
                (lang_value,),
            ).fetchall()

        keywords: list[dict] = []
        for row in rows:
            data = row[0] if not isinstance(row, sqlite3.Row) else row["data"]
            if not data:
                continue
            try:
                keywords.append(json.loads(data))
            except Exception as exc:
                self.logger.error(f"Failed to parse keyword data from cache: {exc}")

        return keywords or None

    def get_keywords_cache_timestamp(
        self, lang_code: LangCode | None = None
    ) -> float | None:
        """
        Return the latest cached_at timestamp for keywords, optionally scoped by language.
        """
        query = "SELECT MAX(cached_at) FROM tblKeywords"
        params: list[str] = []

        if lang_code:
            query += " WHERE lang_code = ?"
            params.append(
                lang_code.value if isinstance(lang_code, LangCode) else str(lang_code)
            )

        with self._connect() as conn:
            row = conn.execute(query, params).fetchone()

        if not row:
            return None

        timestamp = row[0]
        return float(timestamp) if timestamp is not None else None

    def is_keywords_cache_stale(
        self, lang_code: LangCode, ttl_seconds: int | None
    ) -> bool:
        """
        Check if keywords cache is stale for given language.
        """
        if not ttl_seconds:
            return False

        last_cached = self.get_keywords_cache_timestamp(lang_code)
        if last_cached is None:
            return True

        return (time.time() - last_cached) > ttl_seconds

    # === VERSIONS CACHING ===

    def cache_versions(self, versions_data: dict | list, lang_code: LangCode) -> None:
        """
        Cache versions data in the database.

        Args:
            `versions_data` (`dict | list`): Dictionary or list containing version information
            `lang_code` (`LangCode`): Language code for the data
        """
        if not versions_data:
            return

        lang_value = (
            lang_code.value if isinstance(lang_code, LangCode) else str(lang_code)
        )
        cached_at = time.time()

        # versions_data can be either a list or dict
        # Store as a single entry with "latest" as the key
        version_key = "latest"

        payload = (version_key, lang_value, json.dumps(versions_data), cached_at)

        self.logger.debug(
            f"Attempting to upsert versions data into cache database (lang={lang_value})..."
        )

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO tblVersions (version, lang_code, data, cached_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(version, lang_code) DO UPDATE SET
                    data = excluded.data,
                    cached_at = excluded.cached_at;
                """,
                payload,
            )
            conn.commit()

        self.logger.debug(f"Successfully cached versions data for lang={lang_value}.")

    def get_cached_versions(
        self, lang_code: LangCode, ttl_seconds: int | None = None
    ) -> dict | list | None:
        """
        Return cached versions for the requested language, if available.

        Args:
            `lang_code` (`LangCode`): Language code
            `ttl_seconds` (`int | None`): Time-to-live in seconds

        Returns:
            `dict | list | None`: Dictionary or list containing versions data, or None
        """
        if ttl_seconds and self.is_versions_cache_stale(lang_code, ttl_seconds):
            self.logger.info(
                "Versions cache expired for lang=%s. Skipping cached data.", lang_code
            )
            return None

        lang_value = (
            lang_code.value if isinstance(lang_code, LangCode) else str(lang_code)
        )

        with self._connect() as conn:
            # Get the most recent version entry for this language
            row = conn.execute(
                """
                SELECT data FROM tblVersions
                WHERE lang_code = ? AND data IS NOT NULL
                ORDER BY cached_at DESC
                LIMIT 1
                """,
                (lang_value,),
            ).fetchone()

        if not row:
            return None

        data = row[0] if not isinstance(row, sqlite3.Row) else row["data"]
        if not data:
            return None

        try:
            return json.loads(data)
        except Exception as exc:
            self.logger.error(f"Failed to parse versions data from cache: {exc}")
            return None

    def get_versions_cache_timestamp(
        self, lang_code: LangCode | None = None
    ) -> float | None:
        """
        Return the latest cached_at timestamp for versions, optionally scoped by language.

        Args:
            `lang_code` (`LangCode | None`): Optional language code

        Returns:
            `float | None`: Timestamp or None
        """
        query = "SELECT MAX(cached_at) FROM tblVersions"
        params: list[str] = []

        if lang_code:
            query += " WHERE lang_code = ?"
            params.append(
                lang_code.value if isinstance(lang_code, LangCode) else str(lang_code)
            )

        with self._connect() as conn:
            row = conn.execute(query, params).fetchone()

        if not row:
            return None

        timestamp = row[0]
        return float(timestamp) if timestamp is not None else None

    def is_versions_cache_stale(
        self, lang_code: LangCode, ttl_seconds: int | None
    ) -> bool:
        """
        Check if versions cache is stale for given language.

        Args:
            `lang_code` (`LangCode`): Language code
            `ttl_seconds` (`int | None`): Time-to-live in seconds

        Returns:
            `bool`: True if stale, False otherwise
        """
        if not ttl_seconds:
            return False

        last_cached = self.get_versions_cache_timestamp(lang_code)
        if last_cached is None:
            return True

        return (time.time() - last_cached) > ttl_seconds

    # === CACHE MANAGEMENT UTILITIES ===

    def get_cache_stats(self) -> dict:
        """
        Get statistics about cached data.

        Returns:
            `dict`: Dictionary containing cache statistics
        """
        stats = {
            "champions": {
                "total_count": 0,
                "languages": [],
                "oldest_cache": None,
                "newest_cache": None,
            },
            "seasons": {
                "total_count": 0,
                "languages": [],
                "oldest_cache": None,
                "newest_cache": None,
            },
            "versions": {
                "total_count": 0,
                "languages": [],
                "oldest_cache": None,
                "newest_cache": None,
            },
            "keywords": {
                "total_count": 0,
                "languages": [],
                "oldest_cache": None,
                "newest_cache": None,
            },
        }

        with self._connect() as conn:
            # Champions stats
            champ_row = conn.execute(
                "SELECT COUNT(*), MIN(cached_at), MAX(cached_at) FROM tblChampions"
            ).fetchone()
            if champ_row:
                stats["champions"]["total_count"] = champ_row[0]
                stats["champions"]["oldest_cache"] = champ_row[1]
                stats["champions"]["newest_cache"] = champ_row[2]

            champ_langs = conn.execute(
                "SELECT DISTINCT lang_code FROM tblChampions"
            ).fetchall()
            stats["champions"]["languages"] = [row[0] for row in champ_langs]

            # Seasons stats
            season_row = conn.execute(
                "SELECT COUNT(*), MIN(cached_at), MAX(cached_at) FROM tblSeasons"
            ).fetchone()
            if season_row:
                stats["seasons"]["total_count"] = season_row[0]
                stats["seasons"]["oldest_cache"] = season_row[1]
                stats["seasons"]["newest_cache"] = season_row[2]

            season_langs = conn.execute(
                "SELECT DISTINCT lang_code FROM tblSeasons"
            ).fetchall()
            stats["seasons"]["languages"] = [row[0] for row in season_langs]

            # Versions stats
            version_row = conn.execute(
                "SELECT data, MIN(cached_at), MAX(cached_at) FROM tblVersions"
            ).fetchone()
            if version_row and version_row[0]:
                # Count actual versions in the JSON array, not database rows
                version_data = json.loads(version_row[0])
                version_count = (
                    len(version_data) if isinstance(version_data, list) else 1
                )
                stats["versions"]["total_count"] = version_count
                stats["versions"]["oldest_cache"] = version_row[1]
                stats["versions"]["newest_cache"] = version_row[2]

            version_langs = conn.execute(
                "SELECT DISTINCT lang_code FROM tblVersions"
            ).fetchall()
            stats["versions"]["languages"] = [row[0] for row in version_langs]

            # Keywords stats
            keyword_row = conn.execute(
                "SELECT COUNT(*), MIN(cached_at), MAX(cached_at) FROM tblKeywords"
            ).fetchone()
            if keyword_row:
                stats["keywords"]["total_count"] = keyword_row[0]
                stats["keywords"]["oldest_cache"] = keyword_row[1]
                stats["keywords"]["newest_cache"] = keyword_row[2]

            keyword_langs = conn.execute(
                "SELECT DISTINCT lang_code FROM tblKeywords"
            ).fetchall()
            stats["keywords"]["languages"] = [row[0] for row in keyword_langs]

        return stats

    def clear_cache(
        self, cache_type: CacheType = CacheType.ALL, lang_code: LangCode | None = None
    ) -> dict:
        """
        Clear cached data.

        Args:
            `cache_type` (`CacheType`): Type of cache to clear (default: CacheType.ALL)
            `lang_code` (`LangCode | None`): Optional language code to limit clearing to specific language

        Returns:
            `dict`: Dictionary with counts of cleared items
        """
        cache_type_value = (
            cache_type.value if isinstance(cache_type, CacheType) else str(cache_type)
        )

        cleared = {"champions": 0, "seasons": 0, "versions": 0, "keywords": 0}
        lang_value = (
            lang_code.value
            if isinstance(lang_code, LangCode)
            else None
            if lang_code is None
            else str(lang_code)
        )

        with self._connect() as conn:
            if cache_type_value in ["all", "champions"]:
                if lang_value:
                    result = conn.execute(
                        "DELETE FROM tblChampions WHERE lang_code = ?", (lang_value,)
                    )
                else:
                    result = conn.execute("DELETE FROM tblChampions")
                cleared["champions"] = result.rowcount
                self.logger.info(
                    f"Cleared {cleared['champions']} champion entries"
                    + (f" for lang={lang_value}" if lang_value else "")
                )

            if cache_type_value in ["all", "seasons"]:
                if lang_value:
                    result = conn.execute(
                        "DELETE FROM tblSeasons WHERE lang_code = ?", (lang_value,)
                    )
                else:
                    result = conn.execute("DELETE FROM tblSeasons")
                cleared["seasons"] = result.rowcount
                self.logger.info(
                    f"Cleared {cleared['seasons']} season entries"
                    + (f" for lang={lang_value}" if lang_value else "")
                )

            if cache_type_value in ["all", "versions"]:
                if lang_value:
                    result = conn.execute(
                        "DELETE FROM tblVersions WHERE lang_code = ?", (lang_value,)
                    )
                else:
                    result = conn.execute("DELETE FROM tblVersions")
                cleared["versions"] = result.rowcount
                self.logger.info(
                    f"Cleared {cleared['versions']} version entries"
                    + (f" for lang={lang_value}" if lang_value else "")
                )

            if cache_type_value in ["all", "keywords"]:
                if lang_value:
                    result = conn.execute(
                        "DELETE FROM tblKeywords WHERE lang_code = ?", (lang_value,)
                    )
                else:
                    result = conn.execute("DELETE FROM tblKeywords")
                cleared["keywords"] = result.rowcount
                self.logger.info(
                    f"Cleared {cleared['keywords']} keyword entries"
                    + (f" for lang={lang_value}" if lang_value else "")
                )

            conn.commit()

        return cleared
