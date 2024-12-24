from ..models.messages import Message, Metrics
from ..utils.repository import SQLAlchemyRepository


class MessageRepository(SQLAlchemyRepository):
    model = [Message, Metrics]
    