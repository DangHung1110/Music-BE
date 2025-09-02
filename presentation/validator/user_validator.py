from typing import Optional
from pydantic import BaseModel, Field, EmailStr, HttpUrl, validator
import re


class CreateUserRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    image_url: Optional[HttpUrl] = None
    role: Optional[str] = Field("user", pattern=r"^(user|admin)$")
    is_active: Optional[bool] = True

    @validator('username')
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_.-]+$', v):
            raise ValueError("Invalid username format")
        return v

    @validator('password')
    def validate_password(cls, v: str) -> str:
        if not re.search(r'^(?=.*[A-Za-z])(?=.*\d).{6,}$', v):
            raise ValueError('Password must contain at least one letter and one number')
        return v


class UpdateUserRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6, max_length=100)
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    image_url: Optional[HttpUrl] = None
    role: Optional[str] = Field(None, pattern=r"^(user|admin)$")
    is_active: Optional[bool] = None

    @validator('username')
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.match(r'^[a-zA-Z0-9_.-]+$', v):
            raise ValueError("Invalid username format")
        return v

    @validator('password')
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.search(r'^(?=.*[A-Za-z])(?=.*\d).{6,}$', v):
            raise ValueError('Password must contain at least one letter and one number')
        return v


class ListUsersQuery(BaseModel):
    limit: int = Field(50, ge=1, le=200)
    offset: int = Field(0, ge=0)



