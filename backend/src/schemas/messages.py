from datetime import datetime
from pydantic import BaseModel
from .config import TunedModel
from typing import List, Optional


class Message(BaseModel):
    user_id: str=None    
    text: str=None 
    token: str=None
    liked: Optional[bool] = None


class MessageCreate(BaseModel):
    user_id: int=None      
    human_text: str=None   
    ai_text: str=None  


class MessageRead(TunedModel):
    id: int
    user_id: int    
    ai_text: str 
    human_text: str 
    created_at: datetime
    liked: Optional[bool] = None

class MessageReadAll(BaseModel):
    posts: List[MessageRead]
