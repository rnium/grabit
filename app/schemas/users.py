from pydantic import BaseModel, Field

class UserBase(BaseModel):
    username: str = Field(max_length=100)
    name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserView(UserBase):
    class Config:
        from_attributes = True
        
class TokenRefreshRequest(BaseModel):
    refresh_token: str