import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

# def get_database_url() -> str:
#     """Получение адреса базы данных"""
#
#     if os.environ.get('ENV') == 'test':
#         url_engine = os.getenv('DATABASE_URL_TEST')
#     else:
#         url_engine = os.getenv('DATABASE_URL')
#     return url_engine

db_url = os.getenv('DATABASE_URL')
if not db_url:
    raise ValueError("DB_URL не установлен в переменных окружения")

engine = create_async_engine(url=db_url, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
session = async_session()
