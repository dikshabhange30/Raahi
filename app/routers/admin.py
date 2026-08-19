

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User, Community
from app.auth import get_current_admin
from app.schemas import UserResponse



router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/users", response_model=list[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return db.query(User).all()

@router.patch("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if user.is_admin:
        raise HTTPException(
            status_code=400,
            detail="Admin users cannot be deactivated"
        )

    user.is_active = False

    db.commit()
    db.refresh(user)

    return {
        "message": "User deactivated successfully",
        "user_id": user.user_id
    }

@router.patch("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    user.is_active = True

    db.commit()
    db.refresh(user)

    return {
        "message": "User activated successfully",
        "user_id": user.user_id
    }

@router.patch("/communities/{community_id}/deactivate")
def deactivate_community(
    community_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    community = db.query(Community).filter(
        Community.community_id == community_id
    ).first()

    if not community:
        raise HTTPException(
            status_code=404,
            detail="Community not found"
        )

    community.is_active = False

    db.commit()
    db.refresh(community)

    return {
        "message": "Community deactivated successfully",
        "community_id": community.community_id
    }

@router.patch("/communities/{community_id}/activate")
def activate_community(
    community_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    community = db.query(Community).filter(
        Community.community_id == community_id
    ).first()

    if not community:
        raise HTTPException(
            status_code=404,
            detail="Community not found"
        )

    community.is_active = True

    db.commit()
    db.refresh(community)

    return {
        "message": "Community activated successfully",
        "community_id": community.community_id
    }