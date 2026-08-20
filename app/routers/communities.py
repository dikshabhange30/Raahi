

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Community, CommunityMember, User
from app.oauth2 import get_current_user, get_current_admin
from app.schemas import CommunityCreate, CommunityMemberResponse


router = APIRouter(
    prefix="/communities",
    tags=["Communities"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_communities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Community).filter(
        Community.is_active == True
    ).all()

@router.get("/search")
def search_communities(
    city: str | None = None,
    language: str | None = None,
    skip: int = 0,
    limit: int = 20,
    gender: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Community).filter(
        Community.is_active == True
    )

    if city:
        query = query.filter(
            Community.city.ilike(f"%{city}%")
        )

    if language:
        query = query.filter(
            Community.language.ilike(f"%{language}%")
        )

    if gender:
        query = query.filter(
            Community.gender.ilike(f"%{gender}%")
        )

    return query.offset(skip).limit(limit).all()


@router.get("/{community_id}")
def get_community(
    community_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    community = db.query(Community).filter(
        Community.community_id == community_id,
        Community.is_active == True
    ).first()

    if not community:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community not found"
        )

    return community

@router.post("/")
def create_community(
    community_data: CommunityCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    community = Community(
        name=community_data.name,
        city=community_data.city,
        language=community_data.language,
        gender=community_data.gender,
        description=community_data.description
    )

    db.add(community)
    db.commit()
    db.refresh(community)

    return community

@router.post("/{community_id}/join")
def join_community(
    community_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    community = db.query(Community).filter(
        Community.community_id == community_id,
        Community.is_active == True
    ).first()

    if not community:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community not found"
        )

    existing_membership = db.query(CommunityMember).filter(
        CommunityMember.community_id == community_id,
        CommunityMember.user_id == current_user.user_id
    ).first()

    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already a member of this community"
        )

    membership = CommunityMember(
        community_id=community_id,
        user_id=current_user.user_id
    )

    db.add(membership)
    db.commit()

    return {
        "message": "Joined community successfully"
    }

@router.delete("/{community_id}/leave")
def leave_community(
    community_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    membership = db.query(CommunityMember).filter(
        CommunityMember.community_id == community_id,
        CommunityMember.user_id == current_user.user_id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not a member of this community"
        )

    db.delete(membership)
    db.commit()

    return {
        "message": "Left community successfully"
    }

@router.get(
    "/{community_id}/members",
    response_model=list[CommunityMemberResponse]
)
def get_community_members(
    community_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check that community exists
    community = db.query(Community).filter(
        Community.community_id == community_id,
        Community.is_active == True
    ).first()

    if not community:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community not found"
        )

    # Check that current user has joined this community
    membership = db.query(CommunityMember).filter(
        CommunityMember.community_id == community_id,
        CommunityMember.user_id == current_user.user_id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must join this community to view its members"
        )

    # Get all members
    members = (
        db.query(User)
        .join(
            CommunityMember,
            CommunityMember.user_id == User.user_id
        )
        .filter(
            CommunityMember.community_id == community_id,
            User.is_active == True
        )
        .all()
    )

    return members

