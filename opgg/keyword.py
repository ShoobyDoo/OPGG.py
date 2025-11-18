from typing import Optional

from pydantic import BaseModel, Field, field_validator
import logging

logger = logging.getLogger("OPGG.py")


class Keyword(BaseModel):
    """
    Represents a keyword entry returned from /meta/keywords.
    """

    keyword: Optional[str] = None
    label: Optional[str] = None
    description: Optional[str] = None
    arrows: list[str] = Field(default_factory=list)
    is_op: Optional[bool] = None
    context: Optional[str] = None

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if info.field_name != "arrows" and v is None:
            logger.warning(f"Field '{info.field_name}' is None in Keyword model")
        return v
