from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.chat import Conversation, Message

class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_conversation_by_id(self, conversation_id: int, user_id: int) -> Optional[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id, Conversation.user_id == user_id)
            .first()
        )

    def get_user_conversations(self, user_id: int) -> List[Conversation]:
        return (
            self.db.query(Conversation)
            .filter(Conversation.user_id == user_id)
            .order_by(desc(Conversation.updated_at))
            .all()
        )

    def create_conversation(self, user_id: int, title: str = "New Conversation") -> Conversation:
        conv = Conversation(user_id=user_id, title=title)
        self.db.add(conv)
        self.db.commit()
        self.db.refresh(conv)
        return conv

    def update_conversation_title(self, conversation_id: int, title: str) -> Optional[Conversation]:
        conv = self.db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conv:
            conv.title = title
            self.db.commit()
            self.db.refresh(conv)
        return conv

    def delete_conversation(self, conversation_id: int, user_id: int) -> bool:
        conv = self.db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user_id).first()
        if conv:
            self.db.delete(conv)
            self.db.commit()
            return True
        return False

    def add_message(self, conversation_id: int, role: str, content: str, metadata: Optional[dict] = None) -> Message:
        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            message_metadata=metadata
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_messages(self, conversation_id: int) -> List[Message]:
        return (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at)
            .all()
        )
