
from pydantic import BaseModel, ConfigDict
 

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

class UserResponse(BaseModel):   # UserResponse → what we SEND back to the frontend
    id: int
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
   