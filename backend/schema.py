from pydantic import BaseModel

class Message(BaseModel):    
    content: str
    api_key: str
    messages: list

class Healhcheck(BaseModel):    
    api_key: str