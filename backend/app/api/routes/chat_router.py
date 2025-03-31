from typing import Any

from fastapi import APIRouter, HTTPException, status
from app.api.deps import CurrentUser, SessionDep
from app.crud import chat_crud
from app.schemas import chat_schema

router = APIRouter()

EMPTY_CHAT_SESSION_ID = -1
DELEAY_SECONDS_FOR_STREAM = 0.0001

EEVE_KOREAN_MAX_TOKENS = 4096
EEVE_KOREAN_BUFFER_TOKENS = 96


@router.get("/titles", response_model=chat_schema.ChatSessionTitleList)
def get_chat_history_titles(
    db: SessionDep,
    current_user: CurrentUser,
) -> Any:
    db_chat_sessions = chat_crud.get_chat_sessions(db, current_user.id)
    chat_sessions_public = [
        chat_schema.ChatSessionTitle.from_orm(session) for session in db_chat_sessions
    ]
    return chat_schema.ChatSessionTitleList(data=chat_sessions_public)


@router.get("/recent", response_model=chat_schema.ChatSessionId)
def get_recent_chat_session_id(
    db: SessionDep,
    current_user: CurrentUser,
) -> dict:
    recent_chat_session = chat_crud.get_recent_chat_session(db, current_user.id)
    return recent_chat_session


@router.get(
    "/session/{chat_session_id}", response_model=chat_schema.ChatSessionMessageList
)
def get_chat_session_message_list(
    chat_session_id: int, db: SessionDep
) -> chat_schema.ChatSessionMessageList:
    if chat_session_id == EMPTY_CHAT_SESSION_ID:
        return chat_schema.ChatSessionMessageList(data=[])

    db_conversations = chat_crud.get_conversations(db, chat_session_id)
    chat_session_messages = [
        chat_schema.ChatSessionMessage(
            sender=db_conversation.sender, text=db_conversation.message
        )
        for db_conversation in db_conversations
    ]
    return chat_schema.ChatSessionMessageList(data=chat_session_messages)


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_chat(
    chat_session_create_request: chat_schema.ChatSessionCreateRequest,
    db: SessionDep,
    current_user: CurrentUser,
) -> None:
    chat_session_create = chat_schema.ChatSessionCreate(
        user_id=current_user.id, title=chat_session_create_request.title
    )
    chat_crud.create_chat_session(db=db, chat_session_create=chat_session_create)


@router.put("/rename/{chat_session_id}")
def rename_chat_session(
    chat_session_id: int,
    chat_session_update_request: chat_schema.ChatSessionUpdateRequest,
    db: SessionDep,
) -> None:
    chat_session = chat_crud.get_chat_session(db, chat_session_id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="chat session not found")

    chat_crud.update_chat_session(db, chat_session, chat_session_update_request)


@router.delete("/delete/{chat_session_id}")
def delete_chat(chat_session_id: int, db: SessionDep) -> None:
    chat_session = chat_crud.get_chat_session(db, chat_session_id)
    if chat_session is None:
        raise HTTPException(status_code=404, detail="chat session not found")

    chat_crud.delete_chat_session(db, chat_session)


@router.post("/session", status_code=status.HTTP_201_CREATED)
def post_user_conversation(
    user_chat_session_create_request: chat_schema.UserChatSessionCreateRequest,
    db: SessionDep,
    current_user: CurrentUser,
) -> None:
    chat_session = chat_crud.get_chat_session(
        db, user_chat_session_create_request.chat_session_id
    )
    if not chat_session:
        # TODO: user_chat_session_create_request.message와 AI를 이용하여 chat의 title 부여한 후에 ChatCreate 만들기
        chat_session_create = chat_schema.ChatSessionCreate(
            user_id=current_user.id,
        )
        db_chat_session = chat_crud.create_chat_session(
            db=db, chat_session_create=chat_session_create
        )
        user_chat_session_create_request.chat_session_id = db_chat_session.id

    conversation_create = chat_schema.ConversationCreate(
        sender_id=current_user.id,
        chat_session_id=user_chat_session_create_request.chat_session_id,
        sender=user_chat_session_create_request.sender,
        message=user_chat_session_create_request.message,
    )
    chat_crud.create_conversation(db=db, conversation_create=conversation_create)


@router.post("/session/bot", status_code=status.HTTP_201_CREATED)
async def create_bot_conversation(data: dict, db: SessionDep) -> None:
    bot_answer = chat_schema.ConversationCreate(
        chat_session_id=data["chat_session_id"],
        sender="bot",
        message=data["message"],
        sender_id=data["sender_id"],
    )
    chat_crud.create_conversation(db=db, conversation_create=bot_answer)
