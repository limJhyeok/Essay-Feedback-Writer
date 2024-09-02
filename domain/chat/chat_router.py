from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from domain.chat import chat_crud, chat_schema, chat_utils
from domain.user import user_router
from models import User
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
import asyncio
import json
from operator import itemgetter
from langchain_core.runnables import RunnablePassthrough
router = APIRouter(
    prefix = "/api/chat"
)

EMPTY_CHAT_SESSION_ID = -1
DELEAY_SECONDS_FOR_STREAM = 0.0001

EEVE_KOREAN_MAX_TOKENS = 4096
EEVE_KOREAN_BUFFER_TOKENS = 96

@router.get("/titles")
def get_chat_history_titles(current_user: User = Depends(user_router.get_current_user), db: Session = Depends(get_db)):
    db_chat_sessions = chat_crud.get_chat_session_histories(db, current_user.id)
    if not db_chat_sessions:
        return []
    
    chat_session_titles = [{'id': db_chat_session.id, 'name': db_chat_session.title} for db_chat_session in db_chat_sessions]
    return chat_session_titles

@router.get("/session/{chat_session_id}")
def get_conversations(chat_session_id: int, db: Session = Depends(get_db), current_user: User = Depends(user_router.get_current_user)):
    res = {"message_history": {
        "messages": []
        }
    }
    if chat_session_id == EMPTY_CHAT_SESSION_ID:
        return res

    db_conversations = chat_crud.get_conversations(db, chat_session_id)
    if db_conversations:
        res["message_history"]["messages"] = [{"sender": db_conversation.sender, "text": db_conversation.message} for db_conversation in db_conversations]
    return res


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_chat(chat_session_create_request: chat_schema.ChatSessionCreateRequest,
                db: Session = Depends(get_db),
                current_user: User = Depends(user_router.get_current_user)):
    chat_session_create = chat_schema.ChatSessionCreate(
        user_id = current_user.id,
        title = chat_session_create_request.title
    )
    chat_crud.create_chat_session(
        db = db,
        chat_session_create = chat_session_create
    )


@router.post("/session", status_code=status.HTTP_201_CREATED)
def post_user_conversation(user_chat_session_create_request: chat_schema.UserChatSessionCreateRequest,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(user_router.get_current_user)):
    chat_session = chat_crud.get_chat_session(db, user_chat_session_create_request.chat_session_id)
    if not chat_session:
        # TODO: refactoring?(모듈화): create_chat과 매우 비슷
        # TODO: user_chat_session_create_request.message와 AI를 이용하여 chat의 title 부여한 후에 ChatCreate 만들기
        chat_session_create = chat_schema.ChatSessionCreate(
        user_id = current_user.id,
        )
        db_chat_session = chat_crud.create_chat_session(
            db=db,
            chat_session_create=chat_session_create
        )
        user_chat_session_create_request.chat_session_id = db_chat_session.id

    conversation_create = chat_schema.ConversationCreate(
        sender_id = current_user.id,
        chat_session_id = user_chat_session_create_request.chat_session_id,
        sender = user_chat_session_create_request.sender,
        message = user_chat_session_create_request.message
    )
    chat_crud.create_conversation(
        db=db,
        conversation_create=conversation_create
    )

from langchain_core.runnables.history import RunnableWithMessageHistory
@router.post("/generate-answer", status_code=status.HTTP_201_CREATED)
async def generate_answer(generate_answer_request: chat_schema.GenerateAnswerRequest, db: Session = Depends(get_db)):
    # TODO: bot에 따라 다르게 모델 불러오는 Logic 필요
    chat_session_id = generate_answer_request.chat_session_id
    question = generate_answer_request.question

    bot = chat_crud.get_bot(db, generate_answer_request.bot_id)
    llm = get_llm()
    prompt = get_prompt()
    token_trimmer = chat_utils.get_token_trimmer(model = llm, max_tokens = EEVE_KOREAN_MAX_TOKENS - EEVE_KOREAN_BUFFER_TOKENS)
    async def stream_answer(llm, prompt, question):
        if chat_session_id not in chat_utils.chat_session_store or not chat_utils.chat_session_store[chat_session_id].messages:
            chat_utils.get_chat_session_history_from_db(chat_utils.chat_session_store, db, chat_session_id)
            messages = chat_utils.chat_session_store[chat_session_id].messages
        else:
            messages = [HumanMessage(content=question)]
        
        config = {"configurable": {"session_id": f"{chat_session_id}"}}        
        chain = (
                RunnablePassthrough.assign(messages= itemgetter("messages") | token_trimmer)
                | prompt
                | llm
            )
        with_message_history = RunnableWithMessageHistory(chain, chat_utils.get_chat_session_history_from_dict, 
                                                          input_messages_key="messages")
        
        final_response = ""
        for response in with_message_history.stream({"messages": messages},
                                                    config = config):
            final_response += response.content
            yield json.dumps({"status": "processing", "data": response.content}, ensure_ascii=False) + "\n"
            await asyncio.sleep(DELEAY_SECONDS_FOR_STREAM) # 모델 처리속도가 한번에 너무 빨라서 글을 쓰는것 같은 효과를 주지 못함
        await save_bot_conversation(db = db,
                          chat_session_id = chat_session_id,
                          message = final_response,
                          sender_id = bot.id)
        yield json.dumps({"status": "complete", "data": "Stream finished"}, ensure_ascii=False) + "\n"
    return StreamingResponse(stream_answer(llm, prompt,question),
                             media_type = "text/event-stream")


async def save_bot_conversation(db, chat_session_id, message, sender_id):
    bot_conversation_create = chat_schema.ConversationCreate(
        chat_session_id=chat_session_id,
        sender='bot',
        message=message,
        sender_id=sender_id
    )
    chat_crud.create_conversation(db, bot_conversation_create)

def get_prompt():
    prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
    )
    return prompt

def get_llm():
    llm = ChatOllama(
        model="EEVE-Korean-10.8B:latest"
        )
    return llm