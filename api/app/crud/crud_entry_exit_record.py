from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.db.models import EntryExitRecord
from app.crud.schemas.entry_exit_record import EntryExitRecordCreate, EntryExitRecordUpdate, EEAction
from app.db.redis_instance import redis_maker


class CRUDEntryExitRecord(
    CRUDBase[EntryExitRecord, EntryExitRecordCreate, EntryExitRecordUpdate]
):
    def create(
        self,
        db_session: Session,
        *,
        obj_in: EntryExitRecordCreate,
    ) -> EntryExitRecord:
        res = super().create(db_session, obj_in=obj_in)
        r = redis_maker()
        if obj_in.action == EEAction.EXIT:
            r.hdel("now_member", obj_in.user_id)
        elif obj_in.action == EEAction.ENTRY:
            r.hset("now_member", obj_in.user_id, obj_in.time)
        return res

    def update(self) -> None:
        pass


ee_record = CRUDEntryExitRecord(EntryExitRecord)
