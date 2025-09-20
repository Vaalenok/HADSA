from sqlalchemy import LargeBinary
import datetime
import uuid
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    def __repr__(self):
        return f"<{self.__class__.__name__} (id={self.id})>"


class File(Base):
    __tablename__ = "files"

    name: Mapped[str] = mapped_column()
    path: Mapped[str] = mapped_column()
    type: Mapped[str] = mapped_column(default="None")
    size: Mapped[int] = mapped_column(default=0)

    hash: Mapped[str] = mapped_column(unique=True)
    added_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)

    label: Mapped[str | None] = mapped_column()
    notes: Mapped[str | None] = mapped_column()

    embedding: Mapped[bytes | None] = mapped_column(LargeBinary)
