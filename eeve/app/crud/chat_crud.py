import logging

from sqlalchemy import text
from sqlalchemy.orm import Session

# from app.models import Conversation

logger = logging.getLogger(__name__)


def get_conversations(db: Session, chat_session_id: int) -> list:
    query = text(
        """
        SELECT * FROM conversation
        WHERE chat_session_id = :chat_session_id
        ORDER BY id ASC
    """
    )
    result = db.execute(query, {"chat_session_id": chat_session_id})
    conversations = result.fetchall()

    return conversations
