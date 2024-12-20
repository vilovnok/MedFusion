from ..models.messages import Message
from ..utils.repository import SQLAlchemyRepository


class MessageRepository(SQLAlchemyRepository):
    model = [Message]
    