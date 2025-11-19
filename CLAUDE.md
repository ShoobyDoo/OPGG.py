# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OPGG.py is an unofficial Python library for accessing OPGG data via their undocumented API. It provides async methods for fetching League of Legends summoner profiles, match history, champion statistics, and metadata with built-in SQLite caching.

## Development Commands

### Installation
```bash
# Install production dependencies
pip install -r requirements.txt
```

### Code Quality
```bash
# Run linting
ruff check opgg/

# Auto-fix linting issues
ruff check --fix opgg/

# Check code formatting
ruff format --check opgg/

# Auto-format code
ruff format opgg/
```

### Testing
Run individual test files directly with pytest or Python:
```bash
# Using pytest (if installed)
pytest tests/test_filename.py

# Using Python directly
python -m pytest tests/test_filename.py

# Run specific test
python -m pytest tests/test_filename.py::TestClass::test_method -v
```

## Architecture

### Core Design Patterns

1. **Async-First Architecture**: All API calls use `asyncio` + `aiohttp` for concurrent requests. Public methods in `OPGG` class wrap async utility functions with `asyncio.run()`.

2. **Caching Layer**: SQLite-based caching (`opgg/cacher.py`) stores long-lived metadata:
   - Champions (multi-language support)
   - Seasons metadata
   - Game versions
   - Keywords (for OP Score analysis)
   - Configurable TTL via `OPGG_CHAMPION_CACHE_TTL` env var or `.champion_cache_ttl` property

3. **Pydantic Models**: All data structures use Pydantic for validation and serialization:
   - `Summoner` - Player profile data
   - `Game` - Match history entries
   - `Champion` - Champion metadata
   - `SeasonMeta` - Season information
   - `SearchResult` - Wrapper containing Summoner + Region
   - `Keyword` - OP Score keyword definitions

### Key Components

**`opgg/opgg.py`** - Main library class containing:
- `search()` - Find summoners by Riot ID (supports fuzzy matching)
- `get_summoner()` - Fetch full summoner profile
- `get_recent_games()` - Retrieve match history
- `get_all_champions()` - Fetch champion roster (cached)
- `get_champion_by()` - Get champion by ID or name
- `get_champion_stats()` - Ranked stats by tier/region/version
- `get_all_seasons()`, `get_versions()`, `get_keywords()` - Metadata endpoints
- `force_refresh_cache()`, `clear_cache()`, `get_cache_stats()` - Cache management

**`opgg/cacher.py`** - SQLite caching system:
- Database location: `./cache/opgg.py.db`
- Tables: `tblChampions`, `tblSeasons`, `tblVersions`, `tblKeywords`
- Supports per-language caching
- TTL-based staleness checking

**`opgg/utils.py`** - Async utilities:
- `_search_region()`, `_search_all_regions()` - Region-specific searches
- `_fetch_profile()`, `_fetch_profile_multiple()` - Summoner profile fetching
- `_fetch_recent_games()`, `_fetch_recent_games_multiple()` - Game history
- `_fetch_all_champions()`, `_fetch_champion_by_id()` - Champion data
- All methods use aiohttp sessions with proper error handling

**`opgg/params.py`** - Enums and type definitions:
- `Region` - Game regions (NA, EUW, KR, etc.) + `Region.ANY` for multi-region search
- `LangCode` - Language codes for localization
- `GameType` - Filter for game types (TOTAL, RANKED, NORMAL, ARAM, etc.)
- `Queue`, `Tier`, `StatsRegion`, `By`, `CacheType`, `SearchReturnType`

### API Endpoint Structure

The library consumes two base URLs:
- Summoner API: `https://lol-api-summoner.op.gg/api`
- Champion API: `https://lol-api-champion.op.gg/api`

All endpoints require:
- Region parameter (e.g., "na", "kr")
- Language code parameter (`hl` query param, default: en_US)
- Random User-Agent header (via `fake-useragent`)

### Logging

- Logger name: `OPGG.py`
- Log directory: `./logs/`
- Log files: `opgg_YYYY-MM-DD.log`
- Default level: INFO
- Empty log files are auto-cleaned on initialization

## Common Patterns

### Region Handling
- Most methods accept `Region` enum or string
- `Region.ANY` triggers concurrent multi-region search (resource-intensive)
- Always prefer specific region when known

### Language Support
- All metadata methods accept `LangCode` parameter
- Cache is language-scoped (can have same champion in multiple languages)
- Default: `LangCode.ENGLISH`

### Flexible Input Patterns
Methods like `get_summoner()` and `get_recent_games()` support multiple input types:
```python
# Via SearchResult object
summoner = opgg.get_summoner(search_result)

# Via summoner_id + region
summoner = opgg.get_summoner(summoner_id="abc123", region=Region.NA)

# Batch processing (list of SearchResults)
summoners = opgg.get_summoner([result1, result2, result3])
```

### Cache Management
- Champion cache defaults to 1 week TTL
- Use `force_refresh=True` to bypass cache
- Use `force_refresh_cache()` for bulk cache refresh
- Use `clear_cache()` to remove stale data

## Important Notes

### Summoner ID Validation
The codebase actively filters out search results missing `summoner_id` fields. This is critical because OPGG API occasionally returns incomplete data. Check `Utils.filter_results_with_summoner_id()` for implementation details.

### Season Metadata Attachment
When fetching summoner profiles, the library automatically enriches previous season data with `SeasonMeta` objects (display names, split info, etc.). This happens via `_attach_season_meta()` internal method.

### Concurrency Best Practices
- When fetching multiple summoners or games, pass lists to leverage async batch processing
- Single-item calls still work but miss concurrency benefits
- Example: `get_summoner([sr1, sr2, sr3])` is faster than 3 separate calls

### Testing Considerations
- Tests should mock aiohttp responses to avoid hitting live API
- Use `pytest-aiohttp` or similar for async test support
- Cache tests should use isolated test database or in-memory SQLite

## Environment Variables

- `OPGG_CHAMPION_CACHE_TTL` - Champion cache TTL in seconds (default: 604800 = 1 week)

## Code Style

- Follow Python 3.12+ syntax (match statements, type hints, etc.)
- Use async/await for all I/O operations
- Pydantic models for data validation
- Comprehensive logging at appropriate levels
- Type hints on all public methods
