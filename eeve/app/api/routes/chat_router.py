import asyncio
import json
import logging
import os
import shutil

import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.api.deps import SessionDep
from app.api.utils import chat_utils
from app.definitions import ROOT_DIR
from app.schemas import chat_schema

logger = logging.getLogger(__name__)

router = APIRouter()

# EMPTY_CHAT_SESSION_ID = -1
DELEAY_SECONDS_FOR_STREAM = 0.0001

EEVE_KOREAN_MAX_TOKENS = 4096
EEVE_KOREAN_BUFFER_TOKENS = 96

UPLOAD_DIRECTORY = os.path.join(ROOT_DIR, "user-upload")


@router.post("/generate-answer", status_code=status.HTTP_201_CREATED)
async def generate_answer(
    generate_answer_request: chat_schema.GenerateAnswerRequest,
    db: SessionDep,
) -> StreamingResponse:
    # TODO: bot에 따라 다르게 모델 불러오는 Logic 필요
    chat_session_id = generate_answer_request.chat_session_id
    question = generate_answer_request.question
    bot_id = generate_answer_request.bot_id

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
            bot_id,
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
    bot_id: int,
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
    bot_answer = {
        "chat_session_id": chat_session_id,
        "sender": "bot",
        "message": final_response,
        "sender_id": bot_id,
    }

    """
    API call to save the AI response in the database
    Backend API URL: http://{backend_container_name}:{port}/api/v1/chat/session/bot
    HTTP Method: POST
    Request Payload:
    {
        "chat_session_id": str,  # Chat session ID
        "sender": str,           # Sender of the message (e.g., "user" or "bot")
        "message": str,          # AI's response message
        "sender_id": int         # Sender ID (ID of user or bot)
    }
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://backend:8000/api/v1/chat/session/bot",
                json=bot_answer,
                timeout=10,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Save AI Response in DB failed: {e.response.status_code} - {e.response.text}"
            )
            raise HTTPException(
                status_code=e.response.status_code,
                detail="Save AI Response in DB failed",
            )

    yield (
        json.dumps(
            {"status": "complete", "data": "Stream finished"}, ensure_ascii=False
        )
        + "\n"
    )
