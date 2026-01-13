"""Tests for error handling and edge cases."""

import re

import pytest
from aiohttp import ContentTypeError

from opgg import OPGG
from opgg.exceptions import (
    ClientHTTPError,
    NotFoundError,
    OPGGJSONDecodeError,
    RateLimitError,
    ServerHTTPError,
)
from opgg.params import By, Region, SearchReturnType
from opgg.search_result import SearchResult
from opgg.summoner import Summoner

# Case-insensitive URL patterns
SEARCH_URL_PATTERN = re.compile(r".*v3/.*/summoners\?.*", re.IGNORECASE)
PROFILE_URL_PATTERN = re.compile(r".*/summoners/.*/summary.*", re.IGNORECASE)
CHAMPIONS_URL_PATTERN = re.compile(r".*meta/champions\?.*", re.IGNORECASE)


@pytest.fixture
def opgg(temp_db):
    """Create OPGG instance with isolated test database."""
    instance = OPGG()
    instance._cacher.db_path = temp_db
    instance._cacher.setup()
    return instance


class TestHTTPErrorHandling:
    """Test HTTP error handling for various status codes."""

    def test_404_raises_not_found_error(self, opgg, mock_aiohttp):
        """Test 404 response raises NotFoundError."""
        mock_aiohttp.get(
            PROFILE_URL_PATTERN,
            status=404,
            payload={"message": "Summoner not found"},
        )

        search_result = SearchResult(
            summoner=Summoner(summoner_id="nonexistent"),
            region=Region.NA,
        )

        with pytest.raises(NotFoundError):
            opgg.get_summoner(search_result)

    def test_429_raises_rate_limit_error(self, opgg, mock_aiohttp):
        """Test 429 response raises RateLimitError."""
        mock_aiohttp.get(
            re.compile(r".*summoners\?.*riot_id.*"),
            status=429,
            headers={"Retry-After": "60"},
            payload={"message": "Rate limited"},
        )

        with pytest.raises(RateLimitError) as exc_info:
            opgg.search("TestPlayer", Region.NA, SearchReturnType.SIMPLE)

        assert exc_info.value.status_code == 429

    def test_429_includes_retry_after(self, opgg, mock_aiohttp):
        """Test RateLimitError includes retry_after from header."""
        mock_aiohttp.get(
            re.compile(r".*summoners\?.*riot_id.*"),
            status=429,
            headers={"Retry-After": "120"},
            payload={"message": "Rate limited"},
        )

        with pytest.raises(RateLimitError) as exc_info:
            opgg.search("TestPlayer", Region.NA, SearchReturnType.SIMPLE)

        # retry_after should be parsed from header
        assert exc_info.value.retry_after is not None

    def test_400_raises_client_error(self, opgg, mock_aiohttp):
        """Test 400 Bad Request raises ClientHTTPError."""
        mock_aiohttp.get(
            SEARCH_URL_PATTERN,
            status=400,
            payload={"message": "Bad Request"},
        )

        with pytest.raises(ClientHTTPError) as exc_info:
            opgg.search("", Region.NA, SearchReturnType.SIMPLE)

        assert exc_info.value.status_code == 400

    def test_403_raises_client_error(self, opgg, mock_aiohttp):
        """Test 403 Forbidden raises ClientHTTPError."""
        mock_aiohttp.get(
            re.compile(r".*summoners\?.*riot_id.*"),
            status=403,
            payload={"message": "Forbidden"},
        )

        with pytest.raises(ClientHTTPError) as exc_info:
            opgg.search("TestPlayer", Region.NA, SearchReturnType.SIMPLE)

        assert exc_info.value.status_code == 403

    def test_500_raises_server_error(self, opgg, mock_aiohttp):
        """Test 500 Internal Server Error raises ServerHTTPError."""
        mock_aiohttp.get(
            re.compile(r".*summoners\?.*riot_id.*"),
            status=500,
            payload={"error": "Internal server error"},
        )

        with pytest.raises(ServerHTTPError) as exc_info:
            opgg.search("TestPlayer", Region.NA, SearchReturnType.SIMPLE)

        assert exc_info.value.status_code == 500

    def test_503_raises_server_error(self, opgg, mock_aiohttp):
        """Test 503 Service Unavailable raises ServerHTTPError."""
        mock_aiohttp.get(
            re.compile(r".*summoners\?.*riot_id.*"),
            status=503,
            payload={"error": "Service temporarily unavailable"},
        )

        with pytest.raises(ServerHTTPError) as exc_info:
            opgg.search("TestPlayer", Region.NA, SearchReturnType.SIMPLE)

        assert exc_info.value.status_code == 503


@pytest.mark.asyncio
class TestAsyncHTTPErrorHandling:
    """Test HTTP error handling in async methods."""

    async def test_async_404_raises_not_found(self, mock_aiohttp):
        """Test async 404 response raises NotFoundError."""
        mock_aiohttp.get(
            PROFILE_URL_PATTERN,
            status=404,
            payload={"message": "Not found"},
        )

        async with OPGG() as opgg:
            search_result = SearchResult(
                summoner=Summoner(summoner_id="nonexistent"),
                region=Region.NA,
            )

            with pytest.raises(NotFoundError):
                await opgg.get_summoner_async(search_result)

    async def test_async_429_raises_rate_limit(self, mock_aiohttp):
        """Test async 429 response raises RateLimitError."""
        mock_aiohttp.get(
            re.compile(r".*summoners\?.*riot_id.*"),
            status=429,
            headers={"Retry-After": "60"},
            payload={"message": "Rate limited"},
        )

        async with OPGG() as opgg:
            with pytest.raises(RateLimitError):
                await opgg.search_async("TestPlayer", Region.NA, SearchReturnType.SIMPLE)

    async def test_async_500_raises_server_error(self, mock_aiohttp):
        """Test async 500 response raises ServerHTTPError."""
        mock_aiohttp.get(
            re.compile(r".*summoners\?.*riot_id.*"),
            status=500,
            payload={"error": "Internal error"},
        )

        async with OPGG() as opgg:
            with pytest.raises(ServerHTTPError):
                await opgg.search_async("TestPlayer", Region.NA, SearchReturnType.SIMPLE)


class TestResponseParsingErrors:
    """Test response parsing error handling."""

    def test_malformed_json_raises_decode_error(self, opgg, mock_aiohttp):
        """Test malformed JSON response raises OPGGJSONDecodeError."""
        mock_aiohttp.get(
            re.compile(r".*summoners\?.*riot_id.*"),
            status=200,
            body="not valid json {{{",
            content_type="application/json",
        )

        with pytest.raises((OPGGJSONDecodeError, ContentTypeError)):
            opgg.search("TestPlayer", Region.NA, SearchReturnType.SIMPLE)

    def test_empty_response_handled(self, opgg, mock_aiohttp):
        """Test empty response is handled gracefully."""
        mock_aiohttp.get(
            re.compile(r".*summoners\?.*riot_id.*"),
            status=200,
            payload={},
        )

        # Empty response should return empty list, not crash
        results = opgg.search("TestPlayer", Region.NA, SearchReturnType.SIMPLE)
        assert results == []


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_search_with_special_characters(
        self, opgg, mock_aiohttp, fixture_search_single
    ):
        """Test search handles special characters in names."""
        mock_aiohttp.get(
            re.compile(r".*summoners\?.*riot_id.*"),
            payload=fixture_search_single,
        )

        # Special characters should be URL encoded
        results = opgg.search("Player#NA1", Region.NA, SearchReturnType.SIMPLE)

        assert isinstance(results, list)

    def test_search_with_unicode_characters(
        self, opgg, mock_aiohttp, fixture_search_single
    ):
        """Test search handles unicode characters."""
        mock_aiohttp.get(
            re.compile(r".*summoners\?.*riot_id.*"),
            payload=fixture_search_single,
        )

        # Korean characters should work
        results = opgg.search("플레이어", Region.KR, SearchReturnType.SIMPLE)

        assert isinstance(results, list)

    def test_champion_not_found_by_invalid_name(
        self, opgg, mock_aiohttp, fixture_champions_all
    ):
        """Test get_champion_by raises ValueError for nonexistent name."""
        mock_aiohttp.get(
            re.compile(r".*meta/champions\?hl=.*"),
            payload=fixture_champions_all,
        )

        with pytest.raises(ValueError):
            opgg.get_champion_by(By.NAME, "NonExistentChampion123")

    def test_very_long_summoner_name(
        self, opgg, mock_aiohttp, fixture_search_empty
    ):
        """Test handling of very long summoner names."""
        mock_aiohttp.get(
            re.compile(r".*summoners\?.*riot_id.*"),
            payload=fixture_search_empty,
        )

        # Very long name should be handled (even if returns empty)
        long_name = "A" * 100
        results = opgg.search(long_name, Region.NA, SearchReturnType.SIMPLE)

        assert isinstance(results, list)


class TestErrorAttributes:
    """Test error exception attributes are set correctly."""

    def test_http_error_has_status_code(self, opgg, mock_aiohttp):
        """Test HTTPError exceptions include status code."""
        mock_aiohttp.get(
            re.compile(r".*summoners\?.*riot_id.*"),
            status=500,
            payload={"error": "test"},
        )

        with pytest.raises(ServerHTTPError) as exc_info:
            opgg.search("Test", Region.NA, SearchReturnType.SIMPLE)

        assert hasattr(exc_info.value, "status_code")
        assert exc_info.value.status_code == 500

    def test_http_error_has_url(self, opgg, mock_aiohttp):
        """Test HTTPError exceptions include URL."""
        mock_aiohttp.get(
            re.compile(r".*summoners\?.*riot_id.*"),
            status=500,
            payload={"error": "test"},
        )

        with pytest.raises(ServerHTTPError) as exc_info:
            opgg.search("Test", Region.NA, SearchReturnType.SIMPLE)

        assert hasattr(exc_info.value, "url")

    def test_not_found_error_has_resource_type(self, opgg, mock_aiohttp):
        """Test NotFoundError includes resource type."""
        mock_aiohttp.get(
            PROFILE_URL_PATTERN,
            status=404,
            payload={"message": "Not found"},
        )

        search_result = SearchResult(
            summoner=Summoner(summoner_id="test"),
            region=Region.NA,
        )

        with pytest.raises(NotFoundError) as exc_info:
            opgg.get_summoner(search_result)

        assert hasattr(exc_info.value, "resource_type")

    def test_rate_limit_error_has_retry_after(self, opgg, mock_aiohttp):
        """Test RateLimitError includes retry_after attribute."""
        mock_aiohttp.get(
            re.compile(r".*summoners\?.*riot_id.*"),
            status=429,
            headers={"Retry-After": "45"},
            payload={"message": "Rate limited"},
        )

        with pytest.raises(RateLimitError) as exc_info:
            opgg.search("Test", Region.NA, SearchReturnType.SIMPLE)

        assert hasattr(exc_info.value, "retry_after")


class TestExceptionHierarchy:
    """Test exception inheritance for proper exception handling."""

    def test_not_found_is_http_error(self):
        """Test NotFoundError inherits from HTTPError."""
        error = NotFoundError(resource_type="summoner", resource_id="test123")
        from opgg.exceptions import HTTPError

        assert isinstance(error, HTTPError)

    def test_rate_limit_is_http_error(self):
        """Test RateLimitError inherits from HTTPError."""
        error = RateLimitError(retry_after=60)
        from opgg.exceptions import HTTPError

        assert isinstance(error, HTTPError)

    def test_server_error_is_http_error(self):
        """Test ServerHTTPError inherits from HTTPError."""
        error = ServerHTTPError(message="Server error", status_code=500)
        from opgg.exceptions import HTTPError

        assert isinstance(error, HTTPError)

    def test_client_error_is_http_error(self):
        """Test ClientHTTPError inherits from HTTPError."""
        error = ClientHTTPError(message="Bad request", status_code=400)
        from opgg.exceptions import HTTPError

        assert isinstance(error, HTTPError)

    def test_all_errors_are_opgg_error(self):
        """Test all custom exceptions inherit from OPGGError."""
        from opgg.exceptions import OPGGError

        errors = [
            NotFoundError(resource_type="test"),
            RateLimitError(),
            ServerHTTPError(message="test", status_code=500),
            ClientHTTPError(message="test", status_code=400),
            OPGGJSONDecodeError(url="http://test.com"),
        ]

        for error in errors:
            assert isinstance(error, OPGGError)
