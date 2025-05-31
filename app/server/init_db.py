import asyncio

from models import Base, User
from sqlalchemy import select

from database import engine, async_session


async def init_db() -> None:
    """Создание базы данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def add_test_user() -> None:
    """Добавление тестовых пользователей в базу данных"""
    async with async_session() as session:
        existing_users = await session.execute(select(User.name))
        existing_users_names = set(existing_users.scalars().all())
        new_users = [
            User(name='test_user', api_key='test'),
            User(name='222_user', api_key='222'),
            User(name='333_user', api_key='333'),
        ]
        for user in new_users:
            if user.name not in existing_users_names:
                session.add_all(user)
                await session.commit()


async def main() -> None:
    """Инициализация базы банных"""
    await init_db()
    await add_test_user()


if __name__ == '__main__':
    asyncio.run(main())
