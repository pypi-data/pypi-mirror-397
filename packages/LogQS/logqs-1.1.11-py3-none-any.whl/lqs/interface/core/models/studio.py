from typing import Optional

from pydantic import BaseModel


class CommandCall(BaseModel):
    action: str
    kwargs: Optional[dict]


class CommandCallCreateRequest(BaseModel):
    action: str
    kwargs: Optional[dict] = None


class CommandCallDataResponse(BaseModel):
    data: Optional[dict] = None
