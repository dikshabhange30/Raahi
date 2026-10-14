



from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import HelpRequest, CommunityMember, User, Community
from app.schemas import HelpRequestCreate, HelpRequestResponse
from app.routers.users import get_current_user



router = APIRouter(
    prefix="/help-requests",
    tags=["Help Requests"],
)


@router.post(
    "/",
    response_model=HelpRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_help_request(
    payload: HelpRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.recipient_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot send a help request to yourself.",
        )

    community = db.query(Community).filter(
        Community.id == payload.community_id,
        Community.is_active == True,
    ).first()

    if not community:
        raise HTTPException(
            status_code=404,
            detail="Active community not found.",
        )

    recipient = db.query(User).filter(
        User.id == payload.recipient_id,
        User.is_active == True,
    ).first()

    if not recipient:
        raise HTTPException(
            status_code=404,
            detail="Recipient not found or inactive.",
        )

    sender_membership = db.query(CommunityMember).filter(
        CommunityMember.user_id == current_user.id,
        CommunityMember.community_id == payload.community_id,
    ).first()

    recipient_membership = db.query(CommunityMember).filter(
        CommunityMember.user_id == payload.recipient_id,
        CommunityMember.community_id == payload.community_id,
    ).first()

    if not sender_membership or not recipient_membership:
        raise HTTPException(
            status_code=403,
            detail="Both users must belong to this community.",
        )

    if not payload.message.strip():
        raise HTTPException(
            status_code=422,
            detail="Message cannot be empty.",
        )

    help_request = HelpRequest(
        sender_id=current_user.id,
        recipient_id=payload.recipient_id,
        community_id=payload.community_id,
        message=payload.message.strip(),
        status="pending",
    )

    db.add(help_request)
    db.commit()
    db.refresh(help_request)

    return help_request


@router.get("/sent", response_model=list[HelpRequestResponse])
def get_sent_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(HelpRequest)
        .filter(HelpRequest.sender_id == current_user.id)
        .order_by(HelpRequest.created_at.desc())
        .all()
    )


@router.get("/received", response_model=list[HelpRequestResponse])
def get_received_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(HelpRequest)
        .filter(HelpRequest.recipient_id == current_user.id)
        .order_by(HelpRequest.created_at.desc())
        .all()
    )


@router.patch("/{request_id}/accept", response_model=HelpRequestResponse)
def accept_help_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    help_request = db.get(HelpRequest, request_id)

    if not help_request:
        raise HTTPException(
            status_code=404,
            detail="Help request not found.",
        )

    if help_request.recipient_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the recipient can accept this request.",
        )

    if help_request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="This request has already been processed.",
        )

    help_request.status = "accepted"
    db.commit()
    db.refresh(help_request)

    return help_request


@router.patch("/{request_id}/reject", response_model=HelpRequestResponse)
def reject_help_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    help_request = db.get(HelpRequest, request_id)

    if not help_request:
        raise HTTPException(
            status_code=404,
            detail="Help request not found.",
        )

    if help_request.recipient_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only the recipient can reject this request.",
        )

    if help_request.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="This request has already been processed.",
        )

    help_request.status = "rejected"
    db.commit()
    db.refresh(help_request)

    return help_request
