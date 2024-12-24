from datetime import datetime
from pydantic import BaseModel
from .config import TunedModel
from typing import List, Optional


class Message(BaseModel):
    user_id: int=None    
    text: str=None 
    token: str=None
    liked: Optional[bool]=None
    message_id: Optional[int]=None
    opinion: Optional[str]=None


class MessageCreate(BaseModel):
    user_id: int=None      
    human_text: Optional[str]=None   
    ai_text: Optional[str]=None  
    full_metadata: Optional[str]=None
    opinion: Optional[str]=None


class MessageRead(TunedModel):
    id: int
    user_id: int    
    ai_text: str 
    human_text: str
    opinion: Optional[str]=None
    created_at: datetime
    liked: Optional[bool] = None
    full_metadata: Optional[str]=None

class MessageReadAll(BaseModel):
    posts: List[MessageRead]
