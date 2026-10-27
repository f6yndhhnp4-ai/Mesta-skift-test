from datetime import datetime
from pydantic import BaseModel, Field

class WindowRequest(BaseModel):
    line_id: str
    km_from: float = Field(ge=0)
    km_to: float = Field(ge=0)
    start: datetime
    end: datetime
    safety_before_minutes: int = Field(default=10, ge=0, le=180)
    safety_after_minutes: int = Field(default=10, ge=0, le=180)
    minimum_window_minutes: int = Field(default=20, ge=1)

class Occupation(BaseModel):
    start: datetime
    end: datetime
    identifier: str
    kind: str = "train"
    source_version: str | None = None

class WorkWindow(BaseModel):
    start: datetime
    end: datetime
    gross_minutes: int
    net_minutes: int
    preceding: str | None = None
    following: str | None = None

class WindowResponse(BaseModel):
    windows: list[WorkWindow]
    source: str
    retrieved_at: datetime
    warning: str
