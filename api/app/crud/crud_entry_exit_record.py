from app.crud.base import CRUDBase
from app.db.models import EntryExitRecord
from app.crud.schemas.entry_exit_record import EntryExitRecordCreate, EntryExitRecordUpdate


class CRUDEntryExitRecord(
    CRUDBase[EntryExitRecord, EntryExitRecordCreate, EntryExitRecordUpdate]
):
    def update(self) -> None:
        pass


ee_record = CRUDEntryExitRecord(EntryExitRecord)
