from pydantic import BaseModel, EmailStr, validator, Field, HttpUrl
from typing import Optional
import re

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=6, max_length=100, description="User password")
    full_name: Optional[str] = Field(None, min_length=2, max_length=100, description="User full name")
    bio: Optional[str] = Field(None, max_length=500, description="User biography")
    image_url: Optional[HttpUrl] = Field(None, description="Profile image URL")

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_.-]+$', v):
            raise ValueError("Username chỉ được chứa chữ cái, số, dấu gạch dưới (_), gạch ngang (-) hoặc dấu chấm (.)")
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters')
        if len(v) > 100:
            raise ValueError('Password must be less than 100 characters')
        if not re.search(r'^(?=.*[a-zA-Z])(?=.*\d)', v):
            raise ValueError('Password must contain at least one letter and one number')
        return v

    @validator('full_name')
    def validate_full_name(cls, v):
        if v is None:
            return v
        if not v.strip():
            raise ValueError('Full name is required')
        if len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters')
        if len(v.strip()) > 100:
            raise ValueError('Full name must be less than 100 characters')
        if not re.match(r'^[a-zA-Z0-9\s\u00C0-\u017F\u1EA0-\u1EF9]+$', v):
            raise ValueError('Full name contains invalid characters')
        return v
