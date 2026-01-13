"""Unit tests for ResponseHandler class."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock

import aiohttp

from opgg.utils import ResponseHandler
from opgg.exceptions import (
    ClientHTTPError,
    ServerHTTPError,
    NotFoundError,
    RateLimitError,
    OPGGJSONDecodeError,
    ResponseValidationError,
)


@pytest.fixture
def mock_response():
    """Create a mock aiohttp ClientResponse."""
    response = MagicMock(spec=aiohttp.ClientResponse)
    response.headers = {}
    return response


class TestHandleResponseSuccess:
    """Test successful response handling."""

    @pytest.mark.asyncio
    async def test_handles_200_response(self, mock_response):
        """Should parse and return JSON on 200 response."""
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": [1, 2, 3]})

        result = await ResponseHandler.handle_response(mock_response, "http://test.com")

        assert result == {"data": [1, 2, 3]}

    @pytest.mark.asyncio
    async def test_handles_201_response(self, mock_response):
        """Should parse and return JSON on 201 response."""
        mock_response.status = 201
        mock_response.json = AsyncMock(return_value={"created": True})

        result = await ResponseHandler.handle_response(mock_response, "http://test.com")

        assert result == {"created": True}

    @pytest.mark.asyncio
    async def test_handles_empty_response_body(self, mock_response):
        """Should handle empty JSON object."""
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={})

        result = await ResponseHandler.handle_response(mock_response, "http://test.com")

        assert result == {}


class TestHandleResponse404:
    """Test 404 response handling."""

    @pytest.mark.asyncio
    async def test_raises_not_found_error(self, mock_response):
        """Should raise NotFoundError on 404."""
        mock_response.status = 404
        mock_response.text = AsyncMock(return_value="Not Found")

        with pytest.raises(NotFoundError) as exc_info:
            await ResponseHandler.handle_response(mock_response, "http://test.com")

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_allow_404_returns_empty_dict(self, mock_response):
        """Should return empty dict when allow_404=True."""
        mock_response.status = 404
        mock_response.text = AsyncMock(return_value="Not Found")

        result = await ResponseHandler.handle_response(
            mock_response, "http://test.com", allow_404=True
        )

        assert result == {}


class TestHandleResponse429:
    """Test rate limit response handling."""

    @pytest.mark.asyncio
    async def test_raises_rate_limit_error(self, mock_response):
        """Should raise RateLimitError on 429."""
        mock_response.status = 429
        mock_response.headers = {}
        mock_response.text = AsyncMock(return_value="Too Many Requests")

        with pytest.raises(RateLimitError) as exc_info:
            await ResponseHandler.handle_response(mock_response, "http://test.com")

        assert exc_info.value.status_code == 429

    @pytest.mark.asyncio
    async def test_extracts_retry_after_header(self, mock_response):
        """Should extract Retry-After header value."""
        mock_response.status = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_response.text = AsyncMock(return_value="Too Many Requests")

        with pytest.raises(RateLimitError) as exc_info:
            await ResponseHandler.handle_response(mock_response, "http://test.com")

        assert exc_info.value.retry_after == 60


class TestHandleResponse4xx:
    """Test 4xx client error handling."""

    @pytest.mark.asyncio
    async def test_raises_client_http_error_on_400(self, mock_response):
        """Should raise ClientHTTPError on 400."""
        mock_response.status = 400
        mock_response.headers = {}
        mock_response.text = AsyncMock(return_value="Bad Request")

        with pytest.raises(ClientHTTPError) as exc_info:
            await ResponseHandler.handle_response(mock_response, "http://test.com")

        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_raises_client_http_error_on_403(self, mock_response):
        """Should raise ClientHTTPError on 403."""
        mock_response.status = 403
        mock_response.headers = {}
        mock_response.text = AsyncMock(return_value="Forbidden")

        with pytest.raises(ClientHTTPError) as exc_info:
            await ResponseHandler.handle_response(mock_response, "http://test.com")

        assert exc_info.value.status_code == 403


class TestHandleResponse5xx:
    """Test 5xx server error handling."""

    @pytest.mark.asyncio
    async def test_raises_server_http_error_on_500(self, mock_response):
        """Should raise ServerHTTPError on 500."""
        mock_response.status = 500
        mock_response.headers = {}
        mock_response.text = AsyncMock(return_value="Internal Server Error")

        with pytest.raises(ServerHTTPError) as exc_info:
            await ResponseHandler.handle_response(mock_response, "http://test.com")

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_raises_server_http_error_on_503(self, mock_response):
        """Should raise ServerHTTPError on 503."""
        mock_response.status = 503
        mock_response.headers = {}
        mock_response.text = AsyncMock(return_value="Service Unavailable")

        with pytest.raises(ServerHTTPError) as exc_info:
            await ResponseHandler.handle_response(mock_response, "http://test.com")

        assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_preserves_response_body(self, mock_response):
        """Should preserve response body in error."""
        mock_response.status = 500
        mock_response.headers = {}
        mock_response.text = AsyncMock(return_value='{"error": "Internal error"}')

        with pytest.raises(ServerHTTPError) as exc_info:
            await ResponseHandler.handle_response(mock_response, "http://test.com")

        assert exc_info.value.response_body == '{"error": "Internal error"}'


class TestHandleResponseJSONErrors:
    """Test JSON parsing error handling."""

    @pytest.mark.asyncio
    async def test_raises_json_decode_error(self, mock_response):
        """Should raise OPGGJSONDecodeError on invalid JSON."""
        mock_response.status = 200
        mock_response.json = AsyncMock(side_effect=json.JSONDecodeError("test", "", 0))
        mock_response.text = AsyncMock(return_value="not json")

        with pytest.raises(OPGGJSONDecodeError) as exc_info:
            await ResponseHandler.handle_response(mock_response, "http://test.com")

        assert "http://test.com" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_preserves_raw_text_on_json_error(self, mock_response):
        """Should preserve raw text when JSON parsing fails."""
        mock_response.status = 200
        mock_response.json = AsyncMock(side_effect=json.JSONDecodeError("test", "", 0))
        mock_response.text = AsyncMock(return_value="<html>Error page</html>")

        with pytest.raises(OPGGJSONDecodeError) as exc_info:
            await ResponseHandler.handle_response(mock_response, "http://test.com")

        assert exc_info.value.raw_text == "<html>Error page</html>"

    @pytest.mark.asyncio
    async def test_handles_content_type_error(self, mock_response):
        """Should handle aiohttp ContentTypeError."""
        mock_response.status = 200
        mock_response.json = AsyncMock(
            side_effect=aiohttp.ContentTypeError(
                MagicMock(), tuple(), message="Invalid content type"
            )
        )
        mock_response.text = AsyncMock(return_value="plain text response")

        with pytest.raises(OPGGJSONDecodeError):
            await ResponseHandler.handle_response(mock_response, "http://test.com")


class TestHandleResponseValidation:
    """Test response structure validation."""

    @pytest.mark.asyncio
    async def test_validates_expected_keys(self, mock_response):
        """Should validate expected keys in response."""
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"other": "value"})

        with pytest.raises(ResponseValidationError) as exc_info:
            await ResponseHandler.handle_response(
                mock_response, "http://test.com", expected_keys=["data"]
            )

        assert "data" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_passes_validation_when_keys_present(self, mock_response):
        """Should pass validation when expected keys present."""
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"data": [], "meta": {}})

        result = await ResponseHandler.handle_response(
            mock_response, "http://test.com", expected_keys=["data", "meta"]
        )

        assert result == {"data": [], "meta": {}}

    @pytest.mark.asyncio
    async def test_validates_response_is_dict(self, mock_response):
        """Should validate response is a dict."""
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=[1, 2, 3])

        with pytest.raises(ResponseValidationError) as exc_info:
            await ResponseHandler.handle_response(
                mock_response, "http://test.com", expected_keys=["data"]
            )

        assert "dict" in str(exc_info.value)


class TestExtractData:
    """Test extract_data helper method."""

    def test_extracts_data_key(self):
        """Should extract 'data' key by default."""
        content = {"data": [1, 2, 3], "meta": {}}

        result = ResponseHandler.extract_data(content)

        assert result == [1, 2, 3]

    def test_extracts_custom_key(self):
        """Should extract custom key when specified."""
        content = {"items": [1, 2, 3], "data": {}}

        result = ResponseHandler.extract_data(content, key="items")

        assert result == [1, 2, 3]

    def test_returns_default_when_key_missing(self):
        """Should return default when key is missing."""
        content = {"other": "value"}

        result = ResponseHandler.extract_data(content, default=[])

        assert result == []

    def test_default_is_none(self):
        """Default should be None when not specified."""
        content = {"other": "value"}

        result = ResponseHandler.extract_data(content)

        assert result is None

    def test_handles_none_content(self):
        """Should handle None content gracefully."""
        # This will raise AttributeError, which is expected behavior
        # since None doesn't have .get()
        with pytest.raises(AttributeError):
            ResponseHandler.extract_data(None)


class TestValidateStructure:
    """Test _validate_structure helper method."""

    def test_raises_for_non_dict_response(self):
        """Should raise when response is not a dict."""
        with pytest.raises(ResponseValidationError) as exc_info:
            ResponseHandler._validate_structure([1, 2, 3], ["data"], "http://test.com")

        assert "dict" in str(exc_info.value)
        assert "list" in str(exc_info.value)

    def test_raises_for_missing_keys(self):
        """Should raise when expected keys are missing."""
        with pytest.raises(ResponseValidationError) as exc_info:
            ResponseHandler._validate_structure(
                {"a": 1}, ["data", "meta"], "http://test.com"
            )

        assert "data" in str(exc_info.value) or "meta" in str(exc_info.value)

    def test_passes_when_all_keys_present(self):
        """Should not raise when all expected keys are present."""
        # Should not raise
        ResponseHandler._validate_structure(
            {"data": [], "meta": {}}, ["data", "meta"], "http://test.com"
        )

    def test_passes_with_extra_keys(self):
        """Should pass even when extra keys are present."""
        # Should not raise
        ResponseHandler._validate_structure(
            {"data": [], "meta": {}, "extra": "value"},
            ["data", "meta"],
            "http://test.com",
        )
