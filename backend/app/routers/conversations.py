



from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Conversation, Message, HelpRequest, User
from app.schemas import (
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from app.routers.users import get_current_user

router = APIRouter(prefix="/conversations", tags=["Private Conversations"])


def get_participant_conversation(
    conversation_id: int,
    user_id: int,
    db: Session,
):
    conversation = db.get(Conversation, conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    if user_id not in (conversation.user_one_id, conversation.user_two_id):
        raise HTTPException(status_code=403, detail="Access denied.")

    return conversation


@router.get("/", response_model=list[ConversationResponse])
def list_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Conversation)
        .filter(
            (Conversation.user_one_id == current_user.id)
            | (Conversation.user_two_id == current_user.id)
        )
        .order_by(Conversation.created_at.desc())
        .all()
    )


@router.post(
    "/from-request/{request_id}",
    response_model=ConversationResponse,
)
def create_conversation(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    help_request = db.get(HelpRequest, request_id)

    if not help_request:
        raise HTTPException(status_code=404, detail="Help request not found.")

    if current_user.id not in (
        help_request.sender_id,
        help_request.recipient_id,
    ):
        raise HTTPException(status_code=403, detail="Access denied.")

    if help_request.status != "accepted":
        raise HTTPException(
            status_code=400,
            detail="The help request must be accepted first.",
        )

    conversation = (
        db.query(Conversation)
        .filter(Conversation.help_request_id == request_id)
        .first()
    )

    if conversation:
        return conversation

    conversation = Conversation(
        help_request_id=request_id,
        user_one_id=help_request.sender_id,
        user_two_id=help_request.recipient_id,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse],
)
def list_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_participant_conversation(conversation_id, current_user.id, db)

    return (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc(), Message.id.asc())
        .all()
    )


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=201,
)
def send_message(
    conversation_id: int,
    payload: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_participant_conversation(conversation_id, current_user.id, db)

    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    message = Message(
        conversation_id=conversation_id,
        sender_id=current_user.id,
        content=content,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message
