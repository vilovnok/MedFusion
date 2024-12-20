from pydantic import BaseModel, EmailStr, Field

class AuthRegister(BaseModel):
    username: str 
    email: EmailStr
    password: str = Field(min_length=8)

class AuthLogin(BaseModel):
    email: EmailStr=None
    username: str=None
    password: str
