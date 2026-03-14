from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models import User
from app.schemas import user_schema


async def create_user(db: AsyncSession, user_create: user_schema.UserCreate) -> None:
    db_user = User(
        email=user_create.email,
        is_superuser=user_create.is_superuser,
        password=get_password_hash(user_create.password),
    )
    db.add(db_user)
    await db.commit()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def update_user_password(db: AsyncSession, user: User, new_password: str) -> None:
    user.password = new_password
    await db.commit()


async def authenticate(db: AsyncSession, email: str, password: str) -> User | None:
    db_user = await get_user_by_email(db=db, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.password):
        return None
    return db_user
