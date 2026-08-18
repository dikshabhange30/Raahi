
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User, UserLanguage
from app.oauth2 import get_current_user
from app.schemas import UserResponse, UserLanguageCreate



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