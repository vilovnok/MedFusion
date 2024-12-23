from pydantic import BaseModel, EmailStr, Field

class AuthRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class AuthLogin(BaseModel):
    email: EmailStr=None
    password: str
