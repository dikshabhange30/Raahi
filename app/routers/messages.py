
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Conversation, Message, HelpRequest, User
from app.oauth2 import get_current_user
from app.schemas import MessageCreate, MessageResponse


router = APIRouter(
    prefix="/conversations",
    tags=["Messages"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

# send a msg
@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse
)
def send_message(
    conversation_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = db.query(Conversation).filter(
        Conversation.conversation_id == conversation_id,
        Conversation.is_active == True
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    help_request = db.query(HelpRequest).filter(
        HelpRequest.help_request_id == conversation.help_request_id
    ).first()

    if not help_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Help request not found"
        )

    if current_user.user_id not in [
        help_request.needer_id,
        help_request.helper_id
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not part of this conversation"
        )

    new_message = Message(
        conversation_id=conversation_id,
        sender_id=current_user.user_id,
        message=message_data.message
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return new_message

# get conversation msgs
@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse]
)
def get_messages(
    conversation_id: int,
    limit: int = 50,
    before_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if limit > 50:
        limit = 50

    conversation = db.query(Conversation).filter(
        Conversation.conversation_id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    help_request = db.query(HelpRequest).filter(
        HelpRequest.help_request_id == conversation.help_request_id
    ).first()

    if current_user.user_id not in [
        help_request.needer_id,
        help_request.helper_id
    ]:
        raise HTTPException(
            status_code=403,
            detail="You are not part of this conversation"
        )

    query = db.query(Message).filter(
        Message.conversation_id == conversation_id
    )

    if before_id is not None:
        query = query.filter(
            Message.message_id < before_id
        )

    messages = query.order_by(
        Message.message_id.desc()
    ).limit(limit).all()

    return list(reversed(messages))

@router.get("/my")
def get_my_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversations = (
        db.query(Conversation, HelpRequest)
        .join(
            HelpRequest,
            HelpRequest.help_request_id == Conversation.help_request_id
        )
        .filter(
            Conversation.is_active == True,
            (
                (HelpRequest.needer_id == current_user.user_id)
                |
                (HelpRequest.helper_id == current_user.user_id)
            )
        )
        .all()
    )

    result = []

    for conversation, help_request in conversations:

        if help_request.needer_id == current_user.user_id:
            other_user_id = help_request.helper_id
        else:
            other_user_id = help_request.needer_id

        other_user = db.query(User).filter(
            User.user_id == other_user_id
        ).first()

        result.append({
            "conversation_id": conversation.conversation_id,
            "other_user_id": other_user.user_id,
            "other_username": other_user.username,
            "help_request_id": help_request.help_request_id,
            "status": help_request.status,
            "created_at": conversation.created_at
        })

    return result

@router.get("/unread-count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    count = (
        db.query(Message)
        .join(
            Conversation,
            Conversation.conversation_id == Message.conversation_id
        )
        .join(
            HelpRequest,
            HelpRequest.help_request_id == Conversation.help_request_id
        )
        .filter(
            Message.sender_id != current_user.user_id,
            Message.is_read == False,
            Conversation.is_active == True,
            (
                (HelpRequest.needer_id == current_user.user_id)
                |
                (HelpRequest.helper_id == current_user.user_id)
            )
        )
        .count()
    )

    return {
        "unread_count": count
    }