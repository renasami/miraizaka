from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import YEAR

from app.db.base_class import Base


class Grade(str, PyEnum):
    B2 = "B2"
    B3 = "B3"
    B4 = "B4"
    M1 = "M1"
    M2 = "M2"
    D = "D"
    GRADUATED = "GRADUATED"


class EEAction(PyEnum):
    ENTRY = "ENTRY"
    EXIT = "EXIT"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(32), index=True, nullable=False)
    display_name = Column(String(128), index=True, nullable=False)
    grade = Column(Enum(Grade), index=True)
    graduated_year = Column(YEAR)

    ee_records = relationship("EntryExitRecord", back_populates="user")


class EntryExitRecord(Base):
    __tablename__ = "entry_exit_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    time = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(Enum(EEAction), nullable=False)

    user = relationship("User", back_populates="ee_records")
