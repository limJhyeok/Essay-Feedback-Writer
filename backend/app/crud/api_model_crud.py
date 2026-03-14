from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud import ai_provider_crud, bot_crud
from app.models import APIModel, AIProvider
from app.schemas import api_model_schema


async def get_api_model_by_alias(
    db: AsyncSession, alias: str
) -> api_model_schema.APIModel:
    result = await db.execute(select(APIModel).where(APIModel.alias == alias))
    return result.scalars().first()


async def get_api_models_by_provider(
    db: AsyncSession, provider_name: str
) -> list[api_model_schema.APIModel]:
    result = await db.execute(
        select(APIModel).join(AIProvider).where(AIProvider.name == provider_name)
    )
    return result.scalars().all()


async def get_api_model_by_name_and_provider(
    db: AsyncSession, api_model_name: str, provider_name: str
) -> api_model_schema.APIModel | None:
    result = await db.execute(
        select(APIModel)
        .options(selectinload(APIModel.bot))
        .join(AIProvider)
        .where(
            and_(
                AIProvider.name == provider_name,
                APIModel.api_model_name == api_model_name,
            )
        )
    )
    return result.scalars().first()


async def create_api_model(
    db: AsyncSession, api_model_create: api_model_schema.APIModelCreate
) -> api_model_schema.APIModel:
    bot = await bot_crud.get_bot_by_name(db, api_model_create.alias)
    provider = await ai_provider_crud.get_provider_by_name(
        db, api_model_create.provider_name
    )
    new_api_model = APIModel(
        bot_id=bot.id,
        provider_id=provider.id,
        api_model_name=api_model_create.api_model_name,
        alias=api_model_create.alias,
    )

    db.add(new_api_model)
    await db.commit()
    await db.refresh(new_api_model)

    return api_model_schema.APIModel.from_orm(new_api_model)
