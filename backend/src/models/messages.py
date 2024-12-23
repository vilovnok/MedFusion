from ..db.db import Base
from ..schemas.messages import MessageRead
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (Column, String, Boolean, ForeignKey, Integer, TIMESTAMP,text)


class Message(Base):
    __tablename__ = 'messages'
    __table_args__ = {'extend_existing': True}

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True, unique=True)  
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True, nullable=False)
    ai_text = Column(String, nullable=False)
    human_text = Column(String, nullable=False)
    liked = Column(Boolean)
    full_metadata = Column(String)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=text("TIMEZONE('Europe/Moscow', CURRENT_TIMESTAMP)"),
        onupdate=text("TIMEZONE('Europe/Moscow', CURRENT_TIMESTAMP)")
    )
    def to_read_model(self) -> MessageRead:
        return MessageRead(
            id=self.id,
            user_id=self.user_id,
            ai_text=self.ai_text,
            human_text=self.human_text,
            liked=self.liked,
            full_metadata=self.full_metadata,
            created_at=self.created_at
        )