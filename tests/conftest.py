import os
os.environ["ENV"] = "test"
from typing import AsyncGenerator
import asyncio
import pytest
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

load_dotenv()

if os.getenv("ENV") == "test":
    from python_advanced_diploma.app.server.main import app as _app
    from python_advanced_diploma.app.server.models import Base, User

    url_engine = os.getenv("DATABASE_URL_TEST")
    if not url_engine:
        raise ValueError("URL для тестовой базы данных не установлен")

    engine = create_async_engine(url_engine, poolclass=NullPool)
    async_session = async_sessionmaker(
        expire_on_commit=False,
        bind=engine,
    )

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        """
        Переопределяет зависимость получения сессии для тестирования.

        Возвращает:
            AsyncGenerator[AsyncSession, None]: Асинхронный генератор сессии базы данных.
        """
        async with async_session() as s:
            yield s


    @pytest.fixture(scope="session", autouse=True)
    async def setup_test_db() -> AsyncGenerator[None, None]:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
        except Exception as e:
            print(f"Ошибка при delete таблиц: {e}")
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")

        async with async_session() as s:
            new_test_user = User(name="test_user", api_key="test")
            new_222_user = User(name="222_user", api_key="222")
            new_333_user = User(name="333_user", api_key="333")

            new_users = [new_test_user, new_222_user, new_333_user]
            s.add_all(new_users)

            await s.commit()
            await s.refresh(new_test_user)

        yield


    @pytest.fixture
    async def session() -> AsyncGenerator[AsyncSession, None]:
        """
        Создает новую асинхронную сессию для тестов.

        Возвращает:
            AsyncGenerator[AsyncSession, None]: Асинхронный генератор сессии базы данных.
        """
        async with async_session() as s:
            yield s

    @pytest.fixture
    async def client() -> AsyncGenerator[AsyncClient, None]:
        """
        Создает асинхронного клиента для тестирования HTTP-запросов.

        Возвращает:
            AsyncGenerator[AsyncClient, None]: Асинхронный клиент для выполнения запросов к приложению.
        """
        async with AsyncClient(transport=ASGITransport(app=_app)) as c:
            yield c

    @pytest.fixture(scope="session")
    def event_loop():
        loop = asyncio.get_event_loop_policy().new_event_loop()
        yield loop
        loop.close()