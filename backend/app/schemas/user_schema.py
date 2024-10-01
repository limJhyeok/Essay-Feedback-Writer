from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    is_social: bool = Field(False, description="Indicates if the user is a social login user")
    password: str = Field(..., description="Password for regular users")

    @field_validator('email', 'password')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("null value is not allowed")
        return v

class User(BaseModel):
    id: int
    email: EmailStr

class UserEmail(BaseModel):
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str
    email: EmailStr

