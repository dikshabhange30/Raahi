

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import GroupMessage, Community, CommunityMember, User
from app.oauth2 import get_current_user
from app.schemas import GroupMessageCreate, GroupMessageResponse


router = APIRouter(
    prefix="/communities",
    tags=["Community Messages"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "/{community_id}/messages",
    response_model=GroupMessageResponse
)
def send_group_message(
    community_id: int,
    message_data: GroupMessageCreate,
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

    membership = db.query(CommunityMember).filter(
        CommunityMember.community_id == community_id,
        CommunityMember.user_id == current_user.user_id,
        CommunityMember.is_active == True
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must join this community first"
        )

    group_message = GroupMessage(
        community_id=community_id,
        sender_id=current_user.user_id,
        message=message_data.message
    )

    db.add(group_message)
    db.commit()
    db.refresh(group_message)

    return group_message

@router.get(
    "/{community_id}/messages",
    response_model=list[GroupMessageResponse]
)
def get_group_messages(
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

    membership = db.query(CommunityMember).filter(
        CommunityMember.community_id == community_id,
        CommunityMember.user_id == current_user.user_id,
        CommunityMember.is_active == True
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must join this community first"
        )

    return db.query(GroupMessage).filter(
        GroupMessage.community_id == community_id
    ).order_by(
        GroupMessage.created_at.asc()
    ).all()