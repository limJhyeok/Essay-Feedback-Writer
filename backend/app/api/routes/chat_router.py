import asyncio
import json
import os
import shutil
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.api.deps import CurrentUser, SessionDep
from app.api.utils import chat_utils
from app.crud import chat_crud
from app.definitions import ROOT_DIR
from app.models import Bot
from app.schemas import chat_schema

router = APIRouter()

EMPTY_CHAT_SESSION_ID = -1
DELEAY_SECONDS_FOR_STREAM = 0.0001

EEVE_KOREAN_MAX_TOKENS = 4096
EEVE_KOREAN_BUFFER_TOKENS = 96

UPLOAD_DIRECTORY = os.path.join(ROOT_DIR, "user-upload")


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
        # TODO: refactoring?(모듈화): create_chat과 매우 비슷
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


@router.post("/generate-answer", status_code=status.HTTP_201_CREATED)
async def generate_answer(
    generate_answer_request: chat_schema.GenerateAnswerRequest,
    db: SessionDep,
) -> StreamingResponse:
    # TODO: bot에 따라 다르게 모델 불러오는 Logic 필요
    chat_session_id = generate_answer_request.chat_session_id
    question = generate_answer_request.question

    bot = chat_crud.get_bot(db, generate_answer_request.bot_id)
    llm = chat_utils.get_llm()

    token_trimmer = chat_utils.get_token_trimmer(
        model=llm, max_tokens=EEVE_KOREAN_MAX_TOKENS - EEVE_KOREAN_BUFFER_TOKENS
    )
    return StreamingResponse(
        stream_answer(
            llm,
            question,
            chat_session_id,
            db,
            bot,
            token_trimmer,
            DELEAY_SECONDS_FOR_STREAM,
        ),
        media_type="text/event-stream",
    )


@router.post("/{chat_session_id}/upload-pdf/")
async def upload_pdf(chat_session_id: int, file: UploadFile = File(...)) -> dict:
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    splits = chat_utils.load_and_split_documents(file_path)
    retriever = chat_utils.create_vectorstore_and_retriever(splits)
    chat_utils.retriever_store[chat_session_id] = retriever
    return {"filename": file.filename, "status": "processed"}


async def stream_answer(
    llm: ChatOllama,
    question: str,
    chat_session_id: int,
    db: SessionDep,
    bot: Bot,
    token_trimmer: list[BaseMessage],
    delay_seconds_for_stream: float,
):
    chat_session_init_result = await chat_utils.ensure_chat_session_initialized(
        chat_session_id, db
    )
    retriever = chat_utils.retriever_store.get(chat_session_id)
    config = {"configurable": {"session_id": f"{chat_session_id}"}}
    if retriever is not None:
        history_aware_retriever = chat_utils.create_history_aware_retriever_chain(
            llm, retriever
        )
        chain = chat_utils.create_rag_chain(llm, history_aware_retriever)
        with_message_history_keys = {
            "input_messages_key": "input",
            "history_messages_key": "chat_history",
            "output_messages_key": "answer",
        }
        message_history_inputs = {
            "input": question,
        }
    else:
        prompt = chat_utils.get_prompt()
        with_message_history_keys = {
            "input_messages_key": "messages",
        }
        chain = chat_utils.create_chain_with_trimmer(token_trimmer, prompt, llm)
        # TODO: 대화이력 기반 chatbot refactoring 필요
        if chat_session_init_result == "initialized":
            messages = chat_utils.chat_session_store[chat_session_id].messages
        else:
            messages = [HumanMessage(content=question)]
        message_history_inputs = {"messages": messages}

    with_message_history = RunnableWithMessageHistory(
        chain,
        chat_utils.get_chat_session_history_from_dict,
        **with_message_history_keys,
    )

    final_response = ""
    for response in with_message_history.stream(message_history_inputs, config=config):
        answer = response.get("answer") if retriever is not None else response.content
        if answer:
            final_response += answer
            yield (
                json.dumps({"status": "processing", "data": answer}, ensure_ascii=False)
                + "\n"
            )
            await asyncio.sleep(delay_seconds_for_stream)
    await save_bot_conversation(
        db=db,
        chat_session_id=chat_session_id,
        message=final_response,
        sender_id=bot.id if bot else 1,
    )
    yield (
        json.dumps(
            {"status": "complete", "data": "Stream finished"}, ensure_ascii=False
        )
        + "\n"
    )


async def save_bot_conversation(
    db: SessionDep, chat_session_id: int, message: str, sender_id: int
) -> None:
    bot_conversation_create = chat_schema.ConversationCreate(
        chat_session_id=chat_session_id,
        sender="bot",
        message=message,
        sender_id=sender_id,
    )
    chat_crud.create_conversation(db, bot_conversation_create)
