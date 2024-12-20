from ..models.user import User
from ..utils.repository import SQLAlchemyRepository

class UserRepository(SQLAlchemyRepository):
    model = [User]