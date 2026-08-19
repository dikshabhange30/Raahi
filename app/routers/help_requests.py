from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import HelpRequest, CommunityMember, User, Conversation, Notification
from app.oauth2 import get_current_user
from app.schemas import HelpRequestCreate, HelpRequestResponse

from datetime import datetime, timezone


router = APIRouter(
    prefix="/help-requests",
    tags=["Help Requests"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "/",
    response_model=HelpRequestResponse
)
def create_help_request(
    request_data: HelpRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    membership = db.query(CommunityMember).filter(
        CommunityMember.community_id == request_data.community_id,
        CommunityMember.user_id == current_user.user_id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You must join the community first"
        )

    if request_data.helper_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot request help from yourself"
        )

    helper_membership = db.query(CommunityMember).filter(
        CommunityMember.community_id == request_data.community_id,
        CommunityMember.user_id == request_data.helper_id
    ).first()

    if not helper_membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected helper is not a member of this community"
        )

    help_request = HelpRequest(
        community_id=request_data.community_id,
        needer_id=current_user.user_id,
        helper_id=request_data.helper_id,
        message=request_data.message,
        status="pending"
    )

    db.add(help_request)
    db.commit()
    db.refresh(help_request)

    notification = Notification(
        user_id=help_request.helper_id,
        title="New Help Request",
        message=f"{current_user.username} requested your help.",
        notification_type="help_request"
    )
    
    db.add(notification)
    db.commit()

    return help_request

@router.get("/my")
def get_my_help_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    requests = db.query(HelpRequest).filter(
        (
            (HelpRequest.needer_id == current_user.user_id)
            |
            (HelpRequest.helper_id == current_user.user_id)
        )
    ).order_by(
        HelpRequest.created_at.desc()
    ).all()

    return requests

@router.post(
    "/{help_request_id}/accept",
    response_model=HelpRequestResponse
)
def accept_help_request(
    help_request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    help_request = db.query(HelpRequest).filter(
        HelpRequest.help_request_id == help_request_id
    ).first()

    if not help_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Help request not found"
        )

    if help_request.helper_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the selected helper can accept this request"
        )

    if help_request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Help request is no longer pending"
        )

    help_request.status = "accepted"
    help_request.responded_at = datetime.now(timezone.utc)

    notification = Notification(
    user_id=help_request.needer_id,
    title="Help Request Accepted",
    message=f"{current_user.username} accepted your help request.",
    notification_type="help_request_accepted"
)

    db.add(notification)

    conversation = Conversation(
    help_request_id=help_request.help_request_id
)

    db.add(conversation)

    db.commit()
    db.refresh(help_request)

    return help_request

@router.post("/{help_request_id}/reject")
def reject_help_request(
    help_request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    help_request = db.query(HelpRequest).filter(
        HelpRequest.help_request_id == help_request_id
    ).first()

    if not help_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Help request not found"
        )

    if help_request.helper_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the selected helper can reject this request"
        )

    if help_request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Help request is no longer pending"
        )

    help_request.status = "rejected"
    help_request.responded_at = datetime.now(timezone.utc)

    notification = Notification(
    user_id=help_request.needer_id,
    title="Help Request Rejected",
    message=f"{current_user.username} rejected your help request.",
    notification_type="help_request_rejected"
)

    db.add(notification)

    db.commit()
    db.refresh(help_request)

    return help_request