from abc import ABC, abstractmethod
from ..db.db import AsyncSession, async_session_maker
from ..repo.user import UserRepository
from ..repo.message import MessageRepository
from typing import Type

class IUnitOfWork(ABC):
    user: Type[UserRepository]
    message: Type[MessageRepository]

    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self):
        raise NotImplementedError
    
    @abstractmethod
    async def __aexit__(self, *args):
        raise NotImplementedError
    
    @abstractmethod
    async def commit(self):
        raise NotImplementedError
    
    @abstractmethod
    async def rollback(self):
        raise NotImplementedError

class UnitOfWork(IUnitOfWork):
    def __init__(self):
        self.session_factory = async_session_maker

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()
        self.user = UserRepository(self.session)
        self.message = MessageRepository(self.session)

    async def __aexit__(self, *args):
        await self.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
