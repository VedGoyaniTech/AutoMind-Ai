from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.repositories.chat_repo import ChatRepository
from app.schemas.chat import ConversationResponse, MessageResponse
from app.api.v1.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/conversations", tags=["Conversations"])

@router.get("", response_model=List[ConversationResponse])
def get_user_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = ChatRepository(db)
    convs = repo.get_user_conversations(current_user.id)
    res = []
    for c in convs:
        res.append(
            ConversationResponse(
                id=c.id,
                title=c.title,
                created_at=c.created_at,
                updated_at=c.updated_at,
                message_count=len(c.messages)
            )
        )
    return res

@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = ChatRepository(db)
    c = repo.create_conversation(user_id=current_user.id)
    return ConversationResponse(
        id=c.id,
        title=c.title,
        created_at=c.created_at,
        updated_at=c.updated_at,
        message_count=0
    )

@router.get("/{id}/messages", response_model=List[MessageResponse])
def get_conversation_messages(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = ChatRepository(db)
    conv = repo.get_conversation_by_id(id, current_user.id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    msgs = repo.get_messages(id)
    return [
        MessageResponse(
            id=m.id,
            conversation_id=m.conversation_id,
            role=m.role,
            content=m.content,
            metadata=m.message_metadata,
            created_at=m.created_at
        ) for m in msgs
    ]

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = ChatRepository(db)
    success = repo.delete_conversation(id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return None
