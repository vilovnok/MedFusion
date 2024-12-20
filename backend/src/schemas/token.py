from pydantic import BaseModel
from .config import TunedModel

class TokenCreate(TunedModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenRefresh(BaseModel):
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    sub: str
    id: int