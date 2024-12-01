from box import Box


class UpdateData(Box):
    message: str
    last_updated_at: str
    renewable_at: str | None
    finish: bool | None
    delay: int | None


class UpdateResponse(Box):
    """
    A type representing the response from an update request.

    Parameters:

    """

    status: int
    data: UpdateData
