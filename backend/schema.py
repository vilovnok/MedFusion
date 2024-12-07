from pydantic import BaseModel

class Message(BaseModel):    
    content: str
    api_key: str
    history: list

class Healhcheck(BaseModel):    
    api_key: str