
# What we're building
# - GET /communities/ lists active communities.
# - GET /communities/?city=Pune&language=Marathi filters by city and language.
# - POST /communities/ creates a community only if the logged-in user is an admin.
# - Community eligibility accepts female, male, or unisex.



from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Community, CommunityMember, User
from app.routers.users import get_current_user
from app.schemas import CommunityCreate, CommunityResponse, MembershipResponse


router = APIRouter(prefix="/communities", tags=["Communities"])


@router.get("/", response_model=list[CommunityResponse])
def list_communities(
    city: str | None = Query(default=None, min_length=2),
    language: str | None = Query(default=None, min_length=2),
    db: Session = Depends(get_db),
):
    query = db.query(Community).filter(Community.is_active.is_(True))

    if city:
        query = query.filter(Community.city.ilike(city.strip()))

    if language:
        query = query.filter(Community.language.ilike(language.strip()))

    return query.order_by(Community.name).all()


@router.post(
    "/",
    response_model=CommunityResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_community(
    community_data: CommunityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create communities",
        )

    eligibility = community_data.gender_eligibility.strip().lower()

    if eligibility not in {"female", "male", "unisex"}:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Gender eligibility must be female, male, or unisex",
        )

    community = Community(
        name=community_data.name.strip(),
        city=community_data.city.strip(),
        language=community_data.language.strip(),
        gender_eligibility=eligibility,
        description=community_data.description,
        created_by=current_user.id,
    )

    db.add(community)
    db.commit()
    db.refresh(community)

    return community


@router.post(
    "/{community_id}/join",
    response_model=MembershipResponse,
    status_code=status.HTTP_201_CREATED,
)
def join_community(
    community_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not current_user.gender:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Complete your profile and set your gender before joining",
        )

    community = (
        db.query(Community)
        .filter(
            Community.id == community_id,
            Community.is_active.is_(True),
        )
        .first()
    )

    if not community:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Community not found",
        )

    user_gender = current_user.gender.strip().lower()
    eligibility = community.gender_eligibility.strip().lower()

    if eligibility != "unisex" and user_gender != eligibility:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your profile does not meet this community's gender eligibility",
        )

    membership = CommunityMember(
        user_id=current_user.id,
        community_id=community.id,
    )

    db.add(membership)

    try:
        db.commit()
        db.refresh(membership)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already joined this community",
        )

    return membership


@router.delete("/{community_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_community(
    community_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    membership = (
        db.query(CommunityMember)
        .filter(
            CommunityMember.user_id == current_user.id,
            CommunityMember.community_id == community_id,
        )
        .first()
    )

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You have not joined this community",
        )

    db.delete(membership)
    db.commit()


@router.get("/mine", response_model=list[CommunityResponse])
def my_communities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Community)
        .join(
            CommunityMember,
            CommunityMember.community_id == Community.id,
        )
        .filter(
            CommunityMember.user_id == current_user.id,
            Community.is_active.is_(True),
        )
        .order_by(Community.name)
        .all()
    )


