
# schemas.py defines what information the API accepts and returns.

# The identifier field lets us accept either a username or email address.
#  Since full names can be shared by multiple users, we won't use full name as a login identifier.

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    identifier: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str | None = None
    gender: str | None = None
    city: str | None = None
    is_email_verified: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

