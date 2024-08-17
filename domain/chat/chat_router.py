from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from domain.chat import chat_crud
from domain.chat import chat_schema
from domain.user import user_router
from models import User
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
def post_chat_session(_user_chat_sesion_create: chat_schema.UserChatSessionCreate,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(user_router.get_current_user)):
    chat = chat_crud.get_chat(db, _user_chat_sesion_create.chat_id)
    if not chat:
        # TODO: refactoring?(모듈화): create_chat과 매우 비슷
        # TODO: _user_chat_sesion_create.message와 AI를 이용하여 chat의 title 부여한 후에 ChatCreate 만들기
        _chat_create = chat_schema.ChatCreate(
        user_id = current_user.id,
        )
        db_chat = chat_crud.create_chat(
            db=db,
            _chat_create=_chat_create
        )
        _user_chat_sesion_create.chat_id = db_chat.id

    _chat_session_create = chat_schema.ChatSessionCreate(
        user_id = current_user.id,
        chat_id = _user_chat_sesion_create.chat_id,
        sender = "user",
        message = _user_chat_sesion_create.message
    )
    chat_crud.create_chat_session(
        db=db,
        _chat_session_create=_chat_session_create
    )

@router.post("/generate-answer", status_code=status.HTTP_201_CREATED)
def generate_answer(generate_answer_request: chat_schema.GenerateAnswerRequest, db: Session = Depends(get_db)):
    bot = chat_crud.get_bot(db, generate_answer_request.bot_id)
    ####### You should replace the Model to AI model
    class Model:
        def __init__(self):
            pass
        def __call__(self, answer: str, context: list[dict]= None):
            answer = "this is temporary answer"
            if context is not None:
                answer = "following by, this is temporary answer"
            return answer
    model = Model()
    ###############
    if generate_answer_request.context:
        answer = model(generate_answer_request.question, generate_answer_request.context)
    else:
        answer = model(generate_answer_request.question)

    chat_session_create = chat_schema.ChatSessionCreate(
        chat_id = generate_answer_request.chat_id,
        sender = 'bot',
        message = answer,
        sender_id = bot.id
    )
    chat_crud.create_chat_session(db, chat_session_create)
    return answer

    