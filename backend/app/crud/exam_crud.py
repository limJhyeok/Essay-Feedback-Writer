from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import DomainType, Exam, ExamQuestion, Prompt


async def get_exams(
    db: AsyncSession,
    university: Optional[str] = None,
    year: Optional[int] = None,
    track: Optional[str] = None,
) -> list[Exam]:
    stmt = select(Exam)
    if university:
        stmt = stmt.where(Exam.university == university)
    if year:
        stmt = stmt.where(Exam.year == year)
    if track:
        stmt = stmt.where(Exam.track == track)
    stmt = stmt.order_by(Exam.year.desc(), Exam.university)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_exam_by_id(db: AsyncSession, exam_id: int) -> Optional[Exam]:
    stmt = (
        select(Exam)
        .where(Exam.id == exam_id)
        .options(selectinload(Exam.questions).selectinload(ExamQuestion.prompt))
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_questions_by_exam_id(
    db: AsyncSession, exam_id: int
) -> list[ExamQuestion]:
    stmt = (
        select(ExamQuestion)
        .where(ExamQuestion.exam_id == exam_id)
        .order_by(ExamQuestion.question_number)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_ksat_prompts(db: AsyncSession) -> list[Prompt]:
    stmt = select(Prompt).where(Prompt.domain == DomainType.ksat).order_by(Prompt.id)
    result = await db.execute(stmt)
    return result.scalars().all()
