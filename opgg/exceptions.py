"""
Custom exceptions for OPGG.py library.

Exception Hierarchy:
    OPGGError (base)
    ├── APIError (API-related errors)
    │   ├── HTTPError (HTTP status code errors)
    │   │   ├── ClientHTTPError (4xx)
    │   │   └── ServerHTTPError (5xx)
    │   ├── RateLimitError (429)
    │   └── NotFoundError (404)
    ├── NetworkError (connection/transport errors)
    │   ├── ConnectionError
    │   └── TimeoutError
    ├── ResponseError (response processing errors)
    │   ├── JSONDecodeError
    │   └── ResponseValidationError
    └── CacheError (caching errors)
"""

from __future__ import annotations


class OPGGError(Exception):
    """Base exception for all OPGG library errors.

    Inherits from Exception to ensure existing try/except blocks
    catching generic exceptions still work (backward compatibility).

    Attributes:
        message: Human-readable error description
        original_error: The underlying exception, if any
    """

    def __init__(self, message: str, original_error: Exception | None = None):
        self.message = message
        self.original_error = original_error
        super().__init__(message)

    def __repr__(self) -> str:
        if self.original_error:
            return f"{self.__class__.__name__}({self.message!r}, original_error={self.original_error!r})"
        return f"{self.__class__.__name__}({self.message!r})"


class APIError(OPGGError):
    """Base class for API-related errors.

    Attributes:
        url: The URL that was being requested
        method: HTTP method used (GET, POST, etc.)
    """

    def __init__(
        self,
        message: str,
        url: str | None = None,
        method: str = "GET",
        original_error: Exception | None = None,
    ):
        self.url = url
        self.method = method
        super().__init__(message, original_error)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r}, url={self.url!r}, method={self.method!r})"


class HTTPError(APIError):
    """HTTP status code related errors.

    Attributes:
        status_code: HTTP status code
        response_body: Raw response body text (truncated if large)
        headers: Response headers
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        url: str | None = None,
        response_body: str | None = None,
        headers: dict | None = None,
        original_error: Exception | None = None,
    ):
        self.status_code = status_code
        self.response_body = (
            response_body[:1000]
            if response_body and len(response_body) > 1000
            else response_body
        )
        self.headers = headers or {}
        super().__init__(message, url, "GET", original_error)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(status_code={self.status_code}, url={self.url!r}, message={self.message!r})"


class ClientHTTPError(HTTPError):
    """4xx client errors (except 404 and 429)."""

    pass


class ServerHTTPError(HTTPError):
    """5xx server errors."""

    pass


class NotFoundError(HTTPError):
    """404 Not Found - resource doesn't exist.

    Attributes:
        resource_type: Type of resource that wasn't found (e.g., "summoner", "champion")
        resource_id: Identifier of the resource, if available
    """

    def __init__(
        self,
        resource_type: str,
        resource_id: str | None = None,
        url: str | None = None,
        response_body: str | None = None,
        headers: dict | None = None,
        original_error: Exception | None = None,
    ):
        self.resource_type = resource_type
        self.resource_id = resource_id
        message = f"{resource_type} not found"
        if resource_id:
            message = f"{resource_type} '{resource_id}' not found"
        super().__init__(
            message,
            status_code=404,
            url=url,
            response_body=response_body,
            headers=headers,
            original_error=original_error,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(resource_type={self.resource_type!r}, resource_id={self.resource_id!r}, url={self.url!r})"


class RateLimitError(HTTPError):
    """429 Too Many Requests - rate limited.

    Attributes:
        retry_after: Number of seconds to wait before retrying, if provided by API
    """

    def __init__(
        self,
        retry_after: int | None = None,
        url: str | None = None,
        response_body: str | None = None,
        headers: dict | None = None,
        original_error: Exception | None = None,
    ):
        self.retry_after = retry_after
        message = "Rate limited by OPGG API"
        if retry_after:
            message += f" - retry after {retry_after} seconds"
        super().__init__(
            message,
            status_code=429,
            url=url,
            response_body=response_body,
            headers=headers,
            original_error=original_error,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(retry_after={self.retry_after}, url={self.url!r})"


class NetworkError(OPGGError):
    """Network/connection related errors.

    Attributes:
        url: The URL that was being requested when the error occurred
    """

    def __init__(
        self,
        message: str,
        url: str | None = None,
        original_error: Exception | None = None,
    ):
        self.url = url
        super().__init__(message, original_error)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r}, url={self.url!r})"


class OPGGConnectionError(NetworkError):
    """Failed to establish connection to OPGG API."""

    pass


class OPGGTimeoutError(NetworkError):
    """Request to OPGG API timed out."""

    pass


class ResponseError(OPGGError):
    """Errors during response processing.

    Attributes:
        url: The URL that returned the problematic response
    """

    def __init__(
        self,
        message: str,
        url: str | None = None,
        original_error: Exception | None = None,
    ):
        self.url = url
        super().__init__(message, original_error)


class OPGGJSONDecodeError(ResponseError):
    """Failed to decode JSON response from OPGG API.

    Attributes:
        raw_text: The raw response text that failed to parse (truncated)
    """

    def __init__(
        self,
        url: str,
        raw_text: str | None = None,
        original_error: Exception | None = None,
    ):
        self.raw_text = raw_text[:500] if raw_text and len(raw_text) > 500 else raw_text
        super().__init__(f"Failed to decode JSON from {url}", url, original_error)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(url={self.url!r}, raw_text={self.raw_text[:50] if self.raw_text else None!r}...)"


class ResponseValidationError(ResponseError):
    """Response structure doesn't match expected format.

    Attributes:
        expected: Description of expected structure
        got: Description of what was actually received
    """

    def __init__(
        self,
        url: str,
        expected: str,
        got: str | None = None,
        original_error: Exception | None = None,
    ):
        self.expected = expected
        self.got = got
        message = f"Invalid response structure from {url}: expected {expected}"
        if got:
            message += f", got {got}"
        super().__init__(message, url, original_error)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(url={self.url!r}, expected={self.expected!r}, got={self.got!r})"


class CacheError(OPGGError):
    """Cache-related errors (SQLite operations, etc.)."""

    pass
