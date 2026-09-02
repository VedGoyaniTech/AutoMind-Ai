from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator

class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, description="User full name")
    email: EmailStr = Field(..., description="Valid user email address")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    confirm_password: Optional[str] = Field(None, description="Matching password confirmation")

    @field_validator("full_name")
    def validate_full_name(cls, v):
        if not v.strip():
            raise ValueError("Full name cannot be empty or whitespace.")
        return v.strip()


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, description="Password required")
    remember_me: Optional[bool] = False


class UserPreferenceUpdate(BaseModel):
    answer_detail: Optional[str] = "Balanced"
    units: Optional[str] = "Metric"
    currency: Optional[str] = "INR"


class UserPreferenceResponse(BaseModel):
    id: int
    answer_detail: str
    units: str
    currency: str

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_admin: bool
    preference: Optional[UserPreferenceResponse] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    user: UserResponse


class RegisterResponse(BaseModel):
    success: bool = True
    message: str = "Account created successfully"
    access_token: str
    token_type: str = "Bearer"
    user: UserResponse
