from ..db.db import Base
from sqlalchemy import (Column, String, 
                        TIMESTAMP,text)
from sqlalchemy.orm import Mapped, mapped_column
from ..schemas.user import UserRead

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True, unique=True)
    username = Column(String, nullable=False, primary_key=True, index=True)
    email = Column(String, nullable=False, primary_key=True, index=True)
    token = Column(String, nullable=False, default="None")
    hashed_password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("TIMEZONE('Europe/Moscow', CURRENT_TIMESTAMP)"),
        onupdate=text("TIMEZONE('Europe/Moscow', CURRENT_TIMESTAMP)")
    )

    def to_read_model(self) -> UserRead:
        return UserRead(
            id=self.id,
            username=self.username,
            email=self.email,
            token=self.token,
            created_at=self.created_at
        )