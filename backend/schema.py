from pydantic import BaseModel

class Message(BaseModel):    
    content: str
    api_key: str

class Healhcheck(BaseModel):    
    api_key: str