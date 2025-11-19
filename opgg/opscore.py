from pydantic import BaseModel, field_validator
import logging

logger = logging.getLogger("OPGG.py")


class OPScore(BaseModel):
    second: int
    score: float

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(f"Field '{info.field_name}' is None in OPScore model")
        return v


class OPScoreAnalysis(BaseModel):
    left: str
    right: str
    last: str

    @field_validator("*", mode="after")
    def log_none_values(cls, v, info):
        if v is None:
            logger.warning(
                f"Field '{info.field_name}' is None in OPScoreAnalysis model"
            )
        return v
