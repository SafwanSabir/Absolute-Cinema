from pydantic import BaseModel
from datetime import datetime, date, time
from typing import Optional

class MovieBase(BaseModel):
    name: str
    duration_minutes: int

class MovieCreate(MovieBase):
    start_date: date
    start_time: time

class MovieResponse(MovieBase):
    id: int
    start_time: datetime

    class Config:
        from_attributes = True
