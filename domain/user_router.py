from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User

router = APIRouter(
    prefix = "/api/user"
)

@router.get("/")
def test_user(db: Session = Depends(get_db)):
    pass