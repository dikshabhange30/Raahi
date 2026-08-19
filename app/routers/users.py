
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import HTTPException


from app.database import SessionLocal
from app.models import (
    User,
    UserLanguage,
    UserHelpOffered,
    UserHelpNeeded
)

from app.oauth2 import get_current_user
from app.schemas import (
    UserResponse,
    UserLanguageCreate,
    UserHelpOfferedCreate,
    UserHelpNeededCreate,
    UserProfileUpdate
)



router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.post("/languages")
def add_language(
    language_data: UserLanguageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_language = db.query(UserLanguage).filter(
        UserLanguage.user_id == current_user.user_id,
        UserLanguage.language_id == language_data.language_id
    ).first()

    if existing_language:
        raise HTTPException(
            status_code=400,
            detail="Language already added"
        )

    user_language = UserLanguage(
        user_id=current_user.user_id,
        language_id=language_data.language_id
    )

    db.add(user_language)
    db.commit()
    db.refresh(user_language)

    return {
        "message": "Language added successfully",
        "user_language_id": user_language.user_language_id
    }


@router.get("/languages")
def get_my_languages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    languages = (
        db.query(UserLanguage)
        .filter(
            UserLanguage.user_id == current_user.user_id
        )
        .all()
    )

    return languages

@router.delete("/languages/{language_id}")
def remove_language(
    language_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_language = db.query(UserLanguage).filter(
        UserLanguage.user_id == current_user.user_id,
        UserLanguage.language_id == language_id
    ).first()

    if not user_language:
        raise HTTPException(
            status_code=404,
            detail="Language not found in your profile"
        )

    db.delete(user_language)
    db.commit()

    return {
        "message": "Language removed successfully"
    }

@router.post("/help/offered")
def add_help_offered(
    help_data: UserHelpOfferedCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_help = db.query(UserHelpOffered).filter(
        UserHelpOffered.user_id == current_user.user_id,
        UserHelpOffered.help_type_id == help_data.help_type_id
    ).first()

    if existing_help:
        raise HTTPException(
            status_code=400,
            detail="Help type already added to offered list"
        )

    user_help = UserHelpOffered(
        user_id=current_user.user_id,
        help_type_id=help_data.help_type_id
    )

    db.add(user_help)
    db.commit()
    db.refresh(user_help)

    return {
        "message": "Help offered added successfully",
        "user_help_offered_id": user_help.user_help_offered_id
    }

@router.post("/help/needed")
def add_help_needed(
    help_data: UserHelpNeededCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_help = db.query(UserHelpNeeded).filter(
        UserHelpNeeded.user_id == current_user.user_id,
        UserHelpNeeded.help_type_id == help_data.help_type_id
    ).first()

    if existing_help:
        raise HTTPException(
            status_code=400,
            detail="Help type already added to needed list"
        )

    user_help = UserHelpNeeded(
        user_id=current_user.user_id,
        help_type_id=help_data.help_type_id
    )

    db.add(user_help)
    db.commit()
    db.refresh(user_help)

    return {
        "message": "Help needed added successfully",
        "user_help_needed_id": user_help.user_help_needed_id
    }

@router.get("/help/offered")
def get_help_offered(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(UserHelpOffered).filter(
        UserHelpOffered.user_id == current_user.user_id
    ).all()

@router.get("/help/needed")
def get_help_needed(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(UserHelpNeeded).filter(
        UserHelpNeeded.user_id == current_user.user_id
    ).all()

@router.delete("/help/offered/{help_type_id}")
def remove_help_offered(
    help_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_help = db.query(UserHelpOffered).filter(
        UserHelpOffered.user_id == current_user.user_id,
        UserHelpOffered.help_type_id == help_type_id
    ).first()

    if not user_help:
        raise HTTPException(
            status_code=404,
            detail="Help type not found in offered list"
        )

    db.delete(user_help)
    db.commit()

    return {
        "message": "Help offered removed successfully"
    }

@router.delete("/help/needed/{help_type_id}")
def remove_help_needed(
    help_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_help = db.query(UserHelpNeeded).filter(
        UserHelpNeeded.user_id == current_user.user_id,
        UserHelpNeeded.help_type_id == help_type_id
    ).first()

    if not user_help:
        raise HTTPException(
            status_code=404,
            detail="Help type not found in needed list"
        )

    db.delete(user_help)
    db.commit()

    return {
        "message": "Help needed removed successfully"
    }

# Creating  profile update API

@router.put("/profile")
def update_profile(
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if profile_data.profession is not None:
        current_user.profession = profile_data.profession

    if profile_data.bio is not None:
        current_user.bio = profile_data.bio

    if profile_data.preferred_contact is not None:
        current_user.preferred_contact = profile_data.preferred_contact

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Profile updated successfully"
    }

@router.put(
    "/me",
    response_model=UserResponse
)
def update_my_profile(
    profile_data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user = db.query(User).filter(
        User.user_id == current_user.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.full_name = profile_data.full_name
    user.gender = profile_data.gender
    user.city = profile_data.city
    user.profession = profile_data.profession
    user.bio = profile_data.bio
    user.profile_image = profile_data.profile_image
    user.preferred_contact = profile_data.preferred_contact

    db.commit()
    db.refresh(user)

    return user

