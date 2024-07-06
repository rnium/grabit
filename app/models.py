from app.config.database import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, func, Enum
import json


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str]
    hashed_password: Mapped[str]
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)
    joined: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), nullable=False)


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=True)
    data: Mapped[Text] = mapped_column(Text, nullable=True)
    added_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), nullable=False)
    added_by: Mapped['User'] = mapped_column(ForeignKey('users.id'))
    site: Mapped[str] = mapped_column(String, nullable=False)
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    @property
    def data_dict(self):
        try:
            return json.loads(self.data)
        except Exception:
            return {}
