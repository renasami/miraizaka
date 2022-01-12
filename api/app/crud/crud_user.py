from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.db.models import User
from app.crud.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_name(self, db_session: Session, *, name: str) -> Optional[User]:
        return db_session.query(User).filter(User.name == name).first()

    def get_all_ungraduated_member(self, db_session: Session):
        return db_session.query(self.model).filter(User.graduated_year == None).all()  # noqa: E711  # yapf: disable


user = CRUDUser(User)
