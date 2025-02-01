from pydantic import BaseModel


class OPScore(BaseModel):
    second: int
    score: float


class OPScoreAnalysis(BaseModel):
    left: str
    right: str
    last: str
