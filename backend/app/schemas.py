
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


class ProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, max_length=100)
    gender: str | None = Field(default=None, max_length=20)
    city: str | None = Field(default=None, max_length=100)
    profession: str | None = Field(default=None, max_length=100)
    bio: str | None = Field(default=None, max_length=500)


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str | None = None
    gender: str | None = None
    city: str | None = None
    profession: str | None = None
    bio: str | None = None
    is_email_verified: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)



class CommunityCreate(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    city: str = Field(min_length=2, max_length=100)
    language: str = Field(min_length=2, max_length=50)
    gender_eligibility: str
    description: str | None = Field(default=None, max_length=2000)


class CommunityResponse(BaseModel):
    id: int
    name: str
    city: str
    language: str
    gender_eligibility: str
    description: str | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
