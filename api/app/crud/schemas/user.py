from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.db.models import Grade


class UserBase(BaseModel):
    name: Optional[str] = None
    display_name: Optional[str] = None
    grade: Optional[Grade] = None
    graduated_year: Optional[int] = None


class UserCreate(UserBase):
    name: str
    grade: Grade


class UserUpdate(UserBase):
    pass


class UserInDB(UserBase):
    id: int


class NowMember(UserInDB):
    time: datetime
