from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Community, CommunityMember, CommunityMessage, User
from app.schemas import CommunityMessageCreate, CommunityMessageResponse
from app.routers.users import get_current_user

router = APIRouter(prefix="/communities", tags=["Community Chat"])


def verify_membership(community_id: int, user_id: int, db: Session):
    community = db.query(Community).filter(
        Community.id == community_id,
        Community.is_active.is_(True),
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


def serialize_message(message: CommunityMessage, sender: User):
    return {
        "id": message.id,
        "community_id": message.community_id,
        "sender_id": message.sender_id,
        "sender_username": sender.username,
        "sender_full_name": sender.full_name,
        "content": message.content,
        "created_at": message.created_at,
    }


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

    rows = (
        db.query(CommunityMessage, User)
        .join(User, CommunityMessage.sender_id == User.id)
        .filter(CommunityMessage.community_id == community_id)
        .order_by(CommunityMessage.created_at.asc(), CommunityMessage.id.asc())
        .all()
    )

    return [
        serialize_message(message, sender)
        for message, sender in rows
    ]


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

    return serialize_message(message, current_user)