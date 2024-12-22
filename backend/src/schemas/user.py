from datetime import datetime
from pydantic import BaseModel, EmailStr
from .config import TunedModel
from typing import List


class UserCreate(BaseModel):
    token: str=None
    password: str
    email: EmailStr

class UserRead(TunedModel):
    id: int        
    token: str=None
    email: EmailStr
    created_at: datetime

class UserReadAll(BaseModel):
    posts: List[UserRead]
