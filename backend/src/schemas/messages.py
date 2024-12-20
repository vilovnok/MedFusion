from datetime import datetime
from pydantic import BaseModel
from .config import TunedModel
from typing import List


class Message(BaseModel):
    user_id: str=None    
    text: str=None 
    token: str=None

class MessageCreate(BaseModel):
    user_id: int=None      
    human_text: str=None   
    ai_text: str=None  


class MessageRead(TunedModel):
    user_id: int    
    ai_text: str 
    human_text: str 
    created_at: datetime

class MessageReadAll(BaseModel):
    posts: List[MessageRead]
