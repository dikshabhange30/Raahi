
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
 

class UserCreate(BaseModel):   # UserCreate → what we ACCEPT from the frontend when registering
    username: str
    email: str
    password: str
    full_name: str
    gender: str
    city: str
    profession: str | None = None
    bio: str | None = None
    profile_image: str | None = None
    preferred_contact: str | None = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, password: str) -> str:
        if len(password) < 8:
            raise ValueError(
                "Password must be at least 8 characters long"
            )

        if not any(char.islower() for char in password):
            raise ValueError(
                "Password must contain at least one lowercase letter"
            )

        if not any(char.isupper() for char in password):
            raise ValueError(
                "Password must contain at least one uppercase letter"
            )

        if not any(char.isdigit() for char in password):
            raise ValueError(
                "Password must contain at least one number"
            )

        if not any(not char.isalnum() for char in password):
            raise ValueError(
                "Password must contain at least one special character"
            )

        return password

class UserResponse(BaseModel):   # UserResponse → what we SEND back to the frontend
    user_id: int
    username: str
    email: str
    full_name: str
    gender: str
    city: str
    profession: str | None = None
    bio: str | None = None
    profile_image: str | None = None
    preferred_contact: str | None = None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
    is_admin: bool

class CommunityCreate(BaseModel):
    name: str
    city: str
    language: str
    gender: str
    description: str | None = None

class UserLanguageCreate(BaseModel):
    language_id: int
    

class UserHelpOfferedCreate(BaseModel):
    help_type_id: int

class UserHelpNeededCreate(BaseModel):
    help_type_id: int

class UserProfileUpdate(BaseModel):
    profession: str | None = None
    bio: str | None = None
    preferred_contact: str | None = None

class CommunityMemberResponse(BaseModel):
    user_id: int
    username: str
    full_name: str | None = None
    gender: str | None = None
    city: str | None = None
    profession: str | None = None
    bio: str | None = None
    profile_image: str | None = None

    model_config = ConfigDict(from_attributes=True)

class HelpRequestCreate(BaseModel):
    community_id: int
    helper_id: int
    message: str

class HelpRequestResponse(BaseModel):
    help_request_id: int
    community_id: int
    needer_id: int
    helper_id: int
    message: str
    status: str

    model_config = ConfigDict(from_attributes=True)

class MessageCreate(BaseModel):
    message: str


class MessageResponse(BaseModel):
    message_id: int
    conversation_id: int
    sender_id: int
    message: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class GroupMessageCreate(BaseModel):
    message: str


class GroupMessageResponse(BaseModel):
    group_message_id: int
    community_id: int
    sender_id: int
    message: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)