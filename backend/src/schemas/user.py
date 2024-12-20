from datetime import datetime
from pydantic import BaseModel, EmailStr
from .config import TunedModel
from typing import List

class UserCreate(BaseModel):
    username: str 
    email: EmailStr
    hashed_password: str
    token: str

class UserRead(TunedModel):
    id: int    
    username: str 
    email: EmailStr
    token: str
    created_at: datetime

class UserReadAll(BaseModel):
    posts: List[UserRead]
