from pydantic import BaseModel
from datetime import datetime

from app.db.models import EEAction


class EntryExitRecordCreate(BaseModel):
    time: datetime
    user_id: int
    action: EEAction


class EntryExitRecordUpdate(BaseModel):
    pass
