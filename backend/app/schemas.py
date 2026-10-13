
# schemas.py defines what information the API accepts and returns.


from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


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
