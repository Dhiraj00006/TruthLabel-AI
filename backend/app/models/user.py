import enum

from sqlalchemy import Column, DateTime, Enum, Integer, String, func

from app.db import Base


class UserRole(str, enum.Enum):
    inspector = "inspector"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.inspector)
    created_at = Column(DateTime, server_default=func.now())
