from sqlalchemy import URL
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import (
    create_async_engine, async_sessionmaker
    )

from config import (DATABASE_USERNAME, DATABASE, HOST, PORT, PASSWORD)


database_url = URL.create(
    "postgresql+asyncpg",
    username=DATABASE_USERNAME,
    password=PASSWORD,
    port=PORT,
    host=HOST,
    database=DATABASE,
)


engine = create_async_engine(database_url)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)



    
async def get_db():
    async with AsyncSessionLocal() as db:
        yield db

class Base(DeclarativeBase):
    pass