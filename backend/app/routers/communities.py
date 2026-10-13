
# What we're building
# - GET /communities/ lists active communities.
# - GET /communities/?city=Pune&language=Marathi filters by city and language.
# - POST /communities/ creates a community only if the logged-in user is an admin.
# - Community eligibility accepts female, male, or unisex.

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Community, User
from app.routers.users import get_current_user
from app.schemas import CommunityCreate, CommunityResponse


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
