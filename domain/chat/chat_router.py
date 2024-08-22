from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from domain.chat import chat_crud
from domain.chat import chat_schema
from domain.user import user_router
from models import User
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage


router = APIRouter(
    prefix = "/api/chat"
)

EMPTY_CHAT_ID = -1

@router.get("/titles")
def get_chat_history_titles(current_user: User = Depends(user_router.get_current_user), db: Session = Depends(get_db)):
    db_chat_titles = chat_crud.get_chat_histories(db, current_user.id)
    if not db_chat_titles:
        return []
    
    chat_titles = [{'id': db_chat_title.id, 'name': db_chat_title.title} for db_chat_title in db_chat_titles]
    return chat_titles

@router.get("/session/{chat_id}")
def get_chat_session_messages(chat_id: int, db: Session = Depends(get_db), current_user: User = Depends(user_router.get_current_user)):
    res = {"message_history": {
        "messages": []
        }
    }
    if chat_id == EMPTY_CHAT_ID:
        return res

    db_chat_sessions = chat_crud.get_chat_sessions(db, chat_id)
    if db_chat_sessions:
        res["message_history"]["messages"] = [{"sender": db_chat_session.sender, "text": db_chat_session.message} for db_chat_session in db_chat_sessions]
    return res


@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_chat(chat_create_request: chat_schema.ChatCreateRequest,
                db: Session = Depends(get_db),
                current_user: User = Depends(user_router.get_current_user)):
    _chat_create = chat_schema.ChatCreate(
        user_id = current_user.id,
        title = chat_create_request.title
    )
    chat_crud.create_chat(
        db = db,
        _chat_create = _chat_create
    )


@router.post("/session", status_code=status.HTTP_201_CREATED)
def post_chat_session(user_chat_session_create_request: chat_schema.UserChatSessionCreateRequest,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(user_router.get_current_user)):
    chat = chat_crud.get_chat(db, user_chat_session_create_request.chat_id)
    if not chat:
        # TODO: refactoring?(모듈화): create_chat과 매우 비슷
        # TODO: user_chat_session_create_request.message와 AI를 이용하여 chat의 title 부여한 후에 ChatCreate 만들기
        _chat_create = chat_schema.ChatCreate(
        user_id = current_user.id,
        )
        db_chat = chat_crud.create_chat(
            db=db,
            _chat_create=_chat_create
        )
        user_chat_session_create_request.chat_id = db_chat.id

    _chat_session_create = chat_schema.ChatSessionCreate(
        sender_id = current_user.id,
        chat_id = user_chat_session_create_request.chat_id,
        sender = user_chat_session_create_request.sender,
        message = user_chat_session_create_request.message
    )
    chat_crud.create_chat_session(
        db=db,
        _chat_session_create=_chat_session_create
    )


@router.post("/generate-answer", status_code=status.HTTP_201_CREATED)
async def generate_answer(generate_answer_request: chat_schema.GenerateAnswerRequest, db: Session = Depends(get_db)):
    # TODO: bot에 따라 다르게 모델 불러오는 Logic 필요
    bot = chat_crud.get_bot(db, generate_answer_request.bot_id)

    llm = get_llm()
    prompt = get_prompt()
    final_response = ""
    async def stream_answer(llm, prompt, question):
        chain = prompt | llm
        nonlocal final_response
        async for response in chain.astream({"messages": [HumanMessage(content=question)]}):
            final_response += response.content
            yield response.content + "\n"
            # await asyncio.sleep(0.05) # 타이핑 효과를 위해 지연
    streaming_response = StreamingResponse(stream_answer(llm, prompt, generate_answer_request.question),
                                           media_type="text/event-stream")
    async def save_chat_session_in_streaming(streaming_response: StreamingResponse):
        async for chunk in streaming_response.body_iterator:
            yield chunk
        chat_session_create = chat_schema.ChatSessionCreate(
            chat_id=generate_answer_request.chat_id,
            sender='bot',
            message=final_response,
            sender_id=bot.id
        )
        chat_crud.create_chat_session(db, chat_session_create)
    
    return StreamingResponse(save_chat_session_in_streaming(streaming_response), media_type="text/event-stream")

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