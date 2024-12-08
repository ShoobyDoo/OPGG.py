from pydantic import BaseModel


class UpdateData(BaseModel):
    message: str
    last_updated_at: str
    renewable_at: str | None
    finish: bool | None
    delay: int | None


class UpdateResponse(BaseModel):
    status: int
    data: UpdateData
