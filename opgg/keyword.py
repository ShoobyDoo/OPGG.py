from pydantic import BaseModel, Field


class Keyword(BaseModel):
    """
    Represents a keyword entry returned from /meta/keywords.
    """

    keyword: str | None = None
    label: str | None = None
    description: str | None = None
    arrows: list[str] = Field(default_factory=list)
    is_op: bool | None = None
    context: str | None = None
