"""Unit tests for OPGG exception hierarchy."""

from opgg.exceptions import (
    OPGGError,
    APIError,
    HTTPError,
    ClientHTTPError,
    ServerHTTPError,
    NotFoundError,
    RateLimitError,
    NetworkError,
    OPGGConnectionError,
    OPGGTimeoutError,
    ResponseError,
    OPGGJSONDecodeError,
    ResponseValidationError,
    CacheError,
)


class TestExceptionHierarchy:
    """Test that exception inheritance is correct."""

    def test_opgg_error_is_base_exception(self):
        """OPGGError should inherit from Exception for backward compatibility."""
        assert issubclass(OPGGError, Exception)

    def test_api_error_inherits_from_opgg_error(self):
        """APIError should inherit from OPGGError."""
        assert issubclass(APIError, OPGGError)

    def test_http_error_inherits_from_api_error(self):
        """HTTPError should inherit from APIError."""
        assert issubclass(HTTPError, APIError)

    def test_client_http_error_inherits_from_http_error(self):
        """ClientHTTPError should inherit from HTTPError."""
        assert issubclass(ClientHTTPError, HTTPError)

    def test_server_http_error_inherits_from_http_error(self):
        """ServerHTTPError should inherit from HTTPError."""
        assert issubclass(ServerHTTPError, HTTPError)

    def test_not_found_error_inherits_from_http_error(self):
        """NotFoundError should inherit from HTTPError."""
        assert issubclass(NotFoundError, HTTPError)

    def test_rate_limit_error_inherits_from_http_error(self):
        """RateLimitError should inherit from HTTPError."""
        assert issubclass(RateLimitError, HTTPError)

    def test_network_error_inherits_from_opgg_error(self):
        """NetworkError should inherit from OPGGError."""
        assert issubclass(NetworkError, OPGGError)

    def test_connection_error_inherits_from_network_error(self):
        """OPGGConnectionError should inherit from NetworkError."""
        assert issubclass(OPGGConnectionError, NetworkError)

    def test_timeout_error_inherits_from_network_error(self):
        """OPGGTimeoutError should inherit from NetworkError."""
        assert issubclass(OPGGTimeoutError, NetworkError)

    def test_response_error_inherits_from_opgg_error(self):
        """ResponseError should inherit from OPGGError."""
        assert issubclass(ResponseError, OPGGError)

    def test_json_decode_error_inherits_from_response_error(self):
        """OPGGJSONDecodeError should inherit from ResponseError."""
        assert issubclass(OPGGJSONDecodeError, ResponseError)

    def test_response_validation_error_inherits_from_response_error(self):
        """ResponseValidationError should inherit from ResponseError."""
        assert issubclass(ResponseValidationError, ResponseError)

    def test_cache_error_inherits_from_opgg_error(self):
        """CacheError should inherit from OPGGError."""
        assert issubclass(CacheError, OPGGError)


class TestBackwardCompatibility:
    """Test that exceptions can be caught with generic Exception handlers."""

    def test_opgg_error_caught_as_exception(self):
        """OPGGError should be catchable as Exception."""
        try:
            raise OPGGError("test error")
        except Exception as e:
            assert isinstance(e, OPGGError)
            assert str(e) == "test error"

    def test_api_error_caught_as_exception(self):
        """APIError should be catchable as Exception."""
        try:
            raise APIError("api error", url="http://test.com")
        except Exception as e:
            assert isinstance(e, APIError)

    def test_http_error_caught_as_exception(self):
        """HTTPError should be catchable as Exception."""
        try:
            raise HTTPError("http error", status_code=500, url="http://test.com")
        except Exception as e:
            assert isinstance(e, HTTPError)

    def test_network_error_caught_as_exception(self):
        """NetworkError should be catchable as Exception."""
        try:
            raise NetworkError("network error")
        except Exception as e:
            assert isinstance(e, NetworkError)


class TestOPGGError:
    """Test OPGGError base class."""

    def test_message_attribute(self):
        """Should store message as attribute."""
        err = OPGGError("test message")
        assert err.message == "test message"

    def test_original_error_attribute(self):
        """Should store original error as attribute."""
        original = ValueError("original")
        err = OPGGError("wrapper", original_error=original)
        assert err.original_error is original

    def test_original_error_default_none(self):
        """Original error should default to None."""
        err = OPGGError("test")
        assert err.original_error is None

    def test_str_representation(self):
        """String representation should be the message."""
        err = OPGGError("test message")
        assert str(err) == "test message"

    def test_repr_without_original_error(self):
        """Repr should show class name and message."""
        err = OPGGError("test message")
        assert "OPGGError" in repr(err)
        assert "test message" in repr(err)


class TestHTTPError:
    """Test HTTPError and its attributes."""

    def test_status_code_attribute(self):
        """Should store status code."""
        err = HTTPError("error", status_code=404)
        assert err.status_code == 404

    def test_url_attribute(self):
        """Should store URL."""
        err = HTTPError("error", status_code=500, url="http://api.opgg.com/test")
        assert err.url == "http://api.opgg.com/test"

    def test_response_body_attribute(self):
        """Should store response body."""
        err = HTTPError("error", status_code=500, response_body='{"error": "test"}')
        assert err.response_body == '{"error": "test"}'

    def test_response_body_truncation(self):
        """Should truncate very long response bodies."""
        long_body = "x" * 2000
        err = HTTPError("error", status_code=500, response_body=long_body)
        assert len(err.response_body) == 1000

    def test_headers_attribute(self):
        """Should store headers."""
        headers = {"Content-Type": "application/json"}
        err = HTTPError("error", status_code=500, headers=headers)
        assert err.headers == headers

    def test_headers_default_empty_dict(self):
        """Headers should default to empty dict."""
        err = HTTPError("error", status_code=500)
        assert err.headers == {}


class TestNotFoundError:
    """Test NotFoundError specialized exception."""

    def test_resource_type_attribute(self):
        """Should store resource type."""
        err = NotFoundError(resource_type="summoner")
        assert err.resource_type == "summoner"

    def test_resource_id_attribute(self):
        """Should store resource ID."""
        err = NotFoundError(resource_type="summoner", resource_id="abc123")
        assert err.resource_id == "abc123"

    def test_status_code_is_404(self):
        """Status code should always be 404."""
        err = NotFoundError(resource_type="summoner")
        assert err.status_code == 404

    def test_message_without_id(self):
        """Message should be 'type not found' when no ID."""
        err = NotFoundError(resource_type="summoner")
        assert str(err) == "summoner not found"

    def test_message_with_id(self):
        """Message should include ID when provided."""
        err = NotFoundError(resource_type="summoner", resource_id="abc123")
        assert str(err) == "summoner 'abc123' not found"


class TestRateLimitError:
    """Test RateLimitError specialized exception."""

    def test_retry_after_attribute(self):
        """Should store retry_after value."""
        err = RateLimitError(retry_after=60)
        assert err.retry_after == 60

    def test_retry_after_default_none(self):
        """retry_after should default to None."""
        err = RateLimitError()
        assert err.retry_after is None

    def test_status_code_is_429(self):
        """Status code should always be 429."""
        err = RateLimitError()
        assert err.status_code == 429

    def test_message_without_retry_after(self):
        """Message should indicate rate limiting."""
        err = RateLimitError()
        assert "Rate limited" in str(err)

    def test_message_with_retry_after(self):
        """Message should include retry time when provided."""
        err = RateLimitError(retry_after=60)
        assert "60 seconds" in str(err)


class TestOPGGJSONDecodeError:
    """Test OPGGJSONDecodeError specialized exception."""

    def test_url_in_message(self):
        """Message should include URL."""
        err = OPGGJSONDecodeError(url="http://test.com")
        assert "http://test.com" in str(err)

    def test_raw_text_attribute(self):
        """Should store raw text."""
        err = OPGGJSONDecodeError(url="http://test.com", raw_text="not json")
        assert err.raw_text == "not json"

    def test_raw_text_truncation(self):
        """Should truncate very long raw text."""
        long_text = "x" * 1000
        err = OPGGJSONDecodeError(url="http://test.com", raw_text=long_text)
        assert len(err.raw_text) == 500

    def test_preserves_original_error(self):
        """Should preserve original JSON decode error."""
        import json

        try:
            json.loads("not json")
        except json.JSONDecodeError as original:
            err = OPGGJSONDecodeError(url="http://test.com", original_error=original)
            assert err.original_error is original


class TestResponseValidationError:
    """Test ResponseValidationError specialized exception."""

    def test_expected_attribute(self):
        """Should store expected description."""
        err = ResponseValidationError(
            url="http://test.com", expected="dict", got="list"
        )
        assert err.expected == "dict"

    def test_got_attribute(self):
        """Should store got description."""
        err = ResponseValidationError(
            url="http://test.com", expected="dict", got="list"
        )
        assert err.got == "list"

    def test_message_includes_expected(self):
        """Message should include expected format."""
        err = ResponseValidationError(url="http://test.com", expected="dict")
        assert "expected dict" in str(err)

    def test_message_includes_got(self):
        """Message should include what was received."""
        err = ResponseValidationError(
            url="http://test.com", expected="dict", got="list"
        )
        assert "got list" in str(err)
