from typing import TypedDict


class GenericReqParams(TypedDict):
    """
    A generic request parameters type.

    Parameters:
        base_api_url: `str`: The base API URL for the request
        headers: `dict`: The headers to include in the request
    """

    base_api_url: str
    headers: dict


