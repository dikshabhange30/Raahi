



from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Community,
    CommunityMember,
    CommunityMessage,
    User,
)
from app.schemas import CommunityMessageCreate, CommunityMessageResponse
from app.routers.users import get_current_user

router = APIRouter(prefix="/communities", tags=["Community Chat"])


def verify_membership(community_id: int, user_id: int, db: Session):
    community = db.query(Community).filter(
        Community.id == community_id,
        Community.is_active == True,
    ).first()

    if not community:
        raise HTTPException(status_code=404, detail="Community not found.")

    membership = db.query(CommunityMember).filter(
        CommunityMember.community_id == community_id,
        CommunityMember.user_id == user_id,
    ).first()

    if not membership:
        raise HTTPException(
            status_code=403,
            detail="Join this community to access its group chat.",
        )


@router.get(
    "/{community_id}/messages",
    response_model=list[CommunityMessageResponse],
)
def get_community_messages(
    community_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    verify_membership(community_id, current_user.id, db)

    return (
        db.query(CommunityMessage)
        .filter(CommunityMessage.community_id == community_id)
        .order_by(CommunityMessage.created_at.asc(), CommunityMessage.id.asc())
        .all()
    )


@router.post(
    "/{community_id}/messages",
    response_model=CommunityMessageResponse,
    status_code=201,
)
def send_community_message(
    community_id: int,
    payload: CommunityMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    verify_membership(community_id, current_user.id, db)

    content = payload.content.strip()
    if not content:
        raise HTTPException(
            status_code=422,
            detail="Message cannot be empty.",
        )

    message = CommunityMessage(
        community_id=community_id,
        sender_id=current_user.id,
        content=content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message
