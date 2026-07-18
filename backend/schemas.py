from pydantic import BaseModel


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: dict | None=None

